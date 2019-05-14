# coding:utf-8

import requests
from bs4 import BeautifulSoup
import pandas as pd
import warnings
from queue import Queue
from threading import Thread
import os
import time

warnings.filterwarnings('ignore')


def get_all():
    url = 'https://www.amruta.org/all-shri-mataji-talks-in-chronological-order/'
    r = requests.get(url)
    soup = BeautifulSoup(r.text, 'html.parser')
    talk_list = []
    for i in soup.select(".all-event-list li"):
        dic = {}
        if i.select('.talk-date'):
            dic['date'] = i.select('.talk-date')[0].text
            dic['url'] = i.select('a')[0]['href']
            dic['title'] = i.select('a')[0].text
            dic['location'] = i.select('.location')[0].text
            dic['during'] = i.select('.avail-media')[0].text.strip()
            talk_list.append(dic)
    sahaja_df = pd.DataFrame(talk_list)
    sahaja_df['url'] = sahaja_df['url'].map(lambda e: 'https://www.amruta.org%s' % e)
    sahaja_df['amruta_url'] = None
    sahaja_df['Chs'] = None
    return sahaja_df


class Amruta_spider(Thread):
    def __init__(self, queue, sahaja_df):
        Thread.__init__(self)
        self.queue = queue
        self.sahaja_df = sahaja_df

    def run(self):
        while self.queue.qsize():
            print('Queue size: ', self.queue.qsize())
            idx = self.queue.get()
            self.get_page(idx)
            self.queue.task_done()

    def get_page(self, idx):
        try:
            url = self.sahaja_df.loc[idx, 'url']
            proxy = get_proxy()
            proxies = {"http": "http://{}".format(proxy), "https": "https://{}".format(proxy)}
            r = requests.get(url, proxies=proxies, timeout=60)
            if r.url == url:
                self.queue.put(idx)
                return
            soup = BeautifulSoup(r.text, 'html.parser')
            self.sahaja_df.loc[idx, 'git_url'] = '\n'.join(
                i['href'] for i in soup.select('.entry-content a') if 'https' in i.get('href', '')) if soup.select(
                '.entry-content a') else None

            self.sahaja_df.loc[idx, 'amruta_url'] = r.url

            self.sahaja_df.loc[idx, 'youtube_url'] = '\n'.join(
                i['src'] for i in soup.select('.youtube-player')) if soup.select('.youtube-player') else None

            self.sahaja_df.loc[idx, 'youku_url'] = '\n'.join(
                i['href'] for i in soup.select('#yoku-links a')) if soup.select('#yoku-links') else None

            self.sahaja_df.loc[idx, 'eng'] = soup.select('.pf-content')[0].text if soup.select('.pf-content') else None

            print(self.sahaja_df.loc[idx, 'title'], 'completed.')
        except Exception as e:
            print(e)
            self.queue.put(idx)


def get_proxy():
    return requests.get("http://127.0.0.1:5010/get/").text


def main():
    pkl_file = 'sahaja_df.pkl'
    if os.path.exists(pkl_file):
        sahaja_df = pd.read_pickle(pkl_file)
    else:
        sahaja_df = get_all()

    queue = Queue()
    chs_null_ids = sahaja_df[sahaja_df['amruta_url'].isnull()].index

    for i in chs_null_ids:
        queue.put(i)

    for _ in range(30):
        au = Amruta_spider(queue, sahaja_df)
        au.start()

    while True:
        time.sleep(60)
        sahaja_df.to_pickle(pkl_file)
        print('-----------------Saved.----------------------')
        if sahaja_df['amruta_url'].isnull().sum() == 0:
            print('All Done.')
            return


if __name__ == '__main__':
    main()
