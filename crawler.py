import requests
from lxml import etree

BLANK_IMG = "BLANK_IMG"


class Spider:
    @staticmethod
    def crawler(url):
        headers = {"User-Agent": "Mozilla/5.0 (Windows; U; Windows NT 5.1; zh-CN; rv:1.9.1.6) ",
                   "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
                   "Accept-Language": "en-us",
                   "Connection": "keep-alive",
                   "Accept-Charset": "GB2312,utf-8;q=0.7,*;q=0.7"}
        r = requests.get(url, headers=headers, timeout=5)
        print(f"Request Generated! (GET: {url})")
        if r.status_code == 200:
            print("Server Response: 200-OK")
            return r.text
        else:
            print(f"Server Response: {r.status_code}")
            return "error"

    @staticmethod
    def error():
        pass

    class Search:
        def __init__(self, keyword):
            self.keyword = keyword.split(" ")
            self.search_url = "https://flingtrainer.com/?s="
            for kw in self.keyword:
                self.search_url += kw + "+"
            self.search_url = self.search_url[:-1]

            self.sub_names = None
            self.sub_links = None
            self.sub_images = None
            self.text = Spider.crawler(self.search_url)
            if self.text != "error":
                self.parser()
            else:
                Spider.error()

        def run(self):
            re_list = []
            for i in range(len(self.sub_links)):
                if "My Trainers Archive" in self.sub_names[i]:
                    break
                print(f"Name: {self.sub_names[i]} | Link: {self.sub_links[i]} | Image: {self.sub_images[i]}")
                re_list.append([self.sub_names[i], self.sub_links[i], self.sub_images[i], "COMMON"])
            return re_list

        def parser(self):
            html = etree.HTML(self.text)
            # self.sub_names = html.xpath()
            self.sub_names = html.xpath("//div[@class='content']/article/div[2]/h2/a/text()")
            self.sub_links = html.xpath("//div[@class='content']/article/div[2]/h2/a/@href")
            self.sub_images = html.xpath("//div[@class='content']/article/div[1]/div/a/img/@src")
            if self.sub_names and self.sub_names[-1] == "My Trainers Archive (From 2012-2019.05)":
                self.sub_images.append(BLANK_IMG)

    class Download:
        def __init__(self, detail_url):
            self.detail_url = detail_url
            self.download_name = None
            self.download_link = None
            self.download_size = None
            self.download_count = None
            self.download_date = None
            self.text = Spider.crawler(self.detail_url)
            if self.text != "error":
                self.parser()
            else:
                Spider.error()
            self.parser()

        def run(self):
            re_list = []
            for i in range(len(self.download_name)):
                print(
                    f"Name: {self.download_name[i]} | Link: {self.download_link[i]} | Size: {self.download_size[i]} | Count: {self.download_count[i]} | Date: {self.download_date[i]}")
                re_list.append(
                    [self.download_name[i], self.download_link[i], self.download_size[i], self.download_count[i],
                     self.download_date[i]])

            return re_list

        def parser(self):
            html = etree.HTML(self.text)
            self.download_name = html.xpath("//table[@class='da-attachments-table']/tbody/tr/td[1]/a/text()")
            self.download_link = html.xpath("//table[@class='da-attachments-table']/tbody/tr/td[1]/a/@href")
            self.download_date = html.xpath("//table[@class='da-attachments-table']/tbody/tr/td[2]/text()")
            self.download_size = html.xpath("//table[@class='da-attachments-table']/tbody/tr/td[3]/text()")
            self.download_count = html.xpath("//table[@class='da-attachments-table']/tbody/tr/td[4]/text()")

    class ArchivedDownload:
        def __init__(self, keyword):
            self.name_list = []
            self.link_list = []
            self.url = "https://archive.flingtrainer.com/"
            self.text = Spider.crawler(self.url)
            self.keyword = keyword.split(" ")
            self.result_name = []
            self.result_link = []
            self.parser()

        def parser(self):
            html = etree.HTML(self.text)
            print("html", html)
            self.name_list = html.xpath("//table[@class='files']/tr/td/a/text()")
            self.link_list = html.xpath("//table[@class='files']/tr/td/a/@href")

        def run(self):
            print("Keywords: ", self.keyword)
            match = False
            for name in self.name_list:
                for kw in self.keyword:
                    if name.lower().find(kw.lower()) == -1:
                        match = False
                        break
                    match = True
                if match:
                    index = self.name_list.index(name)
                    self.result_name.append(self.name_list[index])
                    self.result_link.append(self.link_list[index])
            re_list = []
            for i in range(len(self.result_name)):
                print(f"Name: {self.name_list[i]} | Link: {self.link_list[i]}")
                re_list.append(
                    [self.name_list[i], "https://archive.flingtrainer.com/" + self.link_list[i], BLANK_IMG, "ARCHIVED"])
            return re_list
