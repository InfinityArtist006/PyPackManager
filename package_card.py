import os
from PyQt5.QtWidgets import QFrame, QHBoxLayout, QVBoxLayout, QLabel, QPushButton, QComboBox
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QFont, QPixmap, QPainter, QColor

class PackageCard(QFrame):
    package_clicked = pyqtSignal(object)
    
    def __init__(self, library, parent=None):
        super().__init__(parent)
        self.library = library
        self.setup_ui()
        
    def setup_ui(self):
        self.setFrameShape(QFrame.StyledPanel)
        self.setStyleSheet("""
            QFrame {
                background-color: #2e2e2e;
                border-radius: 10px;
                margin-bottom: 12px;
            }
        """)
        self.setCursor(Qt.PointingHandCursor)
        
        # Main layout
        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(16, 16, 16, 16)
        main_layout.setSpacing(12)
        
        # Icon
        icon_size = 40
        icon_path = os.path.join(
            os.path.dirname(os.path.abspath(__file__)), 
            "icons", 
            self.library["icon"]
        )
        
        self.icon_label = QLabel()
        
        if os.path.exists(icon_path):
            pixmap = QPixmap(icon_path).scaled(
                icon_size, icon_size, 
                Qt.KeepAspectRatio, Qt.SmoothTransformation
            )
        else:
            # Create a custom icon
            pixmap = QPixmap(icon_size, icon_size)
            pixmap.fill(Qt.transparent)
            
            painter = QPainter(pixmap)
            painter.setRenderHint(QPainter.Antialiasing)
            
            # Draw colored circle based on first letter
            first_letter = self.library["name"][0].upper()
            
            # Different colors for different letters
            color_map = {
                'A': "#FF5733", 'B': "#33FF57", 'C': "#3357FF", 'D': "#F033FF", 
                'E': "#33FFF0", 'F': "#FF3355", 'G': "#FFFF33", 'H': "#33FFFF",
                'I': "#FF33FF", 'J': "#33FF33", 'K': "#3333FF", 'L': "#FF3333",
                'M': "#33FFAA", 'N': "#AA33FF", 'O': "#FFAA33", 'P': "#3377FF",
                'Q': "#FF7733", 'R': "#33FF77", 'S': "#7733FF", 'T': "#FF33AA",
                'U': "#33FFAA", 'V': "#AA33FF", 'W': "#FFAA33", 'X': "#33AAFF",
                'Y': "#FFAA33", 'Z': "#33AAFF"
            }
            
            color = color_map.get(first_letter, "#3776AB")  # Default to Python blue
            
            painter.setBrush(QColor(color))
            painter.setPen(Qt.NoPen)
            painter.drawEllipse(0, 0, icon_size, icon_size)
            
            # Draw first letter
            painter.setPen(Qt.white)
            painter.setFont(QFont("Arial", 16, QFont.Bold))
            painter.drawText(pixmap.rect(), Qt.AlignCenter, first_letter)
            painter.end()
        
        self.icon_label.setPixmap(pixmap)
        self.icon_label.setFixedSize(icon_size, icon_size)
        main_layout.addWidget(self.icon_label)
        
        # Info container - left side
        left_container = QVBoxLayout()
        left_container.setSpacing(6)
        
        # Package name row
        name_container = QHBoxLayout()
        name_container.setSpacing(10)
        
        # Package name
        name_label = QLabel(self.library["name"])
        name_label.setFont(QFont("Arial", 15, QFont.Bold))
        name_label.setStyleSheet("background-color: transparent; color: white;")
        name_container.addWidget(name_label)
        
        # Date if available
        if 'upload_date' in self.library and self.library['upload_date'] != "Unknown":
            date_label = QLabel(f"Updated: {self.library['upload_date']}")
            date_label.setStyleSheet("background-color: transparent; color: #888888; font-size: 12px;")
            name_container.addWidget(date_label)
        
        name_container.addStretch()
        left_container.addLayout(name_container)
        
        # Description
        description_text = self.library.get("description", "No description available")
        if not description_text or description_text.strip() == "":
            description_text = "No description available"
        
        desc_label = QLabel(description_text)
        desc_label.setWordWrap(True)
        desc_label.setStyleSheet("""
            background-color: transparent;
            color: #aaaaaa;
            font-size: 13px;
        """)
        left_container.addWidget(desc_label)
        
        # Add a stretch to keep content at the top
        left_container.addStretch()
        
        main_layout.addLayout(left_container, 1)
        
        # Right container - version and install
        right_container = QHBoxLayout()
        right_container.setSpacing(10)
        
        # Version dropdown
        self.version_dropdown = QComboBox()
        self.version_dropdown.addItems(self.library["versions"])
        self.version_dropdown.setFixedWidth(70)
        self.version_dropdown.setStyleSheet("""
            QComboBox {
                padding: 5px;
                font-size: 13px;
                background-color: #333;
                border: 1px solid #444;
                border-radius: 4px;
                color: white;
            }
            QComboBox::drop-down {
                border: none;
                padding-right: 5px;
            }
        """)
        right_container.addWidget(self.version_dropdown)
        
        # Install button
        self.install_button = QPushButton("Install")
        self.install_button.setFixedWidth(70)
        self.install_button.setStyleSheet("""
            QPushButton {
                padding: 5px;
                font-size: 13px;
                background-color: #0078d7;
                color: white;
                border-radius: 4px;
                border: none;
            }
            QPushButton:hover {
                background-color: #005fa3;
            }
        """)
        right_container.addWidget(self.install_button)
        
        main_layout.addLayout(right_container)
        
    def mousePressEvent(self, event):
        self.package_clicked.emit(self.library)
        super().mousePressEvent(event)
