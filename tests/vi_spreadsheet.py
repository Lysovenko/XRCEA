from sys import path, argv
path.insert(0, '..')
from core import initialize
from core.vi.spreadsheet import Spreadsheet
from core.application import APPLICATION as APP, start
from core.vi.value import Tabular, TabCell


def test():
    val = Tabular(colnames=list("AbC"), coltypes=[None] * 3)
    for i in range(1, 100):
        val.insert_row(i, [
            TabCell(str(j), background=(None, "red", "blue")[j % 3],
                foreground=("green", None, "white", "yellow")[j % 4])
            for j in range(i, i + 3)])
    APP.runtime_data["MainWindow"] = p = \
        Spreadsheet("XRCEA", val)
    p.show()


if __name__ == '__main__':
    APP.on_start.clear()
    APP.on_start.append(test)
    initialize()
    start()
