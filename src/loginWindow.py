from os import listdir, path, remove
from json import dumps, load

from src.ValidateCsv import validate_csv
from src.CsvParse import dictToJson, numProfitableItems, getLastModifiedTime
from src.CustomTableItemDelegate import CustomTableItemDelegate, PaddedWidget

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QHBoxLayout, QVBoxLayout, QSizePolicy, QHeaderView, QAbstractItemView
from qfluentwidgets import (LineEdit, FluentIcon, InfoBarPosition, InfoBar, MessageBox, TransparentToolButton,
                           SmoothScrollArea, TransparentPushButton, SimpleCardWidget, SearchLineEdit,
                           TableWidget)

from qfluentwidgets.components.widgets.label import CaptionLabel

class LoginWindow(SimpleCardWidget):

    # create dict to reference textboxes
        
    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.csvElements = {}
        # Create the scroll area and widget to hold the layout
        self.scroll = SmoothScrollArea()
        self.scroll.setWidgetResizable(True)
        # self.widget = QtWidgets.QWidget()
        self.widget = SimpleCardWidget()
        
        # Create the layout with textboxes and checkboxes
        self.outerLayout = QVBoxLayout()
        
        # create table
        self.createTable()
        
        # fill widget with subwidgets
        self.fillTable()
        
        # Set the outer layout to the widget and add widget to scroll area
        self.widget.setLayout(self.outerLayout)
        self.scroll.setWidget(self.widget)
        self.scroll.enableTransparentBackground()
        
        # Create save and calculate buttons
        self.buttons = SimpleCardWidget()
        buttonLayout = QHBoxLayout()
        buttonLayout.setAlignment(Qt.AlignmentFlag.AlignLeft)
        self.buttons.setLayout(buttonLayout)
        
        self.submit = TransparentPushButton(FluentIcon.SAVE, "Save CSV Values", self)
        self.submit.setSizePolicy(QSizePolicy.Policy.Maximum, QSizePolicy.Policy.Maximum)
        self.submit.clicked.connect(lambda: self.saveJson())
        
        self.refresh = TransparentToolButton(FluentIcon.SYNC, self)
        self.refresh.clicked.connect(lambda: self.refreshTable())
        
        self.search = SearchLineEdit()
        self.search.setPlaceholderText("Search for a CSV by filename or itemname")
        self.search.searchSignal.connect(lambda: self.searchTable(self.search.text()))
        self.search.returnPressed.connect(lambda: self.searchTable(self.search.text()))
        self.search.clearSignal.connect(lambda: self.searchTable(""))

        buttonLayout.addWidget(self.refresh)
        buttonLayout.addWidget(self.submit)
        buttonLayout.addWidget(self.search, Qt.AlignmentFlag.AlignLeft)
                
        # Set scroll area as the main layout
        mainLayout = QVBoxLayout()
        mainLayout.addWidget(self.buttons)
        mainLayout.addWidget(self.scroll)
        self.setLayout(mainLayout)
        self.prefill()
    
    def createTable(self):
        self.table = TableWidget()
        self.table.setItemDelegate(CustomTableItemDelegate(self.table))
        self.table.setWordWrap(True)
        self.table.verticalHeader().setSectionResizeMode(QHeaderView.ResizeMode.ResizeToContents)
        self.table.verticalHeader().setVisible(False)
        self.table.setSelectionMode(QAbstractItemView.SelectionMode.Nelection)
        self.table.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.table.setColumnCount(8)
        self.table.setRowCount(len(listdir("csv\\")))
        self.table.setHorizontalHeaderLabels(["File", "Last Modified", "Item Name", "Sale Price", "Item ID", "Total", "Profitable", ""])
        
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(4, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(5, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(6, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(7, QHeaderView.ResizeMode.Fixed)
        
        self.outerLayout.addWidget(self.table)
    
    def fillTable(self):        
        # get list of csvs
        try:
            csvs = listdir("csv\\")
        except Exception as e:
            # needs to check for csv list, if no list then create one
            print(e)
                
        # create elements
        for idx, csv in enumerate(csvs):
            subelements = {}
                        
            filepathElement = CaptionLabel(f"{csv}")
            modified = CaptionLabel(getLastModifiedTime(csv))
            itemName = LineEdit()
            profit = LineEdit()
            id = LineEdit()
            totalItems = CaptionLabel("")
            profitableItems = CaptionLabel("")
            remove = TransparentPushButton(FluentIcon.CANCEL_MEDIUM)

            remove.clicked.connect(lambda _, csv_path=csv, index=idx: self.removeCSV(csv_path, index))
            itemName.setPlaceholderText("Item Name")
            profit.setPlaceholderText("Sale Price")
            id.setPlaceholderText("Item ID")
            
            items = [filepathElement, modified, PaddedWidget(itemName), PaddedWidget(profit), PaddedWidget(id), totalItems, profitableItems, remove]
            
            for itemIdx, item in enumerate(items):
                self.table.setCellWidget(idx, itemIdx, item)
            
            subelements["path"] = csv
            subelements["itemName"] = itemName
            subelements["profit"] = profit
            subelements["id"] = id
            subelements["totalItems"] = totalItems
            subelements["profitableItems"] = profitableItems
            
            self.csvElements[idx] = subelements
            
    def prefill(self):
        # using the data in previously stored csvs created by updatejson,
        # we fill the lineedits with the already stored text
        
        if path.exists("preload.json"):
            with open("preload.json", "r") as f:
                data = load(f)
        
            for key in self.csvElements.keys():
                for key2 in data.keys():
                    if data[key2]["path"] == self.csvElements[key]["path"]:
                        self.csvElements[key]["itemName"].setText(key2)
                        self.csvElements[key]["profit"].setText(str(data[key2]["profit"]))
                        self.csvElements[key]["id"].setText(str(data[key2]["id"]))
                        break
        
        self.showProfitableItems()
        
        return
    
    def saveJson(self):
        formattedDict = {}
        keys = self.csvElements.keys()
        
        for key in keys:
            path = self.csvElements[key]['path']
            profit = self.csvElements[key]['profit'].text()
            itemName = self.csvElements[key]['itemName'].text()
            id = self.csvElements[key]['id'].text()
            
            if profit == "":
                self.showErrorBar("profit", path)
            elif not profit.isnumeric():
                self.showErrorBar("integer", path)
                
            if itemName == "":
                self.showErrorBar("itemName", path)
                
            if validate_csv(path):
                self.showErrorBar("path", path)
                
            formattedDict[itemName] = {}
            formattedDict[itemName]["path"] = path
            formattedDict[itemName]["profit"] = int(profit)     
            formattedDict[itemName]["id"] = int(id)   
        
        dictToJson(formattedDict)
        with open("preload.json", "w") as f:
            f.write(dumps(formattedDict, indent=4))
        
        return        
    
    def showErrorBar(self, error, filename):
        infobarMsg = ""
        
        if error == "profit":
            infobarMsg = f"Missing \'profit\' field in {filename}."
        if error == "itemName":
            infobarMsg = f"Missing \'itemName\' field in {filename}."
        if error == "path":
            infobarMsg = f"{filename} does not match typical Tempo Monitor CSVs."
        if error == "integer":
            infobarMsg = f"Provided profit value for {filename} is not a number."
        
        InfoBar.error(
            title='Warning',
            content=infobarMsg,
            orient=Qt.Orientation.Horizontal,
            isClosable=True,
            position=InfoBarPosition.TOP_RIGHT,
            duration=2000,
            parent=self
        )
        return

    def showProfitableItems(self):
        for index in self.csvElements.keys():
            if self.csvElements[index]["profit"] != "" and not validate_csv(self.csvElements[index]["path"]):
                profitable, total= numProfitableItems(self.csvElements[index]["path"], int(self.csvElements[index]["profit"].text()))
                self.csvElements[index]["profitableItems"].setText(f"{profitable}")
                self.csvElements[index]["totalItems"].setText(f"{total}")

    def refreshTable(self):
        self.searchTable("")
        self.showProfitableItems()

    def removeCSV(self, csvPath, index):
        # print(csvPath)
        w = MessageBox("Remove CSV", f'Are you sure you want to remove {csvPath}? This action cannot be undone, and will remove the CSV from /csv and the data from preload.json.', self)
        
        if w.exec():
            remove(f"csv/{csvPath}")
            self.csvElements.pop(index, None)
            # self.saveJson()
            # self.searchCSV("") 
            self.fillTable()
            self.prefill()
            
    def searchTable(self, query):
        # search through csvElements (holds widgets)
        keys = []
        print(f"searching with query '{query}'")
        
        for key in self.csvElements.keys():
            if query in self.csvElements[key]['itemName'].text() or query in self.csvElements[key]['path']:
                keys.append(key)
        
        print(f"{keys}")
        self.updateVisibility(keys)
    
    def updateVisibility(self, elements : list):
        for index in self.csvElements.keys():
            if index in elements:
                self.table.showRow(index)
            else:
                self.table.hideRow(index)
                

        