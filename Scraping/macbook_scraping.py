#Import Library
from bs4 import BeautifulSoup
import requests
import time
import re
import sqlite3
import csv

#Scraping Macbook's Review
macbook_texts = []
rates = []
origin_url = 'https://review.kakaku.com/review/newreview/CategoryCD=0029/PageNo='

for page_num in range(1, 30):
    url = origin_url + str(page_num)
    response = requests.get(url)  
    response.encoding = 'utf-8'


    soup = BeautifulSoup(response.text, 'html.parser')

   
    elements = soup.find_all('a')
    for element in elements:
        text = element.get_text().strip()
        match = re.search(r'MacBook (?:Pro|Air)', text)
        if match:
            matched_text = match.group()
            macbook_texts.append(matched_text)

  
    rate_elements = soup.find_all('td', class_=re.compile(r'rate'))
    for rate in rate_elements:
        rate_text = rate.get_text().strip()
        rates.append(rate_text)


    time.sleep(0.1)  


grouped_rates = [rates[i:i + 10] for i in range(0, len(rates), 10)]

macbook_data = list(zip(macbook_texts, grouped_rates))

conn = sqlite3.connect('macbooks.db')
cursor = conn.cursor()

cursor.execute('''
CREATE TABLE IF NOT EXISTS macbook_ratings (
    id INTEGER PRIMARY KEY,
    text TEXT,
    rate TEXT
)
''')

for text, rate_group in macbook_data:
    rate_str = ', '.join(rate_group)  
    cursor.execute('INSERT INTO macbook_ratings (text, rate) VALUES (?, ?)', (text, rate_str))

conn.commit()


cursor.execute('SELECT * FROM macbook_ratings')
macbook_ratings_data = cursor.fetchall()
with open('macbook_ratings.csv', 'w', newline='', encoding='utf-8') as file:
    writer = csv.writer(file)
    writer.writerow(['ID', 'Text', 'Rate'])
    writer.writerows(macbook_ratings_data)

conn.close()