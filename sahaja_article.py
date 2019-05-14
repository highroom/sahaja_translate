# coding:utf-8
import urllib, urllib2, cookielib
import re
import xlsxwriter
import sys
from bs4 import BeautifulSoup
import sqlite3
from multiprocessing.dummy import Pool as ThreadPool
import pickle
reload(sys)
sys.setdefaultencoding('utf-8')
g_lst_t = []
def login():
    username = '827148@qq.com'
    passwd = 'ss123456'
    login_url = 'http://www.amruta.org/wp-login.php'
    cj = cookielib.LWPCookieJar()
    opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cj))
    urllib2.install_opener(opener)
    post_data = {'log': username, 'pwd': passwd, 'wp-submit': 'Log+In'}
    login_data = urllib.urlencode(post_data)
    headers = {'Referer': 'http://www.amruta.org/wp-login.php',
               'Accept-Language': 'zh-CN',
               'User-Agent': 'Mozilla/5.0 (compatible; MSIE 9.0; Windows NT 6.1; WOW64; Trident/5.0)',
               'Content-Type': 'application/x-www-form-urlencoded',
               'Accept-Encoding': 'gzip, deflate',
               'Host': 'www.amruta.org',
               'Connection': 'Keep-Alive',
               'Cache-Control': 'no-cache'
    }
    req = urllib2.Request(login_url, login_data, headers=headers, )
    r = opener.open(req)
    reurl = r.geturl()
    content = urllib2.urlopen(reurl).read()
    if username in content:
        print 'Log in OK'
def GetTlist():
    atk_list_url = 'http://www.amruta.org/all-mothers-talks-in-chronological-order/'
    atk_list_pattern = re.compile(
        r'<li><span class="talk-date">(.*?)</span><a href="(.*?)">(.*)?</a><span class="talk-date">(.*?)</span> </li>')
    content = urllib2.urlopen(atk_list_url).read()
    atk_list = atk_list_pattern.findall(content)
    return atk_list
def write_xls(lst):
    # Create a workbook and add a worksheet.
    workbook = xlsxwriter.Workbook('sahajalist.xlsx')
    worksheet = workbook.add_worksheet()
    # Add a bold format to use to highlight cells.
    bold = workbook.add_format({'bold': 1})
    # Adjust the column width.
    worksheet.set_column(1, 1, 15)
    # Start from the first cell below the headers.
    row = 1
    col = 0
    for l in (lst):
        # Convert the date string into a datetime object.
        worksheet.write_row(row, 0, l)
        row += 1
    workbook.close()
def HandleList(lst):
    tx_url = lst[1]
    tx_flag = lst[3]
    lst_tmp = list(lst)
    print tx_url
    global g_lst_t
    if 'T' in tx_flag:
        try:
            content = urllib2.urlopen(tx_url)
            soup = BeautifulSoup(content)
            result = soup.find(id="content")
            dp_list = (
                ('a'),
                ('div', {'class': 'sharedaddy sd-sharing-enabled'}),
                ('p', {'class': 'postmetadata'}),
                ('div', {'id': 'respond'}),
            )
            for i in dp_list:
                div_t = result.find(*i)
                if div_t:
                    div_t.decompose()
            # div1 = result.find('div', {'class': 'sharedaddy sd-sharing-enabled'})
            # div1.decompose()
            # div2 = result.find('p', {'class': 'postmetadata'})
            # div2.decompose()
            # div3 = result.find('div', {'id': 'respond'})
            # div3.decompose()
            result.prettify()
            result = result.get_text().strip()
            lst_tmp.append(result)
        except Exception as e:
            lst_tmp.append(str(e)+'Need again')
    else:
        lst_tmp.append('No txt')
    g_lst_t.append(lst_tmp)
    # W2sqlt3(lst_tmp)
    return lst_tmp
