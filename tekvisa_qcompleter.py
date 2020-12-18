import sys

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QStandardItemModel, QStandardItem
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QLineEdit, QCompleter


class CodeCompleter(QCompleter):
    ConcatenationRole = Qt.UserRole + 1
    _separator = ":"

    def __init__(self, data, parent=None):
        super().__init__(parent)
        self.create_model(data)

    @staticmethod
    def separator():
        return CodeCompleter._separator

    def splitPath(self, path):
        if path.startswith(CodeCompleter._separator):
            path_parts = path[1:].split(CodeCompleter._separator)
            path_parts[0] = f"{CodeCompleter._separator}{path_parts[0]}"
        else:
            path_parts = path.split(CodeCompleter._separator)

        return path_parts

    def pathFromIndex(self, index):
        path_parts = []
        while index.isValid():
            path_parts.insert(0, self.model().data(index, CodeCompleter.ConcatenationRole))
            index = index.parent()

        return CodeCompleter._separator.join(path_parts)

    def create_model(self, data):
        def add_items(a_parent_node, elements):
            for text, children in sorted(elements.items()):
                if text != "desc":
                    item = QStandardItem(text)
                    item.setData(text, CodeCompleter.ConcatenationRole)
                    a_parent_node.appendRow(item)
                    if type(children) is dict:
                        add_items(item, children)

        model = QStandardItemModel(self)
        add_items(model, data)
        self.setModel(model)


if __name__ == "__main__":
    import tekvisa_control as tek

    class MainApp(QWidget):
        def __init__(self):
            super().__init__()

            model_data = tek.get_commands_three(tek.CmdCase.UPPER)

            self.entry = QLineEdit(self)
            self.completer = CodeCompleter(model_data, self)
            self.completer.setCaseSensitivity(Qt.CaseInsensitive)
            self.completer.setModelSorting(QCompleter.CaseSensitivelySortedModel)
            self.entry.setCompleter(self.completer)
            layout = QVBoxLayout()
            layout.addWidget(self.entry)
            self.setLayout(layout)

    app = QApplication(sys.argv)
    w = MainApp()
    w.show()
    sys.exit(app.exec_())
