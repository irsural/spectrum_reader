from logging.handlers import RotatingFileHandler
import logging
import os

from PyQt5 import QtWidgets, QtCore, QtGui
import pyqtgraph

from irspy.qt.custom_widgets.QTableDelegates import TransparentPainterForWidget
from irspy.settings_ini_parser import BadIniException
from irspy.utils import exception_decorator, exception_decorator_print
from irspy.qt import qt_utils

from ui.py.mainwindow import Ui_MainWindow as MainForm
from MeasureConductor import MeasureConductor
from tekvisa_qcompleter import CmdCompleter
from MeasureManager import MeasureManager
from graphs_control import GraphsControl
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
            self.ui.save_file_name_edit.setText(self.settings.save_file_name)
            self.ui.measure_comment_edit.setText(self.settings.measure_comment)
            self.ui.sa_ip_edit.setText(self.settings.sa_ip)
            self.ui.gnrw_ip_edit.setText(self.settings.gnrw_ip)
            self.ui.points_count_spinbox.setValue(self.settings.graph_points_count)
            self.gnrw_state_changed(False, 0)

            self.graph_widget = pyqtgraph.PlotWidget()
            self.graphs_control = GraphsControl(self.graph_widget, self.settings)
            self.ui.chart_layout.addWidget(self.graph_widget)

            self.cmd_tree = tek.get_commands_three(tek.CmdCase.UPPER)
            self.add_extra_commands(self.cmd_tree)
            self.set_completer(self.cmd_tree)

            self.measure_conductor = MeasureConductor(self.ui.gnrw_ip_edit.text(), self.settings,
                                                      self.graphs_control, self.cmd_tree)
            self.measure_conductor.sa_connect(self.settings.sa_ip)
            self.measure_conductor.tektronix_is_ready.connect(self.tektronix_is_ready)
            self.measure_conductor.gnrw_state_changed.connect(self.gnrw_state_changed)

            self.measure_manager = MeasureManager(self.cmd_tree, self.ui.measures_table, self.settings)

            self.show()
            self.connect_all()

            self.ui.log_scale_checkbox.setChecked(self.settings.log_scale_enabled)

            self.tick_timer = QtCore.QTimer(self)
            self.tick_timer.timeout.connect(self.tick)
            self.tick_timer.start(10)
        else:
            self.close()

    def connect_all(self):
        self.ui.open_about_action.triggered.connect(self.open_about)

        self.ui.send_cmd_button.clicked.connect(self.send_button_clicked)
        self.ui.idn_button.clicked.connect(self.idn_button_clicked)
        self.ui.error_buttons.clicked.connect(self.errors_button_clicked)
        self.ui.sa_connect_button.clicked.connect(self.sa_connect_button_clicked)
        self.ui.gnrw_connect_button.clicked.connect(self.gnrw_connect_button_clicked)
        self.ui.read_specter_button.clicked.connect(self.read_specter_button_clicked)

        self.ui.cmd_edit.textChanged.connect(self.cmd_edit_text_changed)

        self.ui.change_path_button.clicked.connect(self.change_path_button_clicked)
        self.ui.save_file_name_edit.textChanged.connect(self.save_file_name_changed)
        self.ui.measure_comment_edit.textChanged.connect(self.measure_comment_changed)
        self.ui.add_measure_button.clicked.connect(self.add_measure_button_clicked)
        self.ui.remove_measure_button.clicked.connect(self.remove_measure_button_clicked)
        self.ui.copy_measure_button.clicked.connect(self.copy_measure_button_clicked)
        self.ui.move_measure_up_button.clicked.connect(self.move_measure_up_button_clicked)
        self.ui.move_measure_down_button.clicked.connect(self.move_measure_down_button_clicked)
        self.ui.start_measure_button.clicked.connect(self.start_measure_button_clicked)
        self.ui.stop_measure_button.clicked.connect(self.stop_measure_button_clicked)

        self.ui.log_scale_checkbox.toggled.connect(self.log_scale_checkbox_toggled)
        self.ui.csv_import_button.clicked.connect(self.csv_import_button_clicked)
        self.ui.graphs_button.clicked.connect(self.graphs_button_clicked)
        self.ui.clear_graph_button.clicked.connect(self.clear_graph_button_clicked)
        self.ui.points_count_spinbox.editingFinished.connect(self.graph_points_count_changed)

        self.graphs_control.graph_points_count_changed.connect(self.set_graph_points_count)

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
        self.ui.sa_connect_button.setDisabled(a_lock)
        self.ui.gnrw_connect_button.setDisabled(a_lock)
        self.ui.send_cmd_button.setDisabled(a_lock)
        self.ui.idn_button.setDisabled(a_lock)
        self.ui.error_buttons.setDisabled(a_lock)
        self.ui.read_specter_button.setDisabled(a_lock)

        self.ui.change_path_button.setDisabled(a_lock)
        self.ui.add_measure_button.setDisabled(a_lock)
        self.ui.remove_measure_button.setDisabled(a_lock)
        self.ui.move_measure_up_button.setDisabled(a_lock)
        self.ui.move_measure_down_button.setDisabled(a_lock)

        self.ui.start_measure_button.setDisabled(a_lock)

    def tektronix_is_ready(self):
        self.lock_interface(False)

    @exception_decorator
    def tick(self):
        self.measure_conductor.tick()

    @staticmethod
    def add_extra_commands(a_cmd_tree: dict):
        a_cmd_tree[MeasureConductor.SPEC_CMD_WAIT] = {"desc": "Wait N seconds"}
        a_cmd_tree[MeasureConductor.SPEC_CMD_READ_DELAY] = {"desc": "Wait N seconds before reading the answer"}
        a_cmd_tree[MeasureConductor.GNRW_COMMANDS_NODE_NAME] = MeasureConductor.GNRW_COMMANDS_TREE

    def sa_connect_button_clicked(self):
        self.settings.sa_ip = self.ui.sa_ip_edit.text()
        self.measure_conductor.sa_connect(self.ui.sa_ip_edit.text())

    def gnrw_connect_button_clicked(self):
        self.settings.gnrw_ip = self.ui.gnrw_ip_edit.text()
        self.measure_conductor.gnrw_connect(self.ui.gnrw_ip_edit.text())

    def gnrw_state_changed(self, a_connected, a_id):
        if a_connected:
            pixmap = QtGui.QPixmap(":/icons/icons/checkbox_ok.png")
            self.ui.gnrw_factory_number_label.setText(f"№{a_id}")
        else:
            pixmap = QtGui.QPixmap(":/icons/icons/checkbox_fail.png")
            self.ui.gnrw_factory_number_label.setText("")

        self.ui.gnrw_status_label.setPixmap(pixmap.scaled(20, 20, QtCore.Qt.KeepAspectRatio))

    def send_button_clicked(self):
        if self.measure_conductor.exec_cmd(self.ui.cmd_edit.text()):
            self.lock_interface(True)

    def idn_button_clicked(self):
        if self.measure_conductor.exec_cmd("*IDN?"):
            self.lock_interface(True)

    def errors_button_clicked(self):
        if self.measure_conductor.exec_cmd(":SYST:ERR:ALL?"):
            self.lock_interface(True)

    def read_specter_button_clicked(self):
        if self.measure_conductor.exec_cmd(":READ:SPEC?"):
            self.lock_interface(True)

    def tip_full_cmd_checkbox_toggled(self, a_enable):
        self.settings.tip_full_cmd = int(a_enable)

        cmd_case = tek.CmdCase.LOWER if self.settings.tip_full_cmd else tek.CmdCase.UPPER
        self.cmd_tree = tek.get_commands_three(cmd_case)
        self.add_extra_commands(self.cmd_tree)
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

    def save_file_name_changed(self, a_filename):
        self.settings.save_file_name = a_filename

    def measure_comment_changed(self, a_comment):
        self.settings.measure_comment = a_comment

    def add_measure_button_clicked(self):
        self.measure_manager.new_measure()

    def remove_measure_button_clicked(self):
        self.measure_manager.remove_measure()

    def copy_measure_button_clicked(self):
        selected_row = qt_utils.qtablewidget_get_only_selected_row(self.ui.measures_table)
        if selected_row is not None:
            self.measure_manager.copy_measure(selected_row)

    def move_measure_up_button_clicked(self):
        selected_row = qt_utils.qtablewidget_get_only_selected_row(self.ui.measures_table)
        if selected_row is not None:
            self.measure_manager.move_measure_up(selected_row)

    def move_measure_down_button_clicked(self):
        selected_row = qt_utils.qtablewidget_get_only_selected_row(self.ui.measures_table)
        if selected_row is not None:
            self.measure_manager.move_measure_down(selected_row)

    def start_measure_button_clicked(self):
        self.measure_manager.save_config()

        measure_path = self.ui.measure_path_edit.text()
        measure_filename = self.ui.save_file_name_edit.text()

        if measure_path and measure_filename:

            csv_full_filename = f"{measure_path}/{measure_filename}.csv"
            png_full_filename = f"{measure_path}/{measure_filename}.png"
            start_measure = True
            if os.path.isfile(csv_full_filename) or os.path.isfile(png_full_filename):
                res = QtWidgets.QMessageBox.question(self, "Предупреждение",
                                                     f"Измерение {measure_filename} уже существует и будет перезаписано. "
                                                     f"Продолжить?", QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No,
                                                     QtWidgets.QMessageBox.Yes)
                if res == QtWidgets.QMessageBox.No:
                    start_measure = False

            if start_measure:
                self.sa_connect_button_clicked()
                self.gnrw_connect_button_clicked()

                comment = self.ui.measure_comment_edit.text()
                configs = self.measure_manager.get_enabled_configs()
                if self.measure_conductor.start(configs, measure_path, measure_filename, comment):
                    self.lock_interface(True)
        else:
            QtWidgets.QMessageBox.critical(self, "Ошибка",
                                           "Необходимо задать каталог для сохранения и имя сохраняемого файла",
                                           QtWidgets.QMessageBox.Ok, QtWidgets.QMessageBox.Ok)

    def stop_measure_button_clicked(self):
        self.measure_conductor.stop()
        self.lock_interface(False)

    def log_scale_checkbox_toggled(self, a_state: bool):
        self.graphs_control.log_scale_enable(a_state)
        self.settings.log_scale_enabled = int(a_state)

    def csv_import_button_clicked(self):
        filename, _ = QtWidgets.QFileDialog.getOpenFileName(self, "Импорт графика из csv",
                                                            self.ui.measure_path_edit.text(), "CSV (*.csv)")
        if filename:
            self.graphs_control.import_from_csv(filename)

    def graphs_button_clicked(self):
        pass

    def clear_graph_button_clicked(self):
        self.graphs_control.clear()

    def graph_points_count_changed(self):
        if self.ui.points_count_spinbox.value() != self.settings.graph_points_count:
            self.graphs_control.set_points_count(self.ui.points_count_spinbox.value())
            self.settings.graph_points_count = self.ui.points_count_spinbox.value()

    def set_graph_points_count(self, a_points_count: int):
        self.ui.points_count_spinbox.setValue(a_points_count)

    def open_about(self):
        about_dialog = AboutDialog(self)
        about_dialog.exec()

    def closeEvent(self, a_event: QtGui.QCloseEvent):
        self.settings.save_qwidget_state(self.ui.measures_table)
        self.settings.save_qwidget_state(self.ui.mw_splitter_2)
        self.settings.save_qwidget_state(self.ui.mw_splitter_1)
        self.settings.save_qwidget_state(self)
        a_event.accept()
