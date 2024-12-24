# TO-DO
# > add sort-by to table
# > connect to router
# > rewrite router to accept address list
# > figure out how to implement multi-select or maybe even write your own widget 

import locale

from src.Router import Router

from PyQt6.QtCore import Qt
from PyQt6 import QtGui
from PyQt6.QtWidgets import QHBoxLayout, QVBoxLayout, QWidget, QListWidgetItem, QLabel, QFileDialog, QTableWidgetItem, QSizePolicy, QHeaderView, QAbstractItemView
from qfluentwidgets import (SearchLineEdit, PushButton, ListWidget, MessageBox, LineEdit, SimpleCardWidget, TableWidget, CheckBox, FluentIcon)

class RouterWindow(QWidget):

    def __init__(self, parent=None):
        super().__init__(parent=parent)
        locale.setlocale(locale.LC_ALL, '')
        self.selected = []
        self.router = Router()
        self.router.prefill()
        self.storeInfo = Router.loadStoreInfo()
        
        self.setObjectName("routerWindow")
        
        # Create general layouts
        self.mainLayout = QHBoxLayout(self)
        self.leftLayout = QVBoxLayout()
        self.rightLayout = QVBoxLayout()
        
        self.mainLayout.addLayout(self.leftLayout)
        self.mainLayout.addLayout(self.rightLayout)
        
        # Create Left Side w/ Tables
        self.tableHolder = SimpleCardWidget()
        self.leftLayout.addWidget(self.tableHolder)
        self.tableHolderOuterVBox = QVBoxLayout()
        
        self.tableHolder.setLayout(self.tableHolderOuterVBox)
        
        # create top 2 rows of left side table buttons
        self.selectAll = PushButton(FluentIcon.ADD_TO, "Select All Stores")
        self.deselectAll = PushButton(FluentIcon.REMOVE_FROM, "Unselect All Stores")
        
        self.tableRow1 = QHBoxLayout()
        self.tableRow1.addWidget(self.selectAll,alignment=Qt.AlignmentFlag.AlignTop)
        self.tableRow1.addWidget(self.deselectAll, alignment=Qt.AlignmentFlag.AlignTop)
        
        self.tableHolderOuterVBox.addLayout(self.tableRow1)
        
        self.numStoresEdit = LineEdit()
        self.numStoresEdit.setPlaceholderText("Number of stores you want to select from the top")
        self.selectNumStoresButton = PushButton("Select Number Specified")
        
        self.tableRow2 = QHBoxLayout()
        self.tableRow2.addWidget(self.numStoresEdit, alignment=Qt.AlignmentFlag.AlignTop)
        self.tableRow2.addWidget(self.selectNumStoresButton, alignment=Qt.AlignmentFlag.AlignTop)
        
        self.tableHolderOuterVBox.addLayout(self.tableRow2)
        
        # create table
        
        self.table = TableWidget()
        self.table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.table.setBorderVisible(True)
        self.table.setBorderRadius(8)
        self.table.setWordWrap(True)
        self.table.setColumnCount(3)
        self.table.setRowCount(self.router.storeCount() - 1)
        self.table.setHorizontalHeaderLabels(["Address", "Items", "Profits"])
        self.table.verticalHeader().hide()
        # self.table.setSizePolicy(QSizePolicy.Policy.Maximum, QSizePolicy.Policy.Maximum)
        # self.table.resizeColumnsToContents()
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)

        for i, address in enumerate(self.storeInfo.keys()):
            self.table.setItem(i, 0, QTableWidgetItem(address))
            
            itemList = ""
            for item in self.storeInfo[address]['itemList'][:-1]:
                itemList += item + ", "
            itemList += self.storeInfo[address]['itemList'][-1]
            
            self.table.setItem(i, 1, QTableWidgetItem(itemList))
            self.table.setItem(i, 2, QTableWidgetItem(locale.currency(self.storeInfo[address]['store_profit'], grouping=True)))    

        self.tableHolderOuterVBox.addWidget(self.table)
        
        #self.hBoxLayout = QHBoxLayout()
        #self.mainLayout.addLayout(self.hBoxLayout)

        # self.searchBox = SearchLineEdit(self)
        # self.searchBox.setPlaceholderText("test")
        # self.mainLayout.addWidget(self.searchBox, 8, Qt.AlignmentFlag.AlignTop)

