# Places to CSV

This repository contains a **PyQt6** application that allows users to:
1. **Search for a city** via Google Places Text Search.
2. **Fetch places** around that city (attractions, hotels, restaurants) using Google Places Nearby Search.
3. **Select & Download** location information as CSV files, including the option to download all results or just selected ones.

## Requirements
- **Python 3.9+**
- **PyQt6** (for the GUI)
- **Requests** (for HTTP requests to Google APIs)
- **pandas** (for creating CSV files)

You will also need a **Google API Key** with **Google Places API** enabled.

## Dependencies
Install the following libraries:

```bash
pip install PyQt6 requests pandas
```

## Running the App
1. **Clone or download** this repo:
   ```bash
   git clone https://github.com/YOUR-USERNAME/places-to-csv.git
   cd places-to-csv
   ```
2. **Install dependencies** if not already installed:
   ```bash
   pip install PyQt6 requests pandas
   ```
3. **Run the script** from terminal:
   ```bash
   python places.py
   ```

## Usage Instructions
1. On startup, the application **prompts** for your Google API key. Enter a valid key or exit.
2. Type a city name in the **"Enter a City"** field and click **"Search City"**.
3. Select one of the returned city options. This sets the lat/lng for subsequent searches.
4. Choose a **distance** and **unit** (km or mi), then check at least one category (Attractions, Hotels, Restaurants).
5. Click **"Search Places"** to fetch places near the selected city.
6. Results appear in a list. You can:
   - **Check** specific rows and click **"Download Selected CSV"**
   - or click **"Download ALL CSV"** to export everything.

## Note on Google API Key
- Make sure **Places API** (and billing) is enabled on your Google Cloud project.
- The API key must be **active** and **unrestricted** or restricted to the relevant services.

## Example
```bash
python places.py
# Enter API key when prompted
# Enter City: Dubai
# Click "Search City", select the city.
# Set Distance: 5 km
# Check "Hotels"
# Click "Search Places"
# Select some or all results, then download as CSV.
```

## License
MIT License. Feel free to fork and modify.
