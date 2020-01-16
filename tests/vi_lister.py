from sys import path, argv
path.insert(0, '..')
from core import initialize
from core.vi.lister import Lister
from core.application import APPLICATION as APP, start
from core.vi.value import Value


def tick(status):
    from time import sleep
    status["description"] = "Some meaningful text"
    for p in range(100):
        sleep(.1)
        status["part"] = p * .01
        if status.get("stop"):
            break
    status["complete"] = True


def test():
    styles = {"one": (None, "red"), "two": ("blue", None)}
    val = Value(list)
    val.update([
        tuple(map(str, range(i, i + 3))) + ((None, "one", "two")[i % 3],)
        for i in range(1, 100)])
    APP.runtime_data["MainWindow"] = p = \
        Lister("XRCEA", [("A", ("a", "b", "c"))], [val], styles)
    p.show()
    p.bg_process(tick)
    p.print_information("test done")


if __name__ == '__main__':
    APP.on_start.clear()
    APP.on_start.append(test)
    initialize()
    start()
