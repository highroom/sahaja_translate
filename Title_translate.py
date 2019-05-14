# coding: utf-8
import pandas as pd
import re
from googletrans import Translator
from queue import Queue
from threading import Thread
import requests
import time
import warnings
import os

warnings.filterwarnings('ignore')


class SahajaTrans(Thread):
    def __init__(self, queue, sahaja_df):
        Thread.__init__(self)
        self.queue = queue
        self.sahaja_df = sahaja_df

    def run(self):
        while self.queue.qsize():
            print('Queue size: ', self.queue.qsize())
            idx = self.queue.get()
            self.google_translate(idx)
            self.queue.task_done()

    def google_translate(self, idx):
        try:
            content = self.sahaja_df.loc[idx, 'title']
            proxy = get_proxy()
            proxies = {"http": "http://{}".format(proxy)}

            translator = Translator(service_urls=['translate.google.cn'], proxies=proxies, timeout=300)
            translation = translator.translate(content, dest='zh-cn')
            trans_txt = translation.text
            self.sahaja_df.loc[idx, 'chs_title'] = trans_txt
            print(idx, self.sahaja_df.loc[idx, 'title'], 'title completed.')
        except Exception as e:
            print(idx, e)
            self.queue.put(idx)


def get_proxy():
    return requests.get("http://127.0.0.1:5010/get/").text


def main():
    pkl_file = 'sahaja_df.pkl'
    sahaja_df = pd.read_pickle(pkl_file)
    queue = Queue()
    chs_null_ids = sahaja_df[sahaja_df['chs_title'].isnull() & sahaja_df['title'].notnull()].index

    for i in chs_null_ids:
        queue.put(i)

    for _ in range(100):
        sa = SahajaTrans(queue, sahaja_df)
        sa.start()

    while True:
        time.sleep(60)
        sahaja_df.to_pickle(pkl_file)
        print('-----------------Saved.----------------------')
        if sahaja_df.loc[sahaja_df['title'].notnull(), 'chs_title'].isnull().sum() == 0:
            print('All Done.')
            return


if __name__ == '__main__':
    main()
