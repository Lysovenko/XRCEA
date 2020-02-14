from sys import path, argv
path.insert(0, '..')
from inspect import stack
from core import initialize
from core.vi.spreadsheet import Spreadsheet
from core.application import APPLICATION as APP, start
from core.vi.value import Tabular, TabCell, Value
from core.vi import Button


class MyCell(TabCell):
    @property
    def value(self):
        return self.__value

    @value.setter
    def value(self, v):
        print(f"someone called setter with v={v}")
        self.__value = v
        print("\\/ " * 5)
        for i in stack():
            print(f"{i.filename}:{i.lineno} {i.function}")
        print("/\\ " * 5)


def test():
    val = Tabular(colnames=list("AbC"), coltypes=[None] * 3)

    def insert_column(name):
        val.insert_column(0, name, int)
    for i in range(1, 25):
        val.insert_row(i, [
            MyCell(str(j), background=(None, "red", "blue")[j % 3],
                   foreground=("green", None, "orange", "magenta")[j % 4])
            for j in range(i, i + 3)])
    APP.runtime_data["MainWindow"] = p = \
        Spreadsheet("XRCEA", val)
    p.show()
    v = Value(str)
    w = Value(str)
    p.set_form([("some label", v),
                (Button("Button", insert_column), w)], True)


if __name__ == '__main__':
    APP.on_start.clear()
    APP.on_start.append(test)
    initialize()
    start()
