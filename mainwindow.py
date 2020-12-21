from logging.handlers import RotatingFileHandler
from typing import Tuple
import logging
import struct

from PyQt5 import QtWidgets, QtCore, QtGui
from vxi11 import vxi11
import pyqtgraph

from irspy.qt.custom_widgets.QTableDelegates import TransparentPainterForWidget
from irspy.settings_ini_parser import BadIniException
from irspy.qt import qt_utils

from ui.py.mainwindow import Ui_MainWindow as MainForm
from tekvisa_qcompleter import CmdCompleter
from MeasureManager import MeasureManager
from about_dialog import AboutDialog
import tekvisa_control as tek
import settings


class MainWindow(QtWidgets.QMainWindow):

    def __init__(self):
        super().__init__()

        self.ui = MainForm()
        self.ui.setupUi(self)

        try:
            self.settings = settings.get_ini_settings()
            ini_ok = True
        except BadIniException:
            ini_ok = False
            QtWidgets.QMessageBox.critical(self, "Ошибка", 'Файл конфигурации поврежден. Пожалуйста, '
                                                           'удалите файл "settings.ini" и запустите программу заново')
        if ini_ok:
            self.settings.restore_qwidget_state(self)
            self.settings.restore_qwidget_state(self.ui.mw_splitter_1)
            self.settings.restore_qwidget_state(self.ui.mw_splitter_2)
            self.settings.restore_qwidget_state(self.ui.measures_table)

            self.ui.measures_table.setItemDelegate(TransparentPainterForWidget(self.ui.measures_table, "#d4d4ff"))

            self.ui.measure_path_edit.setText(self.settings.save_folder_path)

            self.spec = vxi11.Instrument(self.ui.ip_edit.text())
            self.spec.timeout = 3

            self.wait_response = False
            self.read_bytes = False

            self.graph_widget = pyqtgraph.PlotWidget()
            self.graph_pen = pyqtgraph.mkPen(color=(255, 0, 0), width=2)
            self.init_graph(self.graph_widget)

            self.ui.tip_full_cmd_checkbox.setChecked(self.settings.tip_full_cmd)
            cmd_case = tek.CmdCase.LOWER if self.settings.tip_full_cmd else tek.CmdCase.UPPER
            self.cmd_tree = tek.get_commands_three(cmd_case)
            self.set_completer(self.cmd_tree)

            self.measure_manager = MeasureManager(self.cmd_tree, self.ui.measures_table, self.settings)

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

        self.ui.tip_full_cmd_checkbox.toggled.connect(self.tip_full_cmd_checkbox_toggled)
        self.ui.cmd_edit.textChanged.connect(self.cmd_edit_text_changed)

        self.ui.change_path_button.clicked.connect(self.change_path_button_clicked)
        self.ui.add_measure_button.clicked.connect(self.add_measure_button_clicked)
        self.ui.remove_measure_button.clicked.connect(self.remove_measure_button_clicked)
        self.ui.start_measure_button.clicked.connect(self.start_measure_button_clicked)
        self.ui.stop_measure_button.clicked.connect(self.stop_measure_button_clicked)

    def set_completer(self, a_cmd_tree: dict):
        cmd_completer = CmdCompleter(a_cmd_tree, self)
        cmd_completer.setCaseSensitivity(QtCore.Qt.CaseInsensitive)
        cmd_completer.setModelSorting(QtWidgets.QCompleter.CaseSensitivelySortedModel)
        self.ui.cmd_edit.setCompleter(cmd_completer)

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
        if a_cmd:
            cmd_description = tek.get_cmd_description(a_cmd.split(" ")[0], self.cmd_tree)
            if cmd_description:
                if tek.send_cmd(self.spec, a_cmd) and "?" in a_cmd:
                    self.lock_interface(True)
                    self.wait_response = True
                    self.read_bytes = a_read_bytes
            else:
                self.ui.cmd_description_text_edit.clear()
                self.ui.cmd_description_text_edit.appendPlainText("Неверная команда")

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

    def tip_full_cmd_checkbox_toggled(self, a_enable):
        self.settings.tip_full_cmd = int(a_enable)

        cmd_case = tek.CmdCase.LOWER if self.settings.tip_full_cmd else tek.CmdCase.UPPER
        self.cmd_tree = tek.get_commands_three(cmd_case)
        self.set_completer(self.cmd_tree)
        self.measure_manager.update_cmd_tree(self.cmd_tree)

    def cmd_edit_text_changed(self, a_cmd: str):
        self.ui.cmd_description_text_edit.clear()
        cmd_description = tek.get_cmd_description(a_cmd.split(" ")[0], self.cmd_tree)
        if cmd_description:
            self.ui.cmd_description_text_edit.appendPlainText(cmd_description)
            self.ui.cmd_description_text_edit.verticalScrollBar().setValue(0)

    def change_path_button_clicked(self):
        save_folder_path = QtWidgets.QFileDialog.getExistingDirectory(
            self, "Выберите каталог для сохренения результатов", self.settings.save_folder_path)
        if save_folder_path:
            self.settings.save_folder_path = save_folder_path
            self.ui.measure_path_edit.setText(save_folder_path)

    def add_measure_button_clicked(self):
        self.measure_manager.new_measure()

    def remove_measure_button_clicked(self):
        self.measure_manager.remove_measure()

    def start_measure_button_clicked(self):
        pass

    def stop_measure_button_clicked(self):
        pass

    def open_about(self):
        about_dialog = AboutDialog(self)
        about_dialog.exec()

    def closeEvent(self, a_event: QtGui.QCloseEvent):
        self.settings.save_qwidget_state(self.ui.measures_table)
        self.settings.save_qwidget_state(self.ui.mw_splitter_2)
        self.settings.save_qwidget_state(self.ui.mw_splitter_1)
        self.settings.save_qwidget_state(self)
        a_event.accept()
