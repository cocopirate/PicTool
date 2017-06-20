# -*- coding: utf-8 -*-

import os
import urlparse
import urllib2
import requests
import re
import json
from bs4 import BeautifulSoup
from PyQt5 import QtCore


# 继承 QThread 类
class ParseHtml(QtCore.QThread):
    def __init__(self, url, path):
        super(ParseHtml, self).__init__()
        self.url = url
        self.path = path

    def run(self):
        page_url = self.url
        print '正在准备下载页面代码...'
        html_data = download_page(page_url)

        if html_data:
            if 'taobao' in page_url:
                good_name, good_img_list, desc_img_list = parse_html_taobao(html_data)
                download_img(good_name, good_img_list, desc_img_list, self.path)
            elif 'tmall' in page_url:
                good_name, good_img_list, desc_img_list = parse_html_tmall(html_data)
                download_img(good_name, good_img_list, desc_img_list, self.path)
            elif 'kaola' in page_url:
                good_name, good_img_list, desc_img_list = parse_html_kaola(html_data)
                download_img(good_name, good_img_list, desc_img_list, self.path)
            elif 'jd' in page_url:
                good_name, good_img_list, desc_img_list = parse_html_jd(html_data)
                download_img(good_name, good_img_list, desc_img_list, self.path)
            elif 'hilago' in page_url:
                good_name, good_img_list, desc_img_list = parse_html_hilago(page_url)
                download_img(good_name, good_img_list, desc_img_list, self.path)
            else:
                print '目前仅支持淘宝、天猫、考拉地址、嗨啦购'


def download_page(url):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_2) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/47.0.2526.80 Safari/537.36'
    }
    try:
        if 'taobao' in url:
            data = requests.get(url, headers=headers).content.decode('gbk')
        elif 'tmall' in url:
            data = requests.get(url, headers=headers).content.decode('gbk')
        else:
            data = requests.get(url, headers=headers).content
        return data
    except requests.exceptions.RequestException as e:
        print '请求错误,错误原因：' + str(e)
        return None


# 解析考拉
def parse_html_kaola(html):
    print '页面代码下载完毕，准备解析代码中的图片地址->'

    soup = BeautifulSoup(html, 'lxml')
    good_name = soup.find('title').string

    # 抓取商品主图json
    good_img_pattern = re.compile('goodsImageList\"\:\[(.*?)]', re.S)
    good_img_code = re.findall(good_img_pattern, html)
    good_img_json = '[' + good_img_code[0] + ']'
    good_list = json.loads(good_img_json)

    good_url_list = []
    for img in good_list:
        img_url = img['imageUrl']
        good_url_list.append(img_url)

    # 抓取商品详情json
    desc_pattern = re.compile('detail\"\:\"(.*?)\",', re.S)
    desc_code = re.findall(desc_pattern, html)
    # 商品详情
    desc_soup = BeautifulSoup(desc_code[0], 'lxml')

    desc_url_list = []
    for img in desc_soup.find_all('img'):
        img_url = img.attrs['src'].replace('\\\"', '')
        if 'http:' in img_url:
            desc_url_list.append(img_url)
            print img_url
        else:
            desc_url_list.append('http:' + img_url)
            print img_url

    return good_name, good_url_list, desc_url_list


# 解析tmall
def parse_html_tmall(html):
    print '页面代码下载完毕，准备解析代码中的图片地址->'

    soup = BeautifulSoup(html, 'lxml')
    good_name = soup.find('title').string

    good_url_list = []
    good_img_soup = soup.find('ul', attrs={'id': 'J_UlThumb'})

    for img in good_img_soup.find_all('img'):
        img_url = img.attrs['src'].replace('_60x60q90.jpg', '')
        good_url_list.append('http:' + img_url)

    # 抓取商品详情json
    shop_pattern = re.compile('TShop.Setup\((.*?)\);', re.S)
    shop_setup = re.findall(shop_pattern, html)

    # 获取描述详情
    desc_url = json.loads(shop_setup[0])['api']['descUrl']

    desc_code = download_page('http:' + desc_url)

    soup = BeautifulSoup(desc_code, 'lxml')
    desc_url_list = []
    for img_tag in soup.find_all('img'):
        img_url = img_tag.attrs['src']
        if 'img.alicdn.com' in img_url:
            desc_url_list.append(img_url)

    return good_name, good_url_list, desc_url_list


