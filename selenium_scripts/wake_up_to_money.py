import bs4
import os
import time
from os.path import join
from selenium.webdriver.common.by import By



def get_test(driver, url):
    path='C:/Users/Darks/Desktop'
    driver.get(url)
    page_length = driver.execute_script(
            "window.scrollTo(0, document.body.scrollHeight);var lenOfPage=document.body.scrollHeight;return lenOfPage;")
    match = False
    while (match == False):
        print("scrolling to the end")
        lastCount = page_length
        time.sleep(1.7)
        page_length = driver.execute_script(
            "window.scrollTo(0, document.body.scrollHeight);var lenOfPage=document.body.scrollHeight;return lenOfPage;")
        if lastCount == page_length:
            match = True
    soup = bs4.BeautifulSoup(driver.page_source)
    # print(soup)
    menu_ifood = driver.find_elements(By.XPATH, './/a[@class="aisle-menu__item__link"]')
    menu_ifood = {i.get_attribute('text'): i.get_attribute('href') for i in menu_ifood}
    for category, link in menu_ifood.items():
        print(category)
        print(link)

    

def download_podcast(driver, url, download_dir, date):
    driver.get(url)
    soup = bs4.BeautifulSoup(driver.page_source, 'lxml')
    ul = soup.find('ul', {'class': 'list-unstyled'})
    lq_li = ul.find_all('li')[1]
    download_link = lq_li.find('a')['href']
    download_link = 'http:' + download_link
    driver.get(download_link)
    print('download started')
    # wait for download to start
    time.sleep(5)
    # check for downloads:
    files = os.listdir(download_dir)
    # if the file is downloaded the date will be in the file name
    file = [x for x in files if date in x][0]
    if file:
        print('file: ', file, 'found')
        file_path = os.path.join(download_dir, file)
        # poll download to completion using filesize.
        t0 = time.time()  # start time
        s0 = 0  # file size
        while True:
            s1 = os.stat(file_path).st_size
            if s1 > s0:
                print('file still downloading, sleeping for 10 seconds')
                s0 = s1
                time.sleep(10)
                t1 = time.time()
            if s1 == s0:
                print('download complete')
                time.sleep(5)  # giving the script additional time.
                break
            if t1 - t0 > 300:
                print('max download time exceeded')
                break
        # change file name:
        os.rename(file_path, os.path.join(
            download_dir, 'episode_{}.mp3'.format(date)))
    else:
        print('download failed')
