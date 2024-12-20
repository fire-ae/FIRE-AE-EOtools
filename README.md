# FIRE-AE-EOtools



# Sentinel-2 Data Retrieval Module

## Overview
This module provides an automated approach to retrieving Sentinel-2 data from the Copernicus Open Access Hub using OData. It enables systematic, efficient downloading of satellite data based on user-defined criteria.

## Key Features
- **Token Management**: Automated generation and handling of access tokens.
- **Region of Interest (ROI) Filtering**: Retrieves data based on specified ROI, cloud cover percentage, and date range.
- **Bulk Downloading**: Automates the download process with progress bars and retry mechanisms.
- **Post-Processing**: Filters specific files or bands from downloaded Sentinel-2 data.

## Prerequisites
- Python 3.x
- Modules: `requests`, `pandas`, `os`, `time`, `hashlib`, `tqdm`, `shutil`

Install the required Python packages using:
```bash
pip install requests pandas tqdm
```

## Authentication
Generate an access token and a refresh token using the following command:
```bash
curl -s -X POST https://identity.dataspace.copernicus.eu/auth/realms/CDSE/protocol/openid-connect/token \
-H "Content-Type: application/x-www-form-urlencoded" \
-d "username=##username##" -d "password=##password##" \
-d "grant_type=password" -d "client_id=cdse-public"
```
- **Access Token**: Valid for 600 seconds.
- **Refresh Token**: Valid for 3600 seconds.

Ensure that `client_id` and `client_secret` are correctly set in the script.

## Usage

### 1. Define ROI and Filters
Specify the ROI and filtering criteria in the script:
- **ROI**: Provide WGS 84 coordinates.
- **Cloud Cover**: Set a threshold for cloud cover.
- **Date Range**: Adjust `ContentDate` parameters as required.

### 2. Retrieve Data
Run the script to retrieve metadata for Sentinel-2 products:
```python
json4 = requests.get("https://catalogue.dataspace.copernicus.eu/odata/v1/Products?$filter=...parameters...").json()
```

### 3. Download Products
The script downloads filtered products with a progress bar, automatically refreshing access tokens as needed:
```python
success = download_file_with_progress(download_link, output_path, session)
```

### 4. Post-Processing
To extract specific bands or files (e.g., Scene Classification (SCL) 20m resolution):
```python
shutil.copy(os.path.join(root, file), dest_dir)
```

## Directory Structure
- **`output_dir`**: Directory where downloaded files are stored.
- **`dest_dir`**: Directory for post-processed files.

## Notes
- Avoid server overload by spacing downloads (e.g., 9 seconds between requests).
- Ensure proper error handling for expired tokens and connection issues.

## Example
```python
# Download loop
for idx, row in dfroi.iterrows():
    product_id = row["Id"]
    output_path = os.path.join(output_dir, f"product_{product_id}.zip")
    success = download_file_with_progress(download_link, output_path, session)
```

## License
This module is open-source and available under the MIT License. Contributions are welcome!
