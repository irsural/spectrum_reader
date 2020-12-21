from typing import Union, Dict, List, Tuple
from enum import IntEnum
import logging

from PyQt5 import QtWidgets, QtCore, QtGui

from irspy.built_in_extensions import OrderedDictInsert
from irspy.qt import qt_utils

from irspy.qt.qt_settings_ini_parser import QtSettings
from config_dialog import ConfigDialog


class ConfigTmp:
    def __init__(self):
        self._enable = False

    def is_enabled(self):
        return self._enable

    def enable(self, a_enable: bool):
        self._enable = a_enable


class MeasureManager(QtCore.QObject):
    class MeasureColumn(IntEnum):
        NAME = 0,
        SETTINGS = 1,
        ENABLE = 2

    def __init__(self, a_cmd_tree: dict, a_measures_table: QtWidgets.QTableWidget, a_settings: QtSettings,
                 a_parent=None):
        super().__init__(parent=a_parent)

        self.measures_table = a_measures_table
        self.settings = a_settings

        self.cmd_tree = a_cmd_tree
        self.measures: Dict[str, ConfigTmp] = OrderedDictInsert()

        self.measure_name_before_rename = ""

        self.measures_table.itemDoubleClicked.connect(self.change_measure_name_started)
        self.measures_table.itemChanged.connect(self.measure_name_changed)

    def update_cmd_tree(self, a_cmd_tree: dict):
        self.cmd_tree = a_cmd_tree

    @staticmethod
    def __get_allowable_name(a_existing_names: list, a_name_template: str) -> str:
        new_name = a_name_template
        counter = 0
        while new_name in a_existing_names:
            counter += 1
            new_name = f"{a_name_template}_{counter}"
        return new_name

    def __get_measures_list(self):
        return [self.measures_table.item(row, MeasureManager.MeasureColumn.NAME).text()
                for row in range(self.measures_table.rowCount())]

    def add_measure_in_table(self, a_row_index: int, a_name: str, a_enabled: bool):
        self.measures_table.insertRow(a_row_index)
        self.measures_table.setItem(a_row_index, MeasureManager.MeasureColumn.NAME, QtWidgets.QTableWidgetItem(a_name))
        self.measures_table.setItem(a_row_index, MeasureManager.MeasureColumn.SETTINGS, QtWidgets.QTableWidgetItem())
        self.measures_table.setItem(a_row_index, MeasureManager.MeasureColumn.ENABLE, QtWidgets.QTableWidgetItem())

        button = QtWidgets.QToolButton()
        button.setText("...")
        self.measures_table.setCellWidget(a_row_index, MeasureManager.MeasureColumn.SETTINGS,
                                          qt_utils.wrap_in_layout(button))
        button.clicked.connect(self.edit_measure_parameters_button_clicked)

        cb = QtWidgets.QCheckBox()
        self.measures_table.setCellWidget(a_row_index, MeasureManager.MeasureColumn.ENABLE, qt_utils.wrap_in_layout(cb))
        cb.setChecked(a_enabled)
        cb.toggled.connect(self.enable_measure_checkbox_toggled)

    def new_measure(self, a_name="", a_measure_config: ConfigTmp = None):
        selected_row = qt_utils.get_selected_row(self.measures_table)
        row_index = selected_row + 1 if selected_row is not None else self.measures_table.rowCount()

        new_name = a_name if a_name else self.__get_allowable_name(self.__get_measures_list(), "Измерение")

        measure_config = a_measure_config if a_measure_config else ConfigTmp()
        self.measures.insert(row_index, new_name, measure_config)
        self.add_measure_in_table(row_index, new_name, measure_config.is_enabled())

    def remove_measure(self):
        selected_row = qt_utils.get_selected_row(self.measures_table)
        if selected_row is not None:
            removed_name = self.measures_table.item(selected_row, MeasureManager.MeasureColumn.NAME).text()
            res = QtWidgets.QMessageBox.question(None, "Подтвердите действие",
                                                 f"Удалить измерение с именем {removed_name}? "
                                                 f"Данное действие нельзя отменить",
                                                 QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No,
                                                 QtWidgets.QMessageBox.No)
            if res == QtWidgets.QMessageBox.Yes:
                self.measures_table.removeRow(selected_row)
                del self.measures[removed_name]

    def change_measure_name_started(self, a_item: QtWidgets.QTableWidgetItem):
        if a_item.column() == MeasureManager.MeasureColumn.NAME:
            self.measure_name_before_rename = self.measures_table.item(a_item.row(), a_item.column()).text()
            assert(self.measure_name_before_rename != "")

    def measure_name_changed(self, a_item: QtWidgets.QTableWidgetItem):
        if self.measure_name_before_rename:
            if a_item.column() == MeasureManager.MeasureColumn.NAME:
                if a_item.text():
                    config = self.measures[self.measure_name_before_rename]
                    del self.measures[self.measure_name_before_rename]
                    self.measures.insert(a_item.row(), a_item.text(), config)
                else:
                    a_item.setText(self.measure_name_before_rename)

                self.measure_name_before_rename = ""

    def edit_measure_parameters_button_clicked(self):
        config_dialog = ConfigDialog(self.cmd_tree, self.settings, self.parent())
        config_dialog.exec()

    def enable_measure_checkbox_toggled(self, a_state: bool):
        checkbox: QtWidgets.QPushButton = self.sender()
        for row in range(self.measures_table.rowCount()):
            cell_widget = self.measures_table.cellWidget(row, MeasureManager.MeasureColumn.ENABLE)
            row_checkbox = qt_utils.unwrap_from_layout(cell_widget)
            if checkbox == row_checkbox:
                measure_name = self.measures_table.item(row, MeasureManager.MeasureColumn.NAME).text()
                config = self.measures[measure_name]
                config.enable(a_state)
                break
        else:
            assert False, "Не найдена строка таблицы с виджетом-отправителем сигнала"
