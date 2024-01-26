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
from exchangelib import Account, Credentials, Message, HTMLBody
import pandas as pd

def Scrape_phase1(url, unique_links):
    driver = webdriver.Chrome()

    # Open the URL in the browser
    driver.get(url)
    driver.implicitly_wait(10)

    # Define a wait for the presence of at least one div with class "Nv2PK"
    wait = WebDriverWait(driver, 5)
    all_nv2pk_divs = []
    links = []
    

    try:


        while True:
            # Collect all div elements with class "Nv2PK"
            nv2pk_divs = driver.find_elements(By.CSS_SELECTOR, 'div.Nv2PK')

            # Add the found divs to the list if there are new ones
            if len(nv2pk_divs) > len(all_nv2pk_divs):
                all_nv2pk_divs = nv2pk_divs  # Update the collected divs list
               # print(f"Collected {len(all_nv2pk_divs)} divs")

                # Scroll to a specific element that may trigger more content loading
                last_div = nv2pk_divs[-1]
                driver.execute_script("arguments[0].scrollIntoView(true);", last_div)

                # Introduce a sleep to allow time for content to load (adjust as needed)
                time.sleep(10)  # Adjust the time (in seconds) as needed

                # Wait for the newly loaded divs (optional)
                wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, 'div.Nv2PK')))

                # Get the updated HTML content after scrolling and waiting
                html_content = driver.page_source

                # Create a BeautifulSoup object to parse the updated HTML content
                soup = BeautifulSoup(html_content, 'html.parser')

                # Find all div elements with class "Nv2PK" using BeautifulSoup
                all_nv2pk_divs_soup = soup.find_all('div', class_='Nv2PK')

                # You can now work with the BeautifulSoup-selected elements
                for div in range(len(all_nv2pk_divs_soup)):
                    # Extract specific information from each div, for example:
                    # Extract text
                    item = all_nv2pk_divs_soup[div].find("a")
                    link_of_item = item["href"]

                    #print(link_of_item)
                    links.append(link_of_item)
                    unique_links.add(link_of_item)
            else:
                break



    except (StaleElementReferenceException, TimeoutException) as e:
        # Handle StaleElementReferenceException or TimeoutException
        print(f"An exception occurred: {e}")

    finally:
        #unique_links = set()
        
        driver.quit()
        

def Scrape_phase2(unique_links , df):
    driver = webdriver.Chrome()

    for link in (unique_links):
        entry = []

       
        link_of_item = link

        driver.get(link_of_item)

        src = driver.page_source
        soup = BeautifulSoup(src, 'html.parser')

        name_of_company = soup.find("h1").get_text()
        #print(name_of_company)


        entry.append(name_of_company)


        phone_number = "//www.gstatic.com/images/icons/material/system_gm/2x/phone_gm_blue_24dp.png"
        address = "//www.gstatic.com/images/icons/material/system_gm/2x/place_gm_blue_24dp.png"
        website_link = "//www.gstatic.com/images/icons/material/system_gm/2x/public_gm_blue_24dp.png"
        Email = "NaN"

        #phone_number
        phone_number_icon = soup.find(src = phone_number)

        if(phone_number_icon == None):
            phone_number = "NaN"
        else:
            level2 = phone_number_icon.find_parents(limit = 3)
            phone_number =level2[2].get_text()


        #address
        address_icon = soup.find(src = address)
        if(address_icon == None):
            address = "NaN"
        else:
            level2 = address_icon.find_parents(limit = 3)
            address =level2[2].get_text()


        #website_link
        website_link_icon = soup.find(src = website_link)
        if(website_link_icon == None):
            website_link = "NaN"
        else:
            level2 = website_link_icon.find_parents(limit = 3)
            website_link =level2[2].get_text()






        entry.append(phone_number)
        entry.append(address)
        entry.append(website_link)
        entry.append(Email)

        #print(entry)
        df.append(entry)
    driver.quit()



def Scrape_phase3(df):
    leads=pd.DataFrame(df, columns=['Name of company','Phone Number',  'Location',  'Website Link', 'Email'])
    return leads



def Scrape_phase4(leads):
    df = leads
    driver = webdriver.Chrome()
    for ind in df.index:
        website = df['Website Link'][ind]
        if website != "NaN":
            final_link = "https://" + website + "/"
            
            try:
                driver.set_page_load_timeout(6)  # Set the timeout for the page to load (in seconds)
                driver.get(final_link)
                driver.implicitly_wait(10)
               
                h = driver.page_source
                soup = BeautifulSoup(h, 'html.parser')
                mailto_links = soup.find_all('a', href=lambda href: href and href.startswith('mailto:'))
                #print(len(mailto_links))
                for link in mailto_links:
                    email = link['href'].split(':')[1]
                    df['Email'][ind] = email
                  # Close the driver after scraping
            except TimeoutException:
               # print(f"Timeout occurred while accessing {final_link}. Skipping...")
                continue
            except Exception as e:
                #print(f"An error occurred: {str(e)}")
                #driver.quit()  # Close the driver in case of any other exception
                continue
        else:
            continue
        
    
    driver.quit()
    return leads
