from PyQt5.QtWidgets import (QApplication, QMainWindow)
from sys import path
path.insert(0, '..')
from core.value import Value
from core.qt.lists import VisualList

if __name__ == '__main__':
    import sys
    val = Value(list)

    def choicer(arg):
        lst = val.get()
        lst.insert(0, lst.pop(lst.index(arg)))
        val.update(lst)

    styles = {"one": (None, "red"), "two": ("blue", None)}
    app = QApplication(sys.argv)
    v = QMainWindow()
    v.setWindowTitle("Test VisualList")
    val.update([tuple(map(str, range(i, i + 3))) +
                ((None, "one", "two")[i % 3],) for i in range(1, 300)])
    vl = VisualList(v, ("a", "b", "c"), val, styles)
    vl.set_choicer(choicer)
    v.setCentralWidget(vl)
    v.show()
    sys.exit(app.exec_())
