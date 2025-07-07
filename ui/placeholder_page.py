from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont

def create_placeholder_page(title, message):
    page = QWidget()
    layout = QVBoxLayout(page)
    layout.setContentsMargins(40, 40, 40, 40)
    
    title_label = QLabel(title)
    title_label.setFont(QFont("Arial", 24, QFont.Bold))
    layout.addWidget(title_label)
    
    message_label = QLabel(message)
    message_label.setStyleSheet("color: #aaa; font-size: 16px; margin-top: 10px;")
    layout.addWidget(message_label)
    
    layout.addStretch()
    
    return page
