from typing import List, Tuple, Dict
from enum import IntEnum
import logging

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
        HIDDEN = 3,
        DELETE = 4,
        COUNT = 5

    def __init__(self, a_graph_styles: Dict[str, Tuple[str, bool, bool]],  a_settings: QtSettings, a_parent=None):
        super().__init__(a_parent)

        self.ui = GraphsEditForm()
        self.ui.setupUi(self)

        self.settings = a_settings
        self.settings.restore_qwidget_state(self)
        self.settings.restore_qwidget_state(self.ui.graphs_table)

        self.ui.graphs_table.setItemDelegate(TransparentPainterForWidget(self.ui.graphs_table, "#d4d4ff"))

        self.graph_styles = a_graph_styles

        for name, graph_style in self.graph_styles.items():
            self.add_graph_to_table(name, *graph_style)

        self.ui.ok_button.clicked.connect(self.ok_button_clicked)
        self.ui.cancel_button.clicked.connect(self.reject)
        self.ui.apply_button.clicked.connect(self.apply_button_clicked)

        self.show()

    def add_graph_to_table(self, a_name, a_color, a_bold, a_hidden):
        row_idx = self.ui.graphs_table.rowCount()
        self.ui.graphs_table.insertRow(row_idx)

        self.ui.graphs_table.setItem(row_idx, GraphsEditDialog.Column.NAME, QtWidgets.QTableWidgetItem(a_name))
        self.ui.graphs_table.setItem(row_idx, GraphsEditDialog.Column.COLOR, QtWidgets.QTableWidgetItem())
        self.ui.graphs_table.setItem(row_idx, GraphsEditDialog.Column.BOLD, QtWidgets.QTableWidgetItem())
        self.ui.graphs_table.setItem(row_idx, GraphsEditDialog.Column.HIDDEN, QtWidgets.QTableWidgetItem())
        self.ui.graphs_table.setItem(row_idx, GraphsEditDialog.Column.DELETE, QtWidgets.QTableWidgetItem())

        button = QtWidgets.QPushButton("")
        self.ui.graphs_table.setCellWidget(row_idx, GraphsEditDialog.Column.COLOR, qt_utils.wrap_in_layout(button))
        button.setStyleSheet(f"QPushButton {{ background-color: {a_color}; border: 0px solid black; }}")
        button.clicked.connect(self.graph_color_button_clicked)

        cb = QtWidgets.QCheckBox()
        self.ui.graphs_table.setCellWidget(row_idx, GraphsEditDialog.Column.BOLD, qt_utils.wrap_in_layout(cb))
        cb.toggled.connect(self.bold_graph_checkbox_toggled)

        cb = QtWidgets.QCheckBox()
        self.ui.graphs_table.setCellWidget(row_idx, GraphsEditDialog.Column.HIDDEN, qt_utils.wrap_in_layout(cb))
        cb.toggled.connect(self.hide_graph_checkbox_toggled)

        button = QtWidgets.QPushButton("Удалить")
        self.ui.graphs_table.setCellWidget(row_idx, GraphsEditDialog.Column.DELETE, qt_utils.wrap_in_layout(button))
        button.clicked.connect(self.delete_graph_button_clicked)

    def graph_color_button_clicked(self):
        pass

    def hide_graph_checkbox_toggled(self, a_state):
        pass

    def bold_graph_checkbox_toggled(self, a_state):
        pass

    def delete_graph_button_clicked(self):
        pass

    def ok_button_clicked(self):
        pass

    def apply_button_clicked(self):
        pass

    def __del__(self):
        self.settings.save_qwidget_state(self.ui.graphs_table)
        self.settings.save_qwidget_state(self)
        print("GraphsEditDialog deleted")
