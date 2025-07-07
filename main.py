import sys
from PyQt5.QtWidgets import QApplication
from app_window import PyPackManager

if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    window = PyPackManager()
    window.show()
    sys.exit(app.exec_())
