from typing import Dict, List, Optional
import logging
import json

from PyQt5 import QtGui, QtWidgets, QtCore

from irspy.qt.custom_widgets.QTableDelegates import TransparentPainterForView
from irspy.qt.custom_widgets.editable_qtabbar import EditableQTabBar
from irspy.qt.qt_settings_ini_parser import QtSettings

from ui.py.config_dialog import Ui_config_dialog as ConfigForm
from device_responce_graph import DeviceResponseGraphDialog
from DeviceResponseModel import DeviceResponseModel
from tekvisa_qcompleter import CmdCompleter
from MeasureConfig import MeasureConfig
import tekvisa_control as tek


class ConfigDialog(QtWidgets.QDialog):

    def __init__(self, a_config: MeasureConfig, a_cmd_tree: dict, a_settings: QtSettings, a_parent=None):
        super().__init__(parent=a_parent)

        self.ui = ConfigForm()
        self.ui.setupUi(self)
        self.show()

        self.settings = a_settings
        self.settings.restore_qwidget_state(self)
        self.settings.restore_qwidget_state(self.ui.config_dialog_splitter)

        self.cmd_tree = a_cmd_tree

        self.ui.device_response_table.setItemDelegate(TransparentPainterForView(self.ui.device_response_table, "#d4d4ff"))
        self.device_responses: List[DeviceResponseModel] = []
        self.current_device_response: Optional[None, DeviceResponseModel] = None

        for cmd in a_config.cmd_list():
            self.ui.cmd_text_edit.moveCursor(QtGui.QTextCursor.End)
            self.ui.cmd_text_edit.insertPlainText(cmd + "\n")
            self.ui.cmd_text_edit.moveCursor(QtGui.QTextCursor.End)

        cmd_completer = CmdCompleter(a_cmd_tree, self)
        cmd_completer.setCaseSensitivity(QtCore.Qt.CaseInsensitive)
        cmd_completer.setModelSorting(QtWidgets.QCompleter.CaseSensitivelySortedModel)
        self.ui.cmd_edit.setCompleter(cmd_completer)

        self.tab_bar = EditableQTabBar(self)
        self.ui.devices_bar_layout.addWidget(self.tab_bar.widget())
        self.tab_bar.tab_added.connect(self.new_device_response_added)
        self.tab_bar.tab_deleted.connect(self.device_response_deleted)
        self.tab_bar.tab_changed.connect(self.device_response_selected)

        for idx, (dr_name, dr_table) in enumerate(a_config.get_device_responses().items()):
            self.tab_bar.add_tab_with_name(dr_name)
            self.device_responses[idx] = DeviceResponseModel(dr_name, dr_table)

        self.tab_bar.widget().setCurrentIndex(0)
        self.device_response_selected(0)

        self.ui.normalize_coef_spinbox.setValue(a_config.normalize_coef())
        self.ui.apply_on_limit_checkbox.setChecked(a_config.apply_on_limit())
        self.ui.limit_spinbox.setValue(a_config.limit())

        self.ui.add_cmd_button.clicked.connect(self.add_cmd_button_clicked)

        self.ui.add_row_button.clicked.connect(self.add_row)
        self.ui.delete_row_button.clicked.connect(self.delete_row)
        self.ui.show_graph_button.clicked.connect(self.show_graph_button_clicked)

        self.ui.load_response_from_file_button.clicked.connect(self.load_device_responses_button_clicked)
        self.ui.save_response_to_file_button.clicked.connect(self.save_device_responses_button_clicked)

        self.ui.ok_button.clicked.connect(self.try_accept)
        self.ui.cancel_button.clicked.connect(self.reject)

    def __del__(self):
        print("ConfigDialog deleted")

    def add_row(self):
        if self.current_device_response is not None:
            selection = self.ui.device_response_table.selectionModel().selectedIndexes()
            if selection:
                row = max(selection, key=lambda idx: idx.row()).row() + 1
            else:
                row = self.current_device_response.rowCount()
            self.current_device_response.add_row(row)
            self.ui.device_response_table.resizeRowsToContents()

    def delete_row(self):
        if self.current_device_response is not None:
            # Множество для удаления дубликатов
            removing_rows = list(set(index.row() for index in self.ui.device_response_table.selectionModel().selectedIndexes()))
            removing_rows.sort()
            for row in reversed(removing_rows):
                self.current_device_response.remove_row(row)

    def new_device_response_added(self, a_idx: int):
        name = self.tab_bar.widget().tabText(a_idx)
        new_model = DeviceResponseModel(a_name=name)
        new_model.add_column(1)
        self.device_responses.append(new_model)

    def device_response_deleted(self, a_idx: int):
        self.device_responses.pop(a_idx)
        if not self.device_responses:
            self.current_device_response = None
            self.ui.device_response_table.setModel(self.current_device_response)

    def device_response_selected(self, a_idx: int):
        if self.device_responses:
            self.current_device_response = self.device_responses[a_idx]
            self.ui.device_response_table.setModel(self.current_device_response)
            self.ui.device_response_table.resizeRowsToContents()

    def add_cmd_button_clicked(self):
        cmd = self.ui.cmd_edit.text()
        if cmd:
            cmd_description = tek.get_cmd_description(cmd.split(" ")[0], self.cmd_tree)
            if cmd_description:
                self.ui.cmd_text_edit.insertPlainText(cmd)
                self.ui.cmd_edit.clear()
            else:
                QtWidgets.QMessageBox.critical(self, "Ошибка", "Неверная команда", QtWidgets.QMessageBox.Ok,
                                               QtWidgets.QMessageBox.Ok)

    def load_device_responses_button_clicked(self):
        if self.current_device_response:
            filename, _ = QtWidgets.QFileDialog.getOpenFileName(self, "Загрузка характеристики устройства", "",
                                                                "Файлы характеристики устройства (*.dr)")
            if filename:
                with open(filename, 'r') as file:
                    dr_data = json.loads(file.read())
                    idx = self.tab_bar.widget().currentIndex()

                    self.device_responses[idx] = DeviceResponseModel.from_dict(dr_data)
                    self.device_response_selected(idx)
                    self.tab_bar.widget().setTabText(idx, self.current_device_response.get_name())

    def save_device_responses_button_clicked(self):
        if self.current_device_response:
            filename, _ = QtWidgets.QFileDialog.getSaveFileName(self, "Сохренение характеристики устройства", "",
                                                                "Файлы характеристики устройства (*.dr)")
            if filename:
                device_responses = self.current_device_response.serialize_to_dict()
                config_data = json.dumps(device_responses, indent=4, ensure_ascii=False)
                with open(filename, "w") as file:
                    file.write(config_data)

    def try_accept(self):
        cmd_text = self.ui.cmd_text_edit.toPlainText()
        cmd_list = cmd_text.split("\n")
        cmd_list = list(filter(lambda x: x != "", cmd_list))

        bad_cmds = []
        for cmd in cmd_list:
            cmd_description = tek.get_cmd_description(cmd.split(" ")[0], self.cmd_tree)
            if not cmd_description:
                bad_cmds.append(cmd)

        if bad_cmds:
            bad_cmds_str = "\n".join(bad_cmds)
            QtWidgets.QMessageBox.critical(self, "Ошибка", f"Следующие команды не распознаны:\n{bad_cmds_str}",
                                           QtWidgets.QMessageBox.Ok, QtWidgets.QMessageBox.Ok)
        else:
            self.accept()

    def get_cmd_list(self):
        cmd_text = self.ui.cmd_text_edit.toPlainText()
        cmd_list = cmd_text.split("\n")
        cmd_list = list(filter(lambda x: x != "", cmd_list))

        for cmd in cmd_list:
            cmd_description = tek.get_cmd_description(cmd.split(" ")[0], self.cmd_tree)
            if not cmd_description:
                raise ValueError
        return cmd_list

    def get_device_responses(self) -> Dict[str, List[List[float]]]:
        return {dr.get_name(): dr.get_table() for dr in self.device_responses}

    def get_normalize_coef(self):
        return self.ui.normalize_coef_spinbox.value()

    def get_apply_on_limit(self):
        return self.ui.apply_on_limit_checkbox.isChecked()

    def get_limit(self):
        return self.ui.limit_spinbox.value()

    def show_graph_button_clicked(self):
        dr_idx = self.tab_bar.widget().currentIndex()
        dr = self.device_responses[dr_idx]
        dialog = DeviceResponseGraphDialog(dr.get_table(), self.settings, self)
        dialog.exec()
        dialog.close()

    def closeEvent(self, a_event: QtGui.QCloseEvent) -> None:
        self.settings.save_qwidget_state(self.ui.config_dialog_splitter)
        self.settings.save_qwidget_state(self)
