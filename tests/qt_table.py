from PyQt5.QtWidgets import (QApplication, QMainWindow)
from sys import path
path.insert(0, '..')
from core.vi.value import Tabular, TabCell
from core.qt.table import VisualTable

if __name__ == '__main__':
    import sys
    val = Tabular(colnames=list("AbC"), coltypes=[None] * 3)

    def choicer(arg):
        lst = val.get()
        lst.insert(0, lst.pop(lst.index(arg)))
        val.update(lst)
    app = QApplication(sys.argv)
    v = QMainWindow()
    v.setWindowTitle("Test VisualTable")
    for i in range(1, 300):
        val.insert_row(i, [
            TabCell(str(j), background=(None, "red", "blue")[i % 3])
            for j in range(i, i + 3)])
    vl = VisualTable(v, val)
    v.setCentralWidget(vl)
    v.show()
    sys.exit(app.exec_())
