from typing import Optional, Tuple, List
from collections import deque
from decimal import Decimal
from enum import IntEnum
import logging
import struct
import csv

from PyQt5 import QtWidgets, QtCore, QtGui
from pyqtgraph import PlotWidget, mkPen, exporters
from vxi11 import vxi11

from irspy.utils import Timer, value_to_user_with_units

import tekvisa_control as tek


class SpecterParameters:
    def __init__(self):
        # Все параметры в Гц
        self.x_start = 0
        self.x_stop = 0

        self.y_start = 0
        self.y_stop = 0

        self.center = 0
        self.span = 0
        self.rbw = 0


class TektronixController(QtCore.QObject):
    # Для автоматического режима
    class TekStatus(IntEnum):
        READY = 0
        WAIT_RESPONSE = 1
        WAIT_OPC = 2

    tektronix_is_ready = QtCore.pyqtSignal()

    DEFAULT_CMD_DELAY_S = 0
    OPC_POLL_DELAY_S = 1

    def __init__(self, a_graph_widget: PlotWidget, a_cmd_tree: dict, a_parent=None):
        super().__init__(parent=a_parent)

        self.spec: Optional[None, vxi11.Device] = None

        self.graph_widget = a_graph_widget
        self.graph_pen = mkPen(color=(255, 0, 0), width=2)

        self.cmd_tree = a_cmd_tree

        self.started = False
        self.current_commands = []
        self.cmd_queue_gen = None
        self.current_cmd_queue: Optional[None, deque] = None
        self.wait_timer = Timer(0)
        self.tek_status = self.TekStatus.READY
        self.save_folder = ""

        self.convert_hz = value_to_user_with_units("Гц")

    def reset(self):
        self.started = False
        self.current_commands = []
        self.cmd_queue_gen = None
        self.current_cmd_queue: Optional[None, deque] = None
        self.wait_timer = Timer(0)
        self.tek_status = self.TekStatus.READY
        self.save_folder = ""

    def connect(self, a_ip: str):
        self.spec = vxi11.Instrument(a_ip)
        self.spec.timeout = 3
        logging.debug("Connected")

    def abort_tektronix(self):
        self.send_cmd(":ABOR")

    def handle_measure_error(self, a_error_msg):
        logging.error("Во время измерения произошла ошибка, измерение будет остановлено")
        logging.error(f"{a_error_msg}")

        self.stop()
        self.tektronix_is_ready.emit()

    @staticmethod
    def parse_cmd(a_cmd) -> Tuple[str, str]:
        cmd_param = a_cmd.split(" ", maxsplit=1)
        cmd, param = cmd_param[0], None
        if len(cmd_param) > 1:
            param = cmd_param[1]
        return cmd, param

    def get_specter_parameters(self) -> SpecterParameters:
        spec_params = SpecterParameters()

        spec_params.y_start = float(self.spec.ask(":DISP:SPEC:Y:OFFS?"))
        spec_params.y_stop = spec_params.y_start + 10 * float(self.spec.ask(":DISP:SPEC:Y:PDIV?"))

        spec_params.x_start = float(self.spec.ask(":DISP:SPEC:X:OFFS?"))
        spec_params.x_stop = spec_params.x_start + 10 * float(self.spec.ask(":DISP:SPEC:X:PDIV?"))

        spec_params.center = float(self.spec.ask(":FREQ:CENT?"))
        spec_params.span = float(self.spec.ask(":FREQ:SPAN?"))
        spec_params.rbw = float(self.spec.ask(":SPEC:BAND?"))

        return spec_params

    def tick(self):
        if self.started:
            if self.wait_timer.check():
                if self.tek_status == self.TekStatus.WAIT_RESPONSE:
                    self.tek_status = self.TekStatus.READY
                    answer = tek.read_answer(self.spec)
                    logging.info(f'Read result - "{answer}"')
                elif self.tek_status == self.TekStatus.WAIT_OPC:
                    if tek.is_operation_completed(self.spec):
                        self.tek_status = self.TekStatus.READY
                    else:
                        self.wait_timer.start(self.OPC_POLL_DELAY_S)
                else:
                    if self.current_cmd_queue:
                        current_cmd = self.current_cmd_queue.pop()
                        cmd, param = self.parse_cmd(current_cmd)

                        logging.debug(f'Current cmd - "{current_cmd}"')
                        self.wait_timer.start(TektronixController.DEFAULT_CMD_DELAY_S)

                        if cmd == tek.SpecCmd.WAIT:
                            if param is not None:
                                self.wait_timer.start(int(param))
                            else:
                                self.handle_measure_error(f"Не задан параметр для команды {tek.SpecCmd.WAIT}")

                        else:
                            tek.send_cmd(self.spec, current_cmd)
                            if cmd == "*OPC":
                                self.tek_status = self.TekStatus.WAIT_OPC

                            elif cmd in (":READ:SPEC?", ":READ:SPECtrum?"):
                                binary_spectrum = tek.read_raw_answer(self.spec)

                                if binary_spectrum:
                                    self.draw_spectrum(binary_spectrum, self.get_specter_parameters())

                            elif "?" in cmd:
                                self.tek_status = self.TekStatus.WAIT_RESPONSE

                                if self.current_cmd_queue:
                                    next_cmd, next_param = self.parse_cmd(self.current_cmd_queue[-1])
                                    if next_cmd == tek.SpecCmd.READ_DELAY:
                                        if next_param is not None:
                                            # Убираем из очереди, т.к. это фиктивная команда
                                            self.current_cmd_queue.pop()
                                            logging.debug(f"Read delay {next_param} sec")
                                            self.wait_timer.start(int(next_param))
                                        else:
                                            self.handle_measure_error(
                                                f"Не задан параметр для команды {tek.SpecCmd.READ_DELAY}")
                                    else:
                                        # Читаем сразу, без дефолтной задержки
                                        self.wait_timer.start(0)
                    else:
                        try:
                            self.current_cmd_queue = next(self.cmd_queue_gen)
                            logging.debug("Следующая очередь команд")
                        except StopIteration:
                            self.stop()
                            self.tektronix_is_ready.emit()

    def send_cmd(self, a_cmd: str, a_read_bytes: bool = False) -> bool:
        result = False
        if a_cmd:
            cmd_description = tek.get_cmd_description(a_cmd.split(" ")[0], self.cmd_tree)
            if cmd_description:
                if tek.send_cmd(self.spec, a_cmd) and "?" in a_cmd:
                    self.tek_status = self.TekStatus.WAIT_BYTES if a_read_bytes else self.TekStatus.WAIT_STRING
                    result = True
            else:
                logging.error("Неверная команда")

        return result

    @staticmethod
    def byte_to_char(a_bytes: bytes, a_index: int) -> str:
        return str(a_bytes[a_index:a_index + 1], encoding="ascii")

    def extract_spectrum_data(self, a_data: bytes) -> List[float]:
        digits_num = int(self.byte_to_char(a_data, 1))
        data_length = ""
        for i in range(2, 2 + digits_num):
            data_length += self.byte_to_char(a_data, i)
        first_data_byte = i + 1

        float_bytes = 4
        float_data = []
        for i in range(first_data_byte, len(a_data) - 1, float_bytes):
            sample = struct.unpack('f', a_data[i:i + float_bytes])[0]
            float_data.append(sample)

        return float_data

    def draw_spectrum(self, a_data: bytes, a_spec_params: SpecterParameters):
        if self.byte_to_char(a_data, 0) == '#':
            spec_data = self.extract_spectrum_data(a_data)

            x_discrete = Decimal(a_spec_params.x_stop - a_spec_params.x_start) / (len(spec_data) - 1)
            x_points = [a_spec_params.x_start]
            decimal_sum = Decimal(a_spec_params.x_start)
            for _ in range(len(spec_data) - 1):
                decimal_sum += x_discrete
                x_points.append(float(decimal_sum))

            graph_name = f"Центр {self.convert_hz(a_spec_params.center)}, " \
                         f"Span {self.convert_hz(a_spec_params.span)}, " \
                         f"RBW {self.convert_hz(a_spec_params.rbw)}"

            self.graph_widget.plotItem.clear()
            self.graph_widget.plot(x_points, spec_data, pen=self.graph_pen, name=graph_name)
            self.graph_widget.setYRange(a_spec_params.y_start, a_spec_params.y_stop)

            self.save_results(graph_name, x_points, spec_data)
        else:
            logging.error("Неверные данные для построения графика спектра")

    def get_next_cmd_deque(self):
        for cmd_list in self.current_commands:
            cmd_deque = deque(cmd_list)
            cmd_deque.reverse()
            yield cmd_deque

    def save_results(self, a_filename, a_x_data, a_y_data):
        if self.save_folder:
            png_filename = f"{self.save_folder}/{a_filename}.png"
            csv_filename = f"{self.save_folder}/{a_filename}.csv"

            exporter = exporters.ImageExporter(self.graph_widget.plotItem)
            exporter.parameters()['width'] = 1e3
            exporter.export(png_filename)

            csv_data = zip(a_x_data, a_y_data)
            with open(csv_filename, 'w', newline='') as csv_file:
                writer = csv.writer(csv_file)
                writer.writerows(csv_data)

    def start(self, a_cmd_list: List[list], a_save_folder=""):
        if a_cmd_list and a_cmd_list[0]:
            self.current_commands = a_cmd_list
            self.cmd_queue_gen = self.get_next_cmd_deque()
            self.current_cmd_queue = next(self.cmd_queue_gen)
            self.wait_timer.start(0)
            self.tek_status = self.TekStatus.READY
            self.save_folder = a_save_folder

            self.started = True
        return self.started

    def stop(self):
        self.reset()
