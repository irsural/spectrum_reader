from logging.handlers import RotatingFileHandler
import logging

from PyQt5 import QtWidgets, QtCore, QtGui
import pyqtgraph

from irspy.qt.custom_widgets.QTableDelegates import TransparentPainterForWidget
from irspy.settings_ini_parser import BadIniException
from irspy.utils import exception_decorator, exception_decorator_print
from irspy.qt import qt_utils

from ui.py.mainwindow import Ui_MainWindow as MainForm
from TektronixController import TektronixController
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

            self.set_up_logger()

            self.ui.measures_table.setItemDelegate(TransparentPainterForWidget(self.ui.measures_table, "#d4d4ff"))

            self.ui.measure_path_edit.setText(self.settings.save_folder_path)
            self.ui.ip_edit.setText(self.settings.device_ip)

            self.graph_widget = pyqtgraph.PlotWidget()
            self.init_graph(self.graph_widget)

            self.ui.tip_full_cmd_checkbox.setChecked(self.settings.tip_full_cmd)
            cmd_case = tek.CmdCase.LOWER if self.settings.tip_full_cmd else tek.CmdCase.UPPER
            self.cmd_tree = tek.get_commands_three(cmd_case)
            self.set_completer(self.cmd_tree)

            self.tektronix_controller = TektronixController(self.graph_widget, self.cmd_tree)
            self.tektronix_controller.connect(self.settings.device_ip)
            self.tektronix_controller.tektronix_is_ready.connect(self.tektronix_is_ready)

            self.measure_manager = MeasureManager(self.cmd_tree, self.ui.measures_table, self.settings)

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
        a_graph_widget.setLabel('bottom', 'Частота, Гц', color='black', size=20)
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
        self.ui.tip_full_cmd_checkbox.setDisabled(a_lock)
        self.ui.send_cmd_button.setDisabled(a_lock)
        self.ui.idn_button.setDisabled(a_lock)
        self.ui.error_buttons.setDisabled(a_lock)
        self.ui.read_specter_button.setDisabled(a_lock)

        self.ui.change_path_button.setDisabled(a_lock)
        self.ui.add_measure_button.setDisabled(a_lock)
        self.ui.remove_measure_button.setDisabled(a_lock)

        self.ui.start_measure_button.setDisabled(a_lock)

    def tektronix_is_ready(self):
        self.lock_interface(False)

    @exception_decorator
    def tick(self):
        self.tektronix_controller.tick()

    def connect_button_clicked(self):
        self.settings.device_ip = self.ui.ip_edit.text()
        self.tektronix_controller.connect(self.ui.ip_edit.text())

    def send_button_clicked(self):
        if self.tektronix_controller.start({"Send cmd": [self.ui.cmd_edit.text()]}):
            self.lock_interface(True)

    def idn_button_clicked(self):
        if self.tektronix_controller.start({"IDN": ["*IDN?"]}):
            self.lock_interface(True)

    def errors_button_clicked(self):
        if self.tektronix_controller.start({"Errors": [":SYST:ERR:ALL?"]}):
            self.lock_interface(True)

    def read_specter_button_clicked(self):
        if self.tektronix_controller.start({"Спектр": [":READ:SPEC?"]}, self.ui.measure_path_edit.text()):
            self.lock_interface(True)

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
        self.measure_manager.save_config()
        cmd_list = self.measure_manager.get_enabled_configs()
        if self.tektronix_controller.start(cmd_list, self.ui.measure_path_edit.text(), a_default_start=True):
            self.lock_interface(True)

    def stop_measure_button_clicked(self):
        self.tektronix_controller.stop()
        self.lock_interface(False)

    def open_about(self):
        about_dialog = AboutDialog(self)
        about_dialog.exec()

    def closeEvent(self, a_event: QtGui.QCloseEvent):
        self.settings.save_qwidget_state(self.ui.measures_table)
        self.settings.save_qwidget_state(self.ui.mw_splitter_2)
        self.settings.save_qwidget_state(self.ui.mw_splitter_1)
        self.settings.save_qwidget_state(self)
        a_event.accept()
