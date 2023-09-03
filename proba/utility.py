from django.shortcuts import render
import os
from datetime import datetime
import sys
from selenium.common.exceptions import NoSuchElementException, StaleElementReferenceException
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.chrome.service import Service
from selenium.common.exceptions import ElementClickInterceptedException
import json
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver import ActionChains
from selenium import webdriver
from random import randint
import time

path = os.getcwd()
config_path = f"{path}/proba/config.json"
user = "USER"
dirr = os.path.abspath(os.curdir).rsplit("\\", 1)[0] + f"\\{user}"
options = Options()
options.add_argument("--disable-infobars")
options.add_argument("--disable-dev-shm-usage")
options.add_argument("--disable-blink-features")
options.add_argument("excludeSwitches")
options.add_argument(r"user-data-dir={}".format(dirr))
options.add_experimental_option("excludeSwitches", ['enable-automation'])


def load_conf_file(config_file):
    with open(config_file, "r") as f:
        config = json.load(f)
        inputs = config[user]
    return inputs


dt = load_conf_file(config_path)
# reset_count = input("Reset User count file? Y/N: ")
reset_count = "n"
if reset_count.lower() == "y":
    open("follower_count.txt", "w")
# maxmum_to_follow = int(input("Enter a number of maximum users to follow: "))
maxmum_to_follow = 2
s = Service(ChromeDriverManager().install())
driver = webdriver.Chrome(service=s, options=options)
driver.set_window_size(1400, 720)
driver.get(dt.get('URL'))
driver.implicitly_wait(10)
find = driver.find_element
finds = driver.find_elements


def delay():
    time.sleep(randint(2, 5))


def login(login_email, login_password):
    # Navigate to the login page
    driver.get("https://truthsocial.com/login")

    # Check if the login elements exist
    try:
        username = find(By.XPATH, '//input[@name="username"]')
        password = find(By.XPATH, '//input[@name="password"]')
    except NoSuchElementException:
        print("Login credentials exist or login failed, proceeding to URL")
        # Navigate to the URL from the config file if login fails or user is already logged in
        driver.get(dt.get('URL'))
        return  # Exit the function

    # If login elements exist, proceed with login
    username.clear()
    username.send_keys(login_email)
    password.clear()
    print(dt.get('PASSWORD'))
    password.send_keys(login_password + "\n")

    # Wait to ensure login is successful, you can modify the waiting condition based on the page structure
    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, '//element_after_login')))

    # Navigate to the specific URL after successful login
    driver.get(dt.get('URL'))


def scroll_down():
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    delay()


def ulla_bot(email, password, reset, followers):
    login(email, password)
    total_followed = 0
    with open("follower_count.txt", "r") as f:
        lines = f.read().splitlines()
        if lines:
            total_followed = int(lines[-1])

    # Wait for the button to be clickable
    WebDriverWait(driver, 15).until(EC.element_to_be_clickable((By.XPATH, "//button[contains(., 'ReTruths')]")))

    # Locate and Click on the Button with "ReTruths" Text Inside a div
    retruths_button = driver.find_element(By.XPATH, "//button[contains(., 'ReTruths')]")
    retruths_button.click()
    delay()

    # Locate the scrollable div by data-test-id attribute
    scrollable_div = driver.find_element(By.CSS_SELECTOR, '[data-test-id="virtuoso-scroller"]')

    while True:  # Infinite loop
        # Find the follow buttons inside the scrollable div
        follows = scrollable_div.find_elements(By.XPATH, '//button[.//span[text()="Follow"]]')

        if len(follows) < 1:  # If no follow buttons found
            # Scroll inside the scrollable div
            driver.execute_script("arguments[0].scrollTop += 200", scrollable_div)
            # Wait for 5 seconds
            time.sleep(5)
            # Continue to the next iteration of the loop to try finding follow buttons again
            continue

        # Process the found follow buttons
        for idx, follow in enumerate(follows):
            if total_followed >= maxmum_to_follow:
                break
            try:
                WebDriverWait(driver, 15).until(
                    EC.element_to_be_clickable((By.XPATH, '//button[.//span[text()="Follow"]]')))
                ActionChains(driver).move_to_element(follow).click(follow).perform()
                total_followed += 1
                with open("follower_count.txt", "a") as f:
                    f.write(str(total_followed) + "\n")
                print("\nFollowed count {}".format(total_followed), end="\r")
                delay()
            except ElementClickInterceptedException:
                print("Element not clickable. Scrolling down...")
                driver.execute_script("arguments[0].scrollTop += 200",
                                      scrollable_div)  # Scroll inside the scrollable div

        if total_followed >= maxmum_to_follow:
            break

        print("\nTotal: " + str(total_followed), end="\r")

    sys.exit("Maximum users followed")
