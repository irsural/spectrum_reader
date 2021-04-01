from typing import Optional, Tuple, List, Dict
from collections import deque, defaultdict
from datetime import datetime
from decimal import Decimal
from enum import IntEnum
import logging
import struct
import json
import math

from PyQt5 import QtCore
from vxi11 import vxi11

from irspy.utils import Timer, value_to_user_with_units
from irspy.pokrov import pokrov_dll
from irspy import utils

from graphs_control import GraphsControl
from MeasureConfig import MeasureConfig
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


class MeasureConductor(QtCore.QObject):
    # Для автоматического режима
    class TekStatus(IntEnum):
        READY = 0
        WAIT_STRING = 1
        WAIT_BYTES = 2
        WAIT_OPC = 3

    tektronix_is_ready = QtCore.pyqtSignal()
    gnrw_state_changed = QtCore.pyqtSignal(bool, int)

    DEFAULT_CMD_DELAY_S = 0
    OPC_POLL_DELAY_S = 1

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

    DATE_FORMAT = "%Y%m%d %H%M%S"

    def __init__(self, a_settings, a_graphs_control: GraphsControl, a_cmd_tree: dict, a_parent=None):
        super().__init__(parent=a_parent)

        self.spec: Optional[None, vxi11.Device] = None

        self.settings = a_settings
        self.graphs_control = a_graphs_control
        self.cmd_tree = a_cmd_tree

        self.started = False
        self.current_configs = []
        self.configs_gen = None
        self.current_config: Optional[None, MeasureConfig] = None
        self.current_cmd_queue: Optional[None, deque] = None
        self.wait_timer = Timer(0)
        self.tek_status = self.TekStatus.READY
        self.save_folder = ""
        self.save_filename = ""
        self.comment = ""

        self.pokrov_prev_connected_state = False
        self.gnrw_check_connection_timer = Timer(0.2)
        self.gnrw_check_connection_timer.start()
        self.pokrov = pokrov_dll.PokrovDrv()

        self.convert_hz = value_to_user_with_units("Гц")
        self.graph_names_before_start = []
        self.current_graph_number = 0

    def reset(self):
        self.started = False
        self.current_configs = []
        self.configs_gen = None
        self.current_config = None
        self.current_cmd_queue: Optional[None, deque] = None
        self.wait_timer = Timer(0)
        self.tek_status = self.TekStatus.READY
        self.save_folder = ""
        self.save_filename = ""
        self.comment = ""
        self.graph_names_before_start = []
        self.current_graph_number = 0

    def sa_connect(self, a_ip: str):
        self.spec = vxi11.Instrument(a_ip)
        self.spec.timeout = 3

    def gnrw_connect(self, a_ip: str):
        self.pokrov.connect(a_ip)

    def is_gnrw_connected(self):
        return self.pokrov.is_connected()

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
                            _, self.current_config = next(self.configs_gen)
                            self.current_cmd_queue = deque(self.current_config.cmd_list())
                            self.current_graph_number = 0
                            logging.info("Следующая очередь команд")
                        except StopIteration:
                            self.save_results(self.save_filename)
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
                        self.current_graph_number += 1
                        self.draw_spectrum(binary_spectrum, self.get_specter_parameters())

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

    def normalize_spectrum_data(self, a_amplitudes: List[float], a_frequencies: List[float], a_rbw_hz: float) -> List[float]:
        coef = 10 * math.log(a_rbw_hz / 1000., 10)

        normalized_amplitudes = []
        for amplitude, frequency in zip(a_amplitudes, a_frequencies):
            if self.current_config.apply_on_limit() and amplitude >= self.current_config.limit():
                amplitude += self.current_config.total_device_response(frequency / 1e6)

            amplitude += self.current_config.normalize_coef() - coef
            normalized_amplitudes.append(amplitude)

        # return [a + self.current_config.total_device_response(f / 1e6) - coef + self.current_config.normalize_coef()
        #         for a, f in zip(a_amplitudes, a_frequencies)]

        return normalized_amplitudes

    @staticmethod
    def calculate_x_points(a_x_start: float, a_x_stop: float, a_x_count: int) -> List[float]:
        x_discrete = Decimal(a_x_stop - a_x_start) / (a_x_count - 1)
        x_points = [a_x_start]
        decimal_sum = Decimal(a_x_start)
        for _ in range(a_x_count - 1):
            decimal_sum += x_discrete
            x_points.append(float(decimal_sum))
        return x_points

    def draw_spectrum(self, a_data: bytes, a_spec_params: SpecterParameters):
        if self.byte_to_char(a_data, 0) == '#':
            spec_data = self.extract_spectrum_data(a_data)

            frequencies = self.calculate_x_points(a_spec_params.x_start, a_spec_params.x_stop, len(spec_data))
            amplitudes = self.normalize_spectrum_data(spec_data, frequencies, a_spec_params.rbw)

            pokrov_state = "NO CONN."
            if self.pokrov.is_connected():
                if self.pokrov.is_signal_on():
                    pokrov_state = f"УрП={self.pokrov.ether_power} УрС={self.pokrov.line_power}"
                else:
                    pokrov_state = "OFF"

            graph_name = f"{self.save_filename} {pokrov_state} №{self.current_graph_number}"
            real_graph_name = utils.get_allowable_name(self.graph_names_before_start, graph_name,
                                                       "{new_name} ({number})")

            if real_graph_name not in self.graphs_control.get_graphs_names():
                self.graphs_control.draw_new(real_graph_name, frequencies, amplitudes)
            else:
                self.graphs_control.draw_append(real_graph_name, frequencies, amplitudes)
        else:
            logging.error("Неверные данные для построения графика спектра")

    def get_next_config_deque(self) -> Tuple[str, deque]:
        for name, config in self.current_configs:
            yield name, config

    def save_results(self, a_filename):
        if self.save_folder:
            date_str = datetime.now().strftime(MeasureConductor.DATE_FORMAT)
            frequency_min, frequency_max = self.graphs_control.get_current_x_range()
            filename = f"{self.save_folder}/{date_str} {a_filename} {frequency_min}-{frequency_max}"

            self.graphs_control.save_to_file(filename)

            full_measure_config = {"Комментарий": self.comment.split("\n")}
            config_gen = self.get_next_config_deque()
            for name, config in config_gen:
                full_measure_config[name] = config.cmd_list()

            with open(f"{filename}.json", 'w') as config_file:
                config_file.write(json.dumps(full_measure_config, indent=4, ensure_ascii=False))

    @staticmethod
    def verify_configs(a_configs: List[Tuple[str, MeasureConfig]]):
        success_verified = True

        # read_op_count = []
        # for _, config in a_configs:
        #     cmd_read_op_count = config.cmd_list().count(":READ:SPEC?")
        #     if cmd_read_op_count != 0:
        #         read_op_count.append(cmd_read_op_count)
        #
        # if not all([read_op_count[0] == count for count in read_op_count]):
        #     logging.error("Количество операций чтения в каждой конфигурации должно быть одинаковым, либо равным нулю")
        #     success_verified = False

        return success_verified

    def start(self, a_configs: List[Tuple[str, MeasureConfig]], a_save_folder, a_save_filename, a_comment):
        self.reset()
        if a_configs:
            self.sa_connect(self.settings.sa_ip)
            try:
                connection_ok = tek.check_connection(self.spec)
            except ConnectionRefusedError:
                logging.error("Не удалось подключиться к спектроанализатору. Проверьте IP.")
            else:
                if connection_ok:
                    self.current_configs = a_configs
                    self.configs_gen = self.get_next_config_deque()
                    _, self.current_config = next(self.configs_gen)
                    self.current_cmd_queue = deque(self.current_config.cmd_list())
                    self.wait_timer.start(0)
                    self.tek_status = self.TekStatus.READY

                    self.save_folder = a_save_folder
                    self.save_filename = a_save_filename
                    self.comment = a_comment

                    self.graph_names_before_start = self.graphs_control.get_graphs_names()

                    self.started = True
                else:
                    logging.error("Не удалось установить соединение, необходимо вручную сбросить "
                                  "Remote Interface на спектроанализаторе (System -> Remote setup... -> Off -> On)")
        return self.started

    def exec_cmd(self, a_cmd: str):
        config = [("Last command", MeasureConfig(a_cmd_list=[a_cmd]))]
        return self.start(config, "", "", "")

    def stop(self):
        self.started = False
