from typing import List, Tuple, Dict
from enum import IntEnum
import logging

from pyqtgraph import PlotWidget, PlotDataItem
from PyQt5 import QtGui, QtWidgets, QtCore

from irspy.qt.custom_widgets.QTableDelegates import TransparentPainterForWidget
from irspy.qt.qt_settings_ini_parser import QtSettings
from irspy.qt import qt_utils

from ui.py.graphs_edit_dialog import Ui_graphs_edit_dialog as GraphsEditForm


class GraphsEditDialog(QtWidgets.QDialog):

    class Column(IntEnum):
        NAME = 0,
        COLOR = 1,
        BOLD = 2,
        SHOW = 3,
        DELETE = 4,
        COUNT = 5

    class StylesItem(IntEnum):
        COLOR = 0,
        BOLD = 1,
        SHOW = 2

    DEFAULT_PEN_WIDTH = 2
    BOLD_PEN_WIDTH = 4

    enable_graph = QtCore.pyqtSignal(str, bool)
    remove_graph = QtCore.pyqtSignal(str)

    def __init__(self, a_graph_widget: PlotWidget, a_graph_styles: Dict[str, Tuple[str, bool, bool]], a_lock_changes,
                 a_settings: QtSettings, a_parent=None):
        super().__init__(a_parent)

        self.ui = GraphsEditForm()
        self.ui.setupUi(self)

        self.settings = a_settings
        self.settings.restore_qwidget_state(self)
        self.settings.restore_qwidget_state(self.ui.graphs_table)

        self.ui.graphs_table.setItemDelegate(TransparentPainterForWidget(self.ui.graphs_table, "#d4d4ff"))
        self.ui.graphs_table.cellDoubleClicked.connect(self.cell_double_clicked)

        self.graph_widget = a_graph_widget
        self.graph_styles = a_graph_styles

        for name, style in self.graph_styles.items():
            self.add_graph_to_table(name, *style, a_lock_changes)

        self.ui.show_all_button.clicked.connect(self.show_all_button_clicked)
        self.ui.hide_all_button.clicked.connect(self.hide_all_button_clicked)
        self.ui.delete_all_button.clicked.connect(self.delete_all_button_clicked)

        self.ui.ok_button.clicked.connect(self.ok_button_clicked)
        self.ui.cancel_button.clicked.connect(self.reject)
        self.ui.apply_button.clicked.connect(self.apply_button_clicked)

        self.show()

    @staticmethod
    def __add_non_editable_item(a_table_widget, a_row, a_column, a_text=""):
        item = QtWidgets.QTableWidgetItem(a_text)
        item.setFlags(item.flags() & ~QtCore.Qt.ItemIsEditable)
        a_table_widget.setItem(a_row, a_column, item)

    def add_graph_to_table(self, a_name, a_color, a_bold, a_show, a_lock_changes):
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

    def __get_plot_by_name(self, a_graph_name) -> PlotDataItem:
        for plot in self.graph_widget.plotItem.listDataItems():
            if plot.name() == a_graph_name:
                return plot
        else:
            assert False, f"Не удалось найти график с именем {a_graph_name}"

    def __get_row_by_name(self, a_name):
        for row in range(self.ui.graphs_table.rowCount()):
            pass

    def __get_name_by_row(self, a_row):
        return self.ui.graphs_table.item(a_row, GraphsEditDialog.Column.NAME).text()

    def cell_double_clicked(self, a_row, a_column):
        name = self.__get_name_by_row(a_row)
        color = self.graph_styles[name][GraphsEditDialog.StylesItem.COLOR]
        if a_column == GraphsEditDialog.Column.COLOR:
            new_color = QtWidgets.QColorDialog.getColor(QtGui.QColor(color))
            if new_color.isValid():
                self.ui.graphs_table.item(a_row, GraphsEditDialog.Column.COLOR).setBackground(new_color)

                plot = self.__get_plot_by_name(name)
                current_pen: QtGui.QPen = plot.opts['pen']
                current_pen.setColor(new_color)
                plot.setPen(current_pen)

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
        plot = self.__get_plot_by_name(name)

        current_pen: QtGui.QPen = plot.opts['pen']
        new_width = GraphsEditDialog.BOLD_PEN_WIDTH if a_state else GraphsEditDialog.DEFAULT_PEN_WIDTH
        current_pen.setWidth(new_width)
        plot.setPen(current_pen)

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
        for row in reversed(range(self.ui.graphs_table.rowCount())):
            widget = self.ui.graphs_table.cellWidget(row, GraphsEditDialog.Column.DELETE)
            delete_button = qt_utils.unwrap_from_layout(widget)
            delete_button.click()

    def ok_button_clicked(self):
        self.apply_button_clicked()
        self.accept()

    def apply_button_clicked(self):
        pass

    def __del__(self):
        self.settings.save_qwidget_state(self.ui.graphs_table)
        self.settings.save_qwidget_state(self)
        print("GraphsEditDialog deleted")
