import sys

from src.loginWindow import LoginWindow
from src.dataWindow import DataWindow

from PyQt5 import QtWidgets
# from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QMainWindow, QSizePolicy, QStackedWidget, QApplication
from PyQt5 import QtGui
from PyQt5.QtCore import Qt
from qfluentwidgets import LineEdit, CheckBox, PushButton, FluentIcon, SplitFluentWindow




class MainWindow(QtWidgets.QMainWindow):
    spacer = "         "
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Tempo Helper")

        # Sidebar layout with buttons
        sidebar = QtWidgets.QWidget()
        sidebarLayout = QtWidgets.QVBoxLayout()
        sidebar.setLayout(sidebarLayout)
        
        # Buttons for sidebar navigation
        # self.button1 = PushButton(" CSV Editing ")
        self.button1 = PushButton(self.spacer + "  CSV  ")
        self.button1.setIcon(FluentIcon.ALIGNMENT)
        self.button1.setSizePolicy(QtWidgets.QSizePolicy.Maximum, QtWidgets.QSizePolicy.Maximum)
        self.button1.setStyleSheet("QAbstractButton {qproperty-icon: align-center;}")

        
        # self.button2 = PushButton("Data Analysis")
        self.button2 = PushButton(self.spacer + "Routes")
        self.button2.setIcon(FluentIcon.COMMAND_PROMPT)
        self.button2.setSizePolicy(QtWidgets.QSizePolicy.Maximum, QtWidgets.QSizePolicy.Maximum)
        self.button2.setStyleSheet("QAbstractButton {qproperty-icon: align-center;}")

        sidebarLayout.setAlignment(Qt.AlignTop)
        sidebarLayout.addWidget(self.button1)
        sidebarLayout.addWidget(self.button2)
        
        # Stacked widget to hold the pages (like Chrome tabs)
        self.stackedWidget = QtWidgets.QStackedWidget()
        
        # Add two LoginWindow pages to the stacked widget
        self.page1 = LoginWindow()
        self.page2 = DataWindow()
        self.stackedWidget.addWidget(self.page1)
        self.stackedWidget.addWidget(self.page2)
        
        # Connect buttons to switch pages in the stacked widget
        self.button1.clicked.connect(lambda: self.stackedWidget.setCurrentWidget(self.page1))
        self.button2.clicked.connect(lambda: self.stackedWidget.setCurrentWidget(self.page2))
        
        # Layout for the main window with sidebar and stacked widget
        mainLayout = QtWidgets.QHBoxLayout()
        mainLayout.addWidget(sidebar)
        mainLayout.addWidget(self.stackedWidget)
        
        # Central widget to contain the layout
        centralWidget = QtWidgets.QWidget()
        centralWidget.setLayout(mainLayout)
        self.setCentralWidget(centralWidget)

if __name__ == "__main__":
    QtWidgets.QApplication.setHighDpiScaleFactorRoundingPolicy(Qt.HighDpiScaleFactorRoundingPolicy.PassThrough)
    QtWidgets.QApplication.setAttribute(Qt.AA_EnableHighDpiScaling)
    QtWidgets.QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps)

    app = QtWidgets.QApplication(sys.argv)
    
    # Create and display the main window
    mainWindow = MainWindow()
    mainWindow.show()
    
    sys.exit(app.exec_())

