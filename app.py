import time
import os
import re
import base64
from pathlib import Path
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.print_page_options import PrintOptions

from scraper import extract_questions
from evaluator import get_final_answer
from form_filler import fill_student_details, click_option, submit_form

LOCAL_PROFILE_DIR = os.path.join(os.getcwd(), "automation_profile")

def setup_driver(browser_choice):
    if browser_choice == "Edge":
        options = webdriver.edge.options.Options()
        # FIXED: Added the -- before user-data-dir and profile-directory
        options.add_argument(f"--user-data-dir={LOCAL_PROFILE_DIR}")
        options.add_argument("--profile-directory=Default") 
        
        # --- Anti-Annoyance Flags ---
        options.add_argument("--no-first-run")
        options.add_argument("--disable-sync")
        options.add_argument("--no-default-browser-check")
        options.add_argument("--disable-infobars")
        
        options.add_argument("--start-maximized")
        driver = webdriver.Edge(options=options)
    else:
        options = webdriver.chrome.options.Options()
        # FIXED: Added the -- before user-data-dir and profile-directory
        options.add_argument(f"--user-data-dir={LOCAL_PROFILE_DIR}")
        options.add_argument("--profile-directory=Default") 
        
        # --- Anti-Annoyance Flags ---
        options.add_argument("--no-first-run")
        options.add_argument("--disable-sync")
        options.add_argument("--no-default-browser-check")
        options.add_argument("--disable-infobars")
        
        options.add_argument("--start-maximized")
        driver = webdriver.Chrome(options=options)
        
    return driver
#  --- NEW: DEDICATED LOGIN SETUP FUNCTION ---
# --- UPDATED: DEDICATED LOGIN SETUP FUNCTION ---
def setup_browser_login(user_data):
    print("🌐 Launching browser for initial setup...")
    browser_choice = user_data.get("browser", "Chrome")
    driver = setup_driver(browser_choice)
    
    # Send them directly to Google Login
    driver.get("https://accounts.google.com/")
    
    print("\n🚨 ACTION REQUIRED 🚨")
    print("1. Log in using your @vit.edu email account.")
    print("2. DO NOT close the browser manually by clicking 'X'!")
    print("3. The app will detect your login and cleanly close the browser for you.")
    
    # Keep the script alive and monitor the URL
    while True:
        try:
            current_url = driver.current_url
            # When login succeeds, Google usually redirects to myaccount.google.com
            if "myaccount.google.com" in current_url:
                print("\n✅ Login successfully detected! Saving profile...")
                time.sleep(3) # Wait for cookies to fully write to the hard drive
                break
            time.sleep(2)
        except Exception:
            # If the user ignored the warning and clicked 'X' anyway
            print("\n⚠️ Browser was closed manually. Attempting to save profile...")
            break

    # CRITICAL FIX: This cleanly shuts down the background processes and releases the folder lock!
    try:
        driver.quit()
    except:
        pass
        
    print("✅ Profile is safely unlocked.")
    print("👉 You can now click 'Start Automation'.")

def slow_scroll_to_bottom(driver):
    print("Scrolling to load MCQs...")
    last_height = driver.execute_script("return document.body.scrollHeight")
    while True:
        driver.execute_script("window.scrollBy(0, 800);")
        time.sleep(1)
        new_position = driver.execute_script("return window.pageYOffset + window.innerHeight")
        full_height = driver.execute_script("return document.body.scrollHeight")
        if new_position >= full_height:
            break
    time.sleep(2)

def save_as_pdf(driver):
    print("\nPreparing to save PDF...")
    driver.switch_to.default_content()
    page_title = driver.title if driver.title else "Google_Form"
    safe_title = re.sub(r'[\\/*?:"<>|]', "", page_title).strip()
    filename = f"{safe_title}.pdf"
    downloads_folder = os.path.join(Path.home(), "Downloads")
    full_path = os.path.join(downloads_folder, filename)
    print(f"Generating PDF as: {filename}")
    print_options = PrintOptions()
    print_options.background = True 
    pdf_base64 = driver.print_page(print_options)
    with open(full_path, "wb") as f:
        f.write(base64.b64decode(pdf_base64))
    print(f"✅ PDF saved successfully to: {full_path}")
    iframes = driver.find_elements(By.TAG_NAME, "iframe")
    if len(iframes) > 0:
        driver.switch_to.frame(iframes[0])

# --- UPDATED: AUTOMATION ENTRY POINT ---
def run_automation(user_data):
    print("🚀 Starting Form Automation System")

    browser_choice = user_data.get("browser", "Chrome")
    print(f"Booting up {browser_choice}...")
    driver = setup_driver(browser_choice)
    
    print(f"Opening Form URL: {user_data['form_url']}")
    driver.get(user_data["form_url"])
    
    # Wait 5 seconds to see if Google redirects us to a login page
    time.sleep(5) 
    
    # --- NEW: SAFETY KILL SWITCH ---
    if "accounts.google.com" in driver.current_url or "ServiceLogin" in driver.current_url:
        print("\n❌ ERROR: Form access denied!")
        print("The browser is not logged into your @vit.edu account.")
        print("Please click 'Setup Browser Login' to sign in first.")
        driver.quit()
        return
        
    iframes = driver.find_elements(By.TAG_NAME, "iframe")
    if len(iframes) > 0:
        print("Switching to form iframe...")
        driver.switch_to.frame(iframes[0])
        time.sleep(2)

    print("Filling student details...")
    fill_student_details(driver, user_data)
    time.sleep(2)

    slow_scroll_to_bottom(driver)

    print("Extracting MCQs...")
    questions = extract_questions(driver)
    print(f"Total MCQs found: {len(questions)}")

    if len(questions) == 0:
        print("❌ No MCQs detected. Stopping.")
        driver.quit()
        return

    for i, q in enumerate(questions, 1):
        print(f"\n====================================")
        print(f"Q{i}: {q['question']}")
        final_answer = get_final_answer(q["question"], q["options"], user_data)
        print("Selected:", final_answer)
        click_option(driver, final_answer, q["options"], q["elements"])
        time.sleep(1)

    print("\n✅ All MCQs processed.")
    save_as_pdf(driver)
    submit_form(driver)

    print("\n🎉 AUTOMATION COMPLETE. You may close the app.")
    time.sleep(3)