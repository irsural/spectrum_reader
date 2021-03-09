# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file './ui/config_dialog.ui'
#
# Created by: PyQt5 UI code generator 5.14.1
#
# WARNING! All changes made in this file will be lost!


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_config_dialog(object):
    def setupUi(self, config_dialog):
        config_dialog.setObjectName("config_dialog")
        config_dialog.setWindowModality(QtCore.Qt.ApplicationModal)
        config_dialog.resize(790, 661)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(config_dialog.sizePolicy().hasHeightForWidth())
        config_dialog.setSizePolicy(sizePolicy)
        config_dialog.setMinimumSize(QtCore.QSize(0, 0))
        config_dialog.setMaximumSize(QtCore.QSize(99999, 99999))
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(":/icons/icons/graph_2.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        config_dialog.setWindowIcon(icon)
        self.verticalLayout = QtWidgets.QVBoxLayout(config_dialog)
        self.verticalLayout.setObjectName("verticalLayout")
        self.config_dialog_splitter = QtWidgets.QSplitter(config_dialog)
        self.config_dialog_splitter.setOrientation(QtCore.Qt.Horizontal)
        self.config_dialog_splitter.setObjectName("config_dialog_splitter")
        self.frame_2 = QtWidgets.QFrame(self.config_dialog_splitter)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(1)
        sizePolicy.setVerticalStretch(1)
        sizePolicy.setHeightForWidth(self.frame_2.sizePolicy().hasHeightForWidth())
        self.frame_2.setSizePolicy(sizePolicy)
        self.frame_2.setFrameShape(QtWidgets.QFrame.NoFrame)
        self.frame_2.setFrameShadow(QtWidgets.QFrame.Raised)
        self.frame_2.setObjectName("frame_2")
        self.gridLayout = QtWidgets.QGridLayout(self.frame_2)
        self.gridLayout.setContentsMargins(0, 0, 0, 0)
        self.gridLayout.setHorizontalSpacing(6)
        self.gridLayout.setVerticalSpacing(0)
        self.gridLayout.setObjectName("gridLayout")
        self.label = QtWidgets.QLabel(self.frame_2)
        self.label.setObjectName("label")
        self.gridLayout.addWidget(self.label, 0, 0, 1, 1)
        self.horizontalLayout_4 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_4.setContentsMargins(-1, 6, -1, -1)
        self.horizontalLayout_4.setSpacing(6)
        self.horizontalLayout_4.setObjectName("horizontalLayout_4")
        self.load_response_from_file_button = QtWidgets.QPushButton(self.frame_2)
        self.load_response_from_file_button.setText("")
        icon1 = QtGui.QIcon()
        icon1.addPixmap(QtGui.QPixmap(":/icons/icons/open.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.load_response_from_file_button.setIcon(icon1)
        self.load_response_from_file_button.setObjectName("load_response_from_file_button")
        self.horizontalLayout_4.addWidget(self.load_response_from_file_button)
        self.save_response_to_file_button = QtWidgets.QPushButton(self.frame_2)
        self.save_response_to_file_button.setText("")
        icon2 = QtGui.QIcon()
        icon2.addPixmap(QtGui.QPixmap(":/icons/icons/save.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.save_response_to_file_button.setIcon(icon2)
        self.save_response_to_file_button.setObjectName("save_response_to_file_button")
        self.horizontalLayout_4.addWidget(self.save_response_to_file_button)
        self.show_graph_button = QtWidgets.QPushButton(self.frame_2)
        self.show_graph_button.setText("")
        self.show_graph_button.setIcon(icon)
        self.show_graph_button.setObjectName("show_graph_button")
        self.horizontalLayout_4.addWidget(self.show_graph_button)
        spacerItem = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout_4.addItem(spacerItem)
        self.add_row_button = QtWidgets.QPushButton(self.frame_2)
        self.add_row_button.setText("")
        icon3 = QtGui.QIcon()
        icon3.addPixmap(QtGui.QPixmap(":/icons/icons/add_row.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.add_row_button.setIcon(icon3)
        self.add_row_button.setObjectName("add_row_button")
        self.horizontalLayout_4.addWidget(self.add_row_button)
        self.delete_row_button = QtWidgets.QPushButton(self.frame_2)
        self.delete_row_button.setText("")
        icon4 = QtGui.QIcon()
        icon4.addPixmap(QtGui.QPixmap(":/icons/icons/remove_row.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.delete_row_button.setIcon(icon4)
        self.delete_row_button.setObjectName("delete_row_button")
        self.horizontalLayout_4.addWidget(self.delete_row_button)
        spacerItem1 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout_4.addItem(spacerItem1)
        self.gridLayout.addLayout(self.horizontalLayout_4, 1, 0, 1, 1)
        self.verticalLayout_5 = QtWidgets.QVBoxLayout()
        self.verticalLayout_5.setContentsMargins(-1, 6, -1, -1)
        self.verticalLayout_5.setSpacing(0)
        self.verticalLayout_5.setObjectName("verticalLayout_5")
        self.devices_bar_layout = QtWidgets.QVBoxLayout()
        self.devices_bar_layout.setContentsMargins(0, 0, 0, 0)
        self.devices_bar_layout.setSpacing(0)
        self.devices_bar_layout.setObjectName("devices_bar_layout")
        self.verticalLayout_5.addLayout(self.devices_bar_layout)
        self.device_response_table = QtWidgets.QTableView(self.frame_2)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(2)
        sizePolicy.setVerticalStretch(2)
        sizePolicy.setHeightForWidth(self.device_response_table.sizePolicy().hasHeightForWidth())
        self.device_response_table.setSizePolicy(sizePolicy)
        self.device_response_table.setObjectName("device_response_table")
        self.device_response_table.horizontalHeader().setStretchLastSection(True)
        self.device_response_table.verticalHeader().setVisible(False)
        self.verticalLayout_5.addWidget(self.device_response_table)
        self.gridLayout_2 = QtWidgets.QGridLayout()
        self.gridLayout_2.setContentsMargins(-1, 6, -1, -1)
        self.gridLayout_2.setObjectName("gridLayout_2")
        self.normalize_coef_spinbox = QtWidgets.QDoubleSpinBox(self.frame_2)
        self.normalize_coef_spinbox.setSuffix("")
        self.normalize_coef_spinbox.setMaximum(1000.0)
        self.normalize_coef_spinbox.setObjectName("normalize_coef_spinbox")
        self.gridLayout_2.addWidget(self.normalize_coef_spinbox, 0, 1, 1, 1)
        self.label_5 = QtWidgets.QLabel(self.frame_2)
        self.label_5.setObjectName("label_5")
        self.gridLayout_2.addWidget(self.label_5, 2, 0, 1, 1)
        self.label_3 = QtWidgets.QLabel(self.frame_2)
        self.label_3.setObjectName("label_3")
        self.gridLayout_2.addWidget(self.label_3, 0, 0, 1, 1)
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        spacerItem2 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout.addItem(spacerItem2)
        self.apply_on_limit_checkbox = QtWidgets.QCheckBox(self.frame_2)
        self.apply_on_limit_checkbox.setText("")
        self.apply_on_limit_checkbox.setObjectName("apply_on_limit_checkbox")
        self.horizontalLayout.addWidget(self.apply_on_limit_checkbox)
        spacerItem3 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout.addItem(spacerItem3)
        self.gridLayout_2.addLayout(self.horizontalLayout, 1, 1, 1, 1)
        self.label_4 = QtWidgets.QLabel(self.frame_2)
        self.label_4.setObjectName("label_4")
        self.gridLayout_2.addWidget(self.label_4, 1, 0, 1, 1)
        self.limit_spinbox = QtWidgets.QDoubleSpinBox(self.frame_2)
        self.limit_spinbox.setMinimum(-1000.0)
        self.limit_spinbox.setMaximum(1000.0)
        self.limit_spinbox.setObjectName("limit_spinbox")
        self.gridLayout_2.addWidget(self.limit_spinbox, 2, 1, 1, 1)
        self.verticalLayout_5.addLayout(self.gridLayout_2)
        self.gridLayout.addLayout(self.verticalLayout_5, 2, 0, 1, 1)
        self.frame = QtWidgets.QFrame(self.config_dialog_splitter)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.frame.sizePolicy().hasHeightForWidth())
        self.frame.setSizePolicy(sizePolicy)
        self.frame.setFrameShape(QtWidgets.QFrame.NoFrame)
        self.frame.setFrameShadow(QtWidgets.QFrame.Raised)
        self.frame.setLineWidth(0)
        self.frame.setObjectName("frame")
        self.gridLayout_3 = QtWidgets.QGridLayout(self.frame)
        self.gridLayout_3.setContentsMargins(0, 0, 0, 0)
        self.gridLayout_3.setObjectName("gridLayout_3")
        self.label_2 = QtWidgets.QLabel(self.frame)
        self.label_2.setObjectName("label_2")
        self.gridLayout_3.addWidget(self.label_2, 0, 0, 1, 1)
        self.horizontalLayout_3 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_3.setObjectName("horizontalLayout_3")
        self.cmd_edit = QtWidgets.QLineEdit(self.frame)
        self.cmd_edit.setInputMask("")
        self.cmd_edit.setObjectName("cmd_edit")
        self.horizontalLayout_3.addWidget(self.cmd_edit)
        self.add_cmd_button = QtWidgets.QPushButton(self.frame)
        self.add_cmd_button.setText("")
        icon5 = QtGui.QIcon()
        icon5.addPixmap(QtGui.QPixmap(":/icons/icons/plus.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.add_cmd_button.setIcon(icon5)
        self.add_cmd_button.setDefault(True)
        self.add_cmd_button.setObjectName("add_cmd_button")
        self.horizontalLayout_3.addWidget(self.add_cmd_button)
        self.gridLayout_3.addLayout(self.horizontalLayout_3, 1, 0, 1, 1)
        self.cmd_text_edit = QtWidgets.QPlainTextEdit(self.frame)
        self.cmd_text_edit.setObjectName("cmd_text_edit")
        self.gridLayout_3.addWidget(self.cmd_text_edit, 2, 0, 1, 1)
        self.verticalLayout.addWidget(self.config_dialog_splitter)
        self.horizontalLayout_2 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        spacerItem4 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout_2.addItem(spacerItem4)
        self.ok_button = QtWidgets.QPushButton(config_dialog)
        self.ok_button.setObjectName("ok_button")
        self.horizontalLayout_2.addWidget(self.ok_button)
        self.cancel_button = QtWidgets.QPushButton(config_dialog)
        self.cancel_button.setObjectName("cancel_button")
        self.horizontalLayout_2.addWidget(self.cancel_button)
        self.verticalLayout.addLayout(self.horizontalLayout_2)

        self.retranslateUi(config_dialog)
        QtCore.QMetaObject.connectSlotsByName(config_dialog)

    def retranslateUi(self, config_dialog):
        _translate = QtCore.QCoreApplication.translate
        config_dialog.setWindowTitle(_translate("config_dialog", "Конфигурация измерения"))
        self.label.setText(_translate("config_dialog", "Характеристики аппаратуры"))
        self.label_5.setText(_translate("config_dialog", "Порог"))
        self.label_3.setText(_translate("config_dialog", "Нормализующий коэф."))
        self.label_4.setText(_translate("config_dialog", "Применение по порогу"))
        self.label_2.setText(_translate("config_dialog", "Cценарий выполнения"))
        self.cmd_edit.setPlaceholderText(_translate("config_dialog", "Введите команду"))
        self.ok_button.setText(_translate("config_dialog", "Ок"))
        self.cancel_button.setText(_translate("config_dialog", "Отмена"))
import icons_rc
