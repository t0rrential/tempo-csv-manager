from PyQt6.QtGui import QPixmap, QPainter, QPainterPath
from PyQt6.QtCore import Qt, QSize
from PyQt6.QtWidgets import QSizePolicy
from qfluentwidgets import SimpleCardWidget

class ImageWidget(SimpleCardWidget):
    def __init__(self, image_path):
        super().__init__()
        self.image_path = image_path
        self.pixmap = QPixmap(self.image_path)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)
        self.setMinimumSize(300, 200)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        # Calculate the new height based on the aspect ratio of the image
        aspect_ratio = self.pixmap.height() / self.pixmap.width()
        new_height = int(self.width() * aspect_ratio)
        self.setMinimumHeight(new_height)
        self.setMaximumHeight(new_height)
        self.update()

    def paintEvent(self, event):
        super().paintEvent(event)
        
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        # Create a painter path for rounded corners
        path = QPainterPath()
        path.addRoundedRect(0, 0, self.width(), self.height(), 10, 10)
        painter.setClipPath(path)
        
        # Scale the image to fill the widget while maintaining aspect ratio
        scaled_pixmap = self.pixmap.scaled(self.size(), Qt.AspectRatioMode.KeepAspectRatioByExpanding, Qt.TransformationMode.SmoothTransformation)
        painter.drawPixmap(0, 0, scaled_pixmap)
        painter.end()
