import re
import shutil
import os
import psycopg2
import hashlib
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from collections import defaultdict

# Set up the webdriver (e.g., Chrome)
driver = webdriver.Chrome()

# Navigate to the login page
driver.get("https://SERVER_IP")

# Find the username and password fields, and enter your credentials
username_field = driver.find_element(By.ID, "username")
password_field = driver.find_element(By.ID, "password")
username_field.send_keys("USER")
password_field.send_keys("PASS")

# Find and click the login button
login_button = driver.find_element(By.ID, "login-button")
login_button.click()

# Navigate to the JobSearch page
driver.get("https://SERVER_IP/web/JobSearch")

# Write HTML data
element = WebDriverWait(driver, 20).until(EC.visibility_of_element_located((By.CSS_SELECTOR, "#table0")))
# open file with *.html* extension to write html
file = open("log.txt", "w")
# write then close file
file.write(element.get_attribute("outerHTML"))
file.close()

# Read the HTML content from the log.txt file
with open("log.txt", "r") as file:
    html_content = file.read()

# Extract job IDs from the HTML content
job_id_pattern = r'id="(\d+)"'
job_ids = re.findall(job_id_pattern, html_content)

# Open a new window for each job ID
for job_id in job_ids:
    url = f"https://SERVER_IP/servlet/web.JobPreviewServlet?id={job_id}"
    driver.execute_script(f"window.open('{url}');")

driver.quit()

# Specify the source and destination directories
source_directory = r"C:\SafeQ6\FSP\Service\JobStore"
destination_directory = r"ARCHIVING_DIRECTORY"

# Connect to the PostgreSQL database
connection = psycopg2.connect(
    host="PostgreSQL_SERVER_IP",
    port=5433,
    database="DBNAME",
    user="DBUSER",
    password="DBPASS"
)

# Create a cursor to execute SQL queries
cursor = connection.cursor()

# Get a list of all .png files in the source directory
png_files = [file for file in os.listdir(source_directory) if file.endswith(".png")]

# Copy each .png file to the destination directory
for file in png_files:
    source_path = os.path.join(source_directory, file)
    destination_path = os.path.join(destination_directory, file)
    shutil.copy(source_path, destination_path)

    # Extract the GUID from the file name
    guid = os.path.splitext(file)[0]

    # Query the database to get the origin value "username" for the corresponding Job GUID
    query = f"SELECT smartq_jobs.origin FROM tenant_1.smartq_jobs WHERE smartq_jobs.job_guid = '{guid}'"
    cursor.execute(query)
    result = cursor.fetchone()

    if result:
        origin = result[0]
        # Split the origin name to extract the part within curly braces, which is the username
        origin_name = origin.split("{")[1].split("}")[0]

        new_file_name = f"{origin_name}.png"

        # Check if the new file name already exists
        number = 1
        while os.path.exists(os.path.join(destination_directory, new_file_name)):
            new_file_name = f"{origin_name}{number}.png"
            number += 1

        new_destination_path = os.path.join(destination_directory, new_file_name)
        os.rename(destination_path, new_destination_path)

# Close the database connection and cursor
cursor.close()
connection.close()

# Remove duplicates, define the folder path
folder_path = r"ARCHIVING_DIRECTORY"

# Create a dictionary to store the file sizes and hash values
file_dict = defaultdict(list)

# Iterate over the files in the folder
for file_name in os.listdir(folder_path):
    file_path = os.path.join(folder_path, file_name)

    # Check if the file is a .png file
    if file_name.endswith(".png"):
        # Get the file size
        file_size = os.path.getsize(file_path)

        # Calculate the MD5 hash of the file contents
        with open(file_path, "rb") as file:
            file_content = file.read()
            file_hash = hashlib.md5(file_content).hexdigest()

        # Add the file path to the list corresponding to its size and hash combination
        file_dict[(file_size, file_hash)].append(file_path)

# Iterate over the file dictionary
for file_list in file_dict.values():
    # Check if there are multiple files with the same size and hash combination
    if len(file_list) > 1:
        # Delete all but the first file in the list
        for file_path in file_list[1:]:
            os.remove(file_path)
