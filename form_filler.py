import time
from selenium.webdriver.common.by import By

def fill_student_details(driver, user_data):
    blocks = driver.find_elements(By.XPATH, "//div[@role='listitem']")

    for block in blocks:
        try:
            text = block.text.lower()

            def click_element(element):
                driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", element)
                time.sleep(0.5)
                driver.execute_script("arguments[0].click();", element)

            # TEXT INPUTS
            if any(kw in text for kw in ["email", "full name", "roll number", "prn"]):
                input_box = block.find_element(By.XPATH, ".//input[@type='text' or @type='email']")
                driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", input_box)
                input_box.clear()
                
                # Use user_data from GUI instead of config
                if "email" in text:
                    input_box.send_keys(user_data["email"])
                    print("Filled Email")
                elif "full name" in text:
                    input_box.send_keys(user_data["full_name"])
                    print("Filled Full Name")
                elif "roll number" in text:
                    input_box.send_keys(user_data["roll_number"])
                    print("Filled Roll Number")
                elif "prn" in text:
                    input_box.send_keys(user_data["prn"])
                    print("Filled PRN")
                
                time.sleep(1)

            # DROPDOWNS
            elif any(kw in text for kw in ["college name", "year-mandatory", "year", "branch-division"]):
                dropdown = block.find_element(By.XPATH, ".//div[@role='listbox']")
                click_element(dropdown)
                time.sleep(1)

                if "college name" in text:
                    target_val = user_data['college']
                    print("Selected College")
                elif "year-mandatory" in text or "year" in text:
                    target_val = user_data['year']
                    print("Selected Year")
                elif "branch-division" in text:
                    target_val = user_data['branch_division']
                    print("Selected Branch-Division")

                option = driver.find_element(
                    By.XPATH, f"//div[@role='option' and @data-value='{target_val}']"
                )
                click_element(option)
                time.sleep(1)

        except:
            continue

# ... (Keep your existing click_option and submit_form functions here below) ...

def click_option(driver, final_answer, options, elements):
    clean_answer = final_answer.strip().lower().replace(".", "")
    
    for text, element in zip(options, elements):
        clean_text = text.strip().lower().replace(".", "")
        
        if clean_answer == clean_text or clean_answer in clean_text:
            driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", element)
            time.sleep(0.5)
            driver.execute_script("arguments[0].click();", element)
            print("✅ Clicked:", text)
            return

    print("❌ No exact match found for:", final_answer)

def submit_form(driver):
    print("\nLocating Submit button...")
    try:
        submit_span = driver.find_element(By.XPATH, "//span[contains(text(), 'Submit')]")
        submit_button = submit_span.find_element(By.XPATH, "./ancestor::div[@role='button']")
        
        driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", submit_button)
        time.sleep(1)
        driver.execute_script("arguments[0].click();", submit_button)
        print("✅ Form Submitted Successfully!")
        time.sleep(3)
    except Exception as e:
        print("❌ Could not find or click the Submit button.", e)