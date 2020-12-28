from typing import Optional, Tuple, List, Dict
from collections import deque
from decimal import Decimal
from enum import IntEnum
import logging
import struct
import bisect
import math

from pyqtgraph import PlotWidget, mkPen, exporters, PlotDataItem
from PyQt5 import QtCore
from vxi11 import vxi11

from irspy.utils import Timer, value_to_user_with_units
from irspy.pokrov import pokrov_dll

import tekvisa_control as tek
from config_dialog import TekConfig


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


class MeasureConductor(QtCore.QObject):
    # Для автоматического режима
    class TekStatus(IntEnum):
        READY = 0
        WAIT_STRING = 1
        WAIT_BYTES = 2
        WAIT_OPC = 3

    tektronix_is_ready = QtCore.pyqtSignal()
    gnrw_state_changed = QtCore.pyqtSignal(bool, int)
    graph_points_count_changed = QtCore.pyqtSignal(int)

    DEFAULT_CMD_DELAY_S = 0
    OPC_POLL_DELAY_S = 1

    GRAPH_COLORS = (
        (255, 0, 0),
        (0, 255, 0),
        (0, 0, 255),
        (0, 204, 204),
        (204, 0, 102),
        (204, 204, 0),
        (255, 0, 255),
        (102, 153, 153),
        (255, 153, 0),
        (102, 204, 255),
        (0, 255, 153),
        (204, 102, 255),
    )

    SPEC_CMD_WAIT = ":WAIT"
    SPEC_CMD_READ_DELAY = ":READ_DELAY"

    GNRW_COMMANDS_NODE_NAME = ":GNRW"
    GNRW_CMD_ENABLE = "ENABLE"
    GNRW_CMD_RADIO = "RADIO"
    GNRW_CMD_RADIO_ASK = "RADIO?"
    GNRW_CMD_LINE = "LINE"
    GNRW_CMD_LINE_ASK = "LINE?"

    GNRW_COMMANDS_TREE = {
        GNRW_CMD_ENABLE: {"desc": "Включить/выключить сигнал на ГШ Покров"},
        GNRW_CMD_RADIO: {"desc": "Управление мощностью сигнала поля"},
        GNRW_CMD_RADIO_ASK: {"desc": "Управление мощностью сигнала поля"},
        GNRW_CMD_LINE: {"desc": "Управление мощностью сигнала сети"},
        GNRW_CMD_LINE_ASK: {"desc": "Управление мощностью сигнала сети"},
    }

    GNRW_SYNC_DELAY_S = 2

    def __init__(self, a_gnrw_ip: str, a_settings, a_graph_widget: PlotWidget, a_cmd_tree: dict, a_parent=None):
        super().__init__(parent=a_parent)

        self.spec: Optional[None, vxi11.Device] = None

        self.settings = a_settings
        self.graph_widget = a_graph_widget
        self.cmd_tree = a_cmd_tree

        self.started = False
        self.current_configs = []
        self.configs_gen = None
        self.current_config: Optional[None, TekConfig] = None
        self.current_cmd_queue: Optional[None, deque] = None
        self.wait_timer = Timer(0)
        self.tek_status = self.TekStatus.READY
        self.save_folder = ""
        self.current_measure_name = ""

        self.pokrov_prev_connected_state = False
        self.gnrw_check_connection_timer = Timer(0.2)
        self.gnrw_check_connection_timer.start()
        self.pokrov = pokrov_dll.PokrovDrv()
        self.pokrov.connect(a_gnrw_ip)

        self.current_graph = 0
        self.graphs_data: Dict[int, Tuple[List, List]] = {}

        self.convert_hz = value_to_user_with_units("Гц")

    def reset(self):
        self.started = False
        self.current_configs = []
        self.configs_gen = None
        self.current_config = None
        self.current_cmd_queue: Optional[None, deque] = None
        self.wait_timer = Timer(0)
        self.tek_status = self.TekStatus.READY
        self.save_folder = ""
        self.current_measure_name = ""
        self.current_graph = 0
        self.graphs_data = {}

    def sa_connect(self, a_ip: str):
        self.spec = vxi11.Instrument(a_ip)
        self.spec.timeout = 3
        logging.debug("Connected")

    def gnrw_connect(self, a_ip: str):
        self.pokrov.connect(a_ip)

    def handle_measure_error(self, a_error_msg):
        logging.error("Во время измерения произошла ошибка, измерение будет остановлено")
        logging.error(f"{a_error_msg}")

        self.stop()
        self.tektronix_is_ready.emit()

    def parse_cmd(self, a_cmd) -> Tuple[str, str]:
        cmd_description = tek.get_cmd_description(a_cmd.split(" ")[0], self.cmd_tree)
        if cmd_description:
            cmd_param = a_cmd.split(" ", maxsplit=1)
            cmd, param = cmd_param[0], None
            if len(cmd_param) > 1:
                param = cmd_param[1]
            return cmd, param
        else:
            logging.error(f'Задана несуществующая команда: "{a_cmd}"')
            return "", ""

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

    def get_cmd_delay_before_read(self, a_cmd_queue: deque) -> int:
        delay = 0
        if a_cmd_queue:
            next_cmd, next_param = self.parse_cmd(a_cmd_queue[0])
            if next_cmd == self.SPEC_CMD_READ_DELAY:
                if next_param is not None:
                    # Убираем из очереди, т.к. это фиктивная команда
                    a_cmd_queue.popleft()
                    logging.debug(f"Read delay {next_param} sec")
                    delay = int(next_param)
                else:
                    raise ValueError
        return delay

    def tick(self):
        self.pokrov.tick()

        if self.gnrw_check_connection_timer.check():
            self.gnrw_check_connection_timer.start()

            gnrw_state = self.pokrov.is_connected()
            if gnrw_state != self.pokrov_prev_connected_state:
                self.pokrov_prev_connected_state = gnrw_state

                self.gnrw_state_changed.emit(gnrw_state, self.pokrov.id)

        if self.started:
            if self.wait_timer.check():
                if self.tek_status == self.TekStatus.READY:
                    if self.current_cmd_queue:
                        current_cmd = self.current_cmd_queue.popleft()
                        cmd, param = self.parse_cmd(current_cmd)

                        if cmd:
                            logging.debug(f'Current cmd - "{current_cmd}"')
                            self.wait_timer.start(MeasureConductor.DEFAULT_CMD_DELAY_S)

                            if cmd.startswith(self.GNRW_COMMANDS_NODE_NAME):
                                self.gnrw_send_cmd(cmd, param)

                                try:
                                    delay_before_read = self.get_cmd_delay_before_read(self.current_cmd_queue)
                                    self.wait_timer.start(delay_before_read)
                                except ValueError:
                                    self.handle_measure_error(f"Не задан параметр для команды {self.SPEC_CMD_READ_DELAY}")

                                if not cmd.endswith("?"):
                                    self.wait_timer.start(self.GNRW_SYNC_DELAY_S)

                            elif cmd == self.SPEC_CMD_WAIT:
                                if param is not None:
                                    self.wait_timer.start(int(param))
                                else:
                                    self.handle_measure_error(f"Не задан параметр для команды {self.SPEC_CMD_WAIT}")

                            else:
                                tek.send_cmd(self.spec, current_cmd)
                                if cmd == "*OPC":
                                    self.tek_status = self.TekStatus.WAIT_OPC

                                elif "?" in cmd:
                                    if cmd in (":READ:SPEC?", ":READ:SPECtrum?"):
                                        self.tek_status = self.TekStatus.WAIT_BYTES
                                    else:
                                        self.tek_status = self.TekStatus.WAIT_STRING

                                    try:
                                        delay_before_read = self.get_cmd_delay_before_read(self.current_cmd_queue)
                                        self.wait_timer.start(delay_before_read)
                                    except ValueError:
                                        self.handle_measure_error(f"Не задан параметр для команды {self.SPEC_CMD_READ_DELAY}")
                    else:
                        try:
                            self.current_measure_name, self.current_config = next(self.configs_gen)
                            self.current_cmd_queue = deque(self.current_config.cmd_list())
                            self.current_graph = 0
                            logging.info("Следующая очередь команд")
                        except StopIteration:
                            self.save_results(self.current_measure_name)
                            self.stop()
                            self.tektronix_is_ready.emit()

                elif self.tek_status == self.TekStatus.WAIT_STRING:
                    self.tek_status = self.TekStatus.READY
                    answer = tek.read_answer(self.spec)
                    logging.info(f'Read result - "{answer}"')

                elif self.tek_status == self.TekStatus.WAIT_BYTES:
                    self.tek_status = self.TekStatus.READY
                    binary_spectrum = tek.read_raw_answer(self.spec)
                    if binary_spectrum:
                        self.draw_spectrum(binary_spectrum, self.get_specter_parameters(), self.current_graph)
                        self.current_graph += 1

                elif self.tek_status == self.TekStatus.WAIT_OPC:
                    if tek.is_operation_completed(self.spec):
                        self.tek_status = self.TekStatus.READY
                    else:
                        self.wait_timer.start(self.OPC_POLL_DELAY_S)

    def gnrw_send_cmd(self, a_cmd, a_param):
        gnrw_command = a_cmd.split(':')[2]
        wrong_param_error = False

        if gnrw_command == self.GNRW_CMD_ENABLE:
            if a_param in ('ON', "1"):
                self.pokrov.signal_on(True)
            elif a_param in ('OFF', "0"):
                self.pokrov.signal_on(False)
            else:
                wrong_param_error = True
        elif a_cmd.endswith("?"):
            if gnrw_command == self.GNRW_CMD_LINE_ASK:
                logging.info(self.pokrov.line_power)
            if gnrw_command == self.GNRW_CMD_RADIO_ASK:
                logging.info(self.pokrov.ether_power)
        else:
            try:
                param_value = int(a_param)
            except (ValueError, TypeError):
                wrong_param_error = True
            else:
                if gnrw_command == self.GNRW_CMD_RADIO:
                    self.pokrov.ether_power = param_value
                elif gnrw_command == self.GNRW_CMD_LINE:
                    self.pokrov.line_power = param_value

        if wrong_param_error:
            logging.error(f'Команда "{a_cmd}" - неверный параметр "{a_param}"')

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

    @staticmethod
    def normalize_spectrum_data(a_data: List[float], a_rbw_hz: float) -> List[float]:
        coef = 10 * math.log(a_rbw_hz / 1000., 10)
        return [d - coef for d in a_data]

    @staticmethod
    def calculate_x_points(a_x_start: float, a_x_stop: float, a_x_count: int) -> List[float]:
        x_discrete = Decimal(a_x_stop - a_x_start) / (a_x_count - 1)
        x_points = [a_x_start]
        decimal_sum = Decimal(a_x_start)
        for _ in range(a_x_count - 1):
            decimal_sum += x_discrete
            x_points.append(float(decimal_sum))
        return x_points

    def draw_spectrum(self, a_data: bytes, a_spec_params: SpecterParameters, a_graph_number: int):
        if self.byte_to_char(a_data, 0) == '#':
            amplitudes = self.extract_spectrum_data(a_data)
            amplitudes = self.normalize_spectrum_data(amplitudes, a_spec_params.rbw)
            frequencies = self.calculate_x_points(a_spec_params.x_start, a_spec_params.x_stop, len(amplitudes))

            try:
                x_data, y_data = self.graphs_data[a_graph_number]
                x_data.extend(frequencies)
                y_data.extend(amplitudes)
                plot_data_item: PlotDataItem = self.graph_widget.plotItem.listDataItems()[a_graph_number]
                plot_data_item.setData(x=x_data, y=y_data)

            except KeyError:
                # Это первые данные для графика с a_graph_number номером
                x_data, y_data = frequencies, amplitudes
                graph_color = MeasureConductor.GRAPH_COLORS[a_graph_number % len(MeasureConductor.GRAPH_COLORS)]
                graph_pen = mkPen(color=graph_color, width=2)

                # graph_name = f"{a_graph_number + 1}. {self.convert_hz(a_spec_params.x_start)} - " \
                #              f"{self.convert_hz(a_spec_params.x_stop)}, RBW {self.convert_hz(a_spec_params.rbw)}"

                self.graph_widget.plot(x=x_data, y=y_data, pen=graph_pen, name=str(a_graph_number + 1))
                self.graphs_data[a_graph_number] = (x_data, y_data)

            if y_data:
                y_min, y_max = min(y_data), max(y_data)
                y_start = min((a_spec_params.y_start, y_min))
                y_stop = max((a_spec_params.y_stop, y_max))
                self.graph_widget.setYRange(y_start, y_stop)

                self.graph_points_count_changed.emit(len(y_data))
        else:
            logging.error("Неверные данные для построения графика спектра")

    def set_graph_points_count(self, a_points_count):
        if self.graphs_data:
            for graph_number, (_, (x_data, y_data)) in enumerate(self.graphs_data.items()):
                if x_data:
                    if a_points_count > len(x_data):
                        a_points_count = len(x_data)
                        logging.warning(f"Количество точек на графике = {len(x_data)}")

                    new_data_indices = []
                    factor = (x_data[-1] / x_data[0]) ** (1 / (a_points_count - 1))
                    x = x_data[0]
                    for i in range(1, a_points_count + 1):
                        idx = bisect.bisect_right(x_data, x) - 1
                        new_data_indices.append(idx)
                        x *= factor

                    new_x_data = [x_data[i] for i in new_data_indices]
                    new_y_data = [y_data[i] for i in new_data_indices]

                    plot_data_item: PlotDataItem = self.graph_widget.plotItem.listDataItems()[graph_number]
                    plot_data_item.setData(x=new_x_data, y=new_y_data)

    def get_next_config_deque(self) -> Tuple[str, deque]:
        for name, config in self.current_configs:
            yield name, config

    def save_results(self, a_filename):
        if self.save_folder and self.graph_widget.plotItem.listDataItems():
            png_filename = f"{self.save_folder}/{a_filename}.png"
            csv_filename = f"{self.save_folder}/{a_filename}.csv"

            png_exporter = exporters.ImageExporter(self.graph_widget.plotItem)
            png_exporter.parameters()['width'] = 1e3
            png_exporter.export(png_filename)

            # В LogMode=True сохраняются левые значения
            self.graph_widget.plotItem.setLogMode(x=False, y=False)

            csv_exporter = exporters.CSVExporter(self.graph_widget.plotItem)
            try:
                csv_exporter.export(csv_filename)
            except ValueError:
                logging.error("Не удалось сохранить csv-файл")

            self.graph_widget.plotItem.setLogMode(x=self.settings.log_scale_enabled, y=False)

    def start(self, a_configs: List[Tuple[str, TekConfig]], a_save_folder=""):
        self.reset()
        if a_configs:
            if tek.check_connection(self.spec):
                self.current_configs = a_configs
                self.configs_gen = self.get_next_config_deque()
                self.current_measure_name, self.current_config = next(self.configs_gen)
                self.current_cmd_queue = deque(self.current_config.cmd_list())
                self.wait_timer.start(0)
                self.tek_status = self.TekStatus.READY
                self.save_folder = a_save_folder
                self.graph_widget.plotItem.clear()

                self.current_graph = 0
                self.graphs_data = {}

                self.started = True
            else:
                logging.error("Не удалось установить соединение, необходимо вручную сбросить "
                              "Remote Interface на спектроанализаторе")
        return self.started

    def exec_cmd(self, a_cmd: str):
        config = [("Last command", TekConfig(a_cmd_list=[a_cmd]))]
        return self.start(config)

    def stop(self):
        self.started = False
