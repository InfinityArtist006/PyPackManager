from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QComboBox,
    QFrame, QTextBrowser
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont

def create_library_detail_page(parent):
    page = QWidget()
    layout = QVBoxLayout(page)
    layout.setContentsMargins(40, 40, 40, 40)
    layout.setSpacing(20)

    # Back button
    back_button = QPushButton("← Back to Home")
    back_button.setStyleSheet("""
        QPushButton {
            padding: 8px 16px;
            font-size: 14px;
            background-color: #333;
            color: white;
            border-radius: 6px;
            text-align: left;
            border: none;
        }
        QPushButton:hover {
            background-color: #444;
        }
    """)
    back_button.clicked.connect(parent.go_back_to_home)
    layout.addWidget(back_button, 0, Qt.AlignLeft)

    # Header section
    header = QHBoxLayout()
    header.setSpacing(20)
    
    # Library icon
    parent.detail_icon = QLabel()
    icon_size = 80
    parent.detail_icon.setFixedSize(icon_size, icon_size)
    parent.detail_icon.setStyleSheet("background-color: transparent;")
    header.addWidget(parent.detail_icon)
    
    # Title and developer info
    title_section = QVBoxLayout()
    title_section.setSpacing(8)
    
    # Name and date container
    name_date_container = QHBoxLayout()
    name_date_container.setSpacing(10)
    parent.detail_name = QLabel()
    parent.detail_name.setFont(QFont("Arial", 24, QFont.Bold))
    parent.detail_name.setStyleSheet("background-color: transparent;")
    name_date_container.addWidget(parent.detail_name)
    
    parent.detail_date = QLabel()
    parent.detail_date.setStyleSheet("background-color: transparent; color: #888; font-size: 14px; padding-top: 8px;")
    name_date_container.addWidget(parent.detail_date)
    name_date_container.addStretch()
    
    title_section.addLayout(name_date_container)
    
    parent.detail_developer = QLabel()
    parent.detail_developer.setStyleSheet("background-color: transparent; color: #aaa; font-size: 15px;")
    title_section.addWidget(parent.detail_developer)
    
    header.addLayout(title_section, 1)
    
    # Version selector and install button
    version_section = QVBoxLayout()
    version_section.setSpacing(10)
    
    version_label = QLabel("Version")
    version_label.setStyleSheet("background-color: transparent; color: #aaa; font-size: 14px;")
    version_section.addWidget(version_label)
    
    parent.detail_version = QComboBox()
    parent.detail_version.setFixedWidth(150)
    parent.detail_version.setStyleSheet("""
        QComboBox {
            padding: 8px 12px;
            font-size: 14px;
            background-color: #333;
            border: 1px solid #444;
            border-radius: 6px;
            color: white;
        }
        QComboBox::drop-down {
            border: none;
            padding-right: 10px;
        }
    """)
    version_section.addWidget(parent.detail_version)
    
    install_detail_button = QPushButton("Install")
    install_detail_button.setStyleSheet("""
        QPushButton {
            padding: 10px 30px;
            font-size: 15px;
            background-color: #0078d7;
            color: white;
            border-radius: 6px;
            border: none;
        }
        QPushButton:hover {
            background-color: #005fa3;
        }
    """)
    version_section.addWidget(install_detail_button)
    
    header.addLayout(version_section)
    layout.addLayout(header)
    
    # Library link and tags container
    link_container = QHBoxLayout()
    
    # Library link
    parent.detail_link = QLabel()
    parent.detail_link.setStyleSheet("background-color: transparent; color: white; font-size: 14px; text-decoration: underline;")
    parent.detail_link.setOpenExternalLinks(True)
    link_container.addWidget(parent.detail_link)
    
    link_container.addStretch()
    
    # Tags container
    parent.detail_tags = QHBoxLayout()
    parent.detail_tags.setSpacing(8)
    link_container.addLayout(parent.detail_tags)
    
    layout.addLayout(link_container)
    
    # Separator
    separator = QFrame()
    separator.setFrameShape(QFrame.HLine)
    separator.setFrameShadow(QFrame.Sunken)
    separator.setStyleSheet("background-color: #333; margin: 10px 0;")
    layout.addWidget(separator)
    
    # Description
    desc_label = QLabel("Description")
    desc_label.setFont(QFont("Arial", 18, QFont.Bold))
    desc_label.setStyleSheet("background-color: transparent;")
    layout.addWidget(desc_label)
    
    parent.detail_description = QTextBrowser()
    parent.detail_description.setStyleSheet("""
        QTextBrowser {
            background-color: #252525;
            border: none;
            color: #ddd;
            font-size: 15px;
            padding: 20px;
            border-radius: 8px;
            selection-background-color: #0078d7;
        }
        QScrollBar:vertical {
            border: none;
            background: #333;
            width: 8px;
            border-radius: 4px;
            min-height: 20px;
        }
        QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
            height: 0px;
        }
    """)
    layout.addWidget(parent.detail_description, 1)
    
    return page
