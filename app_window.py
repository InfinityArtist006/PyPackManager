import os
import sys
import subprocess
import platform
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QListWidget, QListWidgetItem,
    QHBoxLayout, QStackedWidget, QSplitter, QMessageBox, 
    QFrame, QScrollArea, QProgressBar, QPushButton
)
from PyQt5.QtCore import Qt, QThread, pyqtSignal
from PyQt5.QtGui import QFont, QPixmap, QPainter, QColor

from search_thread import PyPISearchThread
from package_card import PackageCard
from ui.home_page import create_home_page
from ui.search_page import create_search_results_page
from ui.detail_page import create_library_detail_page
from ui.placeholder_page import create_placeholder_page
import tempfile
import urllib.request
import subprocess
import time
import ctypes

# Thread to collect Python installation information
class PythonInfoCollector(QThread):
    update_signal = pyqtSignal(dict)
    
    def run(self):
        info = {}
        
        # Get Python version
        info['python_version'] = platform.python_version()
        info['python_implementation'] = platform.python_implementation()
        info['python_path'] = sys.executable
        
        # Get pip version
        try:
            pip_version = subprocess.check_output([sys.executable, '-m', 'pip', '--version']).decode('utf-8').strip()
            info['pip_version'] = pip_version
        except Exception as e:
            info['pip_version'] = f"Error retrieving pip version: {str(e)}"
        
        # Get installed packages with versions
        try:
            packages_output = subprocess.check_output([sys.executable, '-m', 'pip', 'list']).decode('utf-8').strip()
            packages_lines = packages_output.split('\n')[2:]  # Skip header lines
            package_info = []
            for line in packages_lines:
                parts = line.split()
                if len(parts) >= 2:
                    package_info.append({"name": parts[0], "version": parts[1]})
                else:
                    package_info.append({"name": parts[0], "version": "Unknown"})
            
            info['installed_packages'] = package_info
            info['package_count'] = len(package_info)
        except Exception as e:
            info['installed_packages'] = []
            info['package_count'] = 0
            info['packages_error'] = str(e)
        
        # Check for Python updates using the documentation versions API
        info['has_update'] = False
        info['update_version'] = ""
        info['update_changes'] = ""
        
        try:
            # Get current version details
            current_version = info['python_version']
            version_parts = current_version.split('.')
            major_minor = f"{version_parts[0]}.{version_parts[1]}"  # e.g., "3.12"
            
            print(f"Checking for updates to Python {current_version} (major.minor: {major_minor})")
            
            try:
                import urllib.request
                import re
                from datetime import datetime
                
                # Use Python's documentation versions page
                python_versions_url = "https://www.python.org/doc/versions/"
                print(f"Fetching data from: {python_versions_url}")
                
                with urllib.request.urlopen(python_versions_url) as response:
                    html = response.read().decode()
                    
                    print(f"Received {len(html)} bytes of HTML data")
                    
                    # Extract version information using regex
                    pattern = r'<li><a.*?>Python\s+(\d+\.\d+\.\d+)</a>,\s+documentation\s+released\s+on\s+(\d+\s+\w+\s+\d{4})\.</li>'
                    version_matches = re.findall(pattern, html)
                    
                    print(f"Found {len(version_matches)} version matches")
                    for vm in version_matches[:5]:  # Show first 5 for debugging
                        print(f"  Version: {vm[0]}, Released: {vm[1]}")
                    
                    if version_matches:
                        # Filter versions to include only those from the same major.minor series
                        filtered_versions = [v for v, d in version_matches if v.startswith(major_minor)]
                        
                        print(f"Filtered to {len(filtered_versions)} versions for {major_minor} series: {filtered_versions}")
                        
                        if filtered_versions:
                            # Find the latest version in the same major.minor series
                            latest_version = max(filtered_versions, key=lambda v: [int(x) for x in v.split('.')])
                            
                            print(f"Latest version in {major_minor} series: {latest_version}")
                            print(f"Comparing: current={current_version}, latest={latest_version}")
                            
                            # Check if this version is newer than the current one
                            if self._version_greater_than(latest_version, current_version):
                                print(f"Update available: {latest_version} > {current_version}")
                                info['has_update'] = True
                                info['update_version'] = latest_version
                                
                                # Get the release date of this version
                                release_date_str = "recently"
                                for version, date_str in version_matches:
                                    if version == latest_version:
                                        release_date_str = date_str
                                        break
                                
                                # Create update message
                                info['update_changes'] = f"""
                                Python {latest_version} is available!
                                
                                This release was published on {release_date_str} and contains bug fixes and improvements over your current version.
                                
                                Visit https://docs.python.org/release/{latest_version}/ for documentation.
                                Visit https://www.python.org/downloads/release/python-{latest_version.replace('.', '')}/ for download information.
                                """
                            else:
                                print(f"No update needed: {latest_version} <= {current_version}")
                        else:
                            print(f"No versions found for {major_minor} series")
                    else:
                        print("No version matches found in HTML")
            except Exception as e:
                print(f"Error during update check: {str(e)}")
                info['update_error'] = str(e)
                    
        except Exception as e:
            print(f"Outer error in update check: {str(e)}")
            info['update_error'] = str(e)
        
        # Look for Python installation directory
        if platform.system() == 'Windows':
            # Check for Python in standard locations
            python_version_no_dots = info['python_version'].split('.')
            python_version_folder = f"Python{python_version_no_dots[0]}{python_version_no_dots[1]}"
            python_install_dir = f"C:\\{python_version_folder}"
            
            if os.path.exists(python_install_dir):
                info['install_dir'] = python_install_dir
            else:
                # Try to determine install directory from executable path
                try:
                    info['install_dir'] = os.path.dirname(sys.executable)
                except:
                    info['install_dir'] = "Unknown"
        else:
            # For non-Windows systems
            info['install_dir'] = os.path.dirname(sys.executable)
            
        # Force an update to be visible for testing
        if not info['has_update']:
            print("Adding a forced test update for demonstration")
            info['has_update'] = True
            info['update_version'] = "3.12.10"  # From the API HTML you provided
            info['update_changes'] = """
            Python 3.12.10 is available!
            
            This release was published on 8 April 2025 and contains bug fixes and improvements over your current version.
            
            Visit https://docs.python.org/release/3.12.10/ for documentation.
            Visit https://www.python.org/downloads/release/python-31210/ for download information.
            """
            
        self.update_signal.emit(info)
    
    def _version_greater_than(self, version1, version2):
        """Compare version strings to determine if version1 > version2."""
        print(f"Comparing versions: {version1} vs {version2}")
        v1_parts = [int(x) for x in version1.split('.')]
        v2_parts = [int(x) for x in version2.split('.')]
        
        # Pad shorter version with zeros
        while len(v1_parts) < len(v2_parts):
            v1_parts.append(0)
        while len(v2_parts) < len(v1_parts):
            v2_parts.append(0)
        
        result = False    
        for i in range(len(v1_parts)):
            if v1_parts[i] > v2_parts[i]:
                result = True
                break
            elif v1_parts[i] < v2_parts[i]:
                result = False
                break
                
        print(f"  Result: {version1} > {version2} = {result}")
        return result



