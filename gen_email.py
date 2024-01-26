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

def generate_email_body(topic):
    api_key = 'Your Api Key'
    openai.api_key = api_key

    prompt_text = f"Write an email about {topic} for some recipent_name let it be x:"
    
    # GPT-3 parameters
    response = openai.Completion.create(
        engine="gpt-3.5-turbo-instruct",
        prompt=prompt_text,
        max_tokens=500  # Adjust max tokens to control the length of the generated text
    )
    
    # Extracting the generated text from the response
    generated_text = response.choices[0].text.strip()
    return generated_text


import pandas as pd
from exchangelib import Credentials, Account, Message, HTMLBody

def create_email_draft_from_excel(subject, general_body, excel_file_path):
    Your_Outlook_email_id = str(input("Your_Outlook_email_id: "))
    password = str(input("Password: "))
    
    # Set up credentials and connect to the Exchange server
    creds = Credentials(username=Your_Outlook_email_id, password=password)
    account = Account(primary_smtp_address=Your_Outlook_email_id, credentials=creds, autodiscover=True)

    # Read details from Excel file
    df = pd.read_excel(excel_file_path)
    
    # Assuming the email addresses are in the last column
    recipients = df.iloc[:, -1].tolist()

    for recipient_email in recipients:
        if pd.notnull(recipient_email):
            email_body = f"{general_body}"
            
            # Create a draft email for each valid recipient
            Message(
                folder=account.drafts,
                subject=subject,
                to_recipients=[recipient_email],
                body=HTMLBody(email_body)
            ).save()

    print("Draft emails created successfully.")
