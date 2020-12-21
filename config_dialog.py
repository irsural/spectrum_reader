import json

from PyQt5 import QtGui, QtWidgets, QtCore

from irspy.qt.qt_settings_ini_parser import QtSettings

from ui.py.config_dialog import Ui_config_dialog as ConfigForm
from tekvisa_qcompleter import CmdCompleter
import tekvisa_control as tek


class ConfigDialog(QtWidgets.QDialog):

    def __init__(self, a_cmd_tree: dict, a_settings: QtSettings, a_parent=None):
        super().__init__(parent=a_parent)

        self.ui = ConfigForm()
        self.ui.setupUi(self)
        self.show()

        self.settings = a_settings
        self.settings.restore_qwidget_state(self)

        self.cmd_tree = a_cmd_tree

        cmd_completer = CmdCompleter(a_cmd_tree, self)
        cmd_completer.setCaseSensitivity(QtCore.Qt.CaseInsensitive)
        cmd_completer.setModelSorting(QtWidgets.QCompleter.CaseSensitivelySortedModel)
        self.ui.cmd_edit.setCompleter(cmd_completer)

        self.ui.add_cmd_button.clicked.connect(self.add_cmd_button_clicked)
        self.ui.remove_cmd_button.clicked.connect(self.remove_cmd_button_clicked)
        self.ui.load_from_file_button.clicked.connect(self.load_from_file_button_clicked)
        self.ui.save_to_file_button.clicked.connect(self.save_to_file_button_clicked)

        self.ui.ok_button.clicked.connect(self.accept)
        self.ui.cancel_button.clicked.connect(self.reject)

    def add_cmd_button_clicked(self):
        cmd = self.ui.cmd_edit.text()
        if cmd:
            cmd_description = tek.get_cmd_description(cmd.split(" ")[0], self.cmd_tree)
            if cmd_description:
                item = QtWidgets.QListWidgetItem(cmd)
                self.ui.cmd_list_widget.insertItem(self.ui.cmd_list_widget.currentRow() + 1, item)
            else:
                QtWidgets.QMessageBox.critical(self, "Ошибка", "Неверная команда", QtWidgets.QMessageBox.Ok,
                                               QtWidgets.QMessageBox.Ok)

    def remove_cmd_button_clicked(self):
        self.ui.cmd_list_widget.takeItem(self.ui.cmd_list_widget.currentRow())

    def load_from_file_button_clicked(self):
        filename, _ = QtWidgets.QFileDialog.getOpenFileName(self, "Загрузка конфигурации", "",
                                                            "Конфигурация TektronixControl (*.tcc)")
        if filename:
            with open(filename, 'r') as file:
                config_data = json.loads(file.read())
                self.ui.cmd_list_widget.clear()
                for config_row in config_data:
                    self.ui.cmd_list_widget.addItem(QtWidgets.QListWidgetItem(config_row))

    def save_to_file_button_clicked(self):
        filename, _ = QtWidgets.QFileDialog.getSaveFileName(self, "Сохренение конфигурации", "",
                                                            "Конфигурация TektronixControl (*.tcc)")
        if filename:
            cmd_list = [self.ui.cmd_list_widget.item(row).text() for row in range(self.ui.cmd_list_widget.count())]
            config_data = json.dumps(cmd_list, indent=4)
            with open(filename, "w") as file:
                file.write(config_data)

    def __del__(self):
        print("ConfigDialog deleted")

    def closeEvent(self, a_event: QtGui.QCloseEvent) -> None:
        self.settings.save_qwidget_state(self)
