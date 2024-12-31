# TO-DO
# > add sort-by to table
# > connect to router
# > rewrite router to accept address list
# > figure out how to implement multi-select or maybe even write your own widget 

import locale

from src.Router import Router

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QHBoxLayout, QVBoxLayout, QWidget, QListWidgetItem, QLabel, QFileDialog, QTableWidgetItem, QSizePolicy, QHeaderView, QAbstractItemView
from qfluentwidgets import (SearchLineEdit, PushButton, ListWidget, MessageBox, LineEdit, SimpleCardWidget, TableWidget, CheckBox, FluentIcon, SpinBox, CommandBar, Action,
                            TransparentToolButton, ComboBox)



class RouterWindow(QWidget):

    def __init__(self, parent=None):
        super().__init__(parent=parent)
        locale.setlocale(locale.LC_ALL, '')
        self.selected = []
        self.router = Router()
        self.router.prefill()
        self.storeInfo = Router.extractData()
        
        self.setObjectName("routerWindow")
        
        # Create general layouts
        self.mainLayout = QHBoxLayout(self)
        self.leftLayout = QVBoxLayout()
        self.rightLayout = QVBoxLayout()
        
        self.mainLayout.addLayout(self.leftLayout)
        self.mainLayout.addLayout(self.rightLayout)
        
        self.leftSide()
        self.rightSide()
        
    def rightSide(self):
        self.rightSideHolder = SimpleCardWidget()
        
        # self.router.run()
        
        self.rightLayout.addWidget(self.rightSideHolder)
        return
        
    def leftSide(self):
        # Create Left Side w/ Tables
        self.tableHolder = SimpleCardWidget()
        self.leftLayout.addWidget(self.tableHolder)
        self.tableHolderOuterVBox = QVBoxLayout()
        
        self.tableHolder.setLayout(self.tableHolderOuterVBox)
        
        
        # create first command bar
        self.firstCommandBarLayout = QHBoxLayout()
        
            # create command bar
        self.firstCommandBar = CommandBar()
        self.firstCommandBar.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonTextBesideIcon)
        
        self.refresh = TransparentToolButton(FluentIcon.SYNC)
        self.refresh.clicked.connect(lambda: self.searchTable(""))

        self.firstCommandBar.addWidget(self.refresh)
        self.firstCommandBar.addActions([
            Action(FluentIcon.ADD_TO, 'Select All', triggered=self.selectAllRows),
            Action(FluentIcon.REMOVE_FROM, 'Unselect All', triggered=self.deselectAllRows)
        ])

            # add bar to fcbl
        self.firstCommandBarLayout.addWidget(self.firstCommandBar)
        
            # create searchbar
        self.searchLayout = QHBoxLayout()
        
        self.searchBar = SearchLineEdit()
        self.searchBar.setPlaceholderText("Search for store by address")
        self.searchBar.searchSignal.connect(lambda: self.searchTable(self.searchBar.text()))
        self.searchBar.clearSignal.connect(lambda: self.searchTable(""))
        
        self.searchBar.setSizePolicy(QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Minimum)  # Only as large as needed
        self.searchLayout.addWidget(self.searchBar)
        self.firstCommandBarLayout.addLayout(self.searchLayout)
        
        # add to view       
        self.tableHolderOuterVBox.addLayout(self.firstCommandBarLayout)


        # create second command bar
        self.secondCommandBarLayout = QHBoxLayout()
        
            # add spinbox
        self.spinLayout = QHBoxLayout()
        self.numStoresEdit = SpinBox()
        self.numStoresEdit.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Preferred) 
        self.selectNumStoresButton = PushButton("Select number specified")
        self.selectNumStoresButton.setSizePolicy(QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Minimum)  # Only as large as needed
        self.selectNumStoresButton.clicked.connect(self.selectTopRows)

        self.spinLayout.addWidget(self.selectNumStoresButton)
        self.spinLayout.addWidget(self.numStoresEdit)
        self.secondCommandBarLayout.addLayout(self.spinLayout)  
        
            # add filter holder
        self.filterBy = ComboBox()
        self.filterBy.setPlaceholderText("Filter by:")
        self.filterList = {
            "By Profit Descending" : sorted(self.storeInfo.keys(), key = lambda k : self.storeInfo[k]['store_profit'], reverse=True),
            "By Profit Ascending" : sorted(self.storeInfo.keys(), key = lambda k : self.storeInfo[k]['store_profit']),
            "By Closest Distance" : sorted(self.storeInfo.keys(), key = lambda k : self.router.store_files[k]['distances'][Router.getHomeAddress()]['distance']),
            "By Furthest Distance" : sorted(self.storeInfo.keys(), key = lambda k : self.router.store_files[k]['distances'][Router.getHomeAddress()]['distance'], reverse=True)
        }
        self.filterBy.addItems([key for key in self.filterList.keys()])
        self.filterBy.currentIndexChanged.connect(lambda i: self.drawTable(list(self.filterList)[i]))
        self.secondCommandBarLayout.addWidget(self.filterBy)
             
        self.tableHolderOuterVBox.addLayout(self.secondCommandBarLayout)
        
        
        # create table
        self.table = TableWidget()
        self.table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.table.setSelectionMode(QAbstractItemView.SelectionMode.MultiSelection)
        self.table.setBorderVisible(True)
        self.table.setBorderRadius(8)
        self.table.setWordWrap(True)
        self.table.setColumnCount(3)
        self.table.setRowCount(self.router.storeCount() - 1)
        self.table.setHorizontalHeaderLabels(["Address", "Items", "Profits"])
        self.table.verticalHeader().hide()
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        
        self.drawTable("By Profit Descending")
        
        self.tableHolderOuterVBox.addWidget(self.table)
        self.tableHolderOuterVBox.addWidget(self.submitButton)
      
    def searchTable(self, query):
        keys = []
        sortedKeys = self.filterList[self.currentFilter]
        
        for idx, address in enumerate(sortedKeys):
            if query in address:
                keys.append(address)
        
        self.updateVisibility(keys)
        
    def updateVisibility(self, keys):
        sortedKeys = self.filterList[self.currentFilter]

        for i, address in enumerate(sortedKeys):
            if address in keys:
                self.table.showRow(i)
            else:
                self.table.hideRow(i)
        
    def drawTable(self, filter):
        sortedKeys = self.filterList[filter]
        self.currentFilter = filter
        
        for i, address in enumerate(sortedKeys):
            self.table.setItem(i, 0, QTableWidgetItem(address))
            # self.table.setItem(i, 0, QTableWidgetItem("no peeking :3"))
            itemList = ""
            for item in self.storeInfo[address]['itemList'][:-1]:
                itemList += item + ", "
            itemList += self.storeInfo[address]['itemList'][-1]
            
            self.table.setItem(i, 1, QTableWidgetItem(itemList))
            self.table.setItem(i, 2, QTableWidgetItem(locale.currency(self.storeInfo[address]['store_profit'], grouping=True)))    

        self.submitButton = PushButton(FluentIcon.SEND, "Find Route")
        
    def selectAllRows(self):
        """Select all rows in the table."""
        self.table.selectAll()

    def deselectAllRows(self):
        """Deselect all rows in the table."""
        self.table.clearSelection()
        
    def selectTopRows(self):
        """Select the top N rows based on the input in the LineEdit."""
        try:
            num = int(self.numStoresEdit.text())
            self.deselectAllRows()
            if num >= 1:
                for i in range(min(num, self.table.rowCount())):
                    self.table.selectRow(i)
        except ValueError:
            pass
        
        #self.hBoxLayout = QHBoxLayout()
        #self.mainLayout.addLayout(self.hBoxLayout)

        # self.searchBox = SearchLineEdit(self)
        # self.searchBox.setPlaceholderText("test")
        # self.mainLayout.addWidget(self.searchBox, 8, Qt.AlignmentFlag.AlignTop)

