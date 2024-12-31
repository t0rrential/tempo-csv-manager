import os
from json import dumps, load

from src.ValidateCsv import validate_csv
from src.CsvParse import dictToJson

from PyQt6.QtCore import Qt
from PyQt6 import QtWidgets
from qfluentwidgets import (LineEdit, LineEdit, FluentIcon, InfoBarPosition, InfoBar, MessageBox, TransparentToolButton,
                           SmoothScrollArea, TransparentPushButton, CardWidget, SimpleCardWidget, SearchLineEdit)

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
        self.outerLayout = QtWidgets.QVBoxLayout()
        
        # fill widget with subwidgets
        self.fillTable()
        
        # Set the outer layout to the widget and add widget to scroll area
        self.widget.setLayout(self.outerLayout)
        self.scroll.setWidget(self.widget)
        self.scroll.enableTransparentBackground()
        
        # Create save and calculate buttons
        self.buttons = SimpleCardWidget()
        buttonLayout = QtWidgets.QHBoxLayout()
        buttonLayout.setAlignment(Qt.AlignmentFlag.AlignLeft)
        self.buttons.setLayout(buttonLayout)
        
        self.submit = TransparentPushButton(FluentIcon.SAVE, "Save CSV Values", self)
        self.submit.setSizePolicy(QtWidgets.QSizePolicy.Policy.Maximum, QtWidgets.QSizePolicy.Policy.Maximum)
        self.submit.clicked.connect(lambda: self.saveJson())
        
        self.refresh = TransparentToolButton(FluentIcon.SYNC, self)
        self.refresh.clicked.connect(lambda: self.searchCSV(""))
        
        self.search = SearchLineEdit()
        self.search.setPlaceholderText("Search for a CSV by filename or itemname")
        self.search.searchSignal.connect(lambda: self.searchCSV(self.search.text()))
        self.search.clearSignal.connect(lambda: self.searchCSV(""))

        buttonLayout.addWidget(self.refresh)
        buttonLayout.addWidget(self.submit)
        buttonLayout.addWidget(self.search, Qt.AlignmentFlag.AlignLeft)
                
        # Set scroll area as the main layout
        mainLayout = QtWidgets.QVBoxLayout()
        mainLayout.addWidget(self.buttons)
        mainLayout.addWidget(self.scroll)
        self.setLayout(mainLayout)
        self.prefill()
    
    def fillTable(self):        
        # get list of csvs
        try:
            csvs = os.listdir("csv\\")
        except Exception as e:
            print(e)
                
        # create elements
        for idx, csv in enumerate(csvs):
            subelements = {}
            #print(csv)
            outFrame = CardWidget()
            
            topLayout = QtWidgets.QVBoxLayout()
            topRowLayout = QtWidgets.QHBoxLayout()
            formLayout = QtWidgets.QFormLayout()
            topLayout.addLayout(topRowLayout)
            topLayout.addLayout(formLayout)
            
            # create inputs
            remove = TransparentPushButton(FluentIcon.CANCEL_MEDIUM, "Remove")
                # lambda explanation:
                # _ is the signal param passed to connect, which we can discard
                # by doing csv_path = csv, we can ensure self.removeCSV gets the correct one
                # as python lambdas/closures get variables by reference, not by value
                # think of it passing a pointer to csv instead of csv itself, and because
                # csv is defined by enumerate it will end up pointing to the last held csv value
            remove.clicked.connect(lambda _, csv_path=csv, index=idx: self.removeCSV(csv_path, index))
            itemName = LineEdit()
            profit = LineEdit()
            id = LineEdit()
            
            topRowLayout.addWidget(CaptionLabel(f"{csv}"))
            topRowLayout.addWidget(remove, alignment=Qt.AlignmentFlag.AlignRight)
            
            formLayout.addRow(CaptionLabel(f"Item Name:"), itemName)
            formLayout.addRow(CaptionLabel(f"Sale Price:"), profit)
            formLayout.addRow(CaptionLabel(f"Item ID:"), id)
            
            outFrame.setLayout(topLayout)
            
            self.outerLayout.addWidget(outFrame)
            
            subelements["path"] = csv
            subelements["outframe"] = outFrame
            subelements["itemName"] = itemName
            subelements["profit"] = profit
            subelements["id"] = id
            
            self.csvElements[idx] = subelements
        
        #print(len(self.csvElements))
    
    def prefill(self):
        # using the data in previously stored csvs created by updatejson,
        # we fill the lineedits with the already stored text
        
        if os.path.exists("preload.json"):
            with open("preload.json", "r") as f:
                data = load(f)
        
            for key in self.csvElements.keys():
                for key2 in data.keys():
                    if data[key2]["path"] == self.csvElements[key]["path"]:
                        self.csvElements[key]["itemName"].setText(key2)
                        self.csvElements[key]["profit"].setText(str(data[key2]["profit"]))
                        self.csvElements[key]["id"].setText(str(data[key2]["id"]))
                        break
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

    def removeCSV(self, csvPath, index):
        print(csvPath)
        w = MessageBox("Remove CSV", f'Are you sure you want to remove {csvPath}? This action cannot be undone, and will remove the CSV from /csv and the data from preload.json.', self)
        
        if w.exec():
            os.remove(f"csv/{csvPath}")
            self.csvElements.pop(index, None)
            # self.saveJson()
            # self.searchCSV("") 
            self.fillTable()
            self.prefill()
            
    def searchCSV(self, query):
        # search through csvElements (holds widgets)
        keys = []
        
        for key in self.csvElements.keys():
            if query in self.csvElements[key]['itemName'].text() or query in self.csvElements[key]['path']:
                keys.append(key)
                
        self.updateOuterLayoutVisibility(keys)
    
    def updateOuterLayoutVisibility(self, elements : list):
        for index in range(self.outerLayout.count()):
            if index in elements:
                self.outerLayout.itemAt(index).widget().setVisible(True)
            else:
                self.outerLayout.itemAt(index).widget().setVisible(False)

        