import Service.Website.BaseWebsite
from lxml import etree
import re
import urllib.parse
import base64
class ReadComicOnline(Service.Website.BaseWebsite.BaseWebsite):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.url = "https://readcomiconline.li"
        self.name = "readcomiconline"
        self.network_service.set_user_agent("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/134.0.0.0 Safari/537.36 Edg/134.0.0.0")
        self.comic_map = {}
        self.chapter_map = {}
        self.image_url = []

    def search(self, searchContent):
        url = self.url + "/Search/Comic"
        # 设置cookie
        with self.network_service.with_cookie("list-view=list;") as service:
            result = service.send_post_request(url, {"keyword": searchContent}, "application/x-www-form-urlencoded")
        # 将结果写入文件
        with open("search.html", "w", encoding="utf-8") as f:
            f.write(result["data"])
        # 解析数据
        tree = etree.HTML(result["data"])
        list = tree.xpath('(//*[@class="odd"])')
        comic_name_list = []
        for item in list:
            name = item.xpath('.//a')[0].text.strip()
            url = self.url+item.xpath('.//a')[0].get("href")
            self.comic_map[name] = url
            comic_name_list.append(name)
        return comic_name_list   

    def get_chapter_list(self, name):
        self.cur_comic_name = name
        url = self.comic_map[name]
        # 不需要cookie
        result = self.network_service.send_get_request(url)
        # 解析数据
        tree = etree.HTML(result["data"])
        list = tree.xpath('(//*[@class="listing"])/tr')
        chapter_list = []
        for i in range(2, len(list)):
            name = list[i].xpath('.//a')[0].text.strip()
            url = self.url+list[i].xpath('.//a')[0].get("href")
            self.chapter_map[name] = url
            chapter_list.append(name)
        chapter_list.reverse()
        return chapter_list
    
    def get_image_url(self, i):
        return self.image_url[i-1]

    def get_chapter_pages_number(self, name):
        url = self.chapter_map[name] + "&s=&quality=hq"
        result = self.network_service.send_get_request(url)
        tree = etree.HTML(result["data"])
        list = tree.xpath('(//*[@id="selectPage"])/option')
        # 同时把图片url解析出来
        text = result["data"]
        # 提取替换字符串
        pattern = r"l = l\.replace\(/(.*?)\/g, 'g'\);"
        replace_str = re.findall(pattern, text)
        # 提取图片url
        pattern = r'^\s*pht\s*=\s*(.*)'
        matches = re.findall(pattern, text, re.MULTILINE)
        self.image_url = []
        for match in matches:
            str = match.strip()
            self.image_url.append(self.parse_url(str[1:-2],replace_str[0]))
        return len(list)
    # 解析url
    def parse_url(self, url, replace_str):
        # Replace custom rules
        url = url.replace(replace_str, "g").replace("b", "pw_.g28x").replace("h", "d2pr.x_27").replace("pw_.g28x", "b").replace("d2pr.x_27", "h")

        # If the URL starts with https
        if not url.startswith("https"):
            modified_url = url
            query_string = modified_url[modified_url.index("?"):]

            if "=s0?" in modified_url:
                modified_url = modified_url[:modified_url.index("=s0?")]
            else:
                modified_url = modified_url[:modified_url.index("=s1600?")]

            modified_url = modified_url[15:33] + modified_url[50:]
            modified_url = modified_url[:len(modified_url) - 11] + modified_url[-2] + modified_url[-1]
            try:
                modified_url = base64.b64decode(modified_url).decode('utf-8')
            except:
                return url
            modified_url = urllib.parse.unquote(modified_url)

            # Remove part of the content and concatenate
            modified_url = modified_url[:13] + modified_url[17:]

            if "=s0" in url:
                modified_url = modified_url[:-2] + "=s0"
            else:
                modified_url = modified_url[:-2] + "=s1600"

            modified_url = modified_url + query_string

            url = "https://2.bp.blogspot.com/" + modified_url +"&t=2"

        return url


    