# 解析taobao
def parse_html_taobao(html):
    print '页面代码下载完毕，准备解析代码中的图片地址->'

    soup = BeautifulSoup(html, 'lxml')
    good_name = soup.find('title').string

    good_url_list = []
    good_img_soup = soup.find('ul', attrs={'id': 'J_UlThumb'})

    for img in good_img_soup.find_all('img'):
        img_url = img.attrs['data-src'].replace('_50x50.jpg', '')
        good_url_list.append('http:' + img_url)

    # 抓取商品详情地址
    desc_pattern = re.compile('\? \'\/\/(.*?)\'', re.S)
    desc_url = re.findall(desc_pattern, html)

    # 获取描述详情
    desc_code = download_page('http://' + desc_url[0])

    soup = BeautifulSoup(desc_code, 'lxml')
    desc_url_list = []
    for img_tag in soup.find_all('img'):
        img_url = img_tag.attrs['src']
        if 'img.alicdn.com' in img_url:
            desc_url_list.append(img_url)

    return good_name, good_url_list, desc_url_list


# 解析jd
def parse_html_jd(html):
    print '页面代码下载完毕，准备解析代码中的图片地址->'

    soup = BeautifulSoup(html, 'lxml')
    good_name = soup.find('title').string

    # 抓取商品主图地址
    good_url_list = []
    good_img_soup = soup.find('div', attrs={'id': 'spec-list'})
    for img in good_img_soup.find_all('img'):
        if 's75x75_jfs' in img.attrs['src']:
            img_url = img.attrs['src'].replace('s75x75_jfs', 's800x800_jfs')
        elif 's54x54_jfs' in img.attrs['src']:
            img_url = img.attrs['src'].replace('s54x54_jfs', 's800x800_jfs')
        else:
            img_url = img.attrs['src'].replace('jfs', 's800x800_jfs')
        good_url_list.append('http:' + img_url)

    # 抓取商品详情地址
    desc_pattern = re.compile('desc\: \'(.*?)\',', re.S)
    desc_url = re.findall(desc_pattern, html)

    # 获取描述详情
    desc_code = download_page('http:' + desc_url[0])

    desc_url_list = []
    desc_soup = BeautifulSoup(desc_code, 'lxml')
    for img in desc_soup.find_all('img'):
        img_url = img.attrs['data-lazyload'].replace('\\\"', '')
        desc_url_list.append('http:' + img_url)

    return good_name, good_url_list, desc_url_list


# 解析hilago
def parse_html_hilago(page_url):
    print '页面代码下载完毕，准备解析代码中的图片地址->'

    good_url_list = []
    result = urlparse.urlparse(page_url)
    params = urlparse.parse_qs(result.query, True)
    good_json = download_page('https://safe.hilago.com/auction/' + params['shopId'][0] + '/' + params['auctionId'][0])
    good_info = json.loads(good_json)
    good_name = good_info['data']['auctionName']
    for img in good_info['data']['images']:
        good_url_list.append(img)
    desc_url_list = []
    desc_soup = BeautifulSoup(good_info['data']['detailUrl'], 'lxml')
    for img in desc_soup.find_all('img'):
        img_url = img.attrs['src']
        if 'https' in img.attrs['src']:
            desc_url_list.append(img_url)
        else:
            desc_url_list.append('https://safe.hilago.com'+img_url)

    return good_name, good_url_list, desc_url_list


# 下载图片
def download_img(good_name, good_img_list, desc_img_list, path):

    print '图片地址获取完毕，准备开始下载图片->'

    # 创建图片存储父目录
    file_path = path+'/'
    if not os.path.isdir(file_path):
        os.mkdir(file_path)

    # 创建某个商品的存储目录
    img_path = file_path + good_name.replace('/', '_')

    if not os.path.isdir(img_path):
        os.mkdir(img_path)

    index = 0

    # 遍历商品图片
    for img_url in good_img_list:
        try:
            download_good_img = urllib2.urlopen(img_url)
            # 保存到本地
            filename = os.path.join(img_path, 'good_img_' + str(index + 1) + '.jpg')
            with open(filename, 'wb') as f:
                f.write(download_good_img.read())
                print '正在下载第' + str(index + 1) + '张商品图片'
                index += 1
        except urllib2.URLError, e:
            print e.reason + '页面地址：' + img_url
    print '--------商品主图下载完毕，开始下载商品详情---------'
    # 创建某个商品的详情存储目录
    desc_img_path = img_path + '/detail'

    if not os.path.isdir(desc_img_path):
        os.mkdir(desc_img_path)

    index = 0

    # 遍历详情图片
    for img_url in desc_img_list:
        try:
            download_desc_img = urllib2.urlopen(img_url)
            # 保存到本地
            filename = os.path.join(desc_img_path, 'desc_img_' + str(index + 1) + '.jpg')
            with open(filename, 'wb') as f:
                f.write(download_desc_img.read())
                print '正在下载第' + str(index + 1) + '张详情图片'
                index += 1
        except urllib2.URLError, e:
            print e.reason + '页面地址：' + img_url

    print '***************本次图片下载完成！*****************'

