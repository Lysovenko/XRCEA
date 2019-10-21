from sys import path, argv
path.insert(0, '..')
from core import initialize
from core.vi.lister import Lister
from core.application import APPLICATION as APP, start
from core.vi.value import Value

def test():
    styles = {"one": (None, "red"), "two": ("blue", None)}
    val = Value(list)
    val.update([tuple(map(str, range(i, i + 3))) +
                ((None, "one", "two")[i % 3],) for i in range(1, 100)])
    APP.runtime_data["MainWindow"] = p =\
            Lister("XRCEA", [("A", ("a","b","c"))], [val], styles)
    p.show()
    print("test done")

if __name__ == '__main__':
    APP.on_start.clear()
    APP.on_start.append(test)
    initialize()
    start()

