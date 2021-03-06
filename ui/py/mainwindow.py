# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file './ui/mainwindow.ui'
#
# Created by: PyQt5 UI code generator 5.14.1
#
# WARNING! All changes made in this file will be lost!


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(926, 756)
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap("./ui\\../main_icon.ico"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        MainWindow.setWindowIcon(icon)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.gridLayout_2 = QtWidgets.QGridLayout(self.centralwidget)
        self.gridLayout_2.setObjectName("gridLayout_2")
        self.mw_splitter_2 = QtWidgets.QSplitter(self.centralwidget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.mw_splitter_2.sizePolicy().hasHeightForWidth())
        self.mw_splitter_2.setSizePolicy(sizePolicy)
        self.mw_splitter_2.setOrientation(QtCore.Qt.Vertical)
        self.mw_splitter_2.setObjectName("mw_splitter_2")
        self.mw_splitter_1 = QtWidgets.QSplitter(self.mw_splitter_2)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(100)
        sizePolicy.setHeightForWidth(self.mw_splitter_1.sizePolicy().hasHeightForWidth())
        self.mw_splitter_1.setSizePolicy(sizePolicy)
        self.mw_splitter_1.setOrientation(QtCore.Qt.Horizontal)
        self.mw_splitter_1.setObjectName("mw_splitter_1")
        self.frame_2 = QtWidgets.QFrame(self.mw_splitter_1)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(1)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.frame_2.sizePolicy().hasHeightForWidth())
        self.frame_2.setSizePolicy(sizePolicy)
        self.frame_2.setFrameShape(QtWidgets.QFrame.NoFrame)
        self.frame_2.setFrameShadow(QtWidgets.QFrame.Raised)
        self.frame_2.setObjectName("frame_2")
        self.verticalLayout = QtWidgets.QVBoxLayout(self.frame_2)
        self.verticalLayout.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout.setObjectName("verticalLayout")
        self.chart_layout = QtWidgets.QHBoxLayout()
        self.chart_layout.setObjectName("chart_layout")
        self.verticalLayout.addLayout(self.chart_layout)
        self.line = QtWidgets.QFrame(self.frame_2)
        self.line.setFrameShape(QtWidgets.QFrame.HLine)
        self.line.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.line.setObjectName("line")
        self.verticalLayout.addWidget(self.line)
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setContentsMargins(-1, -1, -1, 0)
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.csv_import_button = QtWidgets.QPushButton(self.frame_2)
        self.csv_import_button.setObjectName("csv_import_button")
        self.horizontalLayout.addWidget(self.csv_import_button)
        self.graphs_button = QtWidgets.QPushButton(self.frame_2)
        self.graphs_button.setObjectName("graphs_button")
        self.horizontalLayout.addWidget(self.graphs_button)
        self.clear_graph_button = QtWidgets.QPushButton(self.frame_2)
        self.clear_graph_button.setObjectName("clear_graph_button")
        self.horizontalLayout.addWidget(self.clear_graph_button)
        spacerItem = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout.addItem(spacerItem)
        self.label = QtWidgets.QLabel(self.frame_2)
        self.label.setObjectName("label")
        self.horizontalLayout.addWidget(self.label)
        self.reset_graph_points_count_button = QtWidgets.QPushButton(self.frame_2)
        self.reset_graph_points_count_button.setText("")
        icon1 = QtGui.QIcon()
        icon1.addPixmap(QtGui.QPixmap(":/icons/icons/reset.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.reset_graph_points_count_button.setIcon(icon1)
        self.reset_graph_points_count_button.setObjectName("reset_graph_points_count_button")
        self.horizontalLayout.addWidget(self.reset_graph_points_count_button)
        self.points_count_spinbox = QtWidgets.QSpinBox(self.frame_2)
        self.points_count_spinbox.setMinimum(1)
        self.points_count_spinbox.setMaximum(1000000)
        self.points_count_spinbox.setObjectName("points_count_spinbox")
        self.horizontalLayout.addWidget(self.points_count_spinbox)
        self.log_scale_checkbox = QtWidgets.QCheckBox(self.frame_2)
        self.log_scale_checkbox.setObjectName("log_scale_checkbox")
        self.horizontalLayout.addWidget(self.log_scale_checkbox)
        self.verticalLayout.addLayout(self.horizontalLayout)
        self.frame_3 = QtWidgets.QFrame(self.mw_splitter_1)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.frame_3.sizePolicy().hasHeightForWidth())
        self.frame_3.setSizePolicy(sizePolicy)
        self.frame_3.setFrameShape(QtWidgets.QFrame.NoFrame)
        self.frame_3.setFrameShadow(QtWidgets.QFrame.Raised)
        self.frame_3.setObjectName("frame_3")
        self.gridLayout_3 = QtWidgets.QGridLayout(self.frame_3)
        self.gridLayout_3.setContentsMargins(0, 0, 0, 0)
        self.gridLayout_3.setSpacing(6)
        self.gridLayout_3.setObjectName("gridLayout_3")
        self.cmd_edit = QtWidgets.QLineEdit(self.frame_3)
        self.cmd_edit.setObjectName("cmd_edit")
        self.gridLayout_3.addWidget(self.cmd_edit, 7, 0, 1, 1)
        self.save_file_name_edit = QtWidgets.QLineEdit(self.frame_3)
        self.save_file_name_edit.setObjectName("save_file_name_edit")
        self.gridLayout_3.addWidget(self.save_file_name_edit, 13, 0, 1, 2)
        self.cmd_description_text_edit = QtWidgets.QPlainTextEdit(self.frame_3)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(1)
        sizePolicy.setHeightForWidth(self.cmd_description_text_edit.sizePolicy().hasHeightForWidth())
        self.cmd_description_text_edit.setSizePolicy(sizePolicy)
        self.cmd_description_text_edit.setMaximumSize(QtCore.QSize(16777215, 40))
        self.cmd_description_text_edit.setObjectName("cmd_description_text_edit")
        self.gridLayout_3.addWidget(self.cmd_description_text_edit, 5, 0, 1, 2)
        self.horizontalLayout_6 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_6.setObjectName("horizontalLayout_6")
        self.comment_text_edit = QtWidgets.QPlainTextEdit(self.frame_3)
        self.comment_text_edit.setMaximumSize(QtCore.QSize(16777215, 24))
        self.comment_text_edit.setObjectName("comment_text_edit")
        self.horizontalLayout_6.addWidget(self.comment_text_edit)
        self.edit_comment_button = QtWidgets.QPushButton(self.frame_3)
        self.edit_comment_button.setMinimumSize(QtCore.QSize(0, 0))
        self.edit_comment_button.setText("")
        icon2 = QtGui.QIcon()
        icon2.addPixmap(QtGui.QPixmap(":/icons/icons/edit.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.edit_comment_button.setIcon(icon2)
        self.edit_comment_button.setObjectName("edit_comment_button")
        self.horizontalLayout_6.addWidget(self.edit_comment_button)
        self.gridLayout_3.addLayout(self.horizontalLayout_6, 15, 0, 1, 2)
        self.horizontalLayout_2 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        self.idn_button = QtWidgets.QPushButton(self.frame_3)
        self.idn_button.setObjectName("idn_button")
        self.horizontalLayout_2.addWidget(self.idn_button)
        self.error_buttons = QtWidgets.QPushButton(self.frame_3)
        self.error_buttons.setObjectName("error_buttons")
        self.horizontalLayout_2.addWidget(self.error_buttons)
        self.read_specter_button = QtWidgets.QPushButton(self.frame_3)
        self.read_specter_button.setObjectName("read_specter_button")
        self.horizontalLayout_2.addWidget(self.read_specter_button)
        self.gridLayout_3.addLayout(self.horizontalLayout_2, 8, 0, 1, 2)
        self.measure_path_edit = QtWidgets.QLineEdit(self.frame_3)
        self.measure_path_edit.setReadOnly(True)
        self.measure_path_edit.setObjectName("measure_path_edit")
        self.gridLayout_3.addWidget(self.measure_path_edit, 11, 0, 1, 1)
        self.change_path_button = QtWidgets.QPushButton(self.frame_3)
        self.change_path_button.setObjectName("change_path_button")
        self.gridLayout_3.addWidget(self.change_path_button, 11, 1, 1, 1)
        self.label_4 = QtWidgets.QLabel(self.frame_3)
        self.label_4.setObjectName("label_4")
        self.gridLayout_3.addWidget(self.label_4, 4, 0, 1, 1)
        self.line_2 = QtWidgets.QFrame(self.frame_3)
        self.line_2.setFrameShape(QtWidgets.QFrame.HLine)
        self.line_2.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.line_2.setObjectName("line_2")
        self.gridLayout_3.addWidget(self.line_2, 3, 0, 1, 2)
        self.horizontalLayout_4 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_4.setObjectName("horizontalLayout_4")
        self.start_measure_button = QtWidgets.QPushButton(self.frame_3)
        icon3 = QtGui.QIcon()
        icon3.addPixmap(QtGui.QPixmap(":/icons/icons/play.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.start_measure_button.setIcon(icon3)
        self.start_measure_button.setObjectName("start_measure_button")
        self.horizontalLayout_4.addWidget(self.start_measure_button)
        self.stop_measure_button = QtWidgets.QPushButton(self.frame_3)
        icon4 = QtGui.QIcon()
        icon4.addPixmap(QtGui.QPixmap(":/icons/icons/stop.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.stop_measure_button.setIcon(icon4)
        self.stop_measure_button.setObjectName("stop_measure_button")
        self.horizontalLayout_4.addWidget(self.stop_measure_button)
        self.gridLayout_3.addLayout(self.horizontalLayout_4, 19, 0, 1, 2)
        self.send_cmd_button = QtWidgets.QPushButton(self.frame_3)
        self.send_cmd_button.setObjectName("send_cmd_button")
        self.gridLayout_3.addWidget(self.send_cmd_button, 7, 1, 1, 1)
        self.horizontalLayout_5 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_5.setObjectName("horizontalLayout_5")
        self.measures_table = QtWidgets.QTableWidget(self.frame_3)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(2)
        sizePolicy.setHeightForWidth(self.measures_table.sizePolicy().hasHeightForWidth())
        self.measures_table.setSizePolicy(sizePolicy)
        self.measures_table.setSelectionMode(QtWidgets.QAbstractItemView.ExtendedSelection)
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
        self.horizontalLayout_5.addWidget(self.measures_table)
        self.verticalLayout_2 = QtWidgets.QVBoxLayout()
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.add_measure_button = QtWidgets.QPushButton(self.frame_3)
        self.add_measure_button.setText("")
        icon5 = QtGui.QIcon()
        icon5.addPixmap(QtGui.QPixmap(":/icons/icons/plus.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.add_measure_button.setIcon(icon5)
        self.add_measure_button.setObjectName("add_measure_button")
        self.verticalLayout_2.addWidget(self.add_measure_button)
        self.remove_measure_button = QtWidgets.QPushButton(self.frame_3)
        self.remove_measure_button.setText("")
        icon6 = QtGui.QIcon()
        icon6.addPixmap(QtGui.QPixmap(":/icons/icons/minus2.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.remove_measure_button.setIcon(icon6)
        self.remove_measure_button.setObjectName("remove_measure_button")
        self.verticalLayout_2.addWidget(self.remove_measure_button)
        self.copy_measure_button = QtWidgets.QPushButton(self.frame_3)
        self.copy_measure_button.setText("")
        icon7 = QtGui.QIcon()
        icon7.addPixmap(QtGui.QPixmap(":/icons/icons/duplicate.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.copy_measure_button.setIcon(icon7)
        self.copy_measure_button.setObjectName("copy_measure_button")
        self.verticalLayout_2.addWidget(self.copy_measure_button)
        self.move_measure_up_button = QtWidgets.QPushButton(self.frame_3)
        self.move_measure_up_button.setText("")
        icon8 = QtGui.QIcon()
        icon8.addPixmap(QtGui.QPixmap(":/icons/icons/up.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.move_measure_up_button.setIcon(icon8)
        self.move_measure_up_button.setObjectName("move_measure_up_button")
        self.verticalLayout_2.addWidget(self.move_measure_up_button)
        self.move_measure_down_button = QtWidgets.QPushButton(self.frame_3)
        self.move_measure_down_button.setText("")
        icon9 = QtGui.QIcon()
        icon9.addPixmap(QtGui.QPixmap(":/icons/icons/down.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.move_measure_down_button.setIcon(icon9)
        self.move_measure_down_button.setObjectName("move_measure_down_button")
        self.verticalLayout_2.addWidget(self.move_measure_down_button)
        spacerItem1 = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.verticalLayout_2.addItem(spacerItem1)
        self.horizontalLayout_5.addLayout(self.verticalLayout_2)
        self.gridLayout_3.addLayout(self.horizontalLayout_5, 18, 0, 1, 2)
        self.label_8 = QtWidgets.QLabel(self.frame_3)
        self.label_8.setObjectName("label_8")
        self.gridLayout_3.addWidget(self.label_8, 14, 0, 1, 1)
        self.line_3 = QtWidgets.QFrame(self.frame_3)
        self.line_3.setFrameShape(QtWidgets.QFrame.HLine)
        self.line_3.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.line_3.setObjectName("line_3")
        self.gridLayout_3.addWidget(self.line_3, 9, 0, 1, 2)
        self.label_6 = QtWidgets.QLabel(self.frame_3)
        self.label_6.setObjectName("label_6")
        self.gridLayout_3.addWidget(self.label_6, 10, 0, 1, 1)
        self.gridLayout_4 = QtWidgets.QGridLayout()
        self.gridLayout_4.setObjectName("gridLayout_4")
        self.sa_connect_button = QtWidgets.QPushButton(self.frame_3)
        self.sa_connect_button.setObjectName("sa_connect_button")
        self.gridLayout_4.addWidget(self.sa_connect_button, 0, 4, 1, 1)
        self.gnrw_connect_button = QtWidgets.QPushButton(self.frame_3)
        self.gnrw_connect_button.setObjectName("gnrw_connect_button")
        self.gridLayout_4.addWidget(self.gnrw_connect_button, 2, 4, 1, 1)
        self.label_2 = QtWidgets.QLabel(self.frame_3)
        self.label_2.setObjectName("label_2")
        self.gridLayout_4.addWidget(self.label_2, 0, 0, 1, 1)
        self.gnrw_status_label = QtWidgets.QLabel(self.frame_3)
        self.gnrw_status_label.setText("")
        self.gnrw_status_label.setObjectName("gnrw_status_label")
        self.gridLayout_4.addWidget(self.gnrw_status_label, 2, 2, 1, 1)
        self.horizontalLayout_3 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_3.setObjectName("horizontalLayout_3")
        self.label_3 = QtWidgets.QLabel(self.frame_3)
        self.label_3.setObjectName("label_3")
        self.horizontalLayout_3.addWidget(self.label_3)
        self.gnrw_factory_number_label = QtWidgets.QLabel(self.frame_3)
        self.gnrw_factory_number_label.setText("")
        self.gnrw_factory_number_label.setObjectName("gnrw_factory_number_label")
        self.horizontalLayout_3.addWidget(self.gnrw_factory_number_label)
        self.gridLayout_4.addLayout(self.horizontalLayout_3, 2, 0, 1, 1)
        self.sa_ip_edit = QtWidgets.QLineEdit(self.frame_3)
        self.sa_ip_edit.setObjectName("sa_ip_edit")
        self.gridLayout_4.addWidget(self.sa_ip_edit, 0, 3, 1, 1)
        self.gnrw_ip_edit = QtWidgets.QLineEdit(self.frame_3)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.gnrw_ip_edit.sizePolicy().hasHeightForWidth())
        self.gnrw_ip_edit.setSizePolicy(sizePolicy)
        self.gnrw_ip_edit.setObjectName("gnrw_ip_edit")
        self.gridLayout_4.addWidget(self.gnrw_ip_edit, 2, 3, 1, 1)
        self.gridLayout_3.addLayout(self.gridLayout_4, 2, 0, 1, 2)
        self.label_7 = QtWidgets.QLabel(self.frame_3)
        self.label_7.setObjectName("label_7")
        self.gridLayout_3.addWidget(self.label_7, 12, 0, 1, 1)
        self.label_5 = QtWidgets.QLabel(self.frame_3)
        self.label_5.setObjectName("label_5")
        self.gridLayout_3.addWidget(self.label_5, 6, 0, 1, 1)
        self.frame = QtWidgets.QFrame(self.mw_splitter_2)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(1)
        sizePolicy.setHeightForWidth(self.frame.sizePolicy().hasHeightForWidth())
        self.frame.setSizePolicy(sizePolicy)
        self.frame.setFrameShape(QtWidgets.QFrame.NoFrame)
        self.frame.setFrameShadow(QtWidgets.QFrame.Raised)
        self.frame.setObjectName("frame")
        self.gridLayout = QtWidgets.QGridLayout(self.frame)
        self.gridLayout.setContentsMargins(0, 0, 0, 0)
        self.gridLayout.setSpacing(0)
        self.gridLayout.setObjectName("gridLayout")
        self.log_text_edit = QtWidgets.QTextEdit(self.frame)
        self.log_text_edit.setObjectName("log_text_edit")
        self.gridLayout.addWidget(self.log_text_edit, 0, 0, 1, 1)
        self.gridLayout_2.addWidget(self.mw_splitter_2, 0, 0, 1, 1)
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 926, 21))
        self.menubar.setObjectName("menubar")
        self.menu = QtWidgets.QMenu(self.menubar)
        self.menu.setObjectName("menu")
        MainWindow.setMenuBar(self.menubar)
        self.open_about_action = QtWidgets.QAction(MainWindow)
        self.open_about_action.setObjectName("open_about_action")
        self.menu.addAction(self.open_about_action)
        self.menubar.addAction(self.menu.menuAction())

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "SpectrumReader"))
        self.csv_import_button.setText(_translate("MainWindow", "Импорт из CSV"))
        self.graphs_button.setText(_translate("MainWindow", "Графики"))
        self.clear_graph_button.setText(_translate("MainWindow", "Сбросить график"))
        self.label.setText(_translate("MainWindow", "Кол-во точек на графике"))
        self.log_scale_checkbox.setText(_translate("MainWindow", "Логарифм. шкала"))
        self.idn_button.setText(_translate("MainWindow", "*IDN?"))
        self.error_buttons.setText(_translate("MainWindow", "Ошибки"))
        self.read_specter_button.setText(_translate("MainWindow", "Спектр"))
        self.change_path_button.setText(_translate("MainWindow", "Изменить"))
        self.label_4.setText(_translate("MainWindow", "Описание команды"))
        self.start_measure_button.setText(_translate("MainWindow", "Старт"))
        self.stop_measure_button.setText(_translate("MainWindow", "Стоп"))
        self.send_cmd_button.setText(_translate("MainWindow", "Отправить"))
        item = self.measures_table.horizontalHeaderItem(0)
        item.setText(_translate("MainWindow", "Имя"))
        item = self.measures_table.horizontalHeaderItem(1)
        item.setText(_translate("MainWindow", "Настр."))
        item = self.measures_table.horizontalHeaderItem(2)
        item.setText(_translate("MainWindow", "Вкл."))
        self.label_8.setText(_translate("MainWindow", "Комментарий к измерению"))
        self.label_6.setText(_translate("MainWindow", "Путь сохранения измерений"))
        self.sa_connect_button.setText(_translate("MainWindow", "Подключиться"))
        self.gnrw_connect_button.setText(_translate("MainWindow", "Подключиться"))
        self.label_2.setText(_translate("MainWindow", "Спектр."))
        self.label_3.setText(_translate("MainWindow", "GNRW"))
        self.label_7.setText(_translate("MainWindow", "Имя сохраняемого файла"))
        self.label_5.setText(_translate("MainWindow", "Команда"))
        self.menu.setTitle(_translate("MainWindow", "Справка"))
        self.open_about_action.setText(_translate("MainWindow", "О программе..."))
import icons_rc
