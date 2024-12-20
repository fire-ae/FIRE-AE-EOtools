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


# Since json request below contains WGS 84 lat/lon degree format, we provide the region of interest in lat lon separated with commas
roi = POLYGON((34.49221 40.62057,34.49253 40.62053,34.49552 40.62045,34.49754 40.62067,34.49821 40.62089,34.50019 40.62122,34.50122 40.62127,34.50167 40.6213,34.50256 40.62138,34.5044 40.62158,34.50555 40.62157,34.50581 40.62156,34.50727 40.62213,34.50823 40.62242,34.50861 40.62248,34.50886 40.62254,34.50972 40.6227,34.51035 40.62274,34.51048 40.62274,34.51212 40.62298,34.51196 40.62298,34.5118 40.62301,34.51034 40.62339,34.51014 40.62344,34.50997 40.62344,34.50852 40.62388,34.50804 40.6244,34.50828 40.62489,34.50865 40.62529,34.50841 40.62656,34.50849 40.62674,34.50853 40.6269,34.50889 40.62744,34.50916 40.62792,34.50938 40.62834,34.50944 40.62854,34.50942 40.62874,34.50938 40.62884,34.50944 40.62902,34.50965 40.62947,34.50962 40.62962,34.50967 40.62977,34.50963 40.63002,34.50949 40.63022,34.50934 40.63035,34.50896 40.63044,34.50878 40.63061,34.50825 40.6312,34.50856 40.63147,34.50926 40.63171,34.50961 40.63178,34.51011 40.63198,34.51024 40.63202,34.51056 40.63263,34.51085 40.63325,34.51091 40.63368,34.51094 40.63369,34.5111 40.63421,34.51143 40.63517,34.51121 40.63558,34.51077 40.63614,34.5106 40.63627,34.51017 40.6361,34.50987 40.63585,34.50982 40.63604,34.50916 40.63586,34.50905 40.63624,34.50881 40.63674,34.50918 40.637,34.50948 40.63727,34.50889 40.6379,34.50803 40.63867,34.50741 40.63946,34.50718 40.63991,34.50676 40.64086,34.50665 40.64097,34.5064 40.64113,34.50612 40.64122,34.50598 40.6415,34.5052 40.64112,34.50445 40.64053,34.50355 40.6404,34.50278 40.64006,34.50234 40.63987,34.50212 40.63978,34.50192 40.63968,34.50114 40.63931,34.50072 40.63912,34.50031 40.63893,34.49976 40.63843,34.49933 40.63802,34.49911 40.63781,34.49894 40.63763,34.49782 40.63635,34.49755 40.63607,34.4973 40.63583,34.49687 40.6355,34.49625 40.63496,34.49614 40.63486,34.49395 40.63369,34.49288 40.63304,34.49144 40.63203,34.49052 40.63128,34.48949 40.63033,34.48947 40.63006,34.48966 40.62917,34.48999 40.62838,34.48993 40.62813,34.48987 40.62805,34.48992 40.62762,34.48995 40.62738,34.48982 40.62701,34.48983 40.62685,34.49002 40.62634,34.48999 40.62626,34.48985 40.62612,34.48987 40.62568,34.48967 40.62549,34.48961 40.62535,34.48972 40.62513,34.4898 40.62471,34.48978 40.6246,34.48958 40.62426,34.48931 40.62412,34.48927 40.62398,34.4891 40.62377,34.48907 40.62364,34.4892 40.62345,34.48913 40.62324,34.48904 40.6229,34.48911 40.62267,34.48889 40.62243,34.4888 40.6223,34.48879 40.6222,34.48893 40.62203,34.48869 40.62163,34.48839 40.62145,34.48821 40.62127,34.48806 40.62118,34.48798 40.62116,34.48832 40.62048,34.48954 40.62071,34.4902 40.62075,34.49105 40.62069,34.49221 40.62057))

# The following request was divided into lines to read it easily
"""
JSON Line 1-It requests the specific product collection, in this case SENTINEL-2
JSON Line 2-Specifically retrieves its atmospherically corrected L2A product in the next line
JSON Line 3-OData.CSC.Intersects filters the images within the area defined in this line's parentheses, SRID=4326 (Spatial Reference System Identifier) is lat lon WGS 84
JSON Line 4-The next attribute line chooses, among other options, 'cloudCover' attribute at sets it to values lower than 20
JSON Line 5,6 -The last two lines are for date filtering, and also order the date and retrieves only the top 200 from them
"""


