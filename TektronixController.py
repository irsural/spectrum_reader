from typing import Optional, Tuple
from enum import IntEnum
import logging
import struct

from pyqtgraph import PlotWidget, mkPen
from vxi11 import vxi11

import tekvisa_control as tek


class TektronixController:
    class TekStatus:
        READY = 0
        WAIT_STRING = 1
        WAIT_BYTES = 2

    def __init__(self, a_graph_widget: PlotWidget, a_cmd_tree: dict):
        self.spec: Optional[None, vxi11.Device] = None

        self.graph_widget = a_graph_widget
        self.graph_pen = mkPen(color=(255, 0, 0), width=2)

        self.cmd_tree = a_cmd_tree

        self.tek_status = self.TekStatus.READY

    def connect(self, a_ip: str):
        self.spec = vxi11.Instrument(a_ip)
        self.spec.timeout = 3
        logging.debug("Connected")

    def tick(self):
        if self.tek_status != self.TekStatus.READY:
            if self.tek_status == self.TekStatus.WAIT_STRING:
                answer = tek.read_answer(self.spec)
                if answer:
                    logging.info(answer)
            else:
                answer = tek.read_raw_answer(self.spec)
                if answer:
                    self.draw_spectrum(answer)

            self.tek_status = self.TekStatus.READY

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

    def wait_response(self) -> bool:
        return self.tek_status != self.TekStatus.READY

    @staticmethod
    def byte_to_char(a_bytes: bytes, a_index: int) -> str:
        return str(a_bytes[a_index:a_index + 1], encoding="ascii")

    def get_spectrum_data_length(self, a_data: bytes) -> Tuple[int, int]:
        digits_num = int(self.byte_to_char(a_data, 1))
        data_length = ""
        for i in range(2, 2 + digits_num):
            data_length += self.byte_to_char(a_data, i)
        return int(data_length), i + 1

    def draw_spectrum(self, a_data: bytes):
        if self.byte_to_char(a_data, 0) == '#':
            data_length, first_data_byte = self.get_spectrum_data_length(a_data)

            float_bytes = 4
            float_data = []
            for i in range(first_data_byte, len(a_data) - 1, float_bytes):
                sample = struct.unpack('f', a_data[i:i + float_bytes])[0]
                float_data.append(sample)

            self.graph_widget.plotItem.clear()
            self.graph_widget.plot(list(range(len(float_data))), float_data, pen=self.graph_pen, name="Спектр")
        else:
            logging.error("Неверные данные")
