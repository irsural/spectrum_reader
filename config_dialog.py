import logging
import json

from PyQt5 import QtGui, QtWidgets, QtCore

from irspy.qt.qt_settings_ini_parser import QtSettings
from editable_qtabbar import EditableQTabBar

from ui.py.config_dialog import Ui_config_dialog as ConfigForm
from tekvisa_qcompleter import CmdCompleter
import tekvisa_control as tek


class TekConfig:

    def __init__(self, a_cmd_list=None, a_enable=False):
        self._cmd_list = [] if a_cmd_list is None else a_cmd_list
        self._enable = a_enable

    def cmd_list(self):
        return self._cmd_list

    def set_cmd_list(self, a_cmd_list: list):
        self._cmd_list = a_cmd_list

    def is_enabled(self):
        return self._enable

    def enable(self, a_enable: bool):
        self._enable = a_enable

    def to_dict(self):
        return {
            "cmd_list": self._cmd_list,
            "enable": self._enable
        }

    @classmethod
    def from_dict(cls, a_dict: dict):
        cmd_list = a_dict["cmd_list"]
        enable = a_dict["enable"]
        return cls(cmd_list, enable)


class ConfigDialog(QtWidgets.QDialog):

    def __init__(self, a_config: TekConfig, a_cmd_tree: dict, a_settings: QtSettings, a_parent=None):
        super().__init__(parent=a_parent)

        self.ui = ConfigForm()
        self.ui.setupUi(self)
        self.show()

        self.settings = a_settings
        self.settings.restore_qwidget_state(self)
        self.settings.restore_qwidget_state(self.ui.config_dialog_splitter)

        self.cmd_tree = a_cmd_tree

        for cmd in a_config.cmd_list():
            self.ui.cmd_list_widget.addItem(QtWidgets.QListWidgetItem(cmd))

        cmd_completer = CmdCompleter(a_cmd_tree, self)
        cmd_completer.setCaseSensitivity(QtCore.Qt.CaseInsensitive)
        cmd_completer.setModelSorting(QtWidgets.QCompleter.CaseSensitivelySortedModel)
        self.ui.cmd_edit.setCompleter(cmd_completer)

        self.tab_bar = EditableQTabBar(self)
        self.ui.devices_bar_layout.addWidget(self.tab_bar.widget())
        self.tab_bar.tab_added.connect(self.new_device_response_added)
        self.tab_bar.tab_deleted.connect(self.device_response_deleted)
        self.tab_bar.tab_changed.connect(self.device_response_selected)

        self.ui.add_cmd_button.clicked.connect(self.add_cmd_button_clicked)
        self.ui.remove_cmd_button.clicked.connect(self.remove_cmd_button_clicked)
        self.ui.load_script_from_file_button.clicked.connect(self.load_script_from_file_button_clicked)
        self.ui.save_script_to_file_button.clicked.connect(self.save_script_to_file_button_clicked)

        self.ui.cmd_list_widget.currentItemChanged.connect(self.current_list_item_changed)

        self.ui.ok_button.clicked.connect(self.accept)
        self.ui.cancel_button.clicked.connect(self.reject)

    def new_device_response_added(self, a_idx: int):
        logging.debug(f"Tab {a_idx} added")

    def device_response_deleted(self, a_idx: int):
        logging.debug(f"Tab {a_idx} deleted")

    def device_response_selected(self, a_idx: int):
        logging.debug(f"Tab {a_idx} selected")

    def add_cmd_button_clicked(self):
        cmd = self.ui.cmd_edit.text()
        if cmd:
            cmd_description = tek.get_cmd_description(cmd.split(" ")[0], self.cmd_tree)
            if cmd_description:
                item = QtWidgets.QListWidgetItem(cmd)
                self.ui.cmd_list_widget.insertItem(self.ui.cmd_list_widget.currentRow() + 1, item)
                self.ui.cmd_list_widget.setCurrentItem(item)
                self.ui.cmd_edit.clear()
            else:
                QtWidgets.QMessageBox.critical(self, "Ошибка", "Неверная команда", QtWidgets.QMessageBox.Ok,
                                               QtWidgets.QMessageBox.Ok)

    def remove_cmd_button_clicked(self):
        self.ui.cmd_list_widget.takeItem(self.ui.cmd_list_widget.currentRow())

    def load_script_from_file_button_clicked(self):
        filename, _ = QtWidgets.QFileDialog.getOpenFileName(self, "Загрузка конфигурации", "",
                                                            "Конфигурация TektronixControl (*.tcc)")
        if filename:
            with open(filename, 'r') as file:
                config_data = json.loads(file.read())
                self.ui.cmd_list_widget.clear()
                for config_row in config_data:
                    self.ui.cmd_list_widget.addItem(QtWidgets.QListWidgetItem(config_row))

    def save_script_to_file_button_clicked(self):
        filename, _ = QtWidgets.QFileDialog.getSaveFileName(self, "Сохренение конфигурации", "",
                                                            "Конфигурация TektronixControl (*.tcc)")
        if filename:
            cmd_list = [self.ui.cmd_list_widget.item(row).text() for row in range(self.ui.cmd_list_widget.count())]
            config_data = json.dumps(cmd_list, indent=4, ensure_ascii=False)
            with open(filename, "w") as file:
                file.write(config_data)

    def get_cmd_list(self):
        return [self.ui.cmd_list_widget.item(row).text() for row in range(self.ui.cmd_list_widget.count())]

    def current_list_item_changed(self, a_item: QtWidgets.QTableWidgetItem, _):
        if a_item is not None:
            self.ui.cmd_edit.setText(a_item.text())

    def __del__(self):
        print("ConfigDialog deleted")

    def closeEvent(self, a_event: QtGui.QCloseEvent) -> None:
        self.settings.save_qwidget_state(self.ui.config_dialog_splitter)
        self.settings.save_qwidget_state(self)
