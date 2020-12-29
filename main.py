import requests
from bs4 import BeautifulSoup
import csv
import PySimpleGUI as sg
import os
import re

URL = 'https://www.internsg.com/jobs/{}/?f_p=107&f_i&filter_s#isg-top'
QUERY = 'python'
LABEL_SIZE = (12, 1)
INPUT_SIZE = (50, 1)
PAGE_AMOUNT = 5

def scrape(url, query, page_amount):
    """scrape amount of pages and look for those with the query"""
    res = []
    for i in range(1, page_amount+1):
        resp = requests.get(url.format(i))
        soup = BeautifulSoup(resp.text, features="html.parser")

        #Grab job urls from page
        links = set()
        for a in soup.find_all('a'):
            link = a.get('href')
            if link and '/job/' in link:
                links.add(link)

        #For each URL, search for the query and append (job title, url) if query is found.
        for link in links:
            resp = requests.get(link)
            soup = BeautifulSoup(resp.text, features="html.parser")
            div = soup.find('div', id='primary')
            if query in div.get_text().lower():
                title = div.find('h1', 'entry-title').get_text()
                date = re.findall('\d+ [a-zA-Z]{3} \d{4}', div.get_text())[0]
                res.append((title, date, link))

    with open('res.txt', 'w') as f:
        csv.writer(f).writerows(res)
    return res

def read():
    try:
        with open('res.txt') as f:
            res = list(csv.reader(f))
        return res
    except:
        scrape()
        read()

res = read()

# the GUI
sg.theme('DarkAmber')

layout = [
    [sg.Text('URL Format', size=LABEL_SIZE), sg.InputText(URL, size=INPUT_SIZE)],
    [sg.Text('Query', size=LABEL_SIZE), sg.InputText(QUERY, size=INPUT_SIZE)],
    [sg.Text('Page Count', size=LABEL_SIZE), sg.Slider(range=(1, 10), orientation='h', default_value=5)],
    [sg.Table(res, headings=['Job Title', 'Date', 'URL'], key='out', num_rows=10, def_col_width=50, max_col_width=50, enable_events=True)],
    [sg.Button('Scrape')]
]

# Create the Window
window = sg.Window('InternSG Scraper', layout)

# Event Loop to process "events" and get the "values" of the inputs
while True:
    event, values = window.read()
    if event == sg.WIN_CLOSED or event == 'Cancel': # if user closes window or clicks cancel
        break
    elif event == 'Scrape':
        url, query, page_amount, *_ = list(values.values())
        res = scrape(url, query, int(page_amount))
        window['out'].update(res)
    else:
        #copies selected url
        url = res[values['out'][0]][2]
        os.system(f'open {url}')
        
window.close()

        

