from typing import List

from PyQt5 import QtGui, QtWidgets, QtCore
import pyqtgraph

from irspy.qt.qt_settings_ini_parser import QtSettings
from irspy.metrology import Pchip

from ui.py.device_responce_graph_dialog import Ui_device_responce_graph_dialog as DeviceResponseGraphForm


class DeviceResponseGraphDialog(QtWidgets.QDialog):
    SPLINE_POINTS_COUNT = 2000

    def __init__(self, a_device_response_table: List[List[float]], a_settings: QtSettings, a_parent=None):
        super().__init__(a_parent)

        self.ui = DeviceResponseGraphForm()
        self.ui.setupUi(self)

        self.settings = a_settings
        self.settings.restore_qwidget_state(self)

        self.ui.close_button.clicked.connect(self.reject)

        self.graph_widget = pyqtgraph.PlotWidget()
        self.init_graph(self.graph_widget)
        self.draw_response(a_device_response_table)

        self.ui.log_scale_checkbox.toggled.connect(self.log_scale_checkbox_toggled)

        self.show()

    def __del__(self):
        print("DeviceResponseGraphDialog deleted")

    def init_graph(self, a_graph_widget: pyqtgraph.PlotWidget):
        pyqtgraph.setConfigOption('leftButtonPan', False)
        a_graph_widget.setSizePolicy(QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding,
                                                           QtWidgets.QSizePolicy.Preferred))
        a_graph_widget.setSizeIncrement(1, 1)
        a_graph_widget.setBackground('w')
        a_graph_widget.setLabel('bottom', 'Частота, МГц', color='black', size=20)
        a_graph_widget.setLabel('left', 'Амплитуда', color='black', size=20)
        a_graph_widget.showGrid(x=True, y=True)
        a_graph_widget.plotItem.getViewBox().setMouseMode(pyqtgraph.ViewBox.RectMode)

        self.ui.chart_layout.addWidget(a_graph_widget)

    def draw_response(self, a_device_response_table: List[List[float]]):
        x_data = [p[0] for p in a_device_response_table]
        y_data = [p[1] for p in a_device_response_table]

        if x_data:
            spline_x_data = []
            factor = (x_data[-1] / x_data[0]) ** (1 / (self.SPLINE_POINTS_COUNT - 1))
            spline_x_data.append(x_data[0])
            for i in range(1, self.SPLINE_POINTS_COUNT + 1):
                spline_x_data.append(spline_x_data[-1] * factor)

            pchip = Pchip()
            pchip.set_points(x_data, y_data)
            spline_y_data = [pchip.interpolate(x) for x in spline_x_data]

            self.graph_widget.plotItem.plot(x=x_data, y=y_data, pen=pyqtgraph.mkPen(color=(0, 255, 0), width=2))
            self.graph_widget.plotItem.plot(x=spline_x_data, y=spline_y_data, pen=pyqtgraph.mkPen(color=(255, 0, 0), width=2))

    def log_scale_checkbox_toggled(self, a_state):
        self.graph_widget.plotItem.setLogMode(x=a_state, y=False)

    def closeEvent(self, a_event: QtGui.QCloseEvent) -> None:
        self.settings.save_qwidget_state(self)
