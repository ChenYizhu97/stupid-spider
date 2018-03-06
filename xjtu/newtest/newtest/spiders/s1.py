import scrapy
import sys
from scrapy.http import Request
from scrapy.selector import HtmlXPathSelector
import re
import urllib
import os
#print(sys.path)
#import newtest.spiders.s2.tech_parser

class S1Spider(scrapy.spiders.Spider):
    name = "s1"
    allowed_domains = ["xjtu.edu.cn"]
    start_urls = [
            "http://gr.xjtu.edu.cn/web/guest"
            ]
    college_list = dict()
    alpha_list = dict()
    cnt = 0
    def parse(self,response):
        current_url = response.url
        if current_url == "http://gr.xjtu.edu.cn/web/guest":
            items = response.xpath('//td[@width="20%"]/a')
            for idx,x in enumerate(items):
                if idx < 25: continue
                if idx > 51:
                    break
                name = x.xpath('text()').extract()[0]
                href = x.xpath('@href').extract()[0]
                self.college_list[name] = href
                yield Request(href,callback=self.parse)
        elif current_url.startswith('http://gr.xjtu.edu.cn/web/guest/home'):
            items = response.xpath('//td[@align="center"]/a')
            for idx,x in enumerate(items):
                alpha = x.xpath('text()').extract()[0]
                href = x.xpath('@href').extract()[0]
                #print(href)
                yield Request(href,callback=self.alpha_parse)
            

    def alpha_parse(self,response):
        current_url = response.url
        if current_url.startswith('http://gr.xjtu.edu.cn/web/guest/home'):
            items = response.xpath('//td[@width="25%"]//a')
            for idx,x in enumerate(items):
                name = x.xpath('text()').extract()[0]
                href = x.xpath('@href').extract()[0]
                self.cnt += 1
                #print(self.cnt,name)
                yield Request(href,callback = self.selfhome_parse)

    prefix = "http://gr.xjtu.edu.cn"
    tech_name = ""
    def selfhome_parse(self,response):
        #sel = response.xpath('//div[re:test(div/span/text(),"基本信息|个人简介")]')
        sel = response.xpath('//div[re:test(div/div/@class,"portlet-topper")]')[0]
        #print(sel.extract())
        sel = sel.xpath('.//div[@align="left"]')
        src = sel.xpath('.//img/@src').extract()[0]
        src_url = self.prefix+src
        abstract = sel.xpath(".//text()").extract()
        abstract = [x.replace(u"\xa0","").strip() for x in abstract]
        abstract = [x for x in abstract if x != ""]
        print('姓名:',self.tech_name)
        print('照片:',src_url)
        print('个人简介:',abstract)
        print('----------------------') 
        
        
