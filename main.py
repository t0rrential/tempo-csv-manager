# coding:utf-8
import sys
import os

from PyQt6.QtCore import Qt, QUrl
from PyQt6.QtGui import QIcon, QDesktopServices, QPixmap
from PyQt6.QtWidgets import QHBoxLayout, QApplication, QSplashScreen

from src.components.UITemplate import StackedWidget, CustomTitleBar
from src.ui.LoginWindow import LoginWindow
from src.ui.RouterWindow import RouterWindow
from src.ui.SettingsBox import SettingsBox

from qfluentwidgets import (NavigationBar, NavigationItemPosition, MessageBox,
                            isDarkTheme, setTheme, Theme, setThemeColor)
from qfluentwidgets import FluentIcon as FIF
from qframelesswindow import AcrylicWindow

if not os.path.isdir("store_data"):
    os.mkdir("store_data")
    
if not os.path.isdir("csv"):
    os.mkdir("csv")
    
if not os.path.isfile(".env"):
    with open(".env", "w") as f:
        f.write("GOOGLE_MAPS_APIKEY=\"\"")
        f.write("HOME_ADDRESS=\"\"")
        f.write("DISCORD_TOKEN=\"\"")


#class Window(FramelessWindow):
class Window(AcrylicWindow):
    def __init__(self):
        super().__init__()
        self.setMinimumSize(200, 150)
        titleBar = CustomTitleBar(self)
        titleBar.linkThemeToggleButton(lambda: self.toggleCurrentTheme())
        titleBar.setIcon(r"resource/logo.png")
        self.setWindowIcon(QIcon(r'resource/logo.png'))
        self.setTitleBar(titleBar)

        # theme set
        setTheme(Theme.AUTO)
        
        # change the theme color
        setThemeColor('#ff4357')
        
        self.windowEffect.setMicaEffect(self.winId(), False)
        self.hBoxLayout = QHBoxLayout(self)
        self.navigationBar = NavigationBar(self)
        self.stackWidget = StackedWidget(self)

        # create sub interface
        # self.homeInterface = Widget('Home Interface', self)
        self.homeInterface = LoginWindow(self)
        self.appInterface = RouterWindow(self)        
        # self.videoInterface = Widget('Video Interface', self)
        # self.libraryInterface = Widget('library Interface', self)

        # initialize layout
        self.initLayout()
        
        # add items to navigation interface
        self.initNavigation()

        self.initWindow()

    def initLayout(self):
        self.hBoxLayout.setSpacing(0)
        self.hBoxLayout.setContentsMargins(0, 48, 0, 0)
        self.hBoxLayout.addWidget(self.navigationBar)
        self.hBoxLayout.addWidget(self.stackWidget)
        self.hBoxLayout.setStretchFactor(self.stackWidget, 1)

    def initNavigation(self):
        self.addSubInterface(self.homeInterface, FIF.ALIGNMENT, 'CSV', selectedIcon=FIF.HOME_FILL)
        self.addSubInterface(self.appInterface, FIF.COMMAND_PROMPT, 'Routes')
        # self.addSubInterface(self.videoInterface, FIF.VIDEO, 'test')

        # self.addSubInterface(self.libraryInterface, FIF.BOOK_SHELF, 'test', NavigationItemPosition.BOTTOM, FIF.LIBRARY_FILL)
        self.navigationBar.addItem(
            routeKey='Settings',
            icon=FIF.SETTING,
            text='Settings',
            onClick=self.showSettingBox,
            selectable=False,
            position=NavigationItemPosition.BOTTOM,
        )
        
        self.navigationBar.addItem(
            routeKey='About Me',
            icon=FIF.HELP,
            text='about me',
            onClick=self.showMessageBox,
            selectable=False,
            position=NavigationItemPosition.BOTTOM,
        )

        self.stackWidget.currentChanged.connect(self.onCurrentInterfaceChanged)
        self.navigationBar.setCurrentItem(self.homeInterface.objectName())

    def initWindow(self):
        #self.resize(900, 700)
        # self.setWindowIcon(QIcon())
        self.setWindowTitle('Tempo CSV Manager')
        self.titleBar.setAttribute(Qt.WidgetAttribute.WA_StyledBackground)

        desktop = QApplication.primaryScreen().availableGeometry()
        w, h = desktop.width(), desktop.height()
        self.move(w//2 - self.width()//2, h//2 - self.height()//2)
        
        self.setQss()

    def addSubInterface(self, interface, icon, text: str, position=NavigationItemPosition.TOP, selectedIcon=None):
        """ add sub interface """
        self.stackWidget.addWidget(interface)
        self.navigationBar.addItem(
            routeKey=interface.objectName(),
            icon=icon,
            text=text,
            onClick=lambda: self.switchTo(interface),
            selectedIcon=selectedIcon,
            position=position,
        )

    def setQss(self):
        color = 'dark' if isDarkTheme() else 'light'
        with open(f'resource/{color}/demo.qss', encoding='utf-8') as f:
            self.setStyleSheet(f.read())

    def switchTo(self, widget):
        self.stackWidget.setCurrentWidget(widget)

    def onCurrentInterfaceChanged(self, index):
        widget = self.stackWidget.widget(index)
        self.navigationBar.setCurrentItem(widget.objectName())

    def showMessageBox(self):
        w = MessageBox(
            'gucci',
            'hello bro i love you. please go to my github and support',
            self
        )
        w.yesButton.setText('github')
        w.cancelButton.setText('back')

        if w.exec():
            QDesktopServices.openUrl(QUrl("https://github.com/t0rrential"))
    
    def showSettingBox(self):
        # implement custom messagebox class here\
        w = SettingsBox(self)
        if w.exec():
            w.validate()
        return    
    
    def toggleCurrentTheme(self):
        theme = Theme.LIGHT if isDarkTheme() else Theme.DARK  
        color = 'light' if isDarkTheme() else 'dark'
        
        #print(f"theme: {theme} color: {color}")
        
        with open(f'resource/{color}/demo.qss', encoding='utf-8') as f:
            self.setStyleSheet(f.read())
            setTheme(theme, lazy=False)


if __name__ == '__main__':
    QApplication.setHighDpiScaleFactorRoundingPolicy(Qt.HighDpiScaleFactorRoundingPolicy.PassThrough)

    app = QApplication(sys.argv)
    pixmap = QPixmap("logo.png")
    splash = QSplashScreen(pixmap)
    splash.show()
    
    w = Window()
    w.show()
    splash.finish(w)
    
    sys.exit(app.exec())