from PyQt5 import QtWidgets
import sys

from sqlalchemy.orm import Session


from database import engine, ThisProject
from MainWindow import Ui_MainWindow


def on_exit():
    with Session(engine) as session:
        with session.begin():
            thisproject = session.query(ThisProject).first()
            thisproject.name = None


def main():
    app = QtWidgets.QApplication(sys.argv)
    with open("style.qss", "r") as file:
        app.setStyleSheet(file.read())
    MainWindow = QtWidgets.QMainWindow()
    ui = Ui_MainWindow()
    ui.setupUi(MainWindow)
    MainWindow.show()
    app.aboutToQuit.connect(on_exit)
    sys.exit(app.exec_())



if __name__ == "__main__":
    main()

