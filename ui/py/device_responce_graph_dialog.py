# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file './ui/device_responce_graph_dialog.ui'
#
# Created by: PyQt5 UI code generator 5.14.1
#
# WARNING! All changes made in this file will be lost!


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_device_responce_graph_dialog(object):
    def setupUi(self, device_responce_graph_dialog):
        device_responce_graph_dialog.setObjectName("device_responce_graph_dialog")
        device_responce_graph_dialog.resize(422, 356)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(device_responce_graph_dialog.sizePolicy().hasHeightForWidth())
        device_responce_graph_dialog.setSizePolicy(sizePolicy)
        device_responce_graph_dialog.setMinimumSize(QtCore.QSize(0, 0))
        device_responce_graph_dialog.setMaximumSize(QtCore.QSize(99999, 99999))
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(":/icons/icons/graph_2.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        device_responce_graph_dialog.setWindowIcon(icon)
        self.horizontalLayout_2 = QtWidgets.QHBoxLayout(device_responce_graph_dialog)
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        self.verticalLayout = QtWidgets.QVBoxLayout()
        self.verticalLayout.setObjectName("verticalLayout")
        self.chart_layout = QtWidgets.QVBoxLayout()
        self.chart_layout.setObjectName("chart_layout")
        self.verticalLayout.addLayout(self.chart_layout)
        self.horizontalLayout_3 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_3.setObjectName("horizontalLayout_3")
        self.log_scale_checkbox = QtWidgets.QCheckBox(device_responce_graph_dialog)
        self.log_scale_checkbox.setObjectName("log_scale_checkbox")
        self.horizontalLayout_3.addWidget(self.log_scale_checkbox)
        self.verticalLayout.addLayout(self.horizontalLayout_3)
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        spacerItem = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout.addItem(spacerItem)
        self.close_button = QtWidgets.QPushButton(device_responce_graph_dialog)
        self.close_button.setObjectName("close_button")
        self.horizontalLayout.addWidget(self.close_button)
        self.verticalLayout.addLayout(self.horizontalLayout)
        self.horizontalLayout_2.addLayout(self.verticalLayout)

        self.retranslateUi(device_responce_graph_dialog)
        QtCore.QMetaObject.connectSlotsByName(device_responce_graph_dialog)

    def retranslateUi(self, device_responce_graph_dialog):
        _translate = QtCore.QCoreApplication.translate
        device_responce_graph_dialog.setWindowTitle(_translate("device_responce_graph_dialog", "О программе clb_autocalibration"))
        self.log_scale_checkbox.setText(_translate("device_responce_graph_dialog", "Логарифм. шкала"))
        self.close_button.setText(_translate("device_responce_graph_dialog", "Закрыть"))
import icons_rc
