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
    val.update([("1", "2", "3", None), ("4", "5", "6", "one"),
                ("7", "8", "9", "two")])
    vl = VisualList(v, ("a", "b", "c"), val, styles)
    vl.set_choicer(choicer)
    v.setCentralWidget(vl)
    v.show()
    sys.exit(app.exec_())
