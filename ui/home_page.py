from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton,
    QScrollArea, QProgressBar
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont

def create_home_page(parent):
    page = QWidget()
    layout = QVBoxLayout(page)
    layout.setContentsMargins(40, 40, 40, 40)
    layout.setSpacing(30)

    # Title
    title = QLabel("PyPackManager")
    title.setAlignment(Qt.AlignCenter)
    title.setFont(QFont("Arial", 32, QFont.Bold))
    title.setStyleSheet("margin-bottom: 20px;")
    layout.addWidget(title)

    # Search Box
    search_layout = QHBoxLayout()
    search_layout.setSpacing(10)
    
    parent.search_box = QLineEdit()
    parent.search_box.setPlaceholderText("Search for packages... (press Enter to search)")
    parent.search_box.setStyleSheet("""
        QLineEdit {
            padding: 12px 16px;
            font-size: 15px;
            border-radius: 8px;
            background-color: #2a2a2a;
            color: white;
            border: 1px solid #3a3a3a;
        }
        QLineEdit:focus {
            border: 1px solid #0078d7;
        }
    """)
    parent.search_box.returnPressed.connect(parent.search_package)
    search_layout.addWidget(parent.search_box)
    
    search_button = QPushButton("Search")
    search_button.setStyleSheet("""
        QPushButton {
            padding: 12px 20px;
            font-size: 15px;
            background-color: #0078d7;
            color: white;
            border-radius: 8px;
            border: none;
        }
        QPushButton:hover {
            background-color: #005fa3;
        }
    """)
    search_button.clicked.connect(parent.search_package)
    search_layout.addWidget(search_button)
    
    layout.addLayout(search_layout)

    # Loading indicator for initial data
    loading_container = QHBoxLayout()
    loading_container.setContentsMargins(0, 10, 0, 10)
    
    parent.loading_indicator = QLabel("Loading library data from PyPI...")
    parent.loading_indicator.setAlignment(Qt.AlignCenter)
    parent.loading_indicator.setStyleSheet("color: #888; font-size: 14px;")
    loading_container.addWidget(parent.loading_indicator)
    
    # Progress bar
    parent.progress_bar = QProgressBar()
    parent.progress_bar.setRange(0, 0)  # Indeterminate progress
    parent.progress_bar.setTextVisible(False)
    parent.progress_bar.setFixedHeight(4)
    parent.progress_bar.setStyleSheet("""
        QProgressBar {
            border: none;
            background-color: #333;
            border-radius: 2px;
            margin-left: 10px;
            margin-right: 10px;
        }
        QProgressBar::chunk {
            background-color: #0078d7;
            border-radius: 2px;
        }
    """)
    loading_container.addWidget(parent.progress_bar)
    
    layout.addLayout(loading_container)

    # Sections container with scroll
    sections_scroll = QScrollArea()
    sections_scroll.setWidgetResizable(True)
    sections_scroll.setStyleSheet("""
        QScrollArea {
            border: none;
            background: transparent;
        }
        QScrollBar:vertical {
            border: none;
            background: #333;
            width: 8px;
            border-radius: 4px;
        }
        QScrollBar::handle:vertical {
            background: #555;
            border-radius: 4px;
            min-height: 20px;
        }
        QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
            height: 0px;
        }
    """)
    
    sections_widget = QWidget()
    sections_widget.setStyleSheet("background-color: transparent;")
    sections_layout = QVBoxLayout(sections_widget)
    sections_layout.setContentsMargins(0, 0, 0, 0)
    sections_layout.setSpacing(30)
    
    # Recent Libraries
    recent_section = QWidget()
    recent_section.setStyleSheet("background-color: transparent;")
    parent.recent_layout = QVBoxLayout(recent_section)
    parent.recent_layout.setContentsMargins(0, 0, 0, 0)
    parent.recent_layout.setSpacing(8)
    
    recent_header = QLabel("Recent Libraries")
    recent_header.setFont(QFont("Arial", 20, QFont.Bold))
    recent_header.setStyleSheet("background-color: transparent;")
    parent.recent_layout.addWidget(recent_header)
    
    # Placeholder for recent libraries
    parent.recent_placeholder = QLabel("Loading recent libraries...")
    parent.recent_placeholder.setAlignment(Qt.AlignCenter)
    parent.recent_placeholder.setStyleSheet("color: #888; padding: 20px; background-color: #2a2a2a; border-radius: 8px;")
    parent.recent_layout.addWidget(parent.recent_placeholder)
    
    sections_layout.addWidget(recent_section)
    
    # Trending Libraries
    trending_section = QWidget()
    trending_section.setStyleSheet("background-color: transparent;")
    parent.trending_layout = QVBoxLayout(trending_section)
    parent.trending_layout.setContentsMargins(0, 0, 0, 0)
    parent.trending_layout.setSpacing(8)
    
    trending_header = QLabel("Trending Libraries")
    trending_header.setFont(QFont("Arial", 20, QFont.Bold))
    trending_header.setStyleSheet("background-color: transparent;")
    parent.trending_layout.addWidget(trending_header)
    
    # Placeholder for trending libraries
    parent.trending_placeholder = QLabel("Loading trending libraries...")
    parent.trending_placeholder.setAlignment(Qt.AlignCenter)
    parent.trending_placeholder.setStyleSheet("color: #888; padding: 20px; background-color: #2a2a2a; border-radius: 8px;")
    parent.trending_layout.addWidget(parent.trending_placeholder)
    
    sections_layout.addWidget(trending_section)
    
    sections_scroll.setWidget(sections_widget)
    layout.addWidget(sections_scroll, 1)

    return page
