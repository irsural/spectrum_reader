from collections import OrderedDict
from typing import List, Union, Generator, Tuple
from enum import IntEnum
import copy
import logging

from PyQt5.QtCore import QModelIndex, Qt
from PyQt5 import QtCore, QtGui
from PyQt5.QtGui import QColor

from irspy import utils


class DeviceResponseModel(QtCore.QAbstractTableModel):
    HEADER_ROW = 0
    HEADER_COLUMN = 0

    COLUMN_0_HEADER = "Частота"
    COLUMN_1_HEADER = "Коэффициент"

    HEADER_COLOR = QColor(209, 230, 255)
    TABLE_COLOR = QColor(255, 255, 255)

    HZ_UNITS = "МГц"
    DB_UNITS = "дБ?"

    DISPLAY_DATA_PRECISION = 3
    EDIT_DATA_PRECISION = 9

    class Status(IntEnum):
        NOT_CHECKED = 0
        BAD = 1
        GOOD = 2

    data_save_state_changed = QtCore.pyqtSignal(str, bool)
    status_changed = QtCore.pyqtSignal(str, Status)

    def __init__(self, a_name: str, a_init_cells: List[List[float]] = None, a_parent=None):
        super().__init__(a_parent)

        self.__name = a_name
        if a_init_cells is None:
            self.__cells = [[0.]]
        else:
            # Первая строка не учитывается в self.get_table(). Генерируем ее вручную
            self.__cells = [[0. for _ in range(len(a_init_cells[0]))]]
            for row_data in a_init_cells:
                self.__cells.append(copy.deepcopy(row_data))

    def get_table(self):
        return self.__cells[1:]

    def __serialize_cells_to_dict(self):
        data_dict = OrderedDict()
        for row, row_data in enumerate(self.get_table()):
            for column, value in enumerate(row_data):
                data_dict[f"{row},{column}"] = value
        return data_dict

    def serialize_to_dict(self):
        data_dict = {
            "name": self.__name,
            "row_count": self.rowCount() - 1
            ,
            "column_count": self.columnCount(),
            "cells": self.__serialize_cells_to_dict(),
        }
        return data_dict

    @classmethod
    def from_dict(cls, a_data_dict: dict):
        row_count = a_data_dict["row_count"]
        column_count = a_data_dict["column_count"]
        assert row_count != 0 and column_count != 0, "Количество строк и колонок должно быть больше нуля!"

        cells_dict: dict = a_data_dict["cells"]
        assert len(cells_dict) == row_count * column_count, \
            "Количество ячеек должно быть равно количество_строк * количество_колонок"

        cells: List[List[float]] = [[0.] * column_count for _ in range(row_count)]
        for row_column, cell_data in cells_dict.items():
            row, column = int(row_column.split(",")[0]), int(row_column.split(",")[1])
            cells[row][column] = float(cell_data)

        assert all([cell is not None for cell in cells])

        return cls(a_name=a_data_dict["name"], a_init_cells=cells)

    def set_name(self, a_name: str):
        self.__name = a_name

    def get_name(self):
        return self.__name

    @staticmethod
    def __is_cell_header(a_row, a_column):
        return a_row == DeviceResponseModel.HEADER_ROW or a_column == DeviceResponseModel.HEADER_COLUMN

    def __first_cell_index(self) -> QModelIndex:
        return self.index(DeviceResponseModel.HEADER_ROW + 1, DeviceResponseModel.HEADER_COLUMN + 1)

    def __last_cell_index(self) -> QModelIndex:
        return self.index(self.rowCount(), self.columnCount())

    def __get_cells_iterator(self) -> Generator[Tuple[int, int, float], None, None]:
        for row, row_data in enumerate(self.__cells):
            for column, cell in enumerate(row_data):
                if not self.__is_cell_header(row, column):
                    yield row, column, cell

    def add_row(self, a_row: int):
        assert a_row != 0, "Строка не должна иметь 0 индекс!"

        new_data_row = []
        for _ in self.__cells[a_row - 1]:
            new_data = 0.
            new_data_row.append(new_data)

        self.beginInsertRows(QModelIndex(), a_row, a_row)
        self.__cells.insert(a_row, new_data_row)
        self.endInsertRows()

    def remove_row(self, a_row: int):
        if a_row != DeviceResponseModel.HEADER_ROW:
            self.beginRemoveRows(QModelIndex(), a_row, a_row)
            del self.__cells[a_row]
            self.endRemoveRows()

    def add_column(self, a_column: int):
        assert a_column != 0, "Столбец не должен иметь 0 индекс!"

        new_data_column = []
        for _ in self.__cells:
            new_data = 0.
            new_data_column.append(new_data)

        self.beginInsertColumns(QModelIndex(), a_column, a_column)
        for idx, cells_row in enumerate(self.__cells):
            cells_row.insert(a_column, new_data_column[idx])
        self.endInsertColumns()

    def remove_column(self, a_column: int):
        if a_column != DeviceResponseModel.HEADER_COLUMN:
            self.beginRemoveColumns(QModelIndex(), a_column, a_column)
            for cell_row in self.__cells:
                del cell_row[a_column]
            self.endRemoveColumns()

    def get_amplitude(self, a_row):
        return self.__cells[a_row][DeviceResponseModel.HEADER_COLUMN]

    def get_amplitude_with_units(self, a_row) -> str:
        return self.data(self.index(a_row, DeviceResponseModel.HEADER_COLUMN))

    def get_frequency(self, a_column):
        return self.__cells[DeviceResponseModel.HEADER_ROW][a_column]

    def get_frequency_with_units(self, a_column) -> str:
        return self.data(self.index(DeviceResponseModel.HEADER_ROW, a_column))

    def rowCount(self, parent=QModelIndex()):
        return len(self.__cells)

    def columnCount(self, parent=QModelIndex()):
        return len(self.__cells[0])

    def __get_cell_color(self, a_index: QtCore.QModelIndex):
        if self.__is_cell_header(a_index.row(), a_index.column()):
            color = DeviceResponseModel.HEADER_COLOR
        else:
            color = DeviceResponseModel.TABLE_COLOR

        return color

    def get_cell_value(self, a_row: int, a_column: int) -> Union[float, None]:
        assert a_row < self.rowCount() and a_column < self.columnCount(), "Задан неверный индекс ячейки!"
        return self.__cells[a_row][a_column]

    def data(self, index, role=Qt.DisplayRole):
        if not index.isValid() or (self.rowCount() < index.row()) or \
                (role != Qt.DisplayRole and role != Qt.EditRole and role != Qt.BackgroundRole):
            return QtCore.QVariant()
        if role == Qt.BackgroundRole:
            return QtCore.QVariant(QtGui.QBrush(self.__get_cell_color(index)))
        else:

            cell_pos = (index.row(), index.column())
            if cell_pos == (DeviceResponseModel.HEADER_ROW, 0):
                return self.COLUMN_0_HEADER
            elif cell_pos == (DeviceResponseModel.HEADER_ROW, 1):
                return self.COLUMN_1_HEADER
            elif index.row() == DeviceResponseModel.HEADER_ROW:
                units = " " + DeviceResponseModel.DB_UNITS
            elif index.column() == DeviceResponseModel.HEADER_COLUMN:
                units = " " + DeviceResponseModel.HZ_UNITS
            else:
                units = ""

            cell_value = self.__cells[index.row()][index.column()]

            if role == Qt.DisplayRole:
                value = utils.float_to_string(cell_value, self.DISPLAY_DATA_PRECISION)
            else:  # role == Qt.EditRole
                value = utils.float_to_string(cell_value, a_precision=self.EDIT_DATA_PRECISION)

            str_value = f"{value}{units}"

            return str_value

    @staticmethod
    def get_display_precision(a_value: float, a_full_precision: int) -> str:
        """
        Конвертирует число в строку с учетом количества разрядов до запятой
        Например для числа 0,123 precision=a_full_precision
        Для числа 1,234 precision=a_full_precision - 1
        Для числа 12,345 precision=a_full_precision - 2
        """
        value_str = f"{a_value:.9f}"
        before_decimal_count = len(value_str.split('.')[0])
        precision = utils.bound(a_full_precision + 1 - before_decimal_count, 0, a_full_precision)
        return precision

    def setData(self, index: QModelIndex, value: str, role=Qt.EditRole):
        if not index.isValid() or role != Qt.EditRole or self.rowCount() <= index.row():
            return False

        try:
            self.__cells[index.row()][index.column()] = utils.parse_input(value)
            result = True
        except ValueError:
            result = False

        return result

    def flags(self, index):
        item_flags = super().flags(index)
        if index.isValid():
            if index.row() != DeviceResponseModel.HEADER_ROW:
                item_flags |= Qt.ItemIsEditable
        return item_flags
