# TO-DO
# > selection is based on index and not row itself
#   > add some sort of dict that connects row, index, and selection status?
# > connect to router

import locale

from src.Router import Router
from src.imageWidget import ImageWidget
from src.CustomTableItemDelegate import CustomTableItemDelegate

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QHBoxLayout, QVBoxLayout, QWidget, QTableWidgetItem, QSizePolicy, QHeaderView, QAbstractItemView
from qfluentwidgets import (SearchLineEdit, PushButton, SimpleCardWidget, TableWidget, FluentIcon, SpinBox, CommandBar, Action,
                            TransparentToolButton, ComboBox, BodyLabel)



class RouterWindow(QWidget):

    def __init__(self, parent=None):
        super().__init__(parent=parent)
        # set locale for printing money
        locale.setlocale(locale.LC_ALL, '')
        
        # instance variables
        self.selected = []
        self.storeKeys = []
        
        self.router = Router()
        self.router.prefill()
        
        if self.router.validClient:
            self.labels = ["Address", "Items", "Profits", "Distance"]
            self.columncount = 4
        
        else:
            self.labels = ["Address", "Items", "Profits"]
            self.columncount = 3
        
        self.storeInfo = Router.extractData()
        self.homeAddress = Router.getHomeAddress()
        
        self.setObjectName("routerWindow")
        
        # Create general layouts
        self.mainLayout = QHBoxLayout(self)
        self.leftLayout = QVBoxLayout()
        self.rightLayout = QVBoxLayout()
        
        self.mainLayout.addLayout(self.leftLayout, 1)
        self.mainLayout.addLayout(self.rightLayout, 1)
        
        self.leftSide()
        self.rightSide()
        
    def rightSide(self):
        self.rightSideHolder = SimpleCardWidget()
        self.rightLayout.addWidget(self.rightSideHolder)

        self.rightVBox = QVBoxLayout()
        self.rightSideHolder.setLayout(self.rightVBox)
        
        self.photoTest = ImageWidget("map.png")
        self.rightVBox.addWidget(self.photoTest, alignment=Qt.AlignmentFlag.AlignTop)
        
        self.routingTable = TableWidget()
        self.routingTable.setItemDelegate(CustomTableItemDelegate(self.table))
        self.routingTable.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.routingTable.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.routingTable.setSelectionMode(QAbstractItemView.SelectionMode.MultiSelection)
        self.routingTable.setBorderVisible(True)
        self.routingTable.setBorderRadius(8)
        self.routingTable.setWordWrap(True)
        self.routingTable.setColumnCount(self.columncount)
        self.routingTable.setRowCount(self.router.storeCount() - 1)
        self.routingTable.setHorizontalHeaderLabels(self.labels)
        self.routingTable.verticalHeader().hide()
        self.routingTable.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        
        self.rightVBox.addWidget(self.routingTable)
    
    # man i should really move all this to a new class
    # below are all methods for left side of routerWindow
                
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
            "By Profit Ascending" : sorted(self.storeInfo.keys(), key = lambda k : self.storeInfo[k]['store_profit'])
        }
        print(self.router.validClient)
        if self.router.validClient:
            self.filterList.update({
                "By Closest Distance" : sorted(self.storeInfo.keys(), key = lambda k : self.router.store_files[k]['distances'][self.homeAddress]['distance']),
                "By Furthest Distance" : sorted(self.storeInfo.keys(), key = lambda k : self.router.store_files[k]['distances'][self.homeAddress]['distance'], reverse=True)
            })
        self.filterBy.addItems([key for key in self.filterList.keys()])
        self.filterBy.currentIndexChanged.connect(lambda i: self.drawLeftTable(list(self.filterList)[i]))
        self.secondCommandBarLayout.addWidget(self.filterBy)
             
        self.tableHolderOuterVBox.addLayout(self.secondCommandBarLayout)
        
        
        # create table
        self.createLeftTable()
        
        self.submitButton = PushButton(FluentIcon.SEND, "")
        
        # create bottom infobar
        self.infoBar = SimpleCardWidget()
        self.infoBarLayout = QHBoxLayout()
        self.tableInfo = BodyLabel()
        self.infoBarLayout.addWidget(self.tableInfo)
        self.infoBar.setLayout(self.infoBarLayout)
        
        self.drawLeftTable("By Profit Descending")
        
        self.updateInfoBar()
        
        # add everything
        self.tableHolderOuterVBox.addWidget(self.table)
        self.tableHolderOuterVBox.addWidget(self.infoBar)
        self.tableHolderOuterVBox.addWidget(self.submitButton)
        
    def createLeftTable(self):
        """Creates the main table on the left side."""
        
        self.table = TableWidget()
        self.table.setItemDelegate(CustomTableItemDelegate(self.table))
        self.table.setWordWrap(True)
        self.table.verticalHeader().setSectionResizeMode(QHeaderView.ResizeMode.ResizeToContents)
        self.table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.table.setSelectionMode(QAbstractItemView.SelectionMode.MultiSelection)
        self.table.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.table.itemSelectionChanged.connect(self.updateInfoBar)
        
        self.table.setColumnCount(self.columncount)
        self.table.setRowCount(self.router.storeCount() - 1)
        self.table.setHorizontalHeaderLabels(self.labels)
        self.table.verticalHeader().setSectionResizeMode(QHeaderView.ResizeMode.ResizeToContents)
        
        headers = self.table.horizontalHeader()
        headers.setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        headers.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        headers.setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)
        if self.router.validClient:
            headers.setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents)
            # lowk this might be an issue for later, but keep this line in mind
            # when you implement a way for gclient to be added and then table
            # refreshed

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
        
    def drawLeftTable(self, filter):
        self.storeKeys = self.filterList[filter]
        self.currentFilter = filter
        
        for i, address in enumerate(self.storeKeys):
            itemList = ", ".join(self.storeInfo[address]['itemList'])
            rowList = []
            
            rowList.append(QTableWidgetItem(address))
            rowList.append(QTableWidgetItem(itemList))
            rowList.append(QTableWidgetItem(locale.currency(self.storeInfo[address]['store_profit'], grouping=True)))
            if self.router.validClient:
                rowList.append(QTableWidgetItem(f"{self.router.store_files[address]['distances'][self.homeAddress]['distance']} mi"))
            
            for idx, row in enumerate(rowList):
                row.setToolTip(row.text())
                self.table.setItem(i, idx, row)

            # self.table.resizeRowToContents(i)
            # self.table.setItem(i, 0, QTableWidgetItem("no peeking :3"))
            # self.table.setItem(i, 1, QTableWidgetItem("no peeking :3"))
        
        self.searchTable(self.searchBar.text())
        self.submitButton.setText(f"Find Route {self.currentFilter}")
        
        # self.table.resizeRowsToContents()
        
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
        
    def routingButton(self):
        # to-do:
        # convert self.table.selectedIndexes() into actual store addresses
        # feed to router.run()
        #
        # inside of router.run():
        # refactor tsp to take addresses
        # lookup index of each address to add to formatted tsp
        self.router.run()
        
    def resizeEvent(self, a0):
        self.table.resizeRowsToContents()
        self.routingTable.resizeRowsToContents()
        
        return super().resizeEvent(a0)