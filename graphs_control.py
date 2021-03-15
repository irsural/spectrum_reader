from typing import List, Dict, Tuple
import logging
import bisect
import math
import csv

from pyqtgraph import mkPen, exporters, PlotDataItem
from PyQt5 import QtCore, QtWidgets, QtGui
import pyqtgraph

from irspy.qt.qt_settings_ini_parser import QtSettings
from irspy import utils

from graphs_edit_dialog import GraphsEditDialog


class GraphsControl(QtCore.QObject):
    COLORS = (
        "#FF0000",
        "#00FF00",
        "#0000FF",
        "#00CCCC",
        "#CC000C",
        "#CCCC00",
        "#FF00FF",
        "#0C9999",
        "#FF9900",
        "#66CCFF",
        "#00FF99",
        "#CC66255",
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
        self.graphs_styles: Dict[str, Tuple[str, bool, bool]] = {}
        self.points_count = 0

        self.lock = False

    def clear(self):
        self.graph_widget.plotItem.clear()
        self.graphs_data.clear()
        self.graphs_styles.clear()

    def log_scale_enable(self, a_enable):
        self.graph_widget.plotItem.setLogMode(x=a_enable, y=False)

    def open_graphs_edit_dialog(self):
        graphs_edit_dialog = GraphsEditDialog(self.graphs_styles, self.lock, self.settings)
        graphs_edit_dialog.enable_graph.connect(self.enable_graph)
        graphs_edit_dialog.change_graph_color.connect(self.change_graph_color)
        graphs_edit_dialog.bold_graph_enable.connect(self.bold_graph_enable)
        graphs_edit_dialog.remove_graph.connect(self.remove_graph)
        graphs_edit_dialog.rename_graph.connect(self.rename_graph)
        graphs_edit_dialog.exec()
        graphs_edit_dialog.close()

    def enable_graph(self, a_graph_name, a_enable):
        if a_enable:
            color = self.graphs_styles[a_graph_name][GraphsEditDialog.StylesItem.COLOR]
            pen = mkPen(color=color, width=GraphsEditDialog.DEFAULT_PEN_WIDTH)

            x_data, y_data = self.graphs_data[a_graph_name]
            self.graph_widget.plot(x=x_data, y=y_data, pen=pen, name=a_graph_name)
            self.__set_graph_points_count(a_graph_name, self.settings.graph_points_count)
        else:
            plot = self.__get_plot_by_name(a_graph_name)
            self.graph_widget.removeItem(plot)

    def change_graph_color(self, a_graph_name, a_color: QtGui.QColor):
        plot = self.__get_plot_by_name(a_graph_name)

        current_pen: QtGui.QPen = plot.opts['pen']
        current_pen.setColor(a_color)
        plot.setPen(current_pen)

    def bold_graph_enable(self, a_graph_name, a_enable):
        plot = self.__get_plot_by_name(a_graph_name)

        current_pen: QtGui.QPen = plot.opts['pen']
        new_width = GraphsEditDialog.BOLD_PEN_WIDTH if a_enable else GraphsEditDialog.DEFAULT_PEN_WIDTH
        current_pen.setWidth(new_width)
        plot.setPen(current_pen)

    def remove_graph(self, a_graph_name):
        plot = self.__get_plot_by_name(a_graph_name)
        self.graph_widget.removeItem(plot)
        del self.graphs_styles[a_graph_name]
        del self.graphs_data[a_graph_name]

    def rename_graph(self, a_old_name, a_new_name):
        data = self.graphs_data[a_old_name]
        del self.graphs_data[a_old_name]
        self.graphs_data[a_new_name] = data

        plot = self.__get_plot_by_name(a_old_name)
        plot.setData(*data, name=a_new_name)
        self.graph_widget.plotItem.legend.removeItem(plot)
        self.graph_widget.plotItem.legend.addItem(plot, a_new_name)

    def get_graphs_names(self) -> List:
        return list(self.graphs_data.keys())

    def lock_changes(self, a_lock):
        self.lock = a_lock

    def draw_new(self, graph_name, a_x_data, a_y_data):
        assert graph_name not in self.graphs_data, "Нельзя добавлять существующие графики через draw_new()"

        graph_color = GraphsControl.COLORS[len(self.graphs_data) % len(GraphsControl.COLORS)]
        pen = mkPen(color=graph_color, width=GraphsEditDialog.DEFAULT_PEN_WIDTH)
        self.graph_widget.plot(x=a_x_data, y=a_y_data, pen=pen, name=graph_name)

        self.graphs_data[graph_name] = (a_x_data, a_y_data)
        self.graphs_styles[graph_name] = (graph_color, False, True)

        graph_points_count = self.__set_graph_points_count(graph_name, self.settings.graph_points_count)
        self.graph_points_count_changed.emit(graph_points_count)

    def draw_append(self, graph_name, a_x_data, a_y_data):
        assert graph_name in self.graphs_data, f"График {graph_name} не существует"

        x_data, y_data = self.graphs_data[graph_name]
        x_data.extend(a_x_data)
        y_data.extend(a_y_data)
        plot_data_items: PlotDataItem = self.graph_widget.plotItem.listDataItems()
        target_plot_item = list(filter(lambda p: p.name() == graph_name, plot_data_items))[0]
        target_plot_item.setData(x=x_data, y=y_data)

        graph_points_count = self.__set_graph_points_count(graph_name, self.settings.graph_points_count)
        self.graph_points_count_changed.emit(graph_points_count)

    def set_axis_points(self):
        x_min = 9e999
        x_max = 0
        for xs, _ in self.graphs_data.values():
            x_min = x_min if x_min < xs[0] else xs[0]
            x_max = x_max if x_max > xs[-1] else xs[-1]

        ticks = []
        x = x_min
        dx = (x_max - x_min) / 10
        while x <= x_max:
            ticks.append(x)
            x += dx

    def __get_plot_by_name(self, a_graph_name) -> PlotDataItem:
        for plot in self.graph_widget.plotItem.listDataItems():
            if plot.name() == a_graph_name:
                return plot
        else:
            assert False, f"Не удалось найти график с именем {a_graph_name}"

    def __set_graph_points_count(self, a_graph_name, a_count):
        x_data, y_data = self.graphs_data[a_graph_name]
        if x_data:
            if a_count > len(x_data):
                a_count = len(x_data)

            new_data_indices = []
            factor = (x_data[-1] / x_data[0]) ** (1 / (a_count - 1))
            x = x_data[0]
            for i in range(1, a_count + 1):
                idx = bisect.bisect_right(x_data, x) - 1
                new_data_indices.append(idx)
                x *= factor

            new_x_data = [x_data[i] for i in new_data_indices]
            new_y_data = [y_data[i] for i in new_data_indices]

            plot = self.__get_plot_by_name(a_graph_name)
            plot.setData(x=new_x_data, y=new_y_data)

            return a_count
        else:
            return 0

    def set_points_count(self, a_count):
        if self.graphs_data:
            for graph_name in self.graphs_data.keys():
                new_points_count = self.__set_graph_points_count(graph_name, a_count)
                self.graph_points_count_changed.emit(new_points_count)

    def reset_graph_points_count(self):
        if self.graphs_data:
            for graph_number, (x_data, y_data) in enumerate(self.graphs_data.values()):
                if x_data:
                    plot_data_item: PlotDataItem = self.graph_widget.plotItem.listDataItems()[graph_number]
                    plot_data_item.setData(x=x_data, y=y_data)

                    self.graph_points_count_changed.emit(len(x_data))

    def get_current_x_range(self):
        x_min = 9e999
        x_max = 0
        for xs, _ in self.graphs_data.values():
            x_min = x_min if x_min < xs[0] else xs[0]
            x_max = x_max if x_max > xs[-1] else xs[-1]

        x_min_units = utils.value_to_user_with_units("Гц")(x_min)
        x_max_units = utils.value_to_user_with_units("Гц")(x_max)

        return x_min_units, x_max_units

    def save_to_file(self, a_filename):
        if self.graph_widget.plotItem.listDataItems():
            png_filename = f"{a_filename}.png"
            csv_filename = f"{a_filename}.csv"

            png_exporter = exporters.ImageExporter(self.graph_widget.plotItem)
            png_exporter.parameters()['width'] = 1e3
            png_exporter.export(png_filename)

            # В LogMode=True сохраняются левые значения
            self.graph_widget.plotItem.setLogMode(x=False, y=False)
            self.reset_graph_points_count()

            csv_exporter = exporters.CSVExporter(self.graph_widget.plotItem)
            try:
                csv_exporter.export(csv_filename)
            except ValueError:
                logging.error("Не удалось сохранить csv-файл")

            self.set_points_count(self.settings.graph_points_count)
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

        names = [header[:header.rfind("_")] for idx, header in enumerate(headers) if idx % 2 == 0]

        for graph_name, xs, ys in zip(names, x_data, y_data):
            graph_name = utils.get_allowable_name(self.graphs_data.keys(), graph_name, "{new_name} ({number})")
            self.draw_new(f"{graph_name}", xs, ys)
