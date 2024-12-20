"""
Module to automatically retrieve Sentinel-2 data via OData of Copernicus freely, systematically and easily

Generating access token for OData
curl -s -X POST https://identity.dataspace.copernicus.eu/auth/realms/CDSE/protocol/openid-connect/token -H "Content-Type: application/x-www-form-urlencoded" -d "username=##username##" -d "password=##password##" -d "grant_type=password" -d "client_id=cdse-public"

This script generates an access token valid for 600 seconds and refresh token valid for 3600 seconds. For not choking the server, I did not use automatically refreshing refresh token within the code below. But it downloads for one hour just fine.
"""
client_secret = ####client password####
client_id = ####YOUR CLIENT ID HERE AS STRING####


access_token = "access token generated above from CLI"
refresh_token= "refresh token generated above from CLI"

import requests # Retrieves files/data from the internet/cloud/server to the local
import pandas as pd # better representation of what was filtered


# Since json request below contains WGS 84 lat/lon degree format, we provide the region of interest in lat lon separated with commas, this is, of course, put as an example, you need to change it for your case)
roi = POLYGON((34.49221 40.62057,34.49253 40.62053,34.49552 40.620456227)
              
# The following request was divided into lines to read it easily
"""
JSON Line 1-It requests the specific product collection, in this case SENTINEL-2
JSON Line 2-Specifically retrieves its atmospherically corrected L2A product in the next line
JSON Line 3-OData.CSC.Intersects filters the images within the area defined in this line's parentheses, SRID=4326 (Spatial Reference System Identifier) is lat lon WGS 84 (of course, it needs to be modified acc. to ROI)
JSON Line 4-The next attribute line chooses, among other options, 'cloudCover' attribute at sets it to values lower than 20
JSON Line 5,6 -The last two lines are for date filtering, and also order the date and retrieves only the top 200 from them
"""


json4 = requests.get("""https://catalogue.dataspace.copernicus.eu/odata/v1/Products?$filter=Collection/Name eq 'SENTINEL-2' and
                    Attributes/OData.CSC.StringAttribute/any(att:att/Name eq 'productType' and att/OData.CSC.StringAttribute/Value eq 'S2MSI2A') and
                    OData.CSC.Intersects(area=geography'SRID=4326;POLYGON((34.49221 40.62057,34.49253 40.62053,34.49552 40.62045))') and
                    Attributes/OData.CSC.DoubleAttribute/any(att:att/Name eq 'cloudCover' and att/OData.CSC.DoubleAttribute/Value lt 20.00) and
                    ContentDate/Start gt 2023-09-01T00:00:00.000 and
                    ContentDate/Start lt 2024-08-01T00:10:00.000&$orderby=ContentDate/Start&$top=200""").json()
                    
dfroi = pd.DataFrame.from_dict(json4['value']) # With this one can easily prints and look at the file names, dates to see what has been caught in the net

"""
Bulk downloading the filtered things
"""


import os # Operation System file saving-related works
import time # managing elapsed/remaining times
import hashlib
from tqdm import tqdm # Downloading progress bar for the accurate assessment of the situation

"""
The following lines of codes are for automatic access token refreshing
when access token expires after 600 seconds

refresh_access_token() function is the main function for this work.
"""


# Base URL and token endpoints
base_url = "https://download.dataspace.copernicus.eu/odata/v1/Products"
token_url = "https://identity.dataspace.copernicus.eu/auth/realms/CDSE/protocol/openid-connect/token"

# Tokens and credentials
refresh_token = refresh_token
client_id = "cdse-public"

# Directory to save downloaded files
output_dir = "##"
os.makedirs(output_dir, exist_ok=True)

## Function to refresh the access token
def refresh_access_token():
    payload = {
        "grant_type": "refresh_token",
        "refresh_token": refresh_token,
        "client_id": client_id,
    }
    response = requests.post(token_url, data=payload)
    if response.status_code == 200:
        return response.json().get("access_token")
    else:
        raise Exception(f"Failed to refresh token. {response.status_code}: {response.text}")




# Function to download a single file
def download_file_with_progress(url, output_path, session):
    """
    Function to download files, print out errors, and also the progress bar

    response: session.get() structure, with a 60-sec timeout to prevent server overload
              status_code 200 means success, 401 means access token expiration
                  any other codes originating from other problems are failure
              iter_content(chunk_size=8192) is specific chunk of 8192 KB in this work
                  the function controls this, and prevent excessive printing it on screen
                  and also trasnfer it to tqdm to estimate remaining time and file volume

    Function deals with the intermittent several seconds connection lost separately in "except"
    """
  
    try:
        response = session.get(url, stream=True, timeout=60)
        if response.status_code == 200:
            with open(output_path, "wb") as file, tqdm(
                total=int(response.headers.get("content-length", 0)),
                unit="B",
                unit_scale=True,
                desc=f"Downloading {os.path.basename(output_path)}",
            ) as progress_bar:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:  # Filter out keep-alive chunks
                        file.write(chunk)
                        progress_bar.update(len(chunk))
            return True  # Download successful
        elif response.status_code == 401:
            raise Exception("Access token expired.")
        else:
            print(f"Failed to download {url}. Status code: {response.status_code}")
            print(response.text)
            return False
    except requests.exceptions.ConnectionError as e:
        print(f"Connection lost: {e}. Retrying...")
        return False

# Create a session
session = requests.Session()

# Download loop
try:
    access_token = refresh_access_token()  # Get initial token
    session.headers.update({"Authorization": f"Bearer {access_token}"})
    for idx, row in dfroi.iterrows():
        product_id = row["Id"]
        output_path = os.path.join(output_dir, f"product_{product_id}.zip")
        # Skip if file exists
        if os.path.exists(output_path):
            print(f"File already exists: {output_path}. Skipping.")
            continue
        download_link = f"{base_url}({product_id})/$value"
        success = False
        while not success:  # Ensure successful download or retry
            try:
                print(f"Attempting to download: {download_link}")
                success = download_file_with_progress(download_link, output_path, session)
            except Exception as e:
                if "Access token expired" in str(e):
                    print("Access token expired. Refreshing token...")
                    access_token = refresh_access_token()
                    session.headers.update({"Authorization": f"Bearer {access_token}"})
                else:
                    print(f"Error downloading {download_link}: {e}")
                    break
        if not success:
            print(f"Skipping file after multiple attempts: {product_id}")
        else:
            print(f"Downloaded: {output_path}")
        time.sleep(9)  # Wait 9 seconds between downloads
except Exception as e:
    print(f"Critical error: {e}")


"""
A bonus part where a specific band or file are
retrieved from several differrent folders of .SAFE 
Sentinel-2 MSI folders (in this case 20m resampled Scene Classification - SCL
"""

import os
import shutil # a cool module to easily manage files/folders/directories

# Define source directory and destination folder
src_dir = "##"
dest_dir = "##"

# Ensure destination folder exists
os.makedirs(dest_dir, exist_ok=True)

# Walk through the directory and copy matching files
for root, _, files in os.walk(src_dir):
    for file in files:
        if file.endswith("SCL_20m.jp2"):
            shutil.copy(os.path.join(root, file), dest_dir)
