# app.py

from flask import Flask, render_template, request, send_file
from Scraping_business import Scrape_phase1, Scrape_phase2, Scrape_phase3, Scrape_phase4
from Scraping_influncer import Youtube_Scrape_1, Youtube_Scrape_2, Youtube_Scrape_3
import pandas as pd

app = Flask(__name__)

# @app.route('/')
# def home():
#   return render_template('home.html')
  

@app.route('/', methods=['GET', 'POST'])
def business():
   if request.method == 'POST':
        input_link = request.form['input_link']
        unique_links = set()
        Scrape_phase1(input_link, unique_links)
        df = []
        Scrape_phase2(unique_links, df)
        leads = Scrape_phase3(df)
        leads = Scrape_phase4(leads)
       
        file_path = "leads.xlsx"
        leads.to_excel(file_path, index=True)
        return send_file(file_path, as_attachment=True ,download_name='custom_name.xlsx')

   return render_template('Business.html')
 
@app.route('/influencers',methods=['GET', 'POST'])
def influencers():
  if request.method == 'POST':
        input_link = request.form['input_link']
        unique_links = set()
        Youtube_Scrape_1(input_link,unique_links )
        df = []
        Youtube_Scrape_2(unique_links, df)
        leads = Youtube_Scrape_3(df)
        
        
        file_path = "leads.xlsx"
        leads.to_excel(file_path, index=True)
        return send_file(file_path, as_attachment=True ,download_name='custom_name.xlsx')
  return render_template('influencer.html')

        
    
  
   

if __name__ == '__main__':
    app.run(debug=True)
