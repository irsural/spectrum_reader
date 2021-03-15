from logging.handlers import RotatingFileHandler
import logging

from PyQt5 import QtWidgets, QtCore, QtGui
import pyqtgraph

from irspy.qt.custom_widgets.QTableDelegates import TransparentPainterForWidget
from irspy.utils import exception_decorator, exception_decorator_print
from irspy.settings_ini_parser import BadIniException
from irspy.qt import qt_utils

from tektronix_send_cmd_dialog import TektronixSendCmdDialog
from ui.py.mainwindow import Ui_MainWindow as MainForm
from MeasureConductor import MeasureConductor
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
            self.ui.comment_text_edit.insertPlainText(self.settings.measure_comment)
            self.ui.sa_ip_edit.setText(self.settings.sa_ip)
            self.ui.gnrw_ip_edit.setText(self.settings.gnrw_ip)
            self.ui.points_count_spinbox.setValue(self.settings.graph_points_count)
            self.gnrw_state_changed(False, 0)

            self.graph_widget = pyqtgraph.PlotWidget()
            self.graphs_control = GraphsControl(self.graph_widget, self.settings)
            self.ui.chart_layout.addWidget(self.graph_widget)

            self.cmd_tree = tek.get_commands_three(tek.CmdCase.UPPER)
            self.add_extra_commands(self.cmd_tree)

            self.measure_conductor = MeasureConductor(self.settings, self.graphs_control, self.cmd_tree)
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

        self.ui.sa_ip_edit.textChanged.connect(self.sa_ip_changed)
        self.ui.gnrw_ip_edit.textChanged.connect(self.gnrw_ip_changed)

        self.ui.sa_connect_button.clicked.connect(self.sa_connect_button_clicked)
        self.ui.gnrw_connect_button.clicked.connect(self.gnrw_connect_button_clicked)

        self.ui.open_tektronix_send_cmd_dialog_button.clicked.connect(
            self.open_tektronix_send_cmd_dialog_button_clicked)

        self.ui.change_path_button.clicked.connect(self.change_path_button_clicked)
        self.ui.save_file_name_edit.textChanged.connect(self.save_file_name_changed)
        self.ui.comment_text_edit.textChanged.connect(self.comment_changed)
        self.ui.edit_comment_button.clicked.connect(self.edit_comment_button_clicked)
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
        self.ui.reset_graph_points_count_button.clicked.connect(self.reset_graph_points_count_button_clicked)

        self.graphs_control.graph_points_count_changed.connect(self.update_graph_points_count)

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
        self.ui.open_tektronix_send_cmd_dialog_button.setDisabled(a_lock)

        self.ui.change_path_button.setDisabled(a_lock)
        self.ui.add_measure_button.setDisabled(a_lock)
        self.ui.remove_measure_button.setDisabled(a_lock)
        self.ui.move_measure_up_button.setDisabled(a_lock)
        self.ui.move_measure_down_button.setDisabled(a_lock)

        self.ui.save_file_name_edit.setDisabled(a_lock)
        self.ui.comment_text_edit.setDisabled(a_lock)
        self.ui.edit_comment_button.setDisabled(a_lock)

        self.ui.csv_import_button.setDisabled(a_lock)
        self.ui.copy_measure_button.setDisabled(a_lock)

        self.ui.start_measure_button.setDisabled(a_lock)

        self.graphs_control.lock_changes(a_lock)

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

    def open_tektronix_send_cmd_dialog_button_clicked(self):
        tektronix_send_cmd_dialog = TektronixSendCmdDialog(self.cmd_tree, self.settings)
        tektronix_send_cmd_dialog.send_cmd.connect(self.tektronix_send_cmd)
        tektronix_send_cmd_dialog.exec()

    def sa_ip_changed(self, a_text):
        self.settings.sa_ip = a_text

    def sa_connect_button_clicked(self):
        try:
            if self.measure_conductor.exec_cmd("*IDN?"):
                self.lock_interface(True)
        except ConnectionRefusedError:
            logging.error("Не удалось подключиться к спектроанализатору. Проверьте IP.")

    def gnrw_ip_changed(self, a_text):
        self.settings.gnrw_ip = a_text

    def gnrw_connect_button_clicked(self):
        self.measure_conductor.gnrw_connect(self.ui.gnrw_ip_edit.text())

    def gnrw_state_changed(self, a_connected, a_id):
        if a_connected:
            pixmap = QtGui.QPixmap(":/icons/icons/checkbox_ok.png")
            self.ui.gnrw_factory_number_label.setText(f"№{a_id}")
        else:
            pixmap = QtGui.QPixmap(":/icons/icons/checkbox_fail.png")
            self.ui.gnrw_factory_number_label.setText("")

        self.ui.gnrw_status_label.setPixmap(pixmap.scaled(20, 20, QtCore.Qt.KeepAspectRatio))

    def tektronix_send_cmd(self, a_cmd):
        if self.measure_conductor.exec_cmd(a_cmd):
            self.lock_interface(True)

    # def tip_full_cmd_checkbox_toggled(self, a_enable):
    #     self.settings.tip_full_cmd = int(a_enable)
    #
    #     cmd_case = tek.CmdCase.LOWER if self.settings.tip_full_cmd else tek.CmdCase.UPPER
    #     self.cmd_tree = tek.get_commands_three(cmd_case)
    #     self.add_extra_commands(self.cmd_tree)
    #     self.set_completer(self.cmd_tree)
    #     self.measure_manager.update_cmd_tree(self.cmd_tree)

    def change_path_button_clicked(self):
        save_folder_path = QtWidgets.QFileDialog.getExistingDirectory(
            self, "Выберите каталог для сохренения результатов", self.settings.save_folder_path)
        if save_folder_path:
            self.settings.save_folder_path = save_folder_path
            self.ui.measure_path_edit.setText(save_folder_path)

    def save_file_name_changed(self, a_filename):
        self.settings.save_file_name = a_filename

    def comment_changed(self):
        self.settings.measure_comment = self.ui.comment_text_edit.toPlainText()

    def edit_comment_button_clicked(self):
        text, ok = QtWidgets.QInputDialog.getMultiLineText(self, "Ввод комментария", "Комментарий",
                                                           self.ui.comment_text_edit.toPlainText())
        if ok:
            self.ui.comment_text_edit.clear()
            self.ui.comment_text_edit.insertPlainText(text)

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

            start = True
            if not self.measure_conductor.is_gnrw_connected():
                self.measure_conductor.gnrw_connect(self.ui.gnrw_ip_edit.text())
                for i in range(250000):
                    self.tick()

                if not self.measure_conductor.is_gnrw_connected():
                    res = QtWidgets.QMessageBox.critical(self, "Предупреждение",
                                                         "Не удалось подключиться к покрову. Продолжить?",
                                                         QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No,
                                                         QtWidgets.QMessageBox.No)
                    if res == QtWidgets.QMessageBox.No:
                        start = False

            if start:
                comment = self.ui.comment_text_edit.toPlainText()
                configs = self.measure_manager.get_enabled_configs()
                if self.measure_conductor.verify_configs(configs):
                    try:
                        if self.measure_conductor.start(configs, measure_path, measure_filename, comment):
                            self.lock_interface(True)
                    except ConnectionRefusedError:
                        QtWidgets.QMessageBox.critical(
                            self, "Ошибка", "Не удалось установить соединение со спектроанализатором. Проверьте IP.",
                            QtWidgets.QMessageBox.Ok, QtWidgets.QMessageBox.Ok)
                else:
                    QtWidgets.QMessageBox.critical(
                        self, "Ошибка", "В конфигурациях обнаружены ошибки. Подробности в логе.",
                        QtWidgets.QMessageBox.Ok, QtWidgets.QMessageBox.Ok)
        else:
            QtWidgets.QMessageBox.critical(
                self, "Ошибка", "Необходимо задать каталог для сохранения и имя сохраняемого файла",
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

    @exception_decorator_print
    def graphs_button_clicked(self, _):
        self.graphs_control.open_graphs_edit_dialog()

    def clear_graph_button_clicked(self):
        self.graphs_control.clear()

    def graph_points_count_changed(self):
        self.graphs_control.set_points_count(self.ui.points_count_spinbox.value())
        self.settings.graph_points_count = self.ui.points_count_spinbox.value()

    def reset_graph_points_count_button_clicked(self):
        self.graphs_control.reset_graph_points_count()

    def update_graph_points_count(self, a_points_count: int):
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
