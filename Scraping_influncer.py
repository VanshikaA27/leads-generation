import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import StaleElementReferenceException, TimeoutException
from bs4 import BeautifulSoup
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
import requests
import openai
import re
import pandas as pd

def Youtube_Scrape_1(url, unique_links):
    driver = webdriver.Chrome()

    # Open the URL in the browser
    driver.get(url)
    driver.implicitly_wait(10)

    # Define a wait for the presence of at least one div with class "ytd-channel-name"
    wait = WebDriverWait(driver, 10)
    all_channel_divs = []
    
    try:
        while True:

             # Collect all div elements with class "ytd-channel-name"
            channel_divs = driver.find_elements(By.CSS_SELECTOR, 'div.ytd-channel-name')


            # Add the found divs to the list if there are new ones
            if len(channel_divs) > len(all_channel_divs):
                all_channel_divs = channel_divs  # Update the collected divs list
                print(f"Collected {len(all_channel_divs)} divs")

                last_div = channel_divs[-1]
                driver.execute_script("arguments[0].scrollIntoView(true);", last_div)


                # Introduce a sleep to allow time for content to load (adjust as needed)
                time.sleep(10)  # Adjust the time (in seconds) as needed

                # Wait for the newly loaded divs (optional)
                wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, 'div.ytd-channel-name')))

                # Get the updated HTML content after waiting
                html_content = driver.page_source

                # Create a BeautifulSoup object to parse the updated HTML content
                soup = BeautifulSoup(html_content, 'html.parser')

                # Find all div elements with class "ytd-channel-name" using BeautifulSoup
                all_channel_divs_soup = soup.find_all('div', class_='ytd-channel-name')

                # You can now work with the BeautifulSoup-selected elements
                for div in range(len(all_channel_divs_soup)):
                    # Extract specific information from each div, for example:
                    # Extract text
                    item = all_channel_divs_soup[div].find("a")
                    if item:
                        link_of_item = "https://www.youtube.com" + item.get("href", "")
                        

                        unique_links.add(link_of_item)
            else:
                break
    except (StaleElementReferenceException, TimeoutException) as e:
        # Handle StaleElementReferenceException or TimeoutException
       print(f"An exception occurred: {e}")
       
    finally:
        driver.quit()
    
        
        

    
def extract_emails_and_phone_numbers(text):
    email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
    phone_number_pattern = r'\b(?:\+\d{1,2}\s?)?(?:\(\d{1,4}\)|\d{1,4})[-.\s]?(\d{1,10})[-.\s]?(\d{1,10})\b'


    emails = re.findall(email_pattern, text)
    phone_numbers = re.findall(phone_number_pattern, text)

    return {'emails': emails, 'phone_numbers': phone_numbers}



def Youtube_Scrape_2(unique_links, df):
    driver = webdriver.Chrome()

    for link in unique_links:
        entry = []

        link_of_item = link
        channel_name = link.split('@')[1]

        driver.get(link_of_item)

        src = driver.page_source
        soup = BeautifulSoup(src, 'html.parser')

        # Find subscribers count
        subscribers_element = soup.find(id='subscriber-count')
        subscribers = subscribers_element.get_text() if subscribers_element else "N/A"

        # Find videos uploaded count
        videos_uploaded_element = soup.find(id='videos-count')
        videos_uploaded = videos_uploaded_element.get_text() if videos_uploaded_element else "N/A"

        trigger_element = driver.find_element(By.ID, 'channel-tagline')
        trigger_element.click()

        try:
            pop_up_element = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.ID, 'about-container'))
            )
        except Exception as e:
            #print(f"Error: {e}")
            driver.quit()

        pop_up_element_text = pop_up_element.text
        #print(f"Pop-up Element Text: {pop_up_element_text}")

        contact_info = extract_emails_and_phone_numbers(pop_up_element_text)
        extracted_emails = contact_info['emails']
        #phone_numbers = contact_info['phone_numbers']

        entry.append(channel_name)
        entry.append(subscribers)
        entry.append(videos_uploaded)
        entry.append(extracted_emails)
        #entry.append(phone_numbers)
        entry.append(link)

        df.append(entry)  # Corrected to append the 'entry' list

    driver.quit()



def Youtube_Scrape_3(df):
    leads=pd.DataFrame(df, columns=['channel_name','subscribers',  'videos_uploaded',  'emails', 'channel_link'])
    return leads
