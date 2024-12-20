from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import NoSuchElementException, TimeoutException
import time
import requests
from bs4 import BeautifulSoup
import re
import config
import json
import os
from urllib.parse import urlparse
import csv

#instagram username and password
insta_username = "jmurad09@gmail.com"
insta_password = "<PUT IN YOUR PASSWORD>"

#instagram handle/name
keyword = "@2k.drew"

# setup chromedriver
driver = webdriver.Chrome()

# Open the webpage
driver.get("https://www.instagram.com/")

# Target username
timeout = 10
username = WebDriverWait(driver, timeout).until(EC.element_to_be_clickable((By.CSS_SELECTOR, "input[name='username']")))

# password
password = WebDriverWait(driver, timeout).until(EC.element_to_be_clickable((By.CSS_SELECTOR, "input[name='password']")))

# Enter username and password
username.clear()
username.send_keys(insta_username)
password.clear()
password.send_keys(insta_password)

# target the Login button and click it
timeout = 5
loginButton = WebDriverWait(driver, timeout).until(EC.element_to_be_clickable((By.CSS_SELECTOR, "button[type='submit']"))).click()

# Wait up to abut 10 seconds for the search button to be clickable, it will take a little bit of time to login
timeout = 10
searchButton = WebDriverWait(driver, timeout).until(EC.element_to_be_clickable((By.CSS_SELECTOR, 'svg[aria-label="Search"]')))

# Click the search button once it becomes clickable
searchButton.click()

#target the search field to search instagram account
searchBox = WebDriverWait(driver, timeout).until(EC.element_to_be_clickable((By.XPATH, "//input [@placeholder='Search']")))
searchBox.clear()

# Search for instagram handle @handle or keyword
keyword = "@2k.drew"
searchBox.send_keys(keyword)

# check if search has a @ symbol, you can use # too
# remove @ if it is in the name
if keyword.startswith("@"):
    # remove @ symbol
    keyword = keyword[1:]
    
time.sleep(1)
# Find the first element with the specified Xpath that matches the keyword
firstResult = driver.find_element(By.XPATH, f'//span[text()="{keyword}"]')

# click on the first result if it exisits
firstResult.click()

# get inital page height so you can scroll to the bottom of the page
initalHeight = driver.execute_script("return document.body.scrollHeight")

# create a list to store htmls
soups = []

countScrolls = 0
while True:
    # scroll downb to the bottom of the page
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    
    # wait 5 seconds to allow new content to load, adjust as needed
    time.sleep(2)
    
    # parse html
    html = driver.page_source
    
    # create a beautiful soup object from the scaped HTML
    soups.append(BeautifulSoup(html, 'html.parser'))

    # Get current page height
    currentHeight = driver.execute_script("return document.body.scrollHeight")
    
    countScrolls += 1
    print(f"Scroll Count {countScrolls}")
    
    if currentHeight == initalHeight:
        break # exit the loop, can't scroll further

    #update the inital height for the next iteration
    initalHeight = currentHeight # Update the initial height for the next iteration
    
# List to store the post image URLs
post_urls = []

print(f"Length of Soups: {len(soups)}")
for soup in soups:
    # Find all anchor elements with href attributes
    anchors = soup.find_all('a', href=True)
    
    # Filter URLs that start with "/p/" or "/reel/"
    #post_urls.extend([anchor['href'] for anchor in anchors if anchor['href'].startswith(("/p/", "/reel/"))]) Didn't work for me'
    post_urls.extend([anchor['href'] for anchor in anchors if "/p/" in anchor['href']])
    post_urls.extend([anchor['href'] for anchor in anchors if "/reel/" in anchor['href']])

# Convert the list to a set to remove duplicates
unique_post_urls = list(set(post_urls))

print(f"Posts before: {len(post_urls)}, after: {len(unique_post_urls)}")
print(unique_post_urls)

json_list = []

# Define the query parameters to add
query_parameters = "__a=1&__d=dis"

