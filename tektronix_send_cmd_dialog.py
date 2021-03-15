from PyQt5 import QtGui, QtWidgets, QtCore

from ui.py.tektronix_send_cmd_dialog import Ui_tektronix_send_cmd_dialog as TektronixSendCmdForm
from irspy.qt.qt_settings_ini_parser import QtSettings

from tekvisa_qcompleter import CmdCompleter
import tekvisa_control as tek


class TektronixSendCmdDialog(QtWidgets.QDialog):

    send_cmd = QtCore.pyqtSignal(str)

    def __init__(self, a_cmd_tree, a_settings: QtSettings, a_parent=None):
        super().__init__(a_parent)

        self.ui = TektronixSendCmdForm()
        self.ui.setupUi(self)
        self.show()

        self.settings = a_settings
        self.settings.restore_qwidget_state(self)

        self.cmd_tree = a_cmd_tree

        cmd_completer = CmdCompleter(self.cmd_tree, self)
        cmd_completer.setCaseSensitivity(QtCore.Qt.CaseInsensitive)
        cmd_completer.setModelSorting(QtWidgets.QCompleter.CaseSensitivelySortedModel)
        self.ui.cmd_edit.setCompleter(cmd_completer)

        self.ui.send_cmd_button.clicked.connect(self.send_button_clicked)
        self.ui.idn_button.clicked.connect(self.idn_button_clicked)
        self.ui.error_buttons.clicked.connect(self.errors_button_clicked)
        self.ui.read_specter_button.clicked.connect(self.read_specter_button_clicked)
        self.ui.cmd_edit.textChanged.connect(self.cmd_edit_text_changed)

    def send_button_clicked(self):
        self.send_cmd.emit(self.ui.cmd_edit.text())

    def idn_button_clicked(self):
        self.send_cmd.emit("*IDN?")

    def errors_button_clicked(self):
        self.send_cmd.emit(":SYST:ERR:ALL?")

    def read_specter_button_clicked(self):
        self.send_cmd.emit(":READ:SPEC?")

    def cmd_edit_text_changed(self, a_cmd: str):
        self.ui.cmd_description_text_edit.clear()
        cmd_description = tek.get_cmd_description(a_cmd.split(" ")[0], self.cmd_tree)
        if cmd_description:
            self.ui.cmd_description_text_edit.appendPlainText(cmd_description)
            self.ui.cmd_description_text_edit.verticalScrollBar().setValue(0)

    def __del__(self):
        self.settings.save_qwidget_state(self)
        print("TektronixSendCmdDialog deleted")
