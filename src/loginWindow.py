import os
from json import dumps, load

from src import validate_csv
from src import csv_parse

from PyQt5.QtCore import Qt
from PyQt5 import QtWidgets
from qfluentwidgets import LineEdit, CheckBox, LineEdit, PushButton, FluentIcon, InfoBarPosition, InfoBar, SmoothScrollArea

class LoginWindow(QtWidgets.QWidget):
    # create dict to reference textboxes
    csvElements = {}
    spacer = "         "
    
    def __init__(self, parent=None):
        super().__init__(parent=parent)
        
        # Create the scroll area and widget to hold the layout
        self.scroll = SmoothScrollArea()
        self.scroll.setWidgetResizable(True)
        self.widget = QtWidgets.QWidget()
        
        # Create the layout with textboxes and checkboxes
        self.outerLayout = QtWidgets.QVBoxLayout()
        
        # get list of csvs
        try:
            csvs = os.listdir("csv\\")
        except Exception as e:
            print(e)
        
        for idx, csv in enumerate(csvs):
        # for i in range(0, 5):
            subelements = {}
        
            outFrame = QtWidgets.QFrame()
            outFrame.setStyleSheet(".QFrame{ border: 3px solid gray; border-radius: 10px;}");
            
            topLayout = QtWidgets.QFormLayout()
            itemName = LineEdit()
            profit = LineEdit()
            
            topLayout.addRow(QtWidgets.QLabel(f"{csv}"))
            topLayout.addRow("Item Name:", itemName)
            topLayout.addRow("Profit (Cashout - Price):", profit)
            
            outFrame.setLayout(topLayout)
            
            self.outerLayout.addWidget(outFrame)
            
            subelements["path"] = "csv\\" + csv
            subelements["outframe"] = outFrame
            subelements["itemName"] = itemName
            subelements["profit"] = profit
            
            self.csvElements[idx] = subelements
            # self.outerLayout.addLayout(topLayout)
            # self.outerLayout.addLayout(optionsLayout)
        
        # Set the outer layout to the widget and add widget to scroll area
        self.widget.setLayout(self.outerLayout)
        self.scroll.setWidget(self.widget)
        
        # Create save and calculate buttons
        self.buttons = QtWidgets.QWidget()
        buttonLayout = QtWidgets.QHBoxLayout()
        buttonLayout.setAlignment(Qt.AlignLeft)
        self.buttons.setLayout(buttonLayout)
        
        self.submit = PushButton(self.spacer + "Save CSV Values")
        self.submit.setIcon(FluentIcon.SAVE)
        self.submit.setSizePolicy(QtWidgets.QSizePolicy.Maximum, QtWidgets.QSizePolicy.Maximum)
        self.submit.setStyleSheet("QAbstractButton {qproperty-icon: align-center;}")
        self.submit.clicked.connect(lambda: self.saveJson())
        
        self.calculate = PushButton(self.spacer + "Calculate Routes")
        self.calculate.setIcon(FluentIcon.SEND_FILL)
        self.calculate.setSizePolicy(QtWidgets.QSizePolicy.Maximum, QtWidgets.QSizePolicy.Maximum)
        self.calculate.setStyleSheet("QAbstractButton {qproperty-icon: align-center;}")
        # self.calculate.clicked.connect()

        buttonLayout.addWidget(self.submit)
        buttonLayout.addWidget(self.calculate)
        
        # Set scroll area as the main layout
        mainLayout = QtWidgets.QVBoxLayout()
        mainLayout.addWidget(self.buttons)
        mainLayout.addWidget(self.scroll)
        self.setLayout(mainLayout)
        self.prefill()
    
    def prefill(self):
        print("running prefill")
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
                        break
        return
    
    def saveJson(self):
        formattedDict = {}
        keys = self.csvElements.keys()
        
        for key in keys:
            path = self.csvElements[key]['path']
            profit = self.csvElements[key]['profit'].text()
            itemName = self.csvElements[key]['itemName'].text()
            
            if profit == "":
                self.showErrorBar("profit", path)
            elif not profit.isnumeric():
                self.showErrorBar("integer", path)
                
            if itemName == "":
                self.showErrorBar("itemName", path)
                
            if validate_csv.validate_csv(path):
                self.showErrorBar("path", path)
                
            formattedDict[itemName] = {}
            formattedDict[itemName]["path"] = path
            formattedDict[itemName]["profit"] = int(profit)        
        
        csv_parse.dictToJson(formattedDict)
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
            orient=Qt.Horizontal,
            isClosable=True,
            position=InfoBarPosition.TOP_RIGHT,
            duration=2000,
            parent=self
        )
        return
