# TO-DO
# > selection is based on index and not row itself
#   > add some sort of dict that connects row, index, and selection status?
# > connect to router

import locale

from src.Router import Router

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QHBoxLayout, QVBoxLayout, QWidget, QTableWidgetItem, QSizePolicy, QHeaderView, QAbstractItemView
from qfluentwidgets import (SearchLineEdit, PushButton, SimpleCardWidget, TableWidget, FluentIcon, SpinBox, CommandBar, Action,
                            TransparentToolButton, ComboBox, BodyLabel)



class RouterWindow(QWidget):

    def __init__(self, parent=None):
        super().__init__(parent=parent)
        locale.setlocale(locale.LC_ALL, '')
        self.selected = []
        self.router = Router()
        self.homeAddress = Router.getHomeAddress()
        self.router.prefill()
        self.storeInfo = Router.extractData()
        self.storeKeys = []
        
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
            "By Closest Distance" : sorted(self.storeInfo.keys(), key = lambda k : self.router.store_files[k]['distances'][self.homeAddress]['distance']),
            "By Furthest Distance" : sorted(self.storeInfo.keys(), key = lambda k : self.router.store_files[k]['distances'][self.homeAddress]['distance'], reverse=True)
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
        self.table.setColumnCount(4)
        self.table.setRowCount(self.router.storeCount() - 1)
        self.table.setHorizontalHeaderLabels(["Address", "Items", "Profits", "Distance"])
        self.table.verticalHeader().hide()
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table.itemSelectionChanged.connect(self.updateInfoBar)
        
        self.submitButton = PushButton(FluentIcon.SEND, "")
        
        self.infoBar = SimpleCardWidget()
        self.infoBarLayout = QHBoxLayout()
        self.tableInfo = BodyLabel()
        self.infoBarLayout.addWidget(self.tableInfo)
        self.infoBar.setLayout(self.infoBarLayout)
        
        self.drawTable("By Profit Descending")
        
        self.updateInfoBar()
        
        self.tableHolderOuterVBox.addWidget(self.table)
        self.tableHolderOuterVBox.addWidget(self.infoBar)
        self.tableHolderOuterVBox.addWidget(self.submitButton)
      
    def searchTable(self, query):
        keys = []
        
        for idx, address in enumerate(self.storeKeys):
            if query in address or query.lower() in address.lower():
                keys.append(address)
        
        self.updateVisibility(keys)
        
    def updateVisibility(self, keys):
        for i, address in enumerate(self.storeKeys):
            if address in keys:
                self.table.showRow(i)
            else:
                self.table.hideRow(i)
        self.updateInfoBar()
        
    def drawTable(self, filter):
        self.storeKeys = self.filterList[filter]
        self.currentFilter = filter
        runtime = 0
        
        for i, address in enumerate(self.storeKeys):
            runtime += 1
            self.table.setItem(i, 0, QTableWidgetItem(address))
            itemList = ""
            for item in self.storeInfo[address]['itemList'][:-1]:
                itemList += item + ", "
            itemList += self.storeInfo[address]['itemList'][-1]
            
            self.table.setItem(i, 1, QTableWidgetItem(itemList))
            self.table.setItem(i, 2, QTableWidgetItem(locale.currency(self.storeInfo[address]['store_profit'], grouping=True)))    
            self.table.setItem(i, 3, QTableWidgetItem(f"{self.router.store_files[address]['distances'][self.homeAddress]['distance']} mi"))
            
            # self.table.setItem(i, 0, QTableWidgetItem("no peeking :3"))
            # self.table.setItem(i, 1, QTableWidgetItem("no peeking :3"))
        
        self.searchTable(self.searchBar.text())
        self.submitButton.setText(f"Find Route {self.currentFilter}")
        
    def selectAllRows(self):
        """Select all rows in the table."""
        alreadySelected = set([idx.row() for idx in self.table.selectedIndexes()])
        for rowIdx in range(0, self.table.rowCount()):
            if not self.table.isRowHidden(rowIdx) and rowIdx not in alreadySelected:
                self.table.selectRow(rowIdx)
                
    def deselectAllRows(self):
        """Deselect all rows in the table."""
        for rowIdx in range(0, self.table.rowCount()):
            if not self.table.isRowHidden(rowIdx):
                for col in range(4):
                    selectionModel = self.table.selectionModel()
                    selectionModel.select(self.table.model().index(rowIdx, col), selectionModel.SelectionFlag.Deselect)

        self.table.updateSelectedRows()
        # only in python is it harder to unselect
        
    def selectTopRows(self):
        """Select the top N rows based on the input in the LineEdit."""
        num = int(self.numStoresEdit.text())
        if num >= 1:
            for i in range(min(num, self.table.rowCount())):
                self.table.selectRow(i)

        
    def updateInfoBar(self):
        selectedProfit = 0
        shownProfit = 0
                
        for idx in set([idx.row() for idx in self.table.selectedIndexes()]):
            selectedProfit += self.storeInfo[self.storeKeys[idx]]['store_profit']
            
        for rowIdx in range(0, self.table.rowCount()):
            if not self.table.isRowHidden(rowIdx):
                shownProfit += self.storeInfo[self.storeKeys[rowIdx]]['store_profit']
        
        self.tableInfo.setText(f"Selected Profits: ${selectedProfit},       Total Shown Profits: ${shownProfit}")