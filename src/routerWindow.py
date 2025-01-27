# TO-DO
# > selection is based on index and not row itself
#   > add some sort of dict that connects row, index, and selection status?
# > connect to router

import locale
from webbrowser import open as openTab
from copy import deepcopy

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
        # self.router.validClient = False
        
        self.labels = ["Address", "Items", "   Profits   ", "    Costs    "]
        self.columncount = 4
        
        if self.router.validClient:
            self.labels.append("Distance")
            self.columncount = 5
            self.router.addressPermutations()
            self.router.addressMatrix()


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
        self.routingTable.setItemDelegate(CustomTableItemDelegate(self.routingTable))
        self.routingTable.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.routingTable.setSelectionMode(QAbstractItemView.SelectionMode.NoSelection)
        self.routingTable.setWordWrap(True)
        self.routingTable.setColumnCount(self.columncount)
        # self.routingTable.setRowCount(self.router.storeCount() - 1)
        self.routingTable.setHorizontalHeaderLabels(self.labels)
        # self.routingTable.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.routingTable.verticalHeader().setVisible(False)
        self.routingTable.verticalHeader().setSectionResizeMode(QHeaderView.ResizeMode.ResizeToContents)
        self.rightVBox.addWidget(self.routingTable)

        headers = self.routingTable.horizontalHeader()
        headers.setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        headers.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        headers.setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)
        if self.router.validClient:
            headers.setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents)
            
        self.routeInfoWidget = SimpleCardWidget()
        self.routeInfoLayout = QHBoxLayout()
        self.routeTime = BodyLabel()
        self.routeProfit = BodyLabel()
        self.routeInfoLayout.addWidget(self.routeTime)
        self.routeInfoLayout.addWidget(self.routeProfit)
        self.routeInfoWidget.setLayout(self.routeInfoLayout)
        
        self.openLink = PushButton(FluentIcon.CAR, "Open Google Maps Link")
        # self.openLink.clicked.connect(self.routingButton)
        
        self.rightVBox.addWidget(self.routeInfoWidget)
        self.rightVBox.addWidget(self.openLink)
    
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
        self.filterIdx = {
            0: "By Profit Descending",
            1: 'By Profit Ascending',
            2: "By Profit/Cost Ratio Descending",
            3: "By Profit/Cost Ratio Ascending",
            4: "By Closest Distance",
            5: "By Furthest Distance"
        }
        self.filterList = {}
        self.filterList["By Profit Descending"] = sorted(self.storeInfo.keys(), key = lambda k : self.storeInfo[k]['store_profit'])[::-1]
        self.filterList['By Profit Ascending'] = self.filterList["By Profit Descending"][::-1]
        self.filterList["By Profit/Cost Ratio Descending"] = sorted(self.storeInfo.keys(), key = lambda k: 
            sum([self.storeInfo[k][item]['floor']*self.storeInfo[k][item]['price'] for item in self.storeInfo[k]['itemList']]) / self.storeInfo[k]['store_profit'])
        self.filterList["By Profit/Cost Ratio Ascending"] = self.filterList["By Profit/Cost Ratio Descending"][::-1]
        
        if self.router.validClient:
            self.filterList["By Closest Distance"] = sorted(self.storeInfo.keys(), key = lambda k : self.router.store_files[k]['distances'][self.homeAddress]['distance'])
            self.filterList["By Furthest Distance"] = self.filterList["By Closest Distance"][::-1]
            
        self.filterBy.addItems([key for key in self.filterList.keys()])
        self.filterBy.currentIndexChanged.connect(lambda i: self.filterLeftTable(self.filterIdx[i]))
        self.secondCommandBarLayout.addWidget(self.filterBy)
             
        self.tableHolderOuterVBox.addLayout(self.secondCommandBarLayout)
        
        
        # create table
        self.createLeftTable()
        
        self.submitButton = PushButton(FluentIcon.SEND, "")
        self.submitButton.clicked.connect(self.routingButton)
        
        # create bottom infobar
        self.infoBar = SimpleCardWidget()
        self.infoBarLayout = QHBoxLayout()
        self.selectedProfit = BodyLabel()
        self.shownProfit = BodyLabel()
        self.cost = BodyLabel()
        self.infoBarLayout.addWidget(self.selectedProfit)
        self.infoBarLayout.addWidget(self.shownProfit)
        self.infoBarLayout.addWidget(self.cost)
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
        self.table.verticalHeader().setVisible(False)
        self.table.verticalHeader().setSectionResizeMode(QHeaderView.ResizeMode.ResizeToContents)
        self.table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.table.setSelectionMode(QAbstractItemView.SelectionMode.MultiSelection)
        self.table.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.table.itemSelectionChanged.connect(self.updateInfoBar)
        
        self.table.setColumnCount(self.columncount)
        self.table.setRowCount(self.router.storeCount() - 1)
        self.table.setHorizontalHeaderLabels(self.labels)
        
        headers = self.table.horizontalHeader()
        headers.setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        headers.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        headers.setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)
        headers.setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents)
        if self.router.validClient:
            headers.setSectionResizeMode(4, QHeaderView.ResizeMode.ResizeToContents)
            # lowk this might be an issue for later, but keep this line in mind
            # when you implement a way for gclient to be added and then table
            # refreshed
        
    def drawLeftTable(self, filter):
        self.storeKeys = list(self.filterList[filter])
        self.currentFilter = filter
        
        for row, address in enumerate(self.storeKeys):
            itemList = ""
            totalCost = 0
            for item in self.storeInfo[address]['itemList']:
                itemList += f"{self.storeInfo[address][item]['back'] + self.storeInfo[address][item]['floor']}x {item} @ {locale.currency(self.storeInfo[address][item]['price'], grouping=True)}\n\n"
                totalCost += self.storeInfo[address][item]['floor'] * self.storeInfo[address][item]['price']
            # itemList = "\n\n".join(self.storeInfo[address]['itemList'])
            rowList = []
            
            rowList.append(address)
            rowList.append(itemList)
            rowList.append(locale.currency(self.storeInfo[address]['store_profit'], grouping=True))
            rowList.append(locale.currency(totalCost, grouping=True))
            if self.router.validClient:
                rowList.append(f"{self.router.store_files[address]['distances'][self.homeAddress]['distance']} mi")
            
            for col, item in enumerate(rowList):
                qItem = QTableWidgetItem(item)
                qItem.setToolTip(item)
                self.table.setItem(row, col, qItem)

            # self.table.resizeRowToContents(i)
            # self.table.setItem(i, 0, QTableWidgetItem("no peeking :3"))
            # self.table.setItem(i, 1, QTableWidgetItem("no peeking :3"))
        
        self.table.resizeRowsToContents()
        self.searchTable(self.searchBar.text())
        self.submitButton.setText(f"Find Route {self.currentFilter}")
                
    def filterLeftTable(self, filter):
        self.storeKeys = list(self.filterList[filter])
        print(self.storeKeys)
        self.currentFilter = filter
        
        for rowIdx, address in enumerate(self.storeKeys):
            print(address)
            itemList = ""
            totalCost = 0
            for item in self.storeInfo[address]['itemList']:
                itemList += f"{self.storeInfo[address][item]['back'] + self.storeInfo[address][item]['floor']}x {item} @ {locale.currency(self.storeInfo[address][item]['price'], grouping=True)}\n\n"
                totalCost += self.storeInfo[address][item]['floor'] * self.storeInfo[address][item]['price']
            # itemList = "\n\n".join(self.storeInfo[address]['itemList'])
            rowList = []
            
            rowList.append(address)
            rowList.append(itemList)
            rowList.append(locale.currency(self.storeInfo[address]['store_profit'], grouping=True))
            rowList.append(locale.currency(totalCost, grouping=True))
            if self.router.validClient:
                rowList.append(f"{self.router.store_files[address]['distances'][self.homeAddress]['distance']} mi")
            
            for colIdx, row in enumerate(rowList):
                self.table.item(rowIdx, colIdx).setToolTip(row)
                self.table.item(rowIdx, colIdx).setText(row)

        self.table.resizeRowsToContents()
        self.searchTable(self.searchBar.text())
        self.submitButton.setText(f"Find Route {self.currentFilter}")
        
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
        selectedCost = 0
                
        for idx in set([idx.row() for idx in self.table.selectedIndexes()]):
            idx = self.storeKeys[idx]
            selectedProfit += self.storeInfo[idx]['store_profit']
            for item in self.storeInfo[idx]['itemList']:
                selectedCost += self.storeInfo[idx][item]['price'] * self.storeInfo[idx][item]['floor']
            
        for rowIdx in range(0, self.table.rowCount()):
            if not self.table.isRowHidden(rowIdx):
                shownProfit += self.storeInfo[self.storeKeys[rowIdx]]['store_profit']
        
        self.selectedProfit.setText(f"Selected Profits: {locale.currency(selectedProfit, grouping=True)}")
        self.shownProfit.setText(f"Total Shown Profits: {locale.currency(shownProfit, grouping=True)}")  
        self.cost.setText(f"Selected Cost: {locale.currency(selectedCost,  grouping=True)}")         
        
    def routingButton(self):
        # lowk i dont even care about separating ts into methods
        # this combines what would be a rightside draw/filter table and updateinfobar
        selectedRanges = self.table.selectedRanges()
        if len(selectedRanges):
            profits = 0
            
            # get range of selected rows
            selectedRows = set()
            if selectedRanges:
                for selectedRange in selectedRanges:
                    start_row = selectedRange.topRow()
                    end_row = selectedRange.bottomRow()
                    selectedRows.update(range(start_row, end_row + 1))
            
            # sort them
            selectedRows = sorted(selectedRows)
            rows = []
            for row in selectedRows:
                rows.append(self.storeKeys[row])
                
            routingDict = self.router.run(rows)
            
            routing, time = routingDict['routing'], routingDict['time'] 
            routingList = deepcopy(routing)
            
            if Router.getHomeAddress() in routingList:
                routingList.remove(Router.getHomeAddress())
            
            self.routingTable.setRowCount(len(routingList)) #maybe -1?
            
            for row, address in enumerate(routingList):
                itemList = ", ".join(self.storeInfo[address]['itemList'])
                rowList = []
                monies = int(self.storeInfo[address]['store_profit'])
                profits += monies
                
                rowList.append(address)
                rowList.append(itemList)
                rowList.append(locale.currency(monies, grouping=True))
                if self.router.validClient:
                    rowList.append(f"{self.router.store_files[address]['distances'][self.homeAddress]['distance']} mi")
                
                for col, item in enumerate(rowList):
                    qItem = QTableWidgetItem(item)
                    qItem.setToolTip(item)
                    self.routingTable.setItem(row, col, qItem)
                    
            self.routeTime.setText(f"{time}")
            self.routeProfit.setText(f"Profit: {locale.currency(profits, grouping=True)}")
            
            self.openLink.clicked.connect(lambda _, routing=routing: self.linkButton(routing))
        
    def linkButton(self, routing: list):
        # setup linkgen
        print(routing)
        routing.append(Router.getHomeAddress())
        print(routing)
        urlList = []
        urlBase = r"https://www.google.com/maps/dir/"
        
        if len(routing) > 0:
            urlSlice = routing[:8]
            routing = routing[8:]
            urlCopy = urlBase
            
            for addy in urlSlice:
                converted = addy.replace(" ", "+")
                urlCopy += f"{converted}/"
                
            urlList.append(urlCopy)
            
        for url in urlList:
            openTab(url, new=2, autoraise=True)
    
        # todo: 
        #   add infoBar like widget to rightside table
        #   add drive distance to Router
        #   show drive distance, moneys to be made, time spent driving
        #   somehow add removal of a certain item to store? lowk idk how
        #       > probably storeData[store][store_profit] - storeData[store][item]['tprofits'], but also need a way for this to reflect in filtering algos
        #       > connected to rightclick signal on table cells, sends to messagebox with checkboxes next to all items
        #       > checkboxes conencted to method that takes in state of box and item, adds/subtracts store profit from self.storeData based on state

    def resizeEvent(self, a0):
        self.table.resizeRowsToContents()
        self.routingTable.resizeRowsToContents()
        
        return super().resizeEvent(a0)        #self.filterBy.currentIndexChanged.connect(lambda i: self.drawLeftTable(list(self.filterList)[i]))
