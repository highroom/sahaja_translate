# coding:utf-8
from googletrans import Translator
import requests
import warnings
from threading import Thread
import re
from queue import Queue

warnings.filterwarnings('ignore')


class SahajaTrans(Thread):
    def __init__(self, queue, dic):
        Thread.__init__(self)
        self.queue = queue
        self.dic = dic

    def run(self):
        while self.queue.qsize():
            print('Queue size: ', self.queue.qsize())
            idx = self.queue.get()
            self.google_translate(idx)
            self.queue.task_done()

    def google_translate(self, idx):
        try:
            content = self.dic[idx]
            raw_list = split_to_limit_list(content)
            raw_list_num = len(raw_list)
            max_list_num = 400
            trans_txt = ''

            # 判断如果列表太长，就按每400个一个代理进行处理，以免服务器拒绝访问
            for i in range(raw_list_num):
                part_list = raw_list[i * max_list_num: (i + 1) * max_list_num]
                proxy = get_proxy()
                proxies = {"http": "http://{}".format(proxy), "https": "https://{}".format(proxy)}

                translator = Translator(service_urls=['translate.google.cn'], proxies=proxies, timeout=300)
                translations = translator.translate(part_list, dest='zh-cn')
                tran_list = []
                # 判断如果成员不是字符，而是列表的说明不是按行分割的，则按所有原文+所有译文来展示，由于译文没有换行符，手工增加
                for translation in translations:
                    if isinstance(translation, list):
                        origin_list, text_list = [], []
                        for tra in translation:
                            origin_list.append(tra.origin)
                            text_list.append(tra.text)
                            if '\n' in tra.origin:
                                text_list.append('\n\n')
                        tran_list.extend(origin_list)
                        tran_list.extend(text_list)
                    else:
                        tran_list.append(translation.origin)
                        tran_list.append(translation.text)
                        if '\n' in translation.origin:
                            tran_list.append('\n\n')
                trans_txt += ''.join(tran_list)
            self.dic[idx] = trans_txt
            print(idx, 'translation completed.')
        except Exception as e:
            print(idx, e)
            self.queue.put(idx)


def get_proxy():
    return requests.get("http://127.0.0.1:5010/get/").text


# 把字符按换行符拆分成列表，如果其中成员长度超过5000就拆分成小于5000的成员，如[100, [3000, 2000], 2000]
def split_to_limit_list(content):
    limit_length = 5000
    lines = content.splitlines(keepends=True)
    part_num = len(lines)
    for i in range(part_num):
        if len(lines[i]) > limit_length:
            sentences = iter(re.split(r'([.])', lines[i]))
            sen_list, current = [], next(sentences)
            for sentence in sentences:
                if len(current) + len(sentence) >= limit_length:
                    sen_list.append(current)
                    current = sentence
                else:
                    current += sentence
            sen_list.append(current)
            lines[i] = sen_list
    return lines


def read_to_dic(file_name):
    dic = {}
    with open(file_name, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    for key, value in enumerate(lines):
        dic[key] = value
    return dic


def dic_to_file(file_name, dic):
    with open(file_name, 'w', encoding='utf-8', errors='ignore') as f:
        for line in dic.values():
            f.write(line)


def main():
    file_name = '19820222.txt'
    save_name = '19820222_trans.txt'
    dic = read_to_dic(file_name)
    queue = Queue()

    for i in dic:
        queue.put(i)
    for _ in range(30):
        sa = SahajaTrans(queue, dic)
        sa.start()

    queue.join()
    dic_to_file(save_name, dic)
    print('Done')


if __name__ == '__main__':
    main()
