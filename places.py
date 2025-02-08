import sys
import os
import requests
import pandas as pd
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QLabel, QLineEdit, QPushButton,
    QCheckBox, QListWidget, QMessageBox, QHBoxLayout, QListWidgetItem,
    QComboBox, QInputDialog
)

# Google Places Text Search endpoint for city searching
TEXTSEARCH_URL = "https://maps.googleapis.com/maps/api/place/textsearch/json"
# Google Places Nearby Search endpoint for searching POIs
NEARBY_URL = "https://maps.googleapis.com/maps/api/place/nearbysearch/json"

class MacOSPlacesApp(QWidget):
    def __init__(self):
        super().__init__()
        # Coordinates of the selected city
        self.center_lat = None
        self.center_lng = None
        self.results = []  # Will store place dictionaries, each with a 'Category' key
        self.selected_types = []
        self.api_key = None

        self.initUI()

        # Prompt user for API key each launch
        message = (
            "Enter your Google API Key:\n\n"
            "Google Places API must be enabled.\n\n"
            "You can create an API key at:\n"
            "https://console.cloud.google.com/google/maps-apis/credentials"
        )
        key, ok = QInputDialog.getText(
            self,
            "Google API Key",
            message
        )
        if not ok or not key.strip():
            QMessageBox.critical(
                self,
                "No API Key Provided",
                "Application will close without a valid API key."
            )
            sys.exit(0)
        self.api_key = key.strip()

    def initUI(self):
        layout = QVBoxLayout()

        # City Input
        self.city_label = QLabel("Enter a City:")
        self.city_input = QLineEdit()
        layout.addWidget(self.city_label)
        layout.addWidget(self.city_input)

        # Button to find city
        self.find_city_btn = QPushButton("Search City")
        self.find_city_btn.clicked.connect(self.search_city)
        layout.addWidget(self.find_city_btn)

        # List to display city results
        self.city_list_widget = QListWidget()
        self.city_list_widget.itemClicked.connect(self.select_city)
        layout.addWidget(self.city_list_widget)

        # Distance Selection
        self.distance_label = QLabel("Select Distance:")
        self.distance_dropdown = QComboBox()
        self.distance_dropdown.addItems([str(i) for i in range(1, 51)])

        self.unit_dropdown = QComboBox()
        self.unit_dropdown.addItems(["km", "mi"])

        distance_layout = QHBoxLayout()
        distance_layout.addWidget(self.distance_label)
        distance_layout.addWidget(self.distance_dropdown)
        distance_layout.addWidget(self.unit_dropdown)
        layout.addLayout(distance_layout)

        # Checkboxes for place types
        self.attractions_cb = QCheckBox("Attractions")
        self.hotels_cb = QCheckBox("Hotels")
        self.restaurants_cb = QCheckBox("Restaurants")
        layout.addWidget(self.attractions_cb)
        layout.addWidget(self.hotels_cb)
        layout.addWidget(self.restaurants_cb)

        # Button to fetch places
        self.search_btn = QPushButton("Search Places")
        self.search_btn.clicked.connect(self.fetch_places)
        layout.addWidget(self.search_btn)

        # List to display all place results (no 10 limit)
        self.list_widget = QListWidget()
        layout.addWidget(self.list_widget)

        # Buttons for CSV download
        buttons_layout = QHBoxLayout()

        self.download_btn = QPushButton("Download Selected CSV")
        self.download_btn.clicked.connect(self.download_csv)
        buttons_layout.addWidget(self.download_btn)

        self.download_all_btn = QPushButton("Download ALL CSV")
        self.download_all_btn.clicked.connect(self.download_all_csv)
        buttons_layout.addWidget(self.download_all_btn)

        layout.addLayout(buttons_layout)

        self.setLayout(layout)
        self.setWindowTitle("Places to CSV")
        self.resize(600, 600)

    def search_city(self):
        """Searches for a city by name and displays top results."""
        city_name = self.city_input.text().strip()
        if not city_name:
            QMessageBox.warning(self, "Input Error", "Please enter a city name.")
            return

        params = {
            "query": city_name,
            "key": self.api_key
        }
        try:
            response = requests.get(TEXTSEARCH_URL, params=params)
            response.raise_for_status()
            data = response.json()
        except requests.exceptions.RequestException as e:
            QMessageBox.critical(self, "API Error", f"Failed to search city: {str(e)}")
            return

        candidates = data.get("results", [])
        if not candidates:
            QMessageBox.information(self, "No Results", "No city found matching your query.")
            return

        self.city_list_widget.clear()
        for place in candidates:
            desc = place.get("formatted_address") or place.get("name", "Unknown")
            lat = place["geometry"]["location"].get("lat")
            lng = place["geometry"]["location"].get("lng")

            item = QListWidgetItem(desc)
            item.setData(Qt.ItemDataRole.UserRole, (lat, lng))
            self.city_list_widget.addItem(item)

    def select_city(self, item):
        coords = item.data(Qt.ItemDataRole.UserRole)
        if coords:
            self.center_lat, self.center_lng = coords
            QMessageBox.information(
                self,
                "City Selected",
                f"lat={self.center_lat}, lng={self.center_lng}"
            )

    def fetch_places(self):
        """Fetch places of interest near the selected city center."""
        if self.center_lat is None or self.center_lng is None:
            QMessageBox.warning(self, "No City Selected", "Please search and select a city first.")
            return

        self.selected_types = []
        if self.attractions_cb.isChecked():
            self.selected_types.append("tourist_attraction")
        if self.hotels_cb.isChecked():
            self.selected_types.append("lodging")
        if self.restaurants_cb.isChecked():
            self.selected_types.append("restaurant")

        if not self.selected_types:
            QMessageBox.warning(self, "Input Error", "Please select at least one category.")
            return

        # Convert distance to meters
        distance = int(self.distance_dropdown.currentText())
        unit = self.unit_dropdown.currentText()
        radius_meters = distance * 1000 if unit == "km" else distance * 1609

        # Clear old results
        self.results.clear()
        self.list_widget.clear()

        # For each selected type, fetch and store 'Category' in place
        for t in self.selected_types:
            params = {
                "location": f"{self.center_lat},{self.center_lng}",
                "radius": radius_meters,
                "type": t,
                "key": self.api_key
            }
            try:
                response = requests.get(NEARBY_URL, params=params)
                response.raise_for_status()
                data = response.json()
                # Add 'Category' field to each place
                for p in data.get("results", []):
                    p["Category"] = self._category_label(t)
                    self.results.append(p)
            except requests.exceptions.RequestException as e:
                QMessageBox.critical(self, "API Error", f"Failed to fetch places: {str(e)}")
                return

        if not self.results:
            QMessageBox.information(self, "No Results", "No places found for the given criteria.")
            return

        # Display all results (no 10 limit)
        for place in self.results:
            name = place.get("name", "Unknown")
            address = place.get("vicinity", "N/A")
            item = QListWidgetItem(f"{name} - {address}")
            item.setCheckState(Qt.CheckState.Unchecked)
            self.list_widget.addItem(item)

    def _category_label(self, google_type):
        """Map the Google type to a user-friendly category label."""
        # google_type is e.g. 'tourist_attraction', 'lodging', 'restaurant'
        if google_type == "tourist_attraction":
            return "Attractions"
        elif google_type == "lodging":
            return "Hotels"
        elif google_type == "restaurant":
            return "Restaurants"
        return google_type

    def download_csv(self):
        """Downloads a CSV file of selected places, including Category."""
        selected_places = []
        for i in range(self.list_widget.count()):
            item = self.list_widget.item(i)
            if item.checkState() == Qt.CheckState.Checked:
                selected_place = self.results[i]
                selected_places.append({
                    "Name": selected_place.get("name", "Unknown"),
                    "Address": selected_place.get("vicinity", "N/A"),
                    "Latitude": selected_place.get("geometry", {}).get("location", {}).get("lat"),
                    "Longitude": selected_place.get("geometry", {}).get("location", {}).get("lng"),
                    "Category": selected_place.get("Category", "")
                })

        if not selected_places:
            QMessageBox.warning(self, "No Selection", "Please select at least one place.")
            return

        csv_path = self._csv_path("selected_places.csv")
        try:
            df = pd.DataFrame(selected_places)
            df.to_csv(csv_path, index=False)
            QMessageBox.information(
                self,
                "Success",
                f"CSV file downloaded successfully.\nSaved at: {csv_path}"
            )
        except Exception as e:
            QMessageBox.critical(
                self,
                "File Error",
                f"Could not write CSV:\n{str(e)}"
            )

    def download_all_csv(self):
        """Downloads a CSV file of ALL places, ignoring checkbox selections."""
        if not self.results:
            QMessageBox.warning(self, "No Places", "Please search for places first.")
            return

        # Convert all results, including Category
        all_places = []
        for p in self.results:
            all_places.append({
                "Name": p.get("name", "Unknown"),
                "Address": p.get("vicinity", "N/A"),
                "Latitude": p.get("geometry", {}).get("location", {}).get("lat"),
                "Longitude": p.get("geometry", {}).get("location", {}).get("lng"),
                "Category": p.get("Category", "")
            })

        csv_path = self._csv_path("all_places.csv")
        try:
            df = pd.DataFrame(all_places)
            df.to_csv(csv_path, index=False)
            QMessageBox.information(
                self,
                "Success",
                f"All Places CSV downloaded.\nSaved at: {csv_path}"
            )
        except Exception as e:
            QMessageBox.critical(
                self,
                "File Error",
                f"Could not write CSV:\n{str(e)}"
            )

    def _csv_path(self, filename):
        """Create a path on Desktop for the given filename."""
        home_dir = os.path.expanduser("~")
        return os.path.join(home_dir, "Desktop", filename)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MacOSPlacesApp()
    window.show()
    sys.exit(app.exec())