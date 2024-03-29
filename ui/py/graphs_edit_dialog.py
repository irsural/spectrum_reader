# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file './ui/graphs_edit_dialog.ui'
#
# Created by: PyQt5 UI code generator 5.14.1
#
# WARNING! All changes made in this file will be lost!


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_graphs_edit_dialog(object):
    def setupUi(self, graphs_edit_dialog):
        graphs_edit_dialog.setObjectName("graphs_edit_dialog")
        graphs_edit_dialog.resize(878, 479)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(graphs_edit_dialog.sizePolicy().hasHeightForWidth())
        graphs_edit_dialog.setSizePolicy(sizePolicy)
        graphs_edit_dialog.setMinimumSize(QtCore.QSize(0, 0))
        graphs_edit_dialog.setMaximumSize(QtCore.QSize(99999, 99999))
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(":/icons/icons/graph_2.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        graphs_edit_dialog.setWindowIcon(icon)
        self.horizontalLayout_2 = QtWidgets.QHBoxLayout(graphs_edit_dialog)
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        self.verticalLayout = QtWidgets.QVBoxLayout()
        self.verticalLayout.setObjectName("verticalLayout")
        self.gridLayout = QtWidgets.QGridLayout()
        self.gridLayout.setObjectName("gridLayout")
        self.graphs_table = QtWidgets.QTableWidget(graphs_edit_dialog)
        self.graphs_table.setEditTriggers(QtWidgets.QAbstractItemView.DoubleClicked)
        self.graphs_table.setObjectName("graphs_table")
        self.graphs_table.setColumnCount(6)
        self.graphs_table.setRowCount(0)
        item = QtWidgets.QTableWidgetItem()
        self.graphs_table.setHorizontalHeaderItem(0, item)
        item = QtWidgets.QTableWidgetItem()
        self.graphs_table.setHorizontalHeaderItem(1, item)
        item = QtWidgets.QTableWidgetItem()
        self.graphs_table.setHorizontalHeaderItem(2, item)
        item = QtWidgets.QTableWidgetItem()
        self.graphs_table.setHorizontalHeaderItem(3, item)
        item = QtWidgets.QTableWidgetItem()
        self.graphs_table.setHorizontalHeaderItem(4, item)
        item = QtWidgets.QTableWidgetItem()
        font = QtGui.QFont()
        font.setBold(False)
        font.setWeight(50)
        item.setFont(font)
        self.graphs_table.setHorizontalHeaderItem(5, item)
        self.graphs_table.horizontalHeader().setStretchLastSection(True)
        self.graphs_table.verticalHeader().setVisible(False)
        self.gridLayout.addWidget(self.graphs_table, 1, 0, 1, 1)
        self.verticalLayout_2 = QtWidgets.QVBoxLayout()
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.show_all_button = QtWidgets.QPushButton(graphs_edit_dialog)
        self.show_all_button.setObjectName("show_all_button")
        self.verticalLayout_2.addWidget(self.show_all_button)
        self.hide_all_button = QtWidgets.QPushButton(graphs_edit_dialog)
        self.hide_all_button.setObjectName("hide_all_button")
        self.verticalLayout_2.addWidget(self.hide_all_button)
        self.delete_all_button = QtWidgets.QPushButton(graphs_edit_dialog)
        self.delete_all_button.setObjectName("delete_all_button")
        self.verticalLayout_2.addWidget(self.delete_all_button)
        spacerItem = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.verticalLayout_2.addItem(spacerItem)
        self.gridLayout.addLayout(self.verticalLayout_2, 1, 1, 1, 1)
        self.verticalLayout.addLayout(self.gridLayout)
        self.horizontalLayout_2.addLayout(self.verticalLayout)

        self.retranslateUi(graphs_edit_dialog)
        QtCore.QMetaObject.connectSlotsByName(graphs_edit_dialog)

    def retranslateUi(self, graphs_edit_dialog):
        _translate = QtCore.QCoreApplication.translate
        graphs_edit_dialog.setWindowTitle(_translate("graphs_edit_dialog", "Редактирование графиков"))
        item = self.graphs_table.horizontalHeaderItem(0)
        item.setText(_translate("graphs_edit_dialog", "Имя графика"))
        item = self.graphs_table.horizontalHeaderItem(1)
        item.setText(_translate("graphs_edit_dialog", "Цвет"))
        item = self.graphs_table.horizontalHeaderItem(2)
        item.setText(_translate("graphs_edit_dialog", "Жирный"))
        item = self.graphs_table.horizontalHeaderItem(3)
        item.setText(_translate("graphs_edit_dialog", "Показать"))
        item = self.graphs_table.horizontalHeaderItem(4)
        item.setText(_translate("graphs_edit_dialog", "Удалить"))
        item = self.graphs_table.horizontalHeaderItem(5)
        item.setText(_translate("graphs_edit_dialog", "Путь"))
        self.show_all_button.setText(_translate("graphs_edit_dialog", "Показать все"))
        self.hide_all_button.setText(_translate("graphs_edit_dialog", "Скрыть все"))
        self.delete_all_button.setText(_translate("graphs_edit_dialog", "Удалить все"))
import icons_rc
