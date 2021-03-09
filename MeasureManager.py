from typing import Dict, List, Tuple
from enum import IntEnum
import logging
import json

from PyQt5 import QtWidgets, QtCore, QtGui

from irspy.built_in_extensions import OrderedDictInsert
from irspy.qt import qt_utils

from irspy.qt.qt_settings_ini_parser import QtSettings
from config_dialog import ConfigDialog, MeasureConfig


class MeasureManager(QtCore.QObject):
    CURRENT_CONFIG_FILENAME = "current_config.json"

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
        self.measures: Dict[str, MeasureConfig] = OrderedDictInsert()

        self.open_config()
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

    def new_measure(self, a_name="", a_measure_config: MeasureConfig = None):
        selected_row = qt_utils.get_selected_row(self.measures_table)
        row_index = selected_row + 1 if selected_row is not None else self.measures_table.rowCount()

        new_name = a_name if a_name else self.__get_allowable_name(self.__get_measures_list(), "Измерение")

        measure_config = a_measure_config if a_measure_config else MeasureConfig()
        self.measures.insert(row_index, new_name, measure_config)
        self.add_measure_in_table(row_index, new_name, measure_config.is_enabled())
        self.save_config()

    def remove_measure(self):
        selected_rows = [row.row() for row in self.measures_table.selectionModel().selectedRows()]
        selected_rows.sort()

        if selected_rows:
            res = QtWidgets.QMessageBox.question(None, "Подтвердите действие",
                                                 f"Удалить выдыленные измерения? Данное действие нельзя отменить",
                                                 QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No,
                                                 QtWidgets.QMessageBox.No)
            if res == QtWidgets.QMessageBox.Yes:
                for row in reversed(selected_rows):
                    removed_name = self.measures_table.item(row, MeasureManager.MeasureColumn.NAME).text()
                    self.measures_table.removeRow(row)
                    del self.measures[removed_name]
                    self.save_config()

    def swap_measures(self, a_bottom_row):
        """
        Меняет 2 измерения в таблице местами
        :param a_bottom_row: Нижняя строка, которая поменяется местами со строкой, расположенной над ней
        """
        name_item_bottom = self.measures_table.item(a_bottom_row, MeasureManager.MeasureColumn.NAME)
        bottom_name = name_item_bottom.text()
        name_item_top = self.measures_table.item(a_bottom_row - 1, MeasureManager.MeasureColumn.NAME)
        top_name = name_item_top.text()

        name_item_bottom.setText(top_name)
        name_item_top.setText(bottom_name)

        enabled_widget_bottom = self.measures_table.cellWidget(a_bottom_row, MeasureManager.MeasureColumn.ENABLE)
        enabled_checkbox_bottom = qt_utils.unwrap_from_layout(enabled_widget_bottom)
        enabled_widget_top = self.measures_table.cellWidget(a_bottom_row - 1, MeasureManager.MeasureColumn.ENABLE)
        enabled_checkbox_top = qt_utils.unwrap_from_layout(enabled_widget_top)

        bottom_enabled = enabled_checkbox_bottom.isChecked()
        top_enabled = enabled_checkbox_top.isChecked()
        logging.debug(bottom_enabled)
        logging.debug(top_enabled)

        enabled_checkbox_bottom.setChecked(top_enabled)
        enabled_checkbox_top.setChecked(bottom_enabled)

        current_measure_config = self.measures[bottom_name]
        del self.measures[bottom_name]
        self.measures.insert(a_bottom_row - 1, bottom_name, current_measure_config)

    def move_measure_up(self, a_measure_number):
        if a_measure_number > 0:
            self.swap_measures(a_measure_number)
            self.measures_table.selectRow(a_measure_number - 1)
            self.save_config()

    def move_measure_down(self, a_measure_number):
        if a_measure_number < len(self.measures) - 1:
            self.swap_measures(a_measure_number + 1)
            self.measures_table.selectRow(a_measure_number + 1)
            self.save_config()

    def save_config(self):
        with open(MeasureManager.CURRENT_CONFIG_FILENAME, 'w') as config_file:
            json_data = {measure: config.to_dict() for measure, config in self.measures.items()}
            config_file.write(json.dumps(json_data, indent=4, ensure_ascii=False))

    def open_config(self):
        try:
            with open(MeasureManager.CURRENT_CONFIG_FILENAME, 'r') as config_file:
                config: dict = json.loads(config_file.read())
                for measure, measure_config in config.items():
                    self.new_measure(measure, MeasureConfig.from_dict(measure_config))
        except FileNotFoundError:
            pass

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
                    self.save_config()
                else:
                    a_item.setText(self.measure_name_before_rename)

                self.measure_name_before_rename = ""

    def edit_measure_parameters_button_clicked(self):
        sender_button: QtWidgets.QPushButton = self.sender()
        for row in range(self.measures_table.rowCount()):
            cell_widget = self.measures_table.cellWidget(row, MeasureManager.MeasureColumn.SETTINGS)
            settings_button = qt_utils.unwrap_from_layout(cell_widget)
            if sender_button == settings_button:
                measure_name = self.measures_table.item(row, MeasureManager.MeasureColumn.NAME).text()
                config = self.measures[measure_name]
                break
        else:
            assert False, "Не найдена строка таблицы с виджетом-отправителем сигнала"

        config_dialog = ConfigDialog(config, self.cmd_tree, self.settings, self.parent())
        if config_dialog.exec() == QtWidgets.QDialog.Accepted:
            self.measures[measure_name].set_cmd_list(config_dialog.get_cmd_list())
            self.measures[measure_name].set_device_responses(config_dialog.get_device_responses())
            self.measures[measure_name].set_normalize_coef(config_dialog.get_normalize_coef())
            self.measures[measure_name].set_apply_on_limit(config_dialog.get_apply_on_limit())
            self.measures[measure_name].set_limit(config_dialog.get_limit())
            self.save_config()
        config_dialog.close()

    def enable_measure_checkbox_toggled(self, a_state: bool):
        logging.debug("toggle")
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

    def get_enabled_configs(self) -> List[Tuple[str, MeasureConfig]]:
        return [(name, config) for name, config in self.measures.items() if config.is_enabled()]
