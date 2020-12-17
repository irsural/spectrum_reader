from logging.handlers import RotatingFileHandler
from typing import Tuple
import logging
import struct

from PyQt5 import QtWidgets, QtCore, QtGui
from vxi11 import vxi11
import pyqtgraph

from irspy.settings_ini_parser import BadIniException
from irspy.qt import qt_utils

from ui.py.mainwindow import Ui_MainWindow as MainForm
from about_dialog import AboutDialog
import settings

import tekvisa_control as tek


class MainWindow(QtWidgets.QMainWindow):

    def __init__(self):
        super().__init__()

        self.ui = MainForm()
        self.ui.setupUi(self)

        try:
            self.settings = settings.get_clb_autocalibration_settings()
            ini_ok = True
        except BadIniException:
            ini_ok = False
            QtWidgets.QMessageBox.critical(self, "Ошибка", 'Файл конфигурации поврежден. Пожалуйста, '
                                                           'удалите файл "settings.ini" и запустите программу заново')
        if ini_ok:
            self.settings.restore_qwidget_state(self)
            self.settings.restore_qwidget_state(self.ui.mw_splitter_1)
            self.settings.restore_qwidget_state(self.ui.mw_splitter_2)

            self.spec = vxi11.Instrument(self.ui.ip_edit.text())
            self.spec.timeout = 3

            self.wait_response = False
            self.read_bytes = False

            self.graph_widget = pyqtgraph.PlotWidget()
            self.graph_pen = pyqtgraph.mkPen(color=(255, 0, 0), width=2)
            self.init_graph(self.graph_widget)

            self.set_up_logger()
            self.show()
            self.connect_all()

            self.tick_timer = QtCore.QTimer(self)
            self.tick_timer.timeout.connect(self.tick)
            self.tick_timer.start(10)

        else:
            self.close()

    def init_graph(self, a_graph_widget: pyqtgraph.PlotWidget):
        pyqtgraph.setConfigOption('leftButtonPan', False)
        a_graph_widget.setSizePolicy(QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding,
                                                           QtWidgets.QSizePolicy.Preferred))
        a_graph_widget.setSizeIncrement(1, 1)
        a_graph_widget.setBackground('w')
        a_graph_widget.setLabel('bottom', 'Частота, МГц', color='black', size=20)
        a_graph_widget.setLabel('left', 'Амплитуда, dBm', color='black', size=20)
        a_graph_widget.showGrid(x=True, y=True)
        a_graph_widget.plotItem.getViewBox().setMouseMode(pyqtgraph.ViewBox.RectMode)
        a_graph_widget.addLegend()

        self.ui.chart_layout.addWidget(a_graph_widget)

    def connect_all(self):
        self.ui.open_about_action.triggered.connect(self.open_about)

        self.ui.send_cmd_button.clicked.connect(self.send_button_clicked)
        self.ui.idn_button.clicked.connect(self.idn_button_clicked)
        self.ui.error_buttons.clicked.connect(self.errors_button_clicked)
        self.ui.connect_button.clicked.connect(self.connect_button_clicked)
        self.ui.read_specter_button.clicked.connect(self.read_specter_button_clicked)

    def set_up_logger(self):
        log = qt_utils.QTextEditLogger(self.ui.log_text_edit)
        log.setFormatter(logging.Formatter('%(asctime)s - %(message)s', datefmt='%H:%M:%S'))

        file_log = RotatingFileHandler("autocalibration.log", maxBytes=30*1024*1024, backupCount=3, encoding='utf8')
        file_log.setLevel(logging.DEBUG)
        file_log.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s', datefmt='%H:%M:%S'))

        logging.getLogger().addHandler(file_log)
        logging.getLogger().addHandler(log)
        logging.getLogger().setLevel(logging.DEBUG)

    def lock_interface(self, a_lock: bool):
        self.ui.connect_button.setDisabled(a_lock)

        self.ui.send_cmd_button.setDisabled(a_lock)
        self.ui.idn_button.setDisabled(a_lock)
        self.ui.error_buttons.setDisabled(a_lock)

    def tick(self):
        if self.wait_response:
            self.lock_interface(False)
            self.wait_response = False

            if not self.read_bytes:
                answer = tek.read_answer(self.spec)
                if answer:
                    logging.info(answer)
            else:
                answer = tek.read_raw_answer(self.spec)
                if answer:
                    self.draw_spectrum(answer)

    def send_cmd(self, a_cmd: str, a_read_bytes: bool = False):
        if tek.send_cmd(self.spec, a_cmd) and "?" in a_cmd:
            self.lock_interface(True)
            self.wait_response = True
            self.read_bytes = a_read_bytes

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

    def connect_button_clicked(self):
        self.spec = vxi11.Instrument(self.ui.ip_edit.text())
        self.spec.timeout = 3
        logging.debug("Connected")

    def send_button_clicked(self):
        self.send_cmd(self.ui.cmd_edit.text())

    def idn_button_clicked(self):
        self.send_cmd("*IDN?")

    def errors_button_clicked(self):
        self.send_cmd("SYST:ERR:ALL?")

    def read_specter_button_clicked(self):
        self.send_cmd("READ:SPEC?", a_read_bytes=True)

    def open_about(self):
        about_dialog = AboutDialog(self)
        about_dialog.exec()

    def closeEvent(self, a_event: QtGui.QCloseEvent):
        self.settings.save_qwidget_state(self.ui.mw_splitter_2)
        self.settings.save_qwidget_state(self.ui.mw_splitter_1)
        self.settings.save_qwidget_state(self)
        a_event.accept()
