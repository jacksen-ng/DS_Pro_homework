from bs4 import BeautifulSoup
import requests
import time
import re
import sqlite3
import csv

origin_url_window = 'https://review.kakaku.com/review/K0000800909/?Page='
win_rates = []

for page_num in range(1,30):
    url_window = origin_url_window + str(page_num)
    response_window = requests.get(url_window)
    soup = BeautifulSoup(response_window.text, 'html.parser')

    win_elements = soup.find_all('td', class_=re.compile(r'rate'))

    for win_rate in win_elements:
        win_rate_text = win_rate.get_text().strip()
        win_rates.append(win_rate_text)

time.sleep(0.1)

win_group_rates = [win_rates[i:i + 7] for i in range(0,len(win_rates), 7)]

window_data  = list(zip(win_group_rates))

conn = sqlite3.connect('windows_ratings.db')
cursor = conn.cursor()
cursor.execute('''
CREATE TABLE IF NOT EXISTS window_ratings (
    id INTEGER PRIMARY KEY,
    rates TEXT
)
''')

for rates_tuple in window_data:
    
    rates_str = ', '.join(rates_tuple[0])
    cursor.execute('INSERT INTO window_ratings (rates) VALUES (?)', (rates_str,))
conn.commit()


cursor.execute('SELECT * FROM window_ratings')
window_ratings_data = cursor.fetchall()


with open('window_ratings.csv', 'w', newline='', encoding='utf-8') as file:
    writer = csv.writer(file)
    writer.writerow(['ID', 'Rates'])
    writer.writerows(window_ratings_data)


conn.close()