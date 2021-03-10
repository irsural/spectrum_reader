from typing import List, Dict, Tuple
import logging
import bisect
import math
import csv

from pyqtgraph import PlotWidget, mkPen, exporters, PlotDataItem
from PyQt5 import QtCore, QtWidgets, QtGui
import pyqtgraph

from irspy.qt.qt_settings_ini_parser import QtSettings


class GraphsControl(QtCore.QObject):
    COLORS = (
        (255, 0, 0),
        (0, 255, 0),
        (0, 0, 255),
        (0, 204, 204),
        (204, 0, 102),
        (204, 204, 0),
        (255, 0, 255),
        (102, 153, 153),
        (255, 153, 0),
        (102, 204, 255),
        (0, 255, 153),
        (204, 102, 255),
    )

    graph_points_count_changed = QtCore.pyqtSignal(int)

    def __init__(self, a_graph_widget: pyqtgraph.PlotWidget, a_settings: QtSettings, a_parent=None):
        super().__init__(parent=a_parent)

        self.graph_widget = a_graph_widget
        self.settings = a_settings

        pyqtgraph.setConfigOption('leftButtonPan', False)
        self.graph_widget.setSizePolicy(QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding,
                                                              QtWidgets.QSizePolicy.Preferred))
        self.graph_widget.setSizeIncrement(1, 1)
        self.graph_widget.setBackground('w')
        self.graph_widget.setLabel('bottom', 'Частота, Гц', color='black', size=20)
        self.graph_widget.setLabel('left', 'Амплитуда, dBm', color='black', size=20)
        self.graph_widget.showGrid(x=True, y=True)
        self.graph_widget.plotItem.getViewBox().setMouseMode(pyqtgraph.ViewBox.RectMode)
        self.graph_widget.addLegend()

        self.graphs_data: Dict[str, Tuple[List, List]] = {}
        self.points_count = 0

    def clear(self):
        self.graph_widget.plotItem.clear()
        self.graphs_data.clear()

    def log_scale_enable(self, a_enable):
        self.graph_widget.plotItem.setLogMode(x=a_enable, y=False)

    def draw(self, graph_name, a_x_data, a_y_data):
        if graph_name not in self.graphs_data:
            # Это первые данные для графика с именем graph_name
            graph_color = GraphsControl.COLORS[len(self.graphs_data) % len(GraphsControl.COLORS)]

            self.graph_widget.plot(x=a_x_data, y=a_y_data, pen=mkPen(color=graph_color, width=2), name=graph_name)
            self.graphs_data[graph_name] = (a_x_data, a_y_data)
        else:
            x_data, y_data = self.graphs_data[graph_name]
            x_data.extend(a_x_data)
            y_data.extend(a_y_data)
            plot_data_items: PlotDataItem = self.graph_widget.plotItem.listDataItems()
            target_plot_item = list(filter(lambda p: p.name() == graph_name, plot_data_items))[0]
            target_plot_item.setData(x=x_data, y=y_data)

        self.graph_points_count_changed.emit(len(self.graphs_data[graph_name][0]))

    def set_points_count(self, a_count):
        if self.graphs_data:
            for graph_number, (_, (x_data, y_data)) in enumerate(self.graphs_data.items()):
                if x_data:
                    if a_count > len(x_data):
                        a_count = len(x_data)
                        logging.warning(f"Количество точек на графике = {len(x_data)}")

                    new_data_indices = []
                    factor = (x_data[-1] / x_data[0]) ** (1 / (a_count - 1))
                    x = x_data[0]
                    for i in range(1, a_count + 1):
                        idx = bisect.bisect_right(x_data, x) - 1
                        new_data_indices.append(idx)
                        x *= factor

                    new_x_data = [x_data[i] for i in new_data_indices]
                    new_y_data = [y_data[i] for i in new_data_indices]

                    plot_data_item: PlotDataItem = self.graph_widget.plotItem.listDataItems()[graph_number]
                    plot_data_item.setData(x=new_x_data, y=new_y_data)

    def save_to_file(self, a_filename):
        if self.graph_widget.plotItem.listDataItems():
            png_filename = f"{a_filename}.png"
            csv_filename = f"{a_filename}.csv"

            png_exporter = exporters.ImageExporter(self.graph_widget.plotItem)
            png_exporter.parameters()['width'] = 1e3
            png_exporter.export(png_filename)

            # В LogMode=True сохраняются левые значения
            self.graph_widget.plotItem.setLogMode(x=False, y=False)

            csv_exporter = exporters.CSVExporter(self.graph_widget.plotItem)
            try:
                csv_exporter.export(csv_filename)
            except ValueError:
                logging.error("Не удалось сохранить csv-файл")

            self.graph_widget.plotItem.setLogMode(x=self.settings.log_scale_enabled, y=False)

    def import_from_csv(self, a_filename):
        with open(a_filename, 'r') as csv_file:
            csv_reader = csv.reader(csv_file)
            headers = next(csv_reader)
            plots_count = len(headers) // 2

            x_data: List[List[float]] = [[] for _ in range(plots_count)]
            y_data: List[List[float]] = [[] for _ in range(plots_count)]

            for row in csv_reader:
                for column, p in enumerate(row):
                    if column < len(headers):
                        data = x_data if column % 2 == 0 else y_data
                        data[math.floor(column // 2)].append(float(p))

        self.graph_widget.plotItem.clear()
        for i in range(plots_count):
            graph_color = GraphsControl.COLORS[i % len(GraphsControl.COLORS)]
            graph_pen = pyqtgraph.mkPen(color=graph_color, width=2)
            self.graph_widget.plot(x=x_data[i], y=y_data[i], pen=graph_pen, name=str(i + 1))
