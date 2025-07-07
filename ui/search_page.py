from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton, QScrollArea
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont

def create_search_results_page(parent):
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

    # Search results title
    parent.search_results_title = QLabel("Search Results")
    parent.search_results_title.setFont(QFont("Arial", 22, QFont.Bold))
    parent.search_results_title.setStyleSheet("background-color: transparent; margin-bottom: 20px;")
    layout.addWidget(parent.search_results_title)
    
    # Search results container with scroll
    search_scroll = QScrollArea()
    search_scroll.setWidgetResizable(True)
    search_scroll.setFrameShape(QScrollArea.NoFrame)  # Remove frame
    search_scroll.setStyleSheet("""
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
    
    parent.search_results_container = QWidget()
    parent.search_results_container.setStyleSheet("background-color: transparent;")
    parent.search_results_layout = QVBoxLayout(parent.search_results_container)
    parent.search_results_layout.setContentsMargins(0, 0, 0, 0)
    parent.search_results_layout.setSpacing(12)
    parent.search_results_layout.setAlignment(Qt.AlignTop)
    
    # Placeholder for search results
    parent.search_results_placeholder = QLabel("Enter a search term and press Enter to find packages")
    parent.search_results_placeholder.setAlignment(Qt.AlignCenter)
    parent.search_results_placeholder.setStyleSheet("color: #888; padding: 40px; background-color: #2a2a2a; border-radius: 8px;")
    parent.search_results_layout.addWidget(parent.search_results_placeholder)
    
    search_scroll.setWidget(parent.search_results_container)
    layout.addWidget(search_scroll, 1)
    
    return page
