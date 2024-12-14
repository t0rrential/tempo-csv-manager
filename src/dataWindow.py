from PyQt6 import QtWidgets as q
from qfluentwidgets import LineEdit, CheckBox, LineEdit

class DataWindow(q.QWidget):
    def __init__(self, parent=None):
        super().__init__(parent=parent)
        
        # Create the scroll area and widget to hold the layout
        self.scroll = q.QScrollArea()
        self.scroll.setWidgetResizable(True)
        self.widget = q.QWidget()
        
        # Create the layout with textboxes and checkboxes
        self.outerLayout = q.QVBoxLayout()
        
        self.widget.setLayout(self.outerLayout)
        self.scroll.setWidget(self.widget)
        
        # Set scroll area as the main layout
        mainLayout = q.QVBoxLayout()
        mainLayout.addWidget(self.scroll)
        self.setLayout(mainLayout)