# go through all urls
for url in unique_post_urls:
    try:
        # Get the current URL of the page
        current_url = driver.current_url

        # Append the query parameters to the current URL
        modified_url = "https://www.instagram.com/" + url #+ "?" + query_parameters

        # Get URL
        driver.get(modified_url)

        # Wait for a moment to allow new content to load (adjust as needed)
        time.sleep(2)

        # Find the <pre> tag containing the JSON data
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, '//pre'))
        )
        pre_tag = driver.find_element_by_xpath('//pre')

        # Extract the JSON data from the <pre> tag
        json_script = pre_tag.text

        # Parse the JSON data
        json_parsed = json.loads(json_script)

        # Add json to the list
        json_list.append(json_parsed)
    except (NoSuchElementException, TimeoutException, json.JSONDecodeError) as e:
        print(f"Error processing URL {url}: {e}")

# Lists to store URLs and corresponding dates
all_urls = []
all_dates = []

# Iterate through each JSON data in the list
for json_data in json_list:
    
    # Extract the list from the 'items' key
    item_list = json_data.get('items', [])
    
    # Iterate through each item in the 'items' list
    for item in item_list:
        
        # Extract the date the item was taken
        date_taken = item.get('taken_at')  # Move this line inside the loop

        # Check if 'carousel_media' is present
        carousel_media = item.get('carousel_media', [])
        
        # Iterate through each media in the 'carousel_media' list
        for media in carousel_media:
            
            # Extract the image URL from the media
            image_url = media.get('image_versions2', {}).get('candidates', [{}])[0].get('url')
            
            if image_url:
                # Add the image URL and corresponding date to the lists
                all_urls.append(image_url)
                all_dates.append(date_taken)
                print(f"carousel image added")
                
            # Extract the video URL from the media
            video_versions = media.get('video_versions', [])
            if video_versions:
                video_url = video_versions[0].get('url')
                if video_url:
                    
                    # Add the video URL and corresponding date to the lists
                    all_urls.append(video_url)
                    all_dates.append(date_taken)
                    print(f"carousel video added")

        # Handle cases of unique image, instead of carousel
        image_url = item.get('image_versions2', {}).get('candidates', [{}])[0].get('url')
        if image_url:
            
            # Add the image URL and corresponding date to the lists
            all_urls.append(image_url)
            all_dates.append(date_taken)
            print(f"single image added")

        # Check if 'video_versions' key exists
        video_versions = item.get('video_versions', [])
        if video_versions:
            video_url = video_versions[0].get('url')
            if video_url:
                all_urls.append(video_url)
                all_dates.append(date_taken)
                print(f"video added")
                
# Print or use all collected URLs as needed
print(f"Length of All Instagram Urls found: {len(all_urls)}")

# Create a directory to store downloaded files
download_dir = keyword
os.makedirs(download_dir, exist_ok=True)

# Create subfolders for images and videos
image_dir = os.path.join(download_dir, "images")
video_dir = os.path.join(download_dir, "videos")
os.makedirs(image_dir, exist_ok=True)
os.makedirs(video_dir, exist_ok=True)

# Initialize counters for images and videos
image_counter = 1
video_counter = 1

# Iterate through URLs in the all_urls list and download media
for index, url in enumerate(all_urls, 0):
    response = requests.get(url, stream=True)

    # Extract file extension from the URL
    url_path = urlparse(url).path
    file_extension = os.path.splitext(url_path)[1]

    # Determine the file name based on the URL
    if file_extension.lower() in {'.jpg', '.jpeg', '.png', '.gif'}:
        file_name = f"{all_dates[index]}-img-{image_counter}.png"
        destination_folder = image_dir
        image_counter += 1
    elif file_extension.lower() in {'.mp4', '.avi', '.mkv', '.mov'}:
        file_name = f"{all_dates[index]}-vid-{video_counter}.mp4"
        destination_folder = video_dir
        video_counter += 1
    else:
        # Default to the main download directory for other file types
        file_name = f"{all_dates[index]}{file_extension}"
        destination_folder = download_dir

    # Save the file to the appropriate folder
    file_path = os.path.join(destination_folder, file_name)
    
    # Write the content of the response to the file
    with open(file_path, 'wb') as file:
        for chunk in response.iter_content(chunk_size=8192):
            if chunk:
                file.write(chunk)

    print(f"Downloaded: {file_path}")

# Print a message indicating the number of downloaded files and the download directory
print(f"Downloaded {len(all_urls)} files to {download_dir}")
