from PyQt6.QtWidgets import QStyleOptionViewItem, QVBoxLayout, QWidget
from PyQt6.QtGui import QPainter, QTextOption, QColor
from PyQt6.QtCore import QRectF, QSize, Qt, QRect

from qfluentwidgets import TableItemDelegate, isDarkTheme, themeColor


class CustomTableItemDelegate(TableItemDelegate):
    def __init__(self, parent):
        TableItemDelegate.__init__(self, parent)
    
    def paint(self, painter, option, index):   
        painter.setBrush(themeColor())     
        painter.save()
        painter.setRenderHint(QPainter.RenderHint.TextAntialiasing)          
        # Enable text wrapping
        option.displayAlignment = Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter
        option.features |= QStyleOptionViewItem.ViewItemFeature.WrapText
        
        text = index.data(Qt.ItemDataRole.DisplayRole)
        padding = 10
        rect = option.rect.adjusted(padding, padding, -padding, -padding)  # Add padding

        # draw highlight background
        isHover = self.hoverRow == index.row()
        isPressed = self.pressedRow == index.row()
        isAlternate = index.row() % 2 == 0 and self.parent().alternatingRowColors()
        isDark = isDarkTheme()

        c = 255 if isDark else 0
        alpha = 0

        if index.row() not in self.selectedRows:
            if isPressed:
                alpha = 9 if isDark else 6
            elif isHover:
                alpha = 12
            elif isAlternate:
                alpha = 5
        else:
            if isPressed:
                alpha = 15 if isDark else 9
            elif isHover:
                alpha = 25
            else:
                alpha = 17

        if index.data(Qt.ItemDataRole.BackgroundRole):
            painter.setBrush(index.data(Qt.ItemDataRole.BackgroundRole))
        else:
            painter.setBrush(QColor(c, c, c, alpha))
        # self._drawBackground(painter, option, index)

        # draw indicator
        if index.row() in self.selectedRows and index.column() == 0 and self.parent().horizontalScrollBar().value() == 0:
            self._drawIndicator(painter, option, index)

        textOption = QTextOption()
        textOption.setWrapMode(QTextOption.WrapMode.WordWrap)
        textOption.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)

        # Ensure using QRectF instead of QRect
        painter.drawText(QRectF(rect), text, textOption)

        painter.restore()

    def sizeHint(self, option, index):
        text = index.data(Qt.ItemDataRole.DisplayRole)
        metrics = option.fontMetrics
        width = option.rect.width()
        height = metrics.boundingRect(QRect(0, 0, width, 0), Qt.TextFlag.TextWordWrap, text).height()
        return QSize(width, height + 30)  # Adding 10 for padding

class PaddedWidget(QWidget):
    def __init__(self, widget, padding=10):
        super().__init__()
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(padding, padding, padding, padding)
        self.layout.addWidget(widget)
