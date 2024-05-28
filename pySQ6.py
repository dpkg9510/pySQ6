from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import re

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
