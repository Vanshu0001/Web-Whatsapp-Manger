import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import os
import qrcode

# Set the WhatsApp web URL
whatsapp_url = "https://web.whatsapp.com/"

# Create a new Chrome session
options = webdriver.ChromeOptions()
options.add_argument("--user-data-dir=/mnt/data/User_Data")  # Persistent storage on Render
options.add_argument("--headless")  # Run headless
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")
options.add_argument("--disable-gpu")
options.add_argument("--window-size=1920x1080")

driver = webdriver.Chrome(executable_path="/tmp/chromedriver", options=options)

# Navigate to WhatsApp web
driver.get(whatsapp_url)

# Check if there is already an active session
try:
    WebDriverWait(driver, 15).until(EC.presence_of_element_located((By.XPATH, "//div[@data-testid='chat-list']")))
    print("Already logged in.")
except Exception:
    print("Not logged in. Please scan the QR code.")

    # Print the QR code for login
    qr_code = qrcode.make(whatsapp_url)
    qr_code.save("/mnt/data/qr_code.png")  # Save in persistent storage
    print("QR code saved as /mnt/data/qr_code.png")
    print("Scan the QR code to log in.")

    # Wait for the user to scan the QR code
    WebDriverWait(driver, 60).until(EC.presence_of_element_located((By.XPATH, "//div[@data-testid='chat-list']")))

# Display group names and IDs
chat_list = driver.find_element(By.XPATH, "//div[@data-testid='chat-list']")
groups = chat_list.find_elements(By.XPATH, "//div[@data-testid='chat-item']")

print("Available groups:")
group_details = {}
for i, group in enumerate(groups):
    group_name = group.find_element(By.XPATH, ".//span[@class='_3ko75 _5h6Y_ _3Whw5']").text
    group_id = group.get_attribute("data-chat-id")
    group_details[group_id] = group_name
    print(f"{i+1}. {group_name} (ID: {group_id})")

# Prompt user to enter group ID
group_id = input("Enter the group ID from the above list: ")

# Persist the group ID to a file for future use
with open("/mnt/data/group_id.txt", "w") as f:
    f.write(group_id)

print(f"Group ID {group_id} saved for future use.")

# Find the message list
message_list = driver.find_element(By.XPATH, "//div[@data-testid='message-list']")

# Find and delete new messages
while True:
    try:
        new_messages = message_list.find_elements(By.XPATH, "//div[@data-testid='message'][not(@data-message-id)]")

        # Delete the new messages
        for message in new_messages:
            message.find_element(By.XPATH, "//button[@data-testid='message-delete-button']").click()

    except Exception as e:
        print(f"Error: {e}")
        time.sleep(60)

    # Sleep for 1 minute before checking for new messages again
    time.sleep(60)
