# -*- coding: utf-8 -*-
import scrapy
from scrapy.http import Request, FormRequest


class GithubSpider(scrapy.Spider):
    name = 'github'
    allowed_domains = ['github.com']
    # 头信息直接从fiddler中复制出来的
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:58.0) Gecko/20100101 Firefox/58.0',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'Accept-Language': 'zh-CN,zh;q=0.8,zh-TW;q=0.7,zh-HK;q=0.5,en-US;q=0.3,en;q=0.2',
        'Accept-Encoding': 'gzip, deflate, br',
        'Referer': 'https://github.com/',
        'Content-Type': 'application/x-www-form-urlencoded',
    }

    def start_requests(self):
        urls = ['https://github.com/login']
        for url in urls:
            # 重写start_requests方法，通过meta传入cookiejar特殊key，爬取url作为参数传给回调函数
            yield Request(url, meta={'cookiejar': 1}, callback=self.github_login)

    def github_login(self, response):
        # 首先获取authenticity_token,这里可以借助scrapy shell ”url“来获取页面
        # 然后从源码中获取到authenticity_token的值
        authenticity_token = response.xpath("//input[@name='authenticity_token']/@value").extract_first()
        self.logger.info('authenticity_token=' + authenticity_token)
        # url可以从fiddler抓取中获取,dont_click作用是如果是True，表单数据将被提交，而不需要单击任何元素。
        return FormRequest.from_response(response,
                                         url='https://github.com/session',
                                         meta={'cookiejar': response.meta['cookiejar']},
                                         headers=self.headers,
                                         formdata={'utf8': '✓',
                                                   'authenticity_token': authenticity_token,
                                                   'login': '512331228@qq.com',
                                                   'password': 'Lry0218@0129!'},
                                         callback=self.github_after,
                                         dont_click=True,
                                         )

    def github_after(self, response):
        # 获取登录页面主页中的字符串'Browse activity'
        list = response.xpath("//a[@class='tabnav-tab selected']/text()").extract()
        # 如果含有字符串，则打印日志说明登录成功
        if 'Browse activity' in list:
            self.logger.info('我已经登录成功了，这是我获取的关键字：Browse activity')
        else:
            self.logger.error('登录失败')
