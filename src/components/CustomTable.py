import traceback
import sys

from PyQt6.QtWidgets import QSizePolicy, QHeaderView, QAbstractItemView
from PyQt6.QtCore import (
    QObject,
    QThread,
    pyqtSignal,
    pyqtSlot,
)

from src.components.CustomTableItemDelegate import CustomTableItemDelegate

from qfluentwidgets import TableWidget

class WorkerSignals(QObject):
    error = pyqtSignal(tuple)
    result = pyqtSignal(object)

class CustomTableWorker(QThread):
    def __init__(self, fn, *args, **kwargs):
            super().__init__()
            self.fn = fn
            self.args = args
            self.kwargs = kwargs
            self.signals = WorkerSignals()
    
    @pyqtSlot()
    def run(self):
        try:
            result = self.fn(*self.args, **self.kwargs)
        except Exception:
            traceback.print_exc()
            exctype, value = sys.exc_info()[:2]
            self.signals.error.emit((exctype, value, traceback.format_exc()))
        else:
            self.signals.result.emit(result)

class CustomTable(TableWidget):
    
    def __init__(self, type: str, validclient=False, parent=None):
        super().__init__(parent=parent)
        self.labels = ["Address", "Items", "Profits", "Costs", "Distance"]
        
        self.setItemDelegate(CustomTableItemDelegate(self)) # custom delegate
        self.setWordWrap(True)
        
        self.verticalHeader().setSectionResizeMode(QHeaderView.ResizeMode.ResizeToContents)
        self.verticalHeader().setVisible(False)
        
        # loginwindow table settings
        if type == "login":            
            self.setColumnCount(11)
            self.setHorizontalHeaderLabels(["File", "Last Modified", "Item Name", "Sale Price", "Item ID", "MSRP", " Avg ", " Low ", "Total", "Profit", ""])
            
            self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
            self.setSelectionMode(QAbstractItemView.SelectionMode.NoSelection)
            
            header = self.horizontalHeader()
            # table header settings to make everything fit
            header.setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
            header.setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)
            header.setSectionResizeMode(2, QHeaderView.ResizeMode.Interactive)
            header.setSectionResizeMode(3, QHeaderView.ResizeMode.Stretch)
            header.setSectionResizeMode(4, QHeaderView.ResizeMode.Stretch)
            header.setSectionResizeMode(5, QHeaderView.ResizeMode.ResizeToContents)
            header.setSectionResizeMode(6, QHeaderView.ResizeMode.ResizeToContents)
            header.setSectionResizeMode(7, QHeaderView.ResizeMode.ResizeToContents)
            header.setSectionResizeMode(8, QHeaderView.ResizeMode.ResizeToContents)
            header.setSectionResizeMode(9, QHeaderView.ResizeMode.ResizeToContents)
            header.setSectionResizeMode(10, QHeaderView.ResizeMode.ResizeToContents)
        
        elif type == "routerleft":
            # bring ts back to routerleft
            # self.itemSelectionChanged.connect(self.updateInfoBar)
            self.setColumnCount(5 if validclient else 4)
            self.setHorizontalHeaderLabels(self.labels if validclient else self.labels[:-1])
            
            self.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
            self.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
            self.setSelectionMode(QAbstractItemView.SelectionMode.MultiSelection)
            self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
            
            headers = self.horizontalHeader()
            headers.setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
            headers.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
            headers.setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)
            headers.setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents)
            if validclient:
                headers.setSectionResizeMode(4, QHeaderView.ResizeMode.ResizeToContents)
                
        elif type == "routerright":
            self.setColumnCount(5 if validclient else 4)
            self.setHorizontalHeaderLabels(self.labels if validclient else self.labels[:-1])
            
            self.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
            self.setSelectionMode(QAbstractItemView.SelectionMode.NoSelection)

            headers = self.horizontalHeader()
            headers.setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
            headers.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
            headers.setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)
            headers.setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents)
            if validclient:
                headers.setSectionResizeMode(4, QHeaderView.ResizeMode.ResizeToContents)
                
    def routerSearch(storeInfo, storeKeys, query: str):
        filtered = [
            index for index, store in enumerate(storeKeys)
            if query.lower() in store.lower() 
            or any(
                query.lower() in (item.lower() if item != "itemList" or item != "store_profit" else None) # make sure it doesn't get these in search results
                for item in storeInfo[store].keys()
            )
        ]
        
        return filtered
    
    def selectAllRows(self):
        """Select all rows in the table."""
        alreadySelected = set([idx.row() for idx in self.selectedIndexes()])
        for rowIdx in range(0, self.rowCount()):
            if not self.isRowHidden(rowIdx) and rowIdx not in alreadySelected:
                self.selectRow(rowIdx)
                
    def deselectAllRows(self):
        """Deselect all rows in the table."""
        for rowIdx in range(0, self.rowCount()):
            if not self.isRowHidden(rowIdx):
                for col in range(4):
                    selectionModel = self.selectionModel()
                    selectionModel.select(self.model().index(rowIdx, col), selectionModel.SelectionFlag.Deselect)
        
        self.updateSelectedRows()
        # only in python is it harder to unselect