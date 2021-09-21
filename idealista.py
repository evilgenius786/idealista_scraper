import csv
import datetime
import json
import os
import time
import traceback

import undetected_chromedriver as uc
from undetected_chromedriver import ChromeOptions

# delay time
t = 5
# show/hide chrome
hide = False
outfile = ""
out = "idealista.csv"
infile = "urls.txt"
site = "https://www.idealista.com"

headers = ['Date', 'URL', 'Title', 'Neighbourhood', 'District', 'Detail1', 'Detail2', 'Detail3', 'Price (EURO)',
           'Description']

options = ChromeOptions()
options.add_argument('--user-data-dir=C:\\Selenium\\ChromeProfile')
if hide:
    options.add_argument("--headless")
# options.add_argument("--blink-settings=imagesEnabled=false")
driver = uc.Chrome(options=options)


def scrape(href, i):
    global outfile
    print(href)
    try:

        if href not in outfile:
            driver.get(href)
            if "ct.captcha-delivery.com" in driver.page_source:
                print("CAPTCHA detected. Pls solve it...")
                while "ct.captcha-delivery.com" in driver.page_source:
                    time.sleep(1)
            location = find('span', 'main-info__title-minor').split(", ")
            details = driver.find_elements_by_xpath('//div[@class="info-features"]/span')
            info = [str(datetime.datetime.now().strftime('%d/%m/%y %H:%M:%S')), href,
                    find('span', 'main-info__title-main'),
                    location[0] if len(location) > 0 else "No location",
                    location[1] if len(location) > 1 else "No location",
                    details[0].text.replace("\u00b2", "2") if len(details) > 0 else "No detail",
                    details[1].text if len(details) > 1 else "No detail",
                    details[2].text if len(details) > 2 else "No detail",
                    find('span', 'info-data-price').replace("\u20ac", ""),
                    find('div', 'adCommentsLanguage expandable').replace('\n', ' ')]
            data = {"Date": info[0],
                    "URL": info[1],
                    "Title": info[2],
                    "Neighbourhood": info[3],
                    "District": info[4],
                    # "Details": '  '.join(details),
                    "Detail1": info[5],
                    "Detail2": info[6],
                    "Detail3": info[7],
                    "Price (EURO)": info[8],
                    "Description": info[9],
                    # "Location": soup.find('a', {'class': 'main-info__title-map icon-location showMap'}).find(
                    #     'span').text
                    }
            print(json.dumps(data, indent=4))
            appendcsv(out, info)
            appendcsv(f"{i}.csv", info)
        else:
            print("Already scraped", href)
        outfile = outfile + href
    except Exception as e:
        print(f"Error: {e}")
        traceback.print_exc()
        appendtxt('error.txt', href)


def process(url, i):
    print(i, "Processing URL:", url)
    try:
        driver.get(url)
        urls = []
        while True:
            if "ct.captcha-delivery.com" in driver.page_source:
                print("CAPTCHA detected. Pls solve it...")
                while "ct.captcha-delivery.com" in driver.page_source:
                    time.sleep(1)
            time.sleep(1)
            for x in driver.find_elements_by_xpath('//a[@role="heading"]'):
                u = x.get_attribute('href')
                if u not in urls:
                    urls.append(u)
            if "next" in driver.page_source:
                time.sleep(t)
                driver.get(driver.find_element_by_xpath('//li[@class="next"]/a').get_attribute('href'))
            else:
                break
            print(f"Found {len(urls)} URLs so far")
        print(f"Found {len(urls)} URLs in total")
        for href in urls:
            scrape(href, i)
            time.sleep(t)

    except Exception as e:
        print(f"Error: {e}")
        traceback.print_exc()
        appendtxt('error1.txt', url)


def main():
    global outfile
    os.system("color 0a")
    logo()
    if not os.path.isfile(out):
        with open(out, 'a', newline='', encoding='utf8', errors='ignore') as outfile:
            csv.writer(outfile).writerow(headers)
    with open(out, 'r', encoding='utf8', errors='ignore') as o:
        outfile = o.read()
    with open(infile, 'r') as inf:
        urls = inf.read().splitlines()
    for i in range(len(urls)):
        process(urls[i], i)
        time.sleep(t)


def find(tag, attrib):
    try:
        return driver.find_element_by_xpath(f"//{tag}[@class='{attrib}']").text.strip()
    except:
        return "not found"


def appendcsv(f, row):
    rows = [headers, row]
    if not os.path.isfile(f):
        with open(f, 'w', newline='', encoding='utf8', errors='ignore') as outfile:
            outfile.close()
    with open(f, 'r', newline='', encoding='utf8', errors='ignore') as outfile:
        content = csv.reader(outfile)
        try:
            next(content)
        except:
            pass
        for r in content:
            rows.append(r)
    with open(f, 'w', newline='', encoding='utf8', errors='ignore') as outfile:
        csv.writer(outfile).writerows(rows)


def appendtxt(f, line):
    with open(f, 'a') as err:
        err.write(line + "\n")


def logo():
    print("""
        .__    .___            .__  .__          __          
        |__| __| _/____ _____  |  | |__| _______/  |______   
        |  |/ __ |/ __ \\\\__  \ |  | |  |/  ___/\   __\__  \  
        |  / /_/ \  ___/ / __ \|  |_|  |\___ \  |  |  / __ \_
        |__\____ |\___  >____  /____/__/____  > |__| (____  /
                \/    \/     \/             \/            \/ 
=======================================================================
        Data scraping tool by : fiverr.com/muhammadhassan7 
=======================================================================""")


if __name__ == "__main__":
    main()
