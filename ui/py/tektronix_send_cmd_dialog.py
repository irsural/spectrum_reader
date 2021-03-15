# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file './ui/tektronix_send_cmd_dialog.ui'
#
# Created by: PyQt5 UI code generator 5.14.1
#
# WARNING! All changes made in this file will be lost!


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_tektronix_send_cmd_dialog(object):
    def setupUi(self, tektronix_send_cmd_dialog):
        tektronix_send_cmd_dialog.setObjectName("tektronix_send_cmd_dialog")
        tektronix_send_cmd_dialog.resize(267, 193)
        self.gridLayout = QtWidgets.QGridLayout(tektronix_send_cmd_dialog)
        self.gridLayout.setObjectName("gridLayout")
        self.cmd_edit = QtWidgets.QLineEdit(tektronix_send_cmd_dialog)
        self.cmd_edit.setObjectName("cmd_edit")
        self.gridLayout.addWidget(self.cmd_edit, 4, 0, 1, 1)
        self.label_4 = QtWidgets.QLabel(tektronix_send_cmd_dialog)
        self.label_4.setObjectName("label_4")
        self.gridLayout.addWidget(self.label_4, 1, 0, 1, 1)
        self.horizontalLayout_2 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        self.idn_button = QtWidgets.QPushButton(tektronix_send_cmd_dialog)
        self.idn_button.setObjectName("idn_button")
        self.horizontalLayout_2.addWidget(self.idn_button)
        self.error_buttons = QtWidgets.QPushButton(tektronix_send_cmd_dialog)
        self.error_buttons.setObjectName("error_buttons")
        self.horizontalLayout_2.addWidget(self.error_buttons)
        self.read_specter_button = QtWidgets.QPushButton(tektronix_send_cmd_dialog)
        self.read_specter_button.setObjectName("read_specter_button")
        self.horizontalLayout_2.addWidget(self.read_specter_button)
        self.gridLayout.addLayout(self.horizontalLayout_2, 0, 0, 1, 2)
        self.cmd_description_text_edit = QtWidgets.QPlainTextEdit(tektronix_send_cmd_dialog)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(1)
        sizePolicy.setHeightForWidth(self.cmd_description_text_edit.sizePolicy().hasHeightForWidth())
        self.cmd_description_text_edit.setSizePolicy(sizePolicy)
        self.cmd_description_text_edit.setMaximumSize(QtCore.QSize(16777215, 16777215))
        self.cmd_description_text_edit.setObjectName("cmd_description_text_edit")
        self.gridLayout.addWidget(self.cmd_description_text_edit, 2, 0, 1, 2)
        self.send_cmd_button = QtWidgets.QPushButton(tektronix_send_cmd_dialog)
        self.send_cmd_button.setObjectName("send_cmd_button")
        self.gridLayout.addWidget(self.send_cmd_button, 4, 1, 1, 1)
        self.label_5 = QtWidgets.QLabel(tektronix_send_cmd_dialog)
        self.label_5.setObjectName("label_5")
        self.gridLayout.addWidget(self.label_5, 3, 0, 1, 1)

        self.retranslateUi(tektronix_send_cmd_dialog)
        QtCore.QMetaObject.connectSlotsByName(tektronix_send_cmd_dialog)

    def retranslateUi(self, tektronix_send_cmd_dialog):
        _translate = QtCore.QCoreApplication.translate
        tektronix_send_cmd_dialog.setWindowTitle(_translate("tektronix_send_cmd_dialog", "Отправить команду"))
        self.label_4.setText(_translate("tektronix_send_cmd_dialog", "Описание команды"))
        self.idn_button.setText(_translate("tektronix_send_cmd_dialog", "*IDN?"))
        self.error_buttons.setText(_translate("tektronix_send_cmd_dialog", "Ошибки"))
        self.read_specter_button.setText(_translate("tektronix_send_cmd_dialog", "Спектр"))
        self.send_cmd_button.setText(_translate("tektronix_send_cmd_dialog", "Отправить"))
        self.label_5.setText(_translate("tektronix_send_cmd_dialog", "Команда"))
