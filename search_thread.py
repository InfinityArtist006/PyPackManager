import urllib.request
import json
import random
from datetime import datetime, timedelta
from PyQt5.QtCore import QThread, pyqtSignal

class PyPISearchThread(QThread):
    result_ready = pyqtSignal(list)
    error_occurred = pyqtSignal(str)
    
    def __init__(self, query, mode="search"):
        super().__init__()
        self.query = query
        self.mode = mode  # "search", "recent", "trending"
        
    def run(self):
        try:
            result = []
            
            if self.mode == "search" and self.query:
                # Search for a specific package
                url = f"https://pypi.org/pypi/{self.query}/json"
                try:
                    response = urllib.request.urlopen(url)
                    if response.getcode() == 200:
                        data = json.loads(response.read().decode())
                        if "info" in data:
                            # Single package found
                            result.append(self.process_package_data(data))
                except urllib.error.HTTPError as e:
                    if e.code == 404:
                        # Try the search endpoint instead for partial matches
                        self.search_multiple_packages(self.query, result)
                    else:
                        raise e
            
            elif self.mode == "recent":
                # Fetch recently updated packages
                self.fetch_recent_packages(result)
                
            elif self.mode == "trending":
                # Fetch trending packages based on downloads
                self.fetch_trending_packages(result)
                
            self.result_ready.emit(result)
            
        except Exception as e:
            self.error_occurred.emit(f"Error: {str(e)}")
    
    def process_package_data(self, data):
        info = data["info"]
        releases = data["releases"]
        versions = list(releases.keys())
        versions.sort(reverse=True)
        
        # Extract upload date of the latest version if available
        upload_date = "Unknown"
        if versions and versions[0] in releases and releases[versions[0]]:
            try:
                # Format could be like "2022-01-28T09:47:12"
                upload_time = releases[versions[0]][0]["upload_time"]
                # Convert to a more readable format
                dt = datetime.fromisoformat(upload_time.replace("Z", "+00:00"))
                upload_date = dt.strftime("%Y-%m-%d")
            except (KeyError, IndexError, ValueError):
                pass
        
        return {
            "name": info["name"],
            "description": info["summary"] if info["summary"] else "No description available",
            "versions": versions[:5] if versions else ["N/A"],
            "developer": info.get("author", "Unknown"),
            "icon": f"{info['name'].lower()}.png",
            "link": info.get("project_url", f"https://pypi.org/project/{info['name']}/"),
            "long_desc": info.get("description", "No detailed description available"),
            "upload_date": upload_date
        }
    
    def search_multiple_packages(self, query, result_list):
        # Use search to find multiple packages
        # For demo purposes, just get some popular packages that match
        popular_packages = [
            "numpy", "pandas", "requests", "tensorflow", "pytorch", 
            "django", "flask", "scikit-learn", "matplotlib", "scipy",
            "pillow", "sqlalchemy", "beautifulsoup4", "fastapi", "httpx",
            "transformers", "torch", "seaborn", "pytest", "black",
            "pylance", "pyright", "flake8", "mypy", "isort"
        ]
        
        matching_packages = [pkg for pkg in popular_packages if query.lower() in pkg.lower()]
        
        for package_name in matching_packages[:10]:  # Limit to 10 results
            try:
                url = f"https://pypi.org/pypi/{package_name}/json"
                response = urllib.request.urlopen(url)
                if response.getcode() == 200:
                    data = json.loads(response.read().decode())
                    result_list.append(self.process_package_data(data))
            except Exception:
                pass  # Skip any packages that fail to load
    
    def fetch_recent_packages(self, result_list):
        # In a real app, you would use a proper API for this
        # This is a simplified approach
        
        packages = [
            "numpy", "pandas", "requests", "tensorflow", "pytorch", 
            "django", "flask", "scikit-learn", "matplotlib", "scipy",
            "pillow", "sqlalchemy", "beautifulsoup4", "fastapi", "httpx"
        ]
        
        random.shuffle(packages)  # Randomize for demonstration
        
        for package_name in packages[:10]:  # Limit to 10
            try:
                url = f"https://pypi.org/pypi/{package_name}/json"
                response = urllib.request.urlopen(url)
                if response.getcode() == 200:
                    data = json.loads(response.read().decode())
                    result_list.append(self.process_package_data(data))
            except Exception:
                pass  # Skip any packages that fail to load
        
        # Sort by upload date (newest first)
        result_list.sort(key=lambda x: x["upload_date"] if x["upload_date"] != "Unknown" else "9999-99-99", reverse=True)
    
    def fetch_trending_packages(self, result_list):
        # In a real app, you would use download stats or GitHub stars
        # This is a simplified approach
        
        trending_packages = [
            "fastapi", "pydantic", "langchain", "gradio", "streamlit", 
            "transformers", "ray", "pytorch-lightning", "polars", "httpx",
            "pylance", "pyright", "black", "ruff", "mypy"
        ]
        
        for package_name in trending_packages[:10]:
            try:
                url = f"https://pypi.org/pypi/{package_name}/json"
                response = urllib.request.urlopen(url)
                if response.getcode() == 200:
                    data = json.loads(response.read().decode())
                    result_list.append(self.process_package_data(data))
            except Exception:
                pass  # Skip any packages that fail to load
