import json
import os
import requests
from urllib.parse import urlencode
from tqdm import tqdm  # 用于显示下载进度条
from contextlib import contextmanager
class NetworkService:
    """ 通用网络请求服务类，支持 GET、POST、文件下载等 """
    
    def __init__(self):
        self.user_agent = ""
        self.cookie = ""
        self.host = ""
        
    def send_get_request(self, url: str):
        """ 发送 GET 请求，获取网页数据 """
        headers = {}
        if self.user_agent and self.user_agent != "":
            headers["User-Agent"] = self.user_agent
        if self.cookie and self.cookie != "":
            headers["Cookie"] = self.cookie
        if self.host and self.host != "":
            headers["Host"] = self.host
        try:
            response = requests.get(url, headers=headers)
            response.raise_for_status()  # 检查响应状态
            return {"data": response.text}  # 返回网页数据
        except requests.exceptions.RequestException as e:
            return {"error": str(e)}
        

    def send_post_request(self, url: str, data: dict, content_type: str = "application/json"):
        """发送 POST 请求，支持 JSON 和 x-www-form-urlencoded 格式"""
        headers = {}
        if self.user_agent and self.user_agent != "":
            headers["User-Agent"] = self.user_agent
        if self.cookie and self.cookie != "":
            headers["Cookie"] = self.cookie
        if self.host and self.host != "":
            headers["Host"] = self.host
            
        if content_type == "application/json":
            headers["Content-Type"] = "application/json"
            try:
                response = requests.post(url, headers=headers, json=data)
                response.raise_for_status()
                return {"data": response.text}
            except requests.exceptions.RequestException as e:
                return {"error": str(e)}
        elif content_type == "application/x-www-form-urlencoded":
            headers["Content-Type"] = "application/x-www-form-urlencoded"
            try:
                response = requests.post(url, headers=headers, data=urlencode(data))
                response.raise_for_status()
                # 记录cookie
                if "Set-Cookie" in response.headers:
                    self.cookie = response.headers["Set-Cookie"]
                return {"data": response.text}
            except requests.exceptions.RequestException as e:
                return {"error": str(e)}
        else:
            return {"error": "Unsupported content type"}

    def download_file(self, url: str, save_path: str):
        """ 下载文件，并通过进度条显示下载进度 """
        headers = {"User-Agent": self.user_agent} if self.user_agent else {}
        if self.cookie:
            headers["Cookie"] = self.cookie

        try:
            with requests.get(url, headers=headers, stream=True) as response:
                response.raise_for_status()
                total_size = int(response.headers.get('content-length', 0))
                with open(save_path, "wb") as f, tqdm(
                        desc=save_path,
                        total=total_size,
                        unit='B',
                        unit_scale=True) as bar:
                    for chunk in response.iter_content(chunk_size=8192):
                        if chunk:
                            f.write(chunk)
                            bar.update(len(chunk))  # 更新进度条

            return {"status": "success", "path": save_path}
        except requests.exceptions.RequestException as e:
            return {"error": str(e)}

    def set_user_agent(self, user_agent: str):
        """ 设置 User-Agent """
        self.user_agent = user_agent

    def set_cookie(self, cookie: str):
        """ 设置 Cookie """
        self.cookie = cookie
    def set_host(self,host:str):
        self.host = host
    @contextmanager
    def with_cookie(self, cookie):
        self.set_cookie(cookie)
        try:
            yield self
        finally:
            self.set_cookie("")  # 清除 cookie

