"""
    基础api封装，
    所有api请求的基础类
"""
import token
from pathlib import Path

import requests
import allure
import json

import yaml


class BaseAPI:
   """
            api基础类
   """
   def __init__(self,base_url,timeout):
       """
       初始化 API 客户端
       :param base_url: 接口基础地址
       :param timeout : 请求时间超时
       """
       # config_path = Path(__file__).parent/"config"/"config.yaml"
       # with open(config_path,"r",encoding="utf-8") as f:
       #    config = yaml.safe_load(f)
       self.base_url = base_url
       self.timeout = timeout
       """
       创建session请求会话对象，在后面的request中使用
       如果不去创建，就会导致后面请求的时候，每次都要创建连接
       """

       self.session = requests.session()
       # 设置默认 Headers，所有请求自动带上
       self.session.headers.update({
           "User-Agent": "MyTestFramework/1.0",
           "Accept": "application/json"
       })

       # 如果提供了 token，自动添加到所有请求
       if token:
           self.session.headers.update({
               "Authorization": f"Bearer {token}"
           })




   def _get_url(self,path):
       """
       拼接完整的URL
       规定url格式，例如：https://123.4546/pet/
                       https://123.4546/pet
       :return: 完整url
       """
       return f"{self.base_url}{path}"

   def _log_request(self,method,url,**kwargs):
       """
       记录请求日志:记录http请求的详细信息，并将这些信息附加到allure报告中
       :param method:  记录请求使用的方法
       :param url: 请求的路径
       :param kwargs: **kwargs 表示任意数量的关键字参数
       :return: 日志信息
       """
       allure.attach(
                     f"Method: {method}", # 内容：例如：“Method ：POST”
                     name="请求方法", # 附件名称
                     attachment_type=allure.attachment_type.TEXT # 附件类型
                     )
       allure.attach(url,name="请求URL",attachment_type=allure.attachment_type.TEXT)
       # 如果有json请求体 ， 记录请求体
       if 'json' in kwargs:
           allure.attach(
               json.dumps(kwargs['json'], # 请求体数据
                          indent=2, # 缩进两格--美观
                          ensure_ascii=False), # 支持中文显示
               name="请求体", # 附件名称
               attachment_type=allure.attachment_type.JSON # 附件类型为json类型
           )

   def _log_response(self,response):
       """
       记录响应日志
       :param response:
       :return:
       """
       allure.attach(str(response.status_code),name="响应状态码",attachment_type=allure.attachment_type.TEXT)
       try:
           allure.attach(
               json.dump(response.json(),indent=2,ensure_ascii=False),
               name="响应体",
               attachment_type=allure.attachment_type.JSON
           )
       except:
           allure.attach(response.text, name="响应体", attachment_type=allure.attachment_type.TEXT)

   @allure.step("发送{method}请求")
   def _request(self,method,path,**kwargs):
       """
       发送HTTP请求
       @allure.step("发送{method}请求") 整个函数是一个步骤 让报告清晰展示执行流程
       :param method: 请求方法
       :param path:  请求路径
       :param kwargs: 请求的其他参数
       :return:
       """
       # 确保 path 以 / 开头
       if not path.startswith('/'):
           path = '/' + path

       url = self._get_url(path)
       self._log_request(method,url,**kwargs)
       response = self.session.request(
           method = method,
           url= url,
           timeout = self.timeout,
           **kwargs
       )
       self._log_response(response)

       # 4. 添加响应时间到报告
       elapsed_ms = response.elapsed.total_seconds() * 1000
       allure.attach(f"{elapsed_ms:.0f}ms", name="响应时间")

       return response

   def get(self,path,**kwargs):
       return self._request("GET",path,**kwargs)

   def post(self,path,**kwargs):
       return self._request("POST",path,**kwargs)

   def put(self,path,**kwargs):
       return self._request("PUT",path,**kwargs)

   def delete(self, path, **kwargs):
       """发送 DELETE 请求"""
       return self._request("DELETE", path, **kwargs)
