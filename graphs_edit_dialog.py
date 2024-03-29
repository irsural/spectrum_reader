from typing import List, Dict
from enum import IntEnum
import logging

from PyQt5 import QtGui, QtWidgets, QtCore

from irspy.qt.custom_widgets.QTableDelegates import TransparentPainterForWidget
from irspy.qt.qt_settings_ini_parser import QtSettings
from irspy.qt import qt_utils
from irspy import utils

from ui.py.graphs_edit_dialog import Ui_graphs_edit_dialog as GraphsEditForm


class GraphsEditDialog(QtWidgets.QDialog):

    class Column(IntEnum):
        NAME = 0,
        COLOR = 1,
        BOLD = 2,
        SHOW = 3,
        DELETE = 4,
        PATH = 5,
        COUNT = 6

    class PropertiesItem(IntEnum):
        COLOR = 0,
        BOLD = 1,
        SHOW = 2,
        PATH = 3

    DEFAULT_PEN_WIDTH = 2
    BOLD_PEN_WIDTH = 4

    enable_graph = QtCore.pyqtSignal(str, bool)
    change_graph_color = QtCore.pyqtSignal(str, QtGui.QColor)
    bold_graph_enable = QtCore.pyqtSignal(str, bool)
    remove_graph = QtCore.pyqtSignal(str)
    rename_graph = QtCore.pyqtSignal(str, str)

    def __init__(self, a_graph_properties: Dict[str, List], a_lock_changes,
                 a_settings: QtSettings, a_parent=None):
        super().__init__(a_parent)

        self.ui = GraphsEditForm()
        self.ui.setupUi(self)

        self.settings = a_settings
        self.settings.restore_qwidget_state(self)
        self.settings.restore_qwidget_state(self.ui.graphs_table)

        self.ui.graphs_table.setItemDelegate(TransparentPainterForWidget(self.ui.graphs_table, "#d4d4ff"))
        self.ui.graphs_table.cellDoubleClicked.connect(self.cell_double_clicked)

        self.graph_properties = a_graph_properties

        for name, style in self.graph_properties.items():
            self.add_graph_to_table(name, *style, a_lock_changes)

        self.measure_name_before_rename = ""

        self.ui.show_all_button.clicked.connect(self.show_all_button_clicked)
        self.ui.hide_all_button.clicked.connect(self.hide_all_button_clicked)
        self.ui.delete_all_button.clicked.connect(self.delete_all_button_clicked)
        self.ui.graphs_table.itemChanged.connect(self.measure_renamed)

        self.show()

    @staticmethod
    def __add_non_editable_item(a_table_widget, a_row, a_column, a_text=""):
        item = QtWidgets.QTableWidgetItem(a_text)
        item.setFlags(item.flags() & ~QtCore.Qt.ItemIsEditable)
        a_table_widget.setItem(a_row, a_column, item)

    def add_graph_to_table(self, a_name, a_color, a_bold, a_show, a_graph_filepath, a_lock_changes):
        row_idx = self.ui.graphs_table.rowCount()
        self.ui.graphs_table.insertRow(row_idx)

        if a_lock_changes:
            self.__add_non_editable_item(self.ui.graphs_table, row_idx, GraphsEditDialog.Column.NAME, a_name)
        else:
            self.ui.graphs_table.setItem(row_idx, GraphsEditDialog.Column.NAME, QtWidgets.QTableWidgetItem(a_name))

        self.__add_non_editable_item(self.ui.graphs_table, row_idx, GraphsEditDialog.Column.COLOR)
        self.__add_non_editable_item(self.ui.graphs_table, row_idx, GraphsEditDialog.Column.BOLD)
        self.__add_non_editable_item(self.ui.graphs_table, row_idx, GraphsEditDialog.Column.SHOW)
        self.__add_non_editable_item(self.ui.graphs_table, row_idx, GraphsEditDialog.Column.DELETE)
        self.__add_non_editable_item(self.ui.graphs_table, row_idx, GraphsEditDialog.Column.PATH)

        self.ui.graphs_table.item(row_idx, GraphsEditDialog.Column.COLOR).setBackground(QtGui.QColor(a_color))

        cb = QtWidgets.QCheckBox()
        self.ui.graphs_table.setCellWidget(row_idx, GraphsEditDialog.Column.BOLD, qt_utils.wrap_in_layout(cb))
        cb.setChecked(a_bold)
        cb.toggled.connect(self.bold_graph_checkbox_toggled)

        cb = QtWidgets.QCheckBox()
        self.ui.graphs_table.setCellWidget(row_idx, GraphsEditDialog.Column.SHOW, qt_utils.wrap_in_layout(cb))
        cb.setChecked(a_show)
        cb.toggled.connect(self.show_graph_checkbox_toggled)

        button = QtWidgets.QPushButton("Удалить")
        self.ui.graphs_table.setCellWidget(row_idx, GraphsEditDialog.Column.DELETE, qt_utils.wrap_in_layout(button))
        button.clicked.connect(self.delete_graph_button_clicked)

        self.ui.graphs_table.item(row_idx, GraphsEditDialog.Column.PATH).setText(a_graph_filepath)

    def __get_name_by_row(self, a_row):
        return self.ui.graphs_table.item(a_row, GraphsEditDialog.Column.NAME).text()

    def cell_double_clicked(self, a_row, a_column):
        name = self.__get_name_by_row(a_row)

        if a_column == GraphsEditDialog.Column.COLOR:
            color = self.graph_properties[name][GraphsEditDialog.PropertiesItem.COLOR]
            new_color = QtWidgets.QColorDialog.getColor(QtGui.QColor(color))
            if new_color.isValid():
                self.ui.graphs_table.item(a_row, GraphsEditDialog.Column.COLOR).setBackground(new_color)

                self.change_graph_color.emit(name, new_color)

        elif a_column == GraphsEditDialog.Column.NAME:
            self.measure_name_before_rename = name
            assert(self.measure_name_before_rename != "")

    def measure_renamed(self, a_item: QtWidgets.QTableWidgetItem):
        if a_item.column() == GraphsEditDialog.Column.NAME:
            if self.measure_name_before_rename:
                new_name = a_item.text()
                if new_name:
                    new_name = utils.get_allowable_name(self.graph_properties.keys(), new_name)

                    properties = self.graph_properties[self.measure_name_before_rename]
                    del self.graph_properties[self.measure_name_before_rename]
                    self.graph_properties[new_name] = properties

                    self.rename_graph.emit(self.measure_name_before_rename, new_name)

                    if a_item.text() != new_name:
                        # Если заданное имя уже существует и new_name подправлено в get_allowable_name
                        self.measure_name_before_rename = ""
                        a_item.setText(new_name)
                else:
                    old_name = self.measure_name_before_rename
                    self.measure_name_before_rename = ""
                    a_item.setText(old_name)

                self.measure_name_before_rename = ""

    def __get_row_by_sender_widget(self, a_sender, a_sender_column):
        for row in range(self.ui.graphs_table.rowCount()):
            cell_widget = self.ui.graphs_table.cellWidget(row, a_sender_column)
            widget = qt_utils.unwrap_from_layout(cell_widget)

            if a_sender == widget:
                selected_row = row
                break
        else:
            assert False, "Не найдена строка таблицы с виджетом-отправителем сигнала"

        return selected_row

    def show_graph_checkbox_toggled(self, a_state):
        sender_checkbox = self.sender()
        graph_row = self.__get_row_by_sender_widget(sender_checkbox, GraphsEditDialog.Column.SHOW)
        name = self.__get_name_by_row(graph_row)

        self.enable_graph.emit(name, a_state)

    def bold_graph_checkbox_toggled(self, a_state):
        sender_checkbox = self.sender()
        graph_row = self.__get_row_by_sender_widget(sender_checkbox, GraphsEditDialog.Column.BOLD)
        name = self.__get_name_by_row(graph_row)

        self.bold_graph_enable.emit(name, a_state)

    def delete_graph_button_clicked(self):
        delete_button = self.sender()
        deleted_row = self.__get_row_by_sender_widget(delete_button, GraphsEditDialog.Column.DELETE)
        graph_name = self.__get_name_by_row(deleted_row)

        self.ui.graphs_table.removeRow(deleted_row)
        self.remove_graph.emit(graph_name)

    def show_all_button_clicked(self):
        for row in range(self.ui.graphs_table.rowCount()):
            widget = self.ui.graphs_table.cellWidget(row, GraphsEditDialog.Column.SHOW)
            show_checkbox = qt_utils.unwrap_from_layout(widget)
            show_checkbox.setChecked(True)

    def hide_all_button_clicked(self):
        for row in range(self.ui.graphs_table.rowCount()):
            widget = self.ui.graphs_table.cellWidget(row, GraphsEditDialog.Column.SHOW)
            show_checkbox = qt_utils.unwrap_from_layout(widget)
            show_checkbox.setChecked(False)

    def delete_all_button_clicked(self):
        res = QtWidgets.QMessageBox.question(self, "Подтвердите действие", "Вы действительно хотите удалить все графики?",
                                             QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No,
                                             QtWidgets.QMessageBox.Yes)
        if res == QtWidgets.QMessageBox.Yes:
            for row in reversed(range(self.ui.graphs_table.rowCount())):
                widget = self.ui.graphs_table.cellWidget(row, GraphsEditDialog.Column.DELETE)
                delete_button = qt_utils.unwrap_from_layout(widget)
                delete_button.click()

    def ok_button_clicked(self):
        self.accept()

    def __del__(self):
        self.settings.save_qwidget_state(self.ui.graphs_table)
        self.settings.save_qwidget_state(self)
        print("GraphsEditDialog deleted")
