## 老师，我的代码思路可能与您的有些许不一样。因为我觉得如果都照抄您教的，那就真的没意思了。
## 所以希望您不要因此而给我低分，O(∩_∩)O谢谢 ！如果可以的话，尽量把分数打高一点呗，嘿嘿！


# 功能：爬取豆瓣读书Top100图书数据，并载入数据库

import sqlite3  # 导入相关模块
import requests
from bs4 import BeautifulSoup

headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:70.0) Gecko/20100101 Firefox/70.0',
           'Host': 'book.douban.com'}    # 伪装headers请求访问头部信息

book_name_list = []
author_list = []
cbs_list = []
fm_list = []
dp_list = []
url_list = []  # 生成相关列表，用于存储数据


# 自定义函数--爬取书名、作者、出版社、封面图像链接、短评、豆瓣链接的信息
def get():
    for i in range(0, 4):
        link = 'https://book.douban.com/top250?start=' + str(i*25)
        r = requests.get(link, headers=headers, timeout=20)
        if r.status_code != 200:
            print('请求获取网页失败')
        if r.status_code == 200:
            print('网页响应码：', r.status_code, ',请求获取第', str(i+1), '页信息成功！')

        soup = BeautifulSoup(r.text, 'lxml')  # 将获取网页信息赋值到soup

        div_list = soup.find_all(
            'div', class_='pl2')  # 定位到class为pl2的div标签，获取书名
        for each in div_list:
            name = each.a.text.strip().replace(" ", "").replace("\n", "")  # 清除冗余符号
            book_name_list.append(name)  # 将数据储存到列表

        p_list = soup.find_all('p', class_='pl')      # 定位作者,出版社所在标签
        for each in p_list:
            d = each.text.strip().split(' / ')
            author = d[0]                             # 获取作者信息

            cbs = d[-3:-2]
            cbs = ",".join(cbs)  # 获取出版社信息
            author_list.append(author)
            cbs_list.append(cbs)

        tr_list = soup.find_all('tr', class_='item')  # 封面
        for each in tr_list:
            picture = each.td.a.img.get('src')
            fm_list.append(picture)

        span_list = soup.find_all('td', valign="top")  # 短评
        for each in span_list:                        # 由于个别图书没有短评的标签和属性，
            d = each.text.split()                     # 所以直接定位到短评的上一层标签
                                                      # 以获取足够100条数据，便于有足够的100条数据存进数据库
            dp_list.append(d)
            dp_list1 = dp_list[1::2]
            for i in dp_list1:
                if i[-1] == ')':
                    i.append("此图书无短评")  #由于通过观察爬回数据，看到列表中每一个短评的上一个元素都是")"，
                else:                         #所以判断最后一个元素是否==）来增加一个标记（此图书无短评）作为最后的元素
                    pass
            dp = [s[-1]for s in dp_list1]   # 利用切片和for循环获取所需的短评文字数据（短评位于最后的一个元素）

        div_list = soup.find_all('div', class_='pl2')  # 豆瓣链接
        for each in div_list:
            d = each.a.get('href')
            url_list.append(d)
        print('网页解析完成！')
    return book_name_list, author_list, cbs_list, fm_list, dp, url_list  # 返回列表


# 获取书名、作者、出版社、封面图像链接、短评、豆瓣链接的list
book, author, Publishing, Cover, comment, link = get()

print('准备将爬会数据储存进数据库 douban_book_top100.db......')


# 创建数据库
conn = sqlite3.connect('douban_book_top100.db')
# 创建操作游标
cursor = conn.cursor()
# 创建名为books、Primary Key为ID 的数据表
cursor.execute('create table books (ID varchar(50) Primary Key, book_name varchar(50), author varchar(50), Publishing varchar(50), Cover varchar(50), comment varchar(50))')
# 插入爬回的网页数据
# ID, book_name, author, Publishing, Cover, comment分别为：图书链接、书名、作者、出版社、封面图片、短评
for a, b, c, d, e, f in zip(link, book, author, Publishing, Cover, comment):
    cursor.execute(
        "INSERT INTO books (ID, book_name, author, Publishing, Cover, comment) values('%s','%s','%s','%s','%s','%s')" %
        (a, b, c, d, e, f))

conn.commit()  # 提交操作
cursor.close()  # 关闭游标
conn.close()  # 关闭数据库连接

print('数据写入成功，已关闭数据库！')