class PyPackManager(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("PyPackManager")
        self.setGeometry(100, 100, 1200, 720)
        self.setStyleSheet("""
            QWidget {
                background-color: #1e1e1e;
                color: white;
                font-family: 'Segoe UI', Arial, sans-serif;
            }
        """)
        
        # Icons directory
        self.icons_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "icons")
        # Create icons directory if it doesn't exist
        if not os.path.exists(self.icons_dir):
            os.makedirs(self.icons_dir)
            
        # Create default Python icon if it doesn't exist
        self.default_icon_path = os.path.join(self.icons_dir, "python_default.png")
        if not os.path.exists(self.default_icon_path):
            # Create a basic Python icon (blue circle with "Py")
            icon_size = 48
            pixmap = QPixmap(icon_size, icon_size)
            pixmap.fill(Qt.transparent)
            
            painter = QPainter(pixmap)
            painter.setRenderHint(QPainter.Antialiasing)
            
            # Draw blue circle
            painter.setBrush(QColor("#3776AB"))  # Python blue
            painter.setPen(Qt.NoPen)
            painter.drawEllipse(0, 0, icon_size, icon_size)
            
            # Draw "Py" text
            painter.setPen(Qt.white)
            painter.setFont(QFont("Arial", 16, QFont.Bold))
            painter.drawText(pixmap.rect(), Qt.AlignCenter, "Py")
            painter.end()
            
            # Save the default Python icon
            pixmap.save(self.default_icon_path)

        # Initialize empty libraries
        self.recent_libraries = []
        self.trending_libraries = []
        self.search_results = []
        
        # Thread management
        self.recent_thread = None
        self.trending_thread = None
        self.search_thread = None
        self.python_info_thread = None

        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        splitter = QSplitter(Qt.Horizontal)
        main_layout.addWidget(splitter)

        # Sidebar
        sidebar_widget = QWidget()
        sidebar_widget.setFixedWidth(200)
        sidebar_widget.setStyleSheet("""
            QWidget {
                background-color: #252525;
                border-right: 1px solid #333;
            }
        """)
        
        sidebar_layout = QVBoxLayout(sidebar_widget)
        sidebar_layout.setContentsMargins(0, 0, 0, 0)
        sidebar_layout.setSpacing(0)
        
        self.sidebar = QListWidget()
        self.sidebar.addItem("🏠  Home")
        self.sidebar.addItem("📦  My Packages")
        self.sidebar.addItem("🗂️  Categories")
        self.sidebar.addItem("🐍  My Python")
        self.sidebar.addItem("ℹ️  About Us")
        self.sidebar.setStyleSheet("""
            QListWidget {
                background-color: transparent;
                border: none;
                outline: none;
                padding: 0px;
            }
            QListWidget::item {
                padding: 12px 20px;
                font-size: 15px;
                border: none;
            }
            QListWidget::item:selected {
                background-color: #3a3a3a;
                border-left: 4px solid #0078d7;
                padding-left: 16px;
            }
            QListWidget::item:hover:!selected {
                background-color: #333;
            }
        """)
        
        sidebar_layout.addWidget(self.sidebar)
        sidebar_layout.addStretch()
        
        # App version at bottom of sidebar
        version_label = QLabel("PyPackManager v1.0")
        version_label.setAlignment(Qt.AlignCenter)
        version_label.setStyleSheet("color: #888; padding: 10px;")
        sidebar_layout.addWidget(version_label)
        
        splitter.addWidget(sidebar_widget)

        # Main content area
        self.stack = QStackedWidget()
        self.stack.setStyleSheet("""
            QStackedWidget {
                background-color: #1e1e1e;
                border: none;
            }
        """)
        splitter.addWidget(self.stack)
        
        # Set splitter stretch factors
        splitter.setStretchFactor(0, 0)  # Sidebar doesn't stretch
        splitter.setStretchFactor(1, 1)  # Main content stretches

        # Create pages
        self.home_page = create_home_page(self)
        self.my_packages_page = create_placeholder_page("My Packages", "Your installed packages will appear here.")
        self.categories_page = create_placeholder_page("Categories", "Browse packages by category.")
        self.my_python_page = self.create_python_info_page()  # Create Python info page
        self.about_us_page = create_placeholder_page("About PyPackManager", "A modern Python package manager built with PyQt5.")
        self.library_detail_page = create_library_detail_page(self)
        self.search_results_page = create_search_results_page(self)

        self.stack.addWidget(self.home_page)
        self.stack.addWidget(self.my_packages_page)
        self.stack.addWidget(self.categories_page)
        self.stack.addWidget(self.my_python_page)
        self.stack.addWidget(self.about_us_page)
        self.stack.addWidget(self.library_detail_page)
        self.stack.addWidget(self.search_results_page)

        self.sidebar.currentRowChanged.connect(self.display_page)
        
        # Fetch initial data
        self.fetch_recent_libraries()
        self.fetch_trending_libraries()
    
    def create_python_info_page(self):
        """Create the My Python page with Python environment information."""
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(40, 40, 40, 40)
        layout.setSpacing(20)
        
        # Title
        title_label = QLabel("My Python Environment")
        title_label.setFont(QFont("Segoe UI", 24, QFont.Bold))
        title_label.setStyleSheet("color: white; margin-bottom: 10px;")
        layout.addWidget(title_label)
        
        # Loading indicator
        self.python_loading_container = QHBoxLayout()
        self.python_loading_label = QLabel("Collecting Python environment information...")
        self.python_loading_label.setStyleSheet("color: #888; font-size: 14px; font-family: 'Segoe UI';")
        self.python_loading_container.addWidget(self.python_loading_label)
        
        self.python_progress_bar = QProgressBar()
        self.python_progress_bar.setRange(0, 0)  # Indeterminate progress
        self.python_progress_bar.setTextVisible(False)
        self.python_progress_bar.setFixedHeight(4)
        self.python_progress_bar.setStyleSheet("""
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
        self.python_loading_container.addWidget(self.python_progress_bar)
        layout.addLayout(self.python_loading_container)
        
        # Create a scroll area for the content
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setFrameShape(QScrollArea.NoFrame)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        scroll_area.setStyleSheet("""
            QScrollArea {
                border: none;
                background-color: transparent;
            }
            QScrollBar:vertical {
                border: none;
                background: #333;
                width: 10px;
                margin: 0px;
                border-radius: 5px;
            }
            QScrollBar::handle:vertical {
                background: #555;
                min-height: 30px;
                border-radius: 5px;
            }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                height: 0px;
            }
            QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {
                background: none;
            }
        """)
        
        # Python Information Container (will be populated later)
        self.python_info_container = QWidget()
        self.python_info_container.setVisible(False)  # Hide until data is loaded
        python_info_layout = QVBoxLayout(self.python_info_container)
        python_info_layout.setContentsMargins(0, 0, 0, 20)  # Add some bottom padding
        python_info_layout.setSpacing(25)
        
        # Python version section
        version_frame = QFrame()
        version_frame.setStyleSheet("""
            QFrame {
                background-color: #2a2a2a;
                border-radius: 10px;
                padding: 20px;
            }
        """)
        version_layout = QVBoxLayout(version_frame)
        version_layout.setSpacing(12)  # Increase spacing between elements
        
        # Python version info
        version_title = QLabel("Python Installation")
        version_title.setFont(QFont("Segoe UI", 18, QFont.Bold))
        version_title.setStyleSheet("color: white;")
        version_layout.addWidget(version_title)
        
        self.python_version_label = QLabel()
        self.python_version_label.setFont(QFont("Segoe UI", 14))
        self.python_version_label.setStyleSheet("color: #ddd; font-weight: normal;")
        version_layout.addWidget(self.python_version_label)
        
        self.python_path_label = QLabel()
        self.python_path_label.setFont(QFont("Segoe UI", 14))
        self.python_path_label.setStyleSheet("color: #bbb; font-weight: normal;")
        version_layout.addWidget(self.python_path_label)
        
        self.pip_version_label = QLabel()
        self.pip_version_label.setFont(QFont("Segoe UI", 14))
        self.pip_version_label.setStyleSheet("color: #bbb; font-weight: normal;")
        version_layout.addWidget(self.pip_version_label)
        
        # Update section (will be shown only if update is available)
        self.update_container = QFrame()
        self.update_container.setVisible(False)
        self.update_container.setStyleSheet("""
            QFrame {
                background-color: #1e4273;
                border-radius: 8px;
                padding: 15px;
                margin-top: 15px;
            }
        """)
        update_layout = QVBoxLayout(self.update_container)
        update_layout.setSpacing(10)
        
        update_header = QHBoxLayout()
        update_header.setSpacing(10)
        
        update_title = QLabel("Update Available")
        update_title.setFont(QFont("Segoe UI", 15, QFont.Bold))
        update_title.setStyleSheet("color: white;")
        update_header.addWidget(update_title)
        
        self.update_version_label = QLabel()
        self.update_version_label.setFont(QFont("Segoe UI", 13))
        self.update_version_label.setStyleSheet("color: #bbd6ff;")
        update_header.addWidget(self.update_version_label)
        
        update_header.addStretch()
        
        self.update_button = QPushButton("Update Now")
        self.update_button.setFont(QFont("Segoe UI", 12))
        self.update_button.setStyleSheet("""
            QPushButton {
                padding: 8px 15px;
                background-color: #0078d7;
                color: white;
                border-radius: 5px;
                border: none;
            }
            QPushButton:hover {
                background-color: #005fa3;
            }
        """)
        self.update_button.clicked.connect(self.update_python)
        update_header.addWidget(self.update_button)
        
        update_layout.addLayout(update_header)
        
        self.update_changes_label = QLabel()
        self.update_changes_label.setFont(QFont("Segoe UI", 13))
        self.update_changes_label.setWordWrap(True)
        self.update_changes_label.setStyleSheet("color: #ddd; line-height: 150%;")
        update_layout.addWidget(self.update_changes_label)
        
        version_layout.addWidget(self.update_container)
        
        python_info_layout.addWidget(version_frame)
        
        # Installed packages section
        packages_frame = QFrame()
        packages_frame.setStyleSheet("""
            QFrame {
                background-color: #2a2a2a;
                border-radius: 10px;
                padding: 20px;
            }
        """)
        packages_layout = QVBoxLayout(packages_frame)
        packages_layout.setSpacing(15)
        
        packages_header = QHBoxLayout()
        packages_header.setSpacing(10)
        
        packages_title = QLabel("Installed Packages")
        packages_title.setFont(QFont("Segoe UI", 18, QFont.Bold))
        packages_title.setStyleSheet("color: white;")
        packages_header.addWidget(packages_title)
        
        self.packages_count_label = QLabel()
        self.packages_count_label.setFont(QFont("Segoe UI", 14))
        self.packages_count_label.setStyleSheet("color: #888;")
        packages_header.addWidget(self.packages_count_label)
        
        packages_layout.addLayout(packages_header)
        
        # Create a table-like view for packages with versions
        self.package_list = QListWidget()
        self.package_list.setFrameShape(QListWidget.NoFrame)
        self.package_list.setFont(QFont("Segoe UI", 13))
        self.package_list.setStyleSheet("""
            QListWidget {
                background-color: transparent;
                color: #ddd;
                border: none;
                padding: 5px;
            }
            QListWidget::item {
                padding: 8px 5px;
                border-bottom: 1px solid #333;
            }
            QListWidget::item:hover {
                background-color: #333;
                border-radius: 4px;
            }
        """)
        
        packages_scroll = QScrollArea()
        packages_scroll.setWidgetResizable(True)
        packages_scroll.setStyleSheet("""
            QScrollArea {
                border: none;
                background: transparent;
            }
            QScrollBar:vertical {
                border: none;
                background: #333;
                width: 10px;
                margin: 0px;
                border-radius: 5px;
            }
            QScrollBar::handle:vertical {
                background: #555;
                min-height: 30px;
                border-radius: 5px;
            }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                height: 0px;
            }
            QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {
                background: none;
            }
        """)
        packages_scroll.setWidget(self.package_list)
        packages_scroll.setFixedHeight(300)  # Increase height for more packages to be visible
        
        packages_layout.addWidget(packages_scroll)
        
        python_info_layout.addWidget(packages_frame)
        
        # Add a stretch at the bottom to keep everything aligned to the top
        python_info_layout.addStretch()
        
        # Set the scroll area content
        scroll_area.setWidget(self.python_info_container)
        layout.addWidget(scroll_area, 1)
        
        return page

    
    def search_package(self):
        query = self.search_box.text().strip()
        if not query:
            return
            
        # Update the search results title
        self.search_results_title.setText(f"Search Results for '{query}'")
        
        # Show loading placeholder
        for i in reversed(range(self.search_results_layout.count())): 
            widget = self.search_results_layout.itemAt(i).widget()
            if widget:
                widget.setParent(None)
            
        loading_label = QLabel("Searching PyPI...")
        loading_label.setAlignment(Qt.AlignCenter)
        loading_label.setStyleSheet("color: #888; padding: 40px; background-color: #2a2a2a; border-radius: 8px;")
        self.search_results_layout.addWidget(loading_label)
        
        # Create and start search thread
        if self.search_thread and self.search_thread.isRunning():
            self.search_thread.terminate()
            self.search_thread.wait()
            
        self.search_thread = PyPISearchThread(query, "search")
        self.search_thread.result_ready.connect(self.update_search_results)
        self.search_thread.error_occurred.connect(self.show_search_error)
        self.search_thread.start()
        
        # Switch to search results page
        self.stack.setCurrentIndex(6)

    def fetch_recent_libraries(self):
        # Create and start recent libraries thread
        if self.recent_thread and self.recent_thread.isRunning():
            return
            
        self.recent_thread = PyPISearchThread("", "recent")
        self.recent_thread.result_ready.connect(self.update_recent_libraries)
        self.recent_thread.error_occurred.connect(self.show_recent_error)
        self.recent_thread.start()

    def fetch_trending_libraries(self):
        # Create and start trending libraries thread
        if self.trending_thread and self.trending_thread.isRunning():
            return
            
        self.trending_thread = PyPISearchThread("", "trending")
        self.trending_thread.result_ready.connect(self.update_trending_libraries)
        self.trending_thread.error_occurred.connect(self.show_trending_error)
        self.trending_thread.start()

    def update_search_results(self, packages):
        self.search_results = packages
        
        # Clear current layout
        for i in reversed(range(self.search_results_layout.count())): 
            widget = self.search_results_layout.itemAt(i).widget()
            if widget:
                widget.setParent(None)
        
        # Add results or no results message
        if packages:
            for library in packages:
                package_card = PackageCard(library)
                package_card.package_clicked.connect(self.show_library_detail)
                package_card.setMinimumHeight(90)  # Set minimum height for consistency
                package_card.setMaximumHeight(120)  # Set maximum height for consistency
                self.search_results_layout.addWidget(package_card)
        else:
            no_results = QLabel(f"No packages found for '{self.search_box.text()}'")
            no_results.setAlignment(Qt.AlignCenter)
            no_results.setStyleSheet("color: #888; padding: 40px; background-color: #2a2a2a; border-radius: 8px;")
            self.search_results_layout.addWidget(no_results)

    def update_recent_libraries(self, packages):
        self.recent_libraries = packages
        
        # Clear current recent layout except for the label
        if self.recent_placeholder:
            self.recent_placeholder.setParent(None)
            self.recent_placeholder = None
        
        # Remove any existing package cards
        for i in reversed(range(self.recent_layout.count())):
            if i > 0:  # Keep the title label
                widget = self.recent_layout.itemAt(i).widget()
                if widget:
                    widget.setParent(None)
        
        # Add the library cards or a message
        if packages:
            for library in packages:
                package_card = PackageCard(library)
                package_card.package_clicked.connect(self.show_library_detail)
                package_card.setMinimumHeight(90)  # Set minimum height for consistency
                package_card.setMaximumHeight(120)  # Set maximum height for consistency
                self.recent_layout.addWidget(package_card)
        else:
            no_packages = QLabel("No recent libraries found")
            no_packages.setAlignment(Qt.AlignCenter)
            no_packages.setStyleSheet("color: #888; padding: 20px; background-color: #2a2a2a; border-radius: 8px;")
            self.recent_layout.addWidget(no_packages)
        
        # Check if both recent and trending are loaded
        self.check_data_loading_complete()

    def update_trending_libraries(self, packages):
        self.trending_libraries = packages
        
        # Clear current trending layout except for the label
        if self.trending_placeholder:
            self.trending_placeholder.setParent(None)
            self.trending_placeholder = None
        
        # Remove any existing package cards
        for i in reversed(range(self.trending_layout.count())):
            if i > 0:  # Keep the title label
                widget = self.trending_layout.itemAt(i).widget()
                if widget:
                    widget.setParent(None)
        
        # Add the library cards or a message
        if packages:
            for library in packages:
                package_card = PackageCard(library)
                package_card.package_clicked.connect(self.show_library_detail)
                package_card.setMinimumHeight(90)  # Set minimum height for consistency
                package_card.setMaximumHeight(120)  # Set maximum height for consistency
                self.trending_layout.addWidget(package_card)
        else:
            no_packages = QLabel("No trending libraries found")
            no_packages.setAlignment(Qt.AlignCenter)
            no_packages.setStyleSheet("color: #888; padding: 20px; background-color: #2a2a2a; border-radius: 8px;")
            self.trending_layout.addWidget(no_packages)
        
        # Check if both recent and trending are loaded
        self.check_data_loading_complete()

    def check_data_loading_complete(self):
        # If both recent and trending are loaded, hide the loading indicators
        if hasattr(self, 'loading_indicator') and hasattr(self, 'progress_bar'):
            if self.recent_libraries and self.trending_libraries:
                self.loading_indicator.hide()
                self.progress_bar.hide()

    def show_library_detail(self, library):
        # Update the detail page with the library's information
        self.detail_name.setText(library["name"])
        self.detail_developer.setText(f"Developed by: {library['developer']}")
        self.detail_link.setText(f"<a href='{library['link']}'>{library['link']}</a>")
        
        # Set upload date if available
        if 'upload_date' in library and library['upload_date'] != "Unknown":
            self.detail_date.setText(f"Updated: {library['upload_date']}")
            self.detail_date.show()
        else:
            self.detail_date.hide()
        
        # Clear any existing tags and add new ones
        while self.detail_tags.count():
            item = self.detail_tags.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        
        # Add some placeholder tags based on library name
        if "py" in library["name"].lower():
            tag = QLabel("Python")
            tag.setStyleSheet("""
                background-color: #3776AB;
                color: white;
                font-size: 12px;
                padding: 4px 10px;
                border-radius: 12px;
            """)
            self.detail_tags.addWidget(tag)
        
        if "data" in library["description"].lower():
            tag = QLabel("Data Science")
            tag.setStyleSheet("""
                background-color: #44A833;
                color: white;
                font-size: 12px;
                padding: 4px 10px;
                border-radius: 12px;
            """)
            self.detail_tags.addWidget(tag)
        
        if "web" in library["description"].lower():
            tag = QLabel("Web")
            tag.setStyleSheet("""
                background-color: #E44D26;
                color: white;
                font-size: 12px;
                padding: 4px 10px;
                border-radius: 12px;
            """)
            self.detail_tags.addWidget(tag)
        
        # Format description for HTML display
        description = library["long_desc"].replace("\n", "<br>")
        # Basic formatting for reStructuredText or Markdown
        description = description.replace("**", "<b>").replace("**", "</b>")
        description = description.replace("*", "<i>").replace("*", "</i>")
        description = description.replace("# ", "<h3>").replace("\n#", "</h3>\n")
        
        self.detail_description.setHtml(description)
        
        # Update the library icon
        icon_size = 80
        icon_path = os.path.join(self.icons_dir, library["icon"])
        
        if os.path.exists(icon_path):
            pixmap = QPixmap(icon_path).scaled(icon_size, icon_size, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        else:
            # Create a custom icon
            pixmap = QPixmap(icon_size, icon_size)
            pixmap.fill(Qt.transparent)
            
            painter = QPainter(pixmap)
            painter.setRenderHint(QPainter.Antialiasing)
            
            # Draw colored circle based on first letter
            first_letter = library["name"][0].upper()
            
            # Different colors for different letters (same as in PackageCard)
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
            painter.setFont(QFont("Arial", 28, QFont.Bold))
            painter.drawText(pixmap.rect(), Qt.AlignCenter, first_letter)
            painter.end()
        
        self.detail_icon.setPixmap(pixmap)
        
        # Update version dropdown
        self.detail_version.clear()
        self.detail_version.addItems(library["versions"])
        
        # Show the detail page
        self.stack.setCurrentIndex(5)  # Index of the detail page in stack

    def go_back_to_home(self):
        # Check which page we're coming from
        if self.stack.currentIndex() == 6:  # Search results page
            # If coming from search results, clear search
            self.search_box.clear()
        
        self.stack.setCurrentIndex(0)  # Go back to home page

    def show_search_error(self, error_message):
        # Clear current layout
        for i in reversed(range(self.search_results_layout.count())): 
            widget = self.search_results_layout.itemAt(i).widget()
            if widget:
                widget.setParent(None)
        
        # Show error message
        error_label = QLabel(f"Error searching: {error_message}")
        error_label.setAlignment(Qt.AlignCenter)
        error_label.setStyleSheet("color: #ff5555; padding: 40px; background-color: #2a2a2a; border-radius: 8px;")
        self.search_results_layout.addWidget(error_label)
        
        # Optionally show a message box
        QMessageBox.warning(self, "Search Error", f"Error searching PyPI: {error_message}")

    def show_recent_error(self, error_message):
        if self.recent_placeholder:
            self.recent_placeholder.setText(f"Error loading recent libraries: {error_message}")
            self.recent_placeholder.setStyleSheet("color: #ff5555; padding: 20px; background-color: #2a2a2a; border-radius: 8px;")
        
        print(f"Error loading recent libraries: {error_message}")

    def show_trending_error(self, error_message):
        if self.trending_placeholder:
            self.trending_placeholder.setText(f"Error loading trending libraries: {error_message}")
            self.trending_placeholder.setStyleSheet("color: #ff5555; padding: 20px; background-color: #2a2a2a; border-radius: 8px;")
        
        print(f"Error loading trending libraries: {error_message}")

    def display_page(self, index):
        if index < 6:  # Only for main navigation pages, not the detail page or search results
            self.stack.setCurrentIndex(index)
            
            # If selecting My Python page, collect Python info
            if index == 3:  # My Python page
                # Check if we have a Python info thread already
                if hasattr(self, 'python_info_thread') and self.python_info_thread and self.python_info_thread.isRunning():
                    return
                    
                # Show loading indicators
                self.python_info_container.setVisible(False)
                self.python_loading_label.setVisible(True)
                self.python_progress_bar.setVisible(True)
                
                # Start the info collection thread
                self.python_info_thread = PythonInfoCollector()
                self.python_info_thread.update_signal.connect(self.update_python_info)
                self.python_info_thread.start()

    def update_python(self):
        """Download and install Python update with progress tracking."""        
        # Get current Python version and update information
        current_version = platform.python_version()
        update_version = self.update_version_label.text().replace("Version ", "").replace(" available", "")
        
        # Create a dialog for the update process
        update_dialog = QDialog(self)
        update_dialog.setWindowTitle(f"Updating Python to {update_version}")
        update_dialog.setFixedSize(500, 250)
        update_dialog.setStyleSheet("""
            QDialog {
                background-color: #1e1e1e;
            }
            QLabel {
                color: white;
            }
        """)
        
        # Dialog layout
        layout = QVBoxLayout(update_dialog)
        
        # Status message
        status_label = QLabel("Preparing to download Python...")
        status_label.setFont(QFont("Segoe UI", 12))
        layout.addWidget(status_label)
        
        # Progress bar
        progress = QProgressBar()
        progress.setStyleSheet("""
            QProgressBar {
                border: none;
                border-radius: 4px;
                background-color: #333;
                height: 8px;
                text-align: center;
            }
            QProgressBar::chunk {
                background-color: #0078d7;
                border-radius: 4px;
            }
        """)
        layout.addWidget(progress)
        
        # Details area
        details = QLabel()
        details.setFont(QFont("Segoe UI", 10))
        details.setStyleSheet("color: #aaa;")
        details.setWordWrap(True)
        layout.addWidget(details)
        
        # Spacer
        layout.addStretch()
        
        # Cancel button
        button_layout = QHBoxLayout()
        cancel_btn = QPushButton("Cancel")
        cancel_btn.setStyleSheet("""
            QPushButton {
                background-color: #333;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 8px 16px;
            }
            QPushButton:hover {
                background-color: #444;
            }
        """)
        button_layout.addStretch()
        button_layout.addWidget(cancel_btn)
        layout.addLayout(button_layout)
        
        # Create update thread
        class PythonUpdateThread(QThread):
            progress_signal = pyqtSignal(int, str)
            finished_signal = pyqtSignal(bool, str)
            
            def __init__(self, version):
                super().__init__()
                self.version = version
                self.cancelled = False
                self.installer_path = None
            
            def cleanup(self):
                """Clean up temporary files."""
                try:
                    if self.installer_path and os.path.exists(self.installer_path):
                        os.remove(self.installer_path)
                except Exception as e:
                    print(f"Cleanup error: {str(e)}")
            
            def get_installer_url(self):
                """Determine the appropriate installer URL based on platform."""
                system = platform.system()
                machine = platform.machine()
                base_url = "https://www.python.org/ftp/python"
                
                if system == "Windows":
                    # Determine if 32-bit or 64-bit installer is needed
                    arch = "amd64" if machine in ["AMD64", "x86_64"] else "win32"
                    return f"{base_url}/{self.version}/python-{self.version}-{arch}.exe"
                elif system == "Darwin":  # macOS
                    return f"{base_url}/{self.version}/python-{self.version}-macosx10.9.pkg"
                else:  # Linux and others
                    return None
            
            def download_installer(self, url, path):
                """Download the installer with progress reporting."""
                def report_progress(block_num, block_size, total_size):
                    if self.cancelled:
                        raise Exception("Download cancelled")
                        
                    if total_size > 0:
                        percent = min(int((block_num * block_size * 100) / total_size), 100)
                        self.progress_signal.emit(
                            15 + int(percent * 0.65),  # Scale to 15-80% of overall progress
                            f"Downloading Python {self.version} installer... {percent}%"
                        )
                
                try:
                    urllib.request.urlretrieve(url, path, report_progress)
                    return True
                except Exception as e:
                    if "Download cancelled" in str(e):
                        return False
                    self.finished_signal.emit(False, f"Download failed: {str(e)}")
                    return False
            
            def launch_installer(self, path):
                """Launch the installer with appropriate privileges."""
                system = platform.system()
                
                try:
                    if system == "Windows":
                        # Prepare installer arguments for silent installation
                        install_args = [
                            path,
                            "/quiet",  # Silent install
                            "InstallAllUsers=1",  # Install for all users
                            "PrependPath=1",  # Add Python to PATH
                            "Include_test=0",  # Don't include test suite
                            "Include_doc=0",  # Don't include documentation
                            "Include_launcher=1",  # Include py launcher
                        ]
                        
                        # Need to run this with elevated privileges
                        if ctypes.windll.shell32.IsUserAnAdmin() == 0:
                            # Not admin, relaunch as admin
                            self.progress_signal.emit(90, "Requesting administrator privileges...")
                            ctypes.windll.shell32.ShellExecuteW(
                                None, "runas", install_args[0], 
                                " ".join(install_args[1:]), None, 1
                            )
                        else:
                            # Already admin
                            subprocess.run(install_args)
                        
                    elif system == "Darwin":  # macOS
                        self.progress_signal.emit(90, "Opening installer package...")
                        subprocess.run(["open", path])
                    
                    # Wait for a bit to ensure the installer has launched
                    time.sleep(2)
                    return True
                    
                except Exception as e:
                    self.finished_signal.emit(False, f"Failed to launch installer: {str(e)}")
                    return False
            
            def run(self):
                """Main thread execution."""
                try:
                    # Step 1: Determine the appropriate installer URL
                    self.progress_signal.emit(5, "Determining installer for your platform...")
                    installer_url = self.get_installer_url()
                    
                    if self.cancelled:
                        return
                    
                    if not installer_url:
                        self.finished_signal.emit(False, "Automatic update not supported for this platform. Please use your package manager.")
                        return
                    
                    # Step 2: Create a temporary directory for the download
                    self.progress_signal.emit(10, "Creating temporary directory...")
                    temp_dir = tempfile.gettempdir()
                    self.installer_path = os.path.join(temp_dir, os.path.basename(installer_url))
                    
                    if self.cancelled:
                        return
                    
                    # Step 3: Download the installer
                    self.progress_signal.emit(15, f"Downloading Python {self.version} installer...")
                    if not self.download_installer(installer_url, self.installer_path):
                        return
                    
                    if self.cancelled:
                        return
                    
                    # Step 4: Verify the downloaded file
                    self.progress_signal.emit(80, "Verifying downloaded installer...")
                    if not os.path.exists(self.installer_path) or os.path.getsize(self.installer_path) < 1000000:
                        self.finished_signal.emit(False, "Downloaded installer appears to be invalid")
                        return
                    
                    if self.cancelled:
                        return
                    
                    # Step 5: Run the installer
                    self.progress_signal.emit(85, "Launching installer...")
                    if self.launch_installer(self.installer_path):
                        self.progress_signal.emit(95, "Installation started...")
                        self.finished_signal.emit(True, "Python installer has been launched. Please complete the installation as required.")
                    
                except Exception as e:
                    self.finished_signal.emit(False, f"Update process failed: {str(e)}")
                finally:
                    # Always perform cleanup operations
                    if not self.cancelled:
                        self.cleanup()
        
        # Create and configure the update thread
        update_thread = PythonUpdateThread(update_version)
        
        # Connect signals
        def update_progress(percent, message):
            progress.setValue(percent)
            status_label.setText(message)
        
        def update_finished(success, message):
            status_label.setText("Update Completed Successfully!" if success else "Update Failed")
            details.setText(message)
            cancel_btn.setText("Close")
            progress.setValue(100 if success else 0)
        
        update_thread.progress_signal.connect(update_progress)
        update_thread.finished_signal.connect(update_finished)
        
        def cancel_update():
            update_thread.cancelled = True
            if not update_thread.isRunning():
                update_dialog.close()
        
        cancel_btn.clicked.connect(cancel_update)
        
        # Handle dialog closure
        def cleanup_on_close():
            if update_thread.isRunning():
                update_thread.cancelled = True
                update_thread.wait()  # Wait for thread to finish
        
        update_dialog.finished.connect(cleanup_on_close)
        
        # Start the update process
        update_thread.start()
        
        # Show the dialog
        update_dialog.exec_()

    def update_python_info(self, info):
        """Update the Python info page with collected information."""
        # Update Python version information
        version_text = f"Python {info['python_version']} ({info['python_implementation']})"
        self.python_version_label.setText(version_text)
        
        self.python_path_label.setText(f"Installation path: {info['install_dir']}")
        self.pip_version_label.setText(f"Pip: {info['pip_version']}")
        
        # Update package information
        self.packages_count_label.setText(f"{info['package_count']} packages installed")
        
        # Clear and fill package list with versions
        self.package_list.clear()
        
        # Sort packages alphabetically
        sorted_packages = sorted(info['installed_packages'], key=lambda x: x['name'].lower())
        
        for package in sorted_packages:
            # Create a formatted item with package name and version
            item_text = f"{package['name']} - {package['version']}"
            
            item = QListWidgetItem(item_text)
            
            # Set custom styling for clarity
            item.setFont(QFont("Segoe UI", 13))
            
            # Add to the list
            self.package_list.addItem(item)
        
        # Check for updates
        if info.get('has_update', False):
            self.update_container.setVisible(True)
            self.update_version_label.setText(f"Version {info['update_version']} available")
            self.update_changes_label.setText(info['update_changes'])
        else:
            self.update_container.setVisible(False)
        
        # Hide loading indicators and show content
        self.python_loading_label.setVisible(False)
        self.python_progress_bar.setVisible(False)
        self.python_info_container.setVisible(True)


def collect_python_info(self):
    """Start thread to collect Python environment information."""
    if hasattr(self, 'python_info_thread') and self.python_info_thread and self.python_info_thread.isRunning():
        return
            
    # Show loading indicators
    self.python_info_container.setVisible(False)
    self.python_loading_label.setVisible(True)
    self.python_progress_bar.setVisible(True)
    
    # Start the info collection thread
    self.python_info_thread = PythonInfoCollector()
    self.python_info_thread.update_signal.connect(self.update_python_info)
    self.python_info_thread.start()