def W2sqlt3(list_a):
    conn = sqlite3.connect('d:\sahaja.db', check_same_thread=False) # 允许在其他线程中使用这个连接
    cur = conn.cursor()
    cur.execute(''' create table if not exists sahaja_article (postdate text, url text, title text, flag text, content text)''')
    cur.execute('''insert into sahaja_article values (?, ?, ?, ?, ?)''', list_a)
    cur.close()
    conn.commit()
    conn.close()
    print 'insert complete!'
# def Divlist(lst):
# lst_t = []
#     lst_o = []
#     for i in lst:
#         if 'T' in i[3]:
#             lst_t.append(i)
#         else:
#             lst_o.append(i)
#     return (lst_t, lst_o)
# (list_t, list_o) = Divlist(article_list)
if __name__ == '__main__':
    login()
    article_list = GetTlist()
    pool = ThreadPool(10)
    results = pool.map(HandleList, article_list)
    pool.close()
    pool.join()
    output = open('sahaja_data1', 'wb')
    pickle.dump(g_lst_t, output)
    output.close()
#write_xls(article_list)
sahaja_pickup.py
# -*- coding: utf-8 -*-
import sqlite3
import sys
import pickle
import xlsxwriter
reload(sys)
sys.setdefaultencoding('utf-8')
def write2txt(list1):
    f = open('d:/sahaja_article', 'w')
    for i in list1:
        if i[4]:
            f.write(i[4])
        f.close()
def w2sqlt3(list2):
    conn = sqlite3.connect('d:\sahaja.db', check_same_thread=False) # 允许在其他线程中使用这个连接
    conn.text_factory = str
    cur = conn.cursor()
    cur.execute(''' create table if not exists sahaja_article (postdate text, url text, title text, flag text, content text)''')
    cur.executemany('''insert into sahaja_article values (?, ?, ?, ?, ?)''', list2)
    conn.commit()
    conn.close()
    print 'insert complete!'
def write_xls(lst):
    # Create a workbook and add a worksheet.
    workbook = xlsxwriter.Workbook('sahajalist.xlsx')
    worksheet = workbook.add_worksheet()
    # Add a bold format to use to highlight cells.
    bold = workbook.add_format({'bold': 1})
    # Adjust the column width.
    worksheet.set_column(1, 1, 15)
    # Start from the first cell below the headers.
    row = 1
    col = 0
    for l in (lst):
        # Convert the date string into a datetime object.
        worksheet.write_row(row, 0, l)
        row += 1
    workbook.close()
def write_xls_txt(lst):
    row = 1
    col = 0
    workbook = xlsxwriter.Workbook('sahajalist.xlsx')
    worksheet = workbook.add_worksheet()
    title = [u'时间', u'网址', u'标题', u'标志', u'内容']
    bold = workbook.add_format({'bold': 1})
    worksheet.write_row(0, 0, title, bold)
    bold = workbook.add_format({'bold': 1})
    worksheet.set_column(0, 0, 10)
    worksheet.set_column(1, 1, 60)
    worksheet.set_column(2, 2, 40)
    worksheet.set_column(3, 3, 15)
    worksheet.set_column(4, 4, 100)
    for i in lst:
        dt = i[0]
        url = i[1]
        title = i[2].replace("/", "_").replace("?", '_').replace("&#8217;", "'").replace("&#038;", "&").replace("&#8211;", "-")
        flag = i[3]
        content = i[4].replace("&#8217;", "'")
        if 'T' in flag:
            file_name = 'english_txt\\' +dt + ' ' + title + '.txt'
            with open(file_name, 'w') as f:
                f.write(content)
        worksheet.write_string(row, 0, dt)
        worksheet.write_string(row, 1, url)
        worksheet.write_string(row, 2, title)
        worksheet.write_string(row, 3, flag)
        if 'T' in flag:
            worksheet.write_url(row, 4, file_name)
        row += 1
    workbook.close()
pk1_file = open('sahaja_data1', 'rb')
data1 = pickle.load(pk1_file)

write_xls_txt(data1)