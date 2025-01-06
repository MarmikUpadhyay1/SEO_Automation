import time
import random
import pyautogui
import asyncio
from selenium import webdriver  
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, TimeoutException

# Open log file in append mode
log_file = open('session_log.txt', 'a')

def log(message):
    timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
    log_message = f"{timestamp} - {message}"
    print(log_message)
    log_file.write(log_message + "\n")

# Load configuration files (domains and keywords)
def load_config():
    with open('domains.txt', 'r') as f:
        domains = [line.strip() for line in f]

    with open('keywords.txt', 'r') as f:
        keywords = [line.strip() for line in f]
    
    return domains, keywords

# Setup browser with realistic User-Agent and incognito mode
def setup_browser(headless=False):
    chrome_options = Options()
    chrome_options.add_argument("--incognito")  # Incognito mode
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--start-maximized")
    # Setting a realistic User-Agent to mimic human behavior
    if headless:
        chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.150 Safari/537.36")

    driver = webdriver.Chrome(options=chrome_options)
    driver.get("https://www.google.com")

    # Open DevTools in device mode
    time.sleep(2)
    pyautogui.press('f12')  # Open DevTools
    time.sleep(2)
    pyautogui.hotkey('ctrl', 'shift', 'm')  # Toggle Device Toolbar (Responsive Mode)
    time.sleep(2)

    # Select a random device from the Device Toolbar dropdown
    select_random_device()
    
    time.sleep(3)  # Wait for the page to load in responsive mode
    return driver

def select_random_device():
    # Click on the "Dimensions: Responsive" dropdown
    base_x, base_y = 444, 188  # Replace with your actual coordinates for the dropdown
    pyautogui.click(base_x, base_y)
    print("Clicked on Dimensions: Responsive dropdown")

    # Press the down arrow a random number of times between 2 and 10
    random_down_count = random.randint(2, 10)
    print(f"Pressing 'Down' key {random_down_count} times")
    
    for _ in range(random_down_count):
        pyautogui.press('down')
        time.sleep(0.2)  # Small delay between presses for a realistic effect

    # Press 'Enter' to confirm selection
    pyautogui.press('enter')
    print("Confirmed selection")

# Accept Google consent pop-up if it appears
def accept_consent(driver):
    try:
        consent_button = WebDriverWait(driver, 5).until(
            EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'I agree')] | //button[contains(text(), 'Accept')] | //button[contains(text(), 'Agree')]"))
        )
        consent_button.click()
        log("Consent accepted.")
    except (NoSuchElementException, TimeoutException):
        log("Consent popup not found or timed out.")
    except Exception as e:
        log("An error occurred while accepting consent: " + str(e))

def search_google(driver, keyword):
    try:
        search_box = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.NAME, "q")))
        search_box.send_keys(keyword)
        search_box.send_keys(Keys.RETURN)
        log(f"Searched for keyword: {keyword}")
    except NoSuchElementException:
        log("Search box not found.")
    except Exception as e:
        log("An error occurred while searching: " + str(e))

def check_and_click_result(driver, domains):
    try:
        results = WebDriverWait(driver, 10).until(lambda d: d.find_elements(By.XPATH, "//a[@href]"))
        for result in results:
            url = result.get_attribute("href")
            if url and any(domain in url for domain in domains):
                log(f"Found matching domain: {url}. Visiting...")
                result.click()
                return True
        log("No matching domain found in the first 100 Google results.")
    except Exception as e:
        log("An error occurred while checking results: " + str(e))
    return False

def visit_random_domain(driver, domains):
    random_domain = random.choice(domains)
    log(f"No matching domain found. Visiting {random_domain} directly.")
    driver.get(f"http://{random_domain}")

def simulate_scrolling(driver, duration):
    end_time = time.time() + duration
    log(f"Simulating scrolling for {duration} seconds.")
    while time.time() < end_time:
        driver.execute_script("window.scrollBy(0, document.body.scrollHeight / 3);")
        time.sleep(random.uniform(2, 5))  # Random pauses during scrolling

def main():
    # Load configuration files
    domains, keywords = load_config()
    
    # Setup the browser
    driver = setup_browser(headless=False)

    try:
        accept_consent(driver)

        # Select a random keyword to search
        keyword = random.choice(keywords)
        log(f"Searching for: {keyword}")
        search_google(driver, keyword)

        # Check results and either click or visit a random domain
        if not check_and_click_result(driver, domains):
            visit_random_domain(driver, domains)

        # Simulate user interaction by scrolling for a random duration
        duration = random.randint(100, 200)  # Random session duration in seconds
        simulate_scrolling(driver, duration)

    finally:
        log("Session complete. Closing browser.")
        driver.quit()
        log_file.close()

if __name__ == "__main__":
    main()
