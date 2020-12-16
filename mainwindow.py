from logging.handlers import RotatingFileHandler
import logging

from PyQt5 import QtWidgets, QtCore, QtGui
from vxi11 import vxi11

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

            self.spec = vxi11.Instrument(self.ui.ip_edit.text())
            self.spec.timeout = 3

            self.wait_response = False

            self.set_up_logger()
            self.show()
            self.connect_all()

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
        self.ui.connect_button.clicked.connect(self.connect_button_clicked)

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

            answer = tek.read_answer(self.spec)
            if answer:
                logging.info(answer)

    def send_cmd(self, a_cmd: str):
        if tek.send_cmd(self.spec, a_cmd) and "?" in a_cmd:
            self.lock_interface(True)
            self.wait_response = True

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

    def open_about(self):
        about_dialog = AboutDialog(self)
        about_dialog.exec()

    def closeEvent(self, a_event: QtGui.QCloseEvent):
        self.settings.save_qwidget_state(self)
        a_event.accept()
