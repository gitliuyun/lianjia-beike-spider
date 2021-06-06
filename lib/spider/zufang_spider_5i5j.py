#!/usr/bin/env python
# coding=utf-8
# author: zengyuetian
# 此代码仅供学习与交流，请勿用于商业用途。
# 爬取租房数据的爬虫派生类

import re
import threadpool
from bs4 import BeautifulSoup
from lib.item.zufang import *
from lib.spider.base_spider import *
from lib.utility.date import *
from lib.utility.path import *
from lib.zone.area import *
from lib.zone.city import get_city
import lib.utility.version
import pymysql


class ZuFangBaseSpiderWiWj(BaseSpider):
    def collect_area_zufang_data(self, city_name, area_name, fmt="csv"):
        """
        对于每个板块,获得这个板块下所有出租房的信息
        并且将这些信息写入文件保存
        :param city_name: 城市
        :param area_name: 板块
        :param fmt: 保存文件格式
        :return: None
        """
        district_name = area_dict.get(area_name, "")
        # 开始获得需要的板块数据
        zufangs = self.get_area_zufang_info(city_name, area_name)

        db = pymysql.connect(host='127.0.0.1', port=3306, user='root', password='123456', database='lianjia',
                             charset='utf8')
        cursor = db.cursor()
        sql = "INSERT INTO zufang(district, area, xiaoqu, layout, size, price) VALUES (%s,%s,%s,%s,%s,%s)"
        try:
            # 执行sql语句
            cursor.executemany(sql, zufangs)
            # 提交到数据库执行
            db.commit()
        except Exception as e:
            db.rollback()

        # 关闭数据库连接
        db.close()
        print("Finish crawl area: " + district_name + ", save data to db")

    @staticmethod
    def get_area_zufang_info(city_name, area_name):
        matches = None
        """
        通过爬取页面获取城市指定版块的租房信息
        :param city_name: 城市
        :param area_name: 版块
        :return: 出租房信息列表
        """
        district_name = area_dict.get(area_name, "")
        chinese_district = get_chinese_district(district_name)
        chinese_area = chinese_area_dict.get(area_name, "")
        zufang_list = []
        num = 1
        # 从第一页开始,一直遍历到最后一页
        headers = create_headers()
        regex = re.compile(r'.*?href="(.+)".*?')
        while True:
            if num == 1:
                page = 'http://{0}.{1}.com/zufang/{2}'.format(city_name, SPIDER_NAME, area_name)
            else:
                BaseSpider.random_delay()
                page = 'http://{0}.{1}.com/zufang/{2}/n{3}'.format(city_name, SPIDER_NAME, area_name, num)
            print("爬取页面：" + page)
            response = requests.get(page, timeout=10, headers=headers)
            print(response)
            print(response.status_code == 200)
            if not response.status_code == 200:
                break
            html = response.content
            if '<HTML><HEAD><script>window.location.href=' in str(html):
                url = regex.search(str(html)).group(1)
                html = requests.get(url, headers=headers).text

            soup = BeautifulSoup(html, "lxml")
            print(not "下一页" in str(soup))
            # 获得有小区信息的panel
            ul_element = soup.find('ul', class_="pList")
            if ul_element is None:
                break
            house_elements = ul_element.find_all('li')

            if len(house_elements) == 0:
                continue
            # else:
            #     print(len(house_elements))

            for house_elem in house_elements:
                try:
                    price = house_elem.find('p', class_="redC").text.replace("\n", "").replace("\t", "")
                    xiaoqu = house_elem.find_all(href=re.compile("xiaoqu"))[0].next
                    layout = house_elem.find_all('i',class_="i_01")[0].next.split('·')[0]
                    size = house_elem.find_all('i',class_="i_01")[0].next.split('·')[1]
                    zufang_list.append((chinese_district, chinese_area, xiaoqu, layout, size, price))
                except Exception as e:
                    print("=" * 20 + " page no data")
                    print(e)
                    print(page)
                    print("=" * 20)
            if not "下一页" in str(soup):
                break
            else:
                num += 1
        return zufang_list

    def start(self):
        self.collect_area_zufang_data("bj", "changpingqu", fmt="csv")


if __name__ == '__main__':
    #self.collect_area_zufang_data("bj", "andingmen", fmt="csv")
    pass
