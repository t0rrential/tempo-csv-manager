# coding:utf-8
import subprocess
import sys
import random

from src.Router import Router

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QMovie
from PyQt6.QtWidgets import QHBoxLayout, QVBoxLayout, QWidget, \
    QListWidgetItem, QLabel, QFileDialog
from qfluentwidgets import (SearchLineEdit, PushButton, ListWidget, MessageBox)

class DataWindow(QWidget):

    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.mainLayout = QVBoxLayout(self)
        self.hBoxLayout = QHBoxLayout()
        self.mainLayout.addLayout(self.hBoxLayout)
        self.setObjectName("test")

        self.searchBox = SearchLineEdit(self)
        self.searchBox.setPlaceholderText("test")
        self.hBoxLayout.addWidget(self.searchBox, 8, Qt.AlignmentFlag.AlignTop)

        self.music_list = ListWidget(self)

        # Load the GIF


        self.mainLayout.addWidget(self.music_list)

