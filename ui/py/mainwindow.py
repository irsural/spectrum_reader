# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file './ui/mainwindow.ui'
#
# Created by: PyQt5 UI code generator 5.15.2
#
# WARNING: Any manual changes made to this file will be lost when pyuic5 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(716, 607)
        font = QtGui.QFont()
        font.setPointSize(10)
        MainWindow.setFont(font)
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap("./ui\\../main_icon.ico"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        MainWindow.setWindowIcon(icon)
        MainWindow.setAnimated(True)
        MainWindow.setDocumentMode(False)
        self.centralWidget = QtWidgets.QWidget(MainWindow)
        self.centralWidget.setObjectName("centralWidget")
        self.gridLayout = QtWidgets.QGridLayout(self.centralWidget)
        self.gridLayout.setContentsMargins(3, 3, 3, 3)
        self.gridLayout.setSpacing(6)
        self.gridLayout.setObjectName("gridLayout")
        self.mw_splitter_2 = QtWidgets.QSplitter(self.centralWidget)
        self.mw_splitter_2.setOrientation(QtCore.Qt.Vertical)
        self.mw_splitter_2.setObjectName("mw_splitter_2")
        self.mw_splitter_1 = QtWidgets.QSplitter(self.mw_splitter_2)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(1)
        sizePolicy.setHeightForWidth(self.mw_splitter_1.sizePolicy().hasHeightForWidth())
        self.mw_splitter_1.setSizePolicy(sizePolicy)
        self.mw_splitter_1.setOrientation(QtCore.Qt.Horizontal)
        self.mw_splitter_1.setObjectName("mw_splitter_1")
        self.layoutWidget = QtWidgets.QWidget(self.mw_splitter_1)
        self.layoutWidget.setObjectName("layoutWidget")
        self.chart_layout = QtWidgets.QVBoxLayout(self.layoutWidget)
        self.chart_layout.setContentsMargins(3, 3, 3, 3)
        self.chart_layout.setSpacing(6)
        self.chart_layout.setObjectName("chart_layout")
        self.layoutWidget1 = QtWidgets.QWidget(self.mw_splitter_1)
        self.layoutWidget1.setObjectName("layoutWidget1")
        self.verticalLayout_3 = QtWidgets.QVBoxLayout(self.layoutWidget1)
        self.verticalLayout_3.setContentsMargins(3, 3, 11, 3)
        self.verticalLayout_3.setSpacing(6)
        self.verticalLayout_3.setObjectName("verticalLayout_3")
        self.gridLayout_2 = QtWidgets.QGridLayout()
        self.gridLayout_2.setContentsMargins(3, -1, -1, -1)
        self.gridLayout_2.setSpacing(6)
        self.gridLayout_2.setObjectName("gridLayout_2")
        self.label_3 = QtWidgets.QLabel(self.layoutWidget1)
        self.label_3.setObjectName("label_3")
        self.gridLayout_2.addWidget(self.label_3, 3, 0, 1, 1)
        self.cmd_edit = QtWidgets.QLineEdit(self.layoutWidget1)
        self.cmd_edit.setObjectName("cmd_edit")
        self.gridLayout_2.addWidget(self.cmd_edit, 8, 0, 1, 1)
        self.send_cmd_button = QtWidgets.QPushButton(self.layoutWidget1)
        self.send_cmd_button.setObjectName("send_cmd_button")
        self.gridLayout_2.addWidget(self.send_cmd_button, 8, 1, 1, 1)
        self.connect_button = QtWidgets.QPushButton(self.layoutWidget1)
        self.connect_button.setObjectName("connect_button")
        self.gridLayout_2.addWidget(self.connect_button, 1, 1, 1, 1)
        self.ip_edit = QtWidgets.QLineEdit(self.layoutWidget1)
        self.ip_edit.setObjectName("ip_edit")
        self.gridLayout_2.addWidget(self.ip_edit, 1, 0, 1, 1)
        self.line_2 = QtWidgets.QFrame(self.layoutWidget1)
        self.line_2.setFrameShape(QtWidgets.QFrame.HLine)
        self.line_2.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.line_2.setObjectName("line_2")
        self.gridLayout_2.addWidget(self.line_2, 2, 0, 1, 2)
        self.label_2 = QtWidgets.QLabel(self.layoutWidget1)
        self.label_2.setObjectName("label_2")
        self.gridLayout_2.addWidget(self.label_2, 0, 0, 1, 1)
        self.horizontalLayout_5 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_5.setSpacing(6)
        self.horizontalLayout_5.setObjectName("horizontalLayout_5")
        self.idn_button = QtWidgets.QPushButton(self.layoutWidget1)
        self.idn_button.setObjectName("idn_button")
        self.horizontalLayout_5.addWidget(self.idn_button)
        self.error_buttons = QtWidgets.QPushButton(self.layoutWidget1)
        self.error_buttons.setObjectName("error_buttons")
        self.horizontalLayout_5.addWidget(self.error_buttons)
        self.read_specter_button = QtWidgets.QPushButton(self.layoutWidget1)
        self.read_specter_button.setObjectName("read_specter_button")
        self.horizontalLayout_5.addWidget(self.read_specter_button)
        self.gridLayout_2.addLayout(self.horizontalLayout_5, 9, 0, 1, 2)
        self.cmd_description_text_edit = QtWidgets.QPlainTextEdit(self.layoutWidget1)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.cmd_description_text_edit.sizePolicy().hasHeightForWidth())
        self.cmd_description_text_edit.setSizePolicy(sizePolicy)
        self.cmd_description_text_edit.setMaximumSize(QtCore.QSize(16777215, 60))
        self.cmd_description_text_edit.setReadOnly(True)
        self.cmd_description_text_edit.setObjectName("cmd_description_text_edit")
        self.gridLayout_2.addWidget(self.cmd_description_text_edit, 4, 0, 3, 2)
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setSpacing(6)
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.label = QtWidgets.QLabel(self.layoutWidget1)
        self.label.setObjectName("label")
        self.horizontalLayout.addWidget(self.label)
        self.tip_full_cmd_checkbox = QtWidgets.QCheckBox(self.layoutWidget1)
        self.tip_full_cmd_checkbox.setObjectName("tip_full_cmd_checkbox")
        self.horizontalLayout.addWidget(self.tip_full_cmd_checkbox)
        self.gridLayout_2.addLayout(self.horizontalLayout, 7, 0, 1, 2)
        self.verticalLayout_3.addLayout(self.gridLayout_2)
        self.line = QtWidgets.QFrame(self.layoutWidget1)
        self.line.setFrameShape(QtWidgets.QFrame.HLine)
        self.line.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.line.setObjectName("line")
        self.verticalLayout_3.addWidget(self.line)
        self.verticalLayout_2 = QtWidgets.QVBoxLayout()
        self.verticalLayout_2.setSpacing(6)
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.label_4 = QtWidgets.QLabel(self.layoutWidget1)
        self.label_4.setObjectName("label_4")
        self.verticalLayout_2.addWidget(self.label_4)
        self.horizontalLayout_3 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_3.setSpacing(6)
        self.horizontalLayout_3.setObjectName("horizontalLayout_3")
        self.measure_path_edit = QtWidgets.QLineEdit(self.layoutWidget1)
        self.measure_path_edit.setObjectName("measure_path_edit")
        self.horizontalLayout_3.addWidget(self.measure_path_edit)
        self.change_path_button = QtWidgets.QPushButton(self.layoutWidget1)
        self.change_path_button.setObjectName("change_path_button")
        self.horizontalLayout_3.addWidget(self.change_path_button)
        self.verticalLayout_2.addLayout(self.horizontalLayout_3)
        self.horizontalLayout_2 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_2.setSpacing(6)
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        self.measures_table = QtWidgets.QTableWidget(self.layoutWidget1)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(1)
        sizePolicy.setHeightForWidth(self.measures_table.sizePolicy().hasHeightForWidth())
        self.measures_table.setSizePolicy(sizePolicy)
        self.measures_table.setSelectionMode(QtWidgets.QAbstractItemView.SingleSelection)
        self.measures_table.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectRows)
        self.measures_table.setObjectName("measures_table")
        self.measures_table.setColumnCount(3)
        self.measures_table.setRowCount(0)
        item = QtWidgets.QTableWidgetItem()
        self.measures_table.setHorizontalHeaderItem(0, item)
        item = QtWidgets.QTableWidgetItem()
        self.measures_table.setHorizontalHeaderItem(1, item)
        item = QtWidgets.QTableWidgetItem()
        self.measures_table.setHorizontalHeaderItem(2, item)
        self.measures_table.horizontalHeader().setStretchLastSection(True)
        self.horizontalLayout_2.addWidget(self.measures_table)
        self.verticalLayout_4 = QtWidgets.QVBoxLayout()
        self.verticalLayout_4.setSpacing(6)
        self.verticalLayout_4.setObjectName("verticalLayout_4")
        self.add_measure_button = QtWidgets.QPushButton(self.layoutWidget1)
        self.add_measure_button.setText("")
        icon1 = QtGui.QIcon()
        icon1.addPixmap(QtGui.QPixmap(":/icons/icons/plus.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.add_measure_button.setIcon(icon1)
        self.add_measure_button.setObjectName("add_measure_button")
        self.verticalLayout_4.addWidget(self.add_measure_button)
        self.remove_measure_button = QtWidgets.QPushButton(self.layoutWidget1)
        self.remove_measure_button.setText("")
        icon2 = QtGui.QIcon()
        icon2.addPixmap(QtGui.QPixmap(":/icons/icons/minus2.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.remove_measure_button.setIcon(icon2)
        self.remove_measure_button.setObjectName("remove_measure_button")
        self.verticalLayout_4.addWidget(self.remove_measure_button)
        spacerItem = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.verticalLayout_4.addItem(spacerItem)
        self.horizontalLayout_2.addLayout(self.verticalLayout_4)
        self.verticalLayout_2.addLayout(self.horizontalLayout_2)
        self.horizontalLayout_4 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_4.setSpacing(6)
        self.horizontalLayout_4.setObjectName("horizontalLayout_4")
        self.start_measure_button = QtWidgets.QPushButton(self.layoutWidget1)
        self.start_measure_button.setObjectName("start_measure_button")
        self.horizontalLayout_4.addWidget(self.start_measure_button)
        self.stop_measure_button = QtWidgets.QPushButton(self.layoutWidget1)
        self.stop_measure_button.setObjectName("stop_measure_button")
        self.horizontalLayout_4.addWidget(self.stop_measure_button)
        self.verticalLayout_2.addLayout(self.horizontalLayout_4)
        self.verticalLayout_3.addLayout(self.verticalLayout_2)
        self.verticalLayoutWidget = QtWidgets.QWidget(self.mw_splitter_2)
        self.verticalLayoutWidget.setObjectName("verticalLayoutWidget")
        self.verticalLayout = QtWidgets.QVBoxLayout(self.verticalLayoutWidget)
        self.verticalLayout.setContentsMargins(3, 3, 3, 3)
        self.verticalLayout.setSpacing(6)
        self.verticalLayout.setObjectName("verticalLayout")
        self.log_text_edit = QtWidgets.QTextEdit(self.verticalLayoutWidget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.log_text_edit.sizePolicy().hasHeightForWidth())
        self.log_text_edit.setSizePolicy(sizePolicy)
        self.log_text_edit.setObjectName("log_text_edit")
        self.verticalLayout.addWidget(self.log_text_edit)
        self.gridLayout.addWidget(self.mw_splitter_2, 0, 0, 1, 1)
        MainWindow.setCentralWidget(self.centralWidget)
        self.menuBar = QtWidgets.QMenuBar(MainWindow)
        self.menuBar.setGeometry(QtCore.QRect(0, 0, 716, 19))
        font = QtGui.QFont()
        font.setPointSize(8)
        self.menuBar.setFont(font)
        self.menuBar.setObjectName("menuBar")
        self.menu = QtWidgets.QMenu(self.menuBar)
        font = QtGui.QFont()
        font.setPointSize(8)
        self.menu.setFont(font)
        self.menu.setObjectName("menu")
        MainWindow.setMenuBar(self.menuBar)
        self.open_about_action = QtWidgets.QAction(MainWindow)
        self.open_about_action.setObjectName("open_about_action")
        self.menu.addAction(self.open_about_action)
        self.menuBar.addAction(self.menu.menuAction())

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "TektronixControl"))
        self.label_3.setText(_translate("MainWindow", "Описание команды"))
        self.send_cmd_button.setText(_translate("MainWindow", "Отправить"))
        self.connect_button.setText(_translate("MainWindow", "Подключиться"))
        self.ip_edit.setText(_translate("MainWindow", "192.168.0.91"))
        self.label_2.setText(_translate("MainWindow", "IP"))
        self.idn_button.setText(_translate("MainWindow", "*IDN?"))
        self.error_buttons.setText(_translate("MainWindow", "Ошибки"))
        self.read_specter_button.setText(_translate("MainWindow", "Спектр"))
        self.label.setText(_translate("MainWindow", "Команда"))
        self.tip_full_cmd_checkbox.setText(_translate("MainWindow", "Полные команды"))
        self.label_4.setText(_translate("MainWindow", "Путь сохранения измерений"))
        self.change_path_button.setText(_translate("MainWindow", "Изменить"))
        item = self.measures_table.horizontalHeaderItem(0)
        item.setText(_translate("MainWindow", "Имя"))
        item = self.measures_table.horizontalHeaderItem(1)
        item.setText(_translate("MainWindow", "Настр."))
        item = self.measures_table.horizontalHeaderItem(2)
        item.setText(_translate("MainWindow", "Вкл."))
        self.start_measure_button.setText(_translate("MainWindow", "Старт"))
        self.stop_measure_button.setText(_translate("MainWindow", "Стоп"))
        self.menu.setTitle(_translate("MainWindow", "Справка"))
        self.open_about_action.setText(_translate("MainWindow", "О программе..."))
import icons_rc