json4 = requests.get("""https://catalogue.dataspace.copernicus.eu/odata/v1/Products?$filter=Collection/Name eq 'SENTINEL-2' and
                    Attributes/OData.CSC.StringAttribute/any(att:att/Name eq 'productType' and att/OData.CSC.StringAttribute/Value eq 'S2MSI2A') and
                    OData.CSC.Intersects(area=geography'SRID=4326;POLYGON((34.49221 40.62057,34.49253 40.62053,34.49552 40.62045,34.49754 40.62067,34.49821 40.62089,34.50019 40.62122,34.50122 40.62127,34.50167 40.6213,34.50256 40.62138,34.5044 40.62158,34.50555 40.62157,34.50581 40.62156,34.50727 40.62213,34.50823 40.62242,34.50861 40.62248,34.50886 40.62254,34.50972 40.6227,34.51035 40.62274,34.51048 40.62274,34.51212 40.62298,34.51196 40.62298,34.5118 40.62301,34.51034 40.62339,34.51014 40.62344,34.50997 40.62344,34.50852 40.62388,34.50804 40.6244,34.50828 40.62489,34.50865 40.62529,34.50841 40.62656,34.50849 40.62674,34.50853 40.6269,34.50889 40.62744,34.50916 40.62792,34.50938 40.62834,34.50944 40.62854,34.50942 40.62874,34.50938 40.62884,34.50944 40.62902,34.50965 40.62947,34.50962 40.62962,34.50967 40.62977,34.50963 40.63002,34.50949 40.63022,34.50934 40.63035,34.50896 40.63044,34.50878 40.63061,34.50825 40.6312,34.50856 40.63147,34.50926 40.63171,34.50961 40.63178,34.51011 40.63198,34.51024 40.63202,34.51056 40.63263,34.51085 40.63325,34.51091 40.63368,34.51094 40.63369,34.5111 40.63421,34.51143 40.63517,34.51121 40.63558,34.51077 40.63614,34.5106 40.63627,34.51017 40.6361,34.50987 40.63585,34.50982 40.63604,34.50916 40.63586,34.50905 40.63624,34.50881 40.63674,34.50918 40.637,34.50948 40.63727,34.50889 40.6379,34.50803 40.63867,34.50741 40.63946,34.50718 40.63991,34.50676 40.64086,34.50665 40.64097,34.5064 40.64113,34.50612 40.64122,34.50598 40.6415,34.5052 40.64112,34.50445 40.64053,34.50355 40.6404,34.50278 40.64006,34.50234 40.63987,34.50212 40.63978,34.50192 40.63968,34.50114 40.63931,34.50072 40.63912,34.50031 40.63893,34.49976 40.63843,34.49933 40.63802,34.49911 40.63781,34.49894 40.63763,34.49782 40.63635,34.49755 40.63607,34.4973 40.63583,34.49687 40.6355,34.49625 40.63496,34.49614 40.63486,34.49395 40.63369,34.49288 40.63304,34.49144 40.63203,34.49052 40.63128,34.48949 40.63033,34.48947 40.63006,34.48966 40.62917,34.48999 40.62838,34.48993 40.62813,34.48987 40.62805,34.48992 40.62762,34.48995 40.62738,34.48982 40.62701,34.48983 40.62685,34.49002 40.62634,34.48999 40.62626,34.48985 40.62612,34.48987 40.62568,34.48967 40.62549,34.48961 40.62535,34.48972 40.62513,34.4898 40.62471,34.48978 40.6246,34.48958 40.62426,34.48931 40.62412,34.48927 40.62398,34.4891 40.62377,34.48907 40.62364,34.4892 40.62345,34.48913 40.62324,34.48904 40.6229,34.48911 40.62267,34.48889 40.62243,34.4888 40.6223,34.48879 40.6222,34.48893 40.62203,34.48869 40.62163,34.48839 40.62145,34.48821 40.62127,34.48806 40.62118,34.48798 40.62116,34.48832 40.62048,34.48954 40.62071,34.4902 40.62075,34.49105 40.62069,34.49221 40.62057))') and
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
