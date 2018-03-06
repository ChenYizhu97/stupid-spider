import scrapy
from scrapy.http import Request
from scrapy.selector import HtmlXPathSelector
import re
import urllib
import os

class tech_item(scrapy.Item):
    name = scrapy.Field()
    img = scrapy.Field()
    abstract = scrapy.Field()
    info_dict = scrapy.Field()



class tech_parser(scrapy.spiders.Spider):
    name = "tech_parser"
    allowed_domains = ['xjtu.edu.cn']
    start_urls = [
            'http://gr.xjtu.edu.cn/web/dunnlu',
            'http://gr.xjtu.edu.cn/web/chenw',
            'http://gr.xjtu.edu.cn/web/xwzhang',
            'http://gr.xjtu.edu.cn/web/jhong',
            'http://gr.xjtu.edu.cn/web/ke.huang',
            'http://gr.xjtu.edu.cn/web/caojy',
            ]
    prefix = "http://gr.xjtu.edu.cn"
    #tech_name = ""
    def parse(self,response):
        sel = response.xpath('//div[re:test(div/div/@class,"portlet-topper")]')[0]
        sel = sel.xpath('.//div[@align="left"]')
        src = sel.xpath('.//img/@src').extract()[0]
        src_url = self.prefix+src
        abstract = sel.xpath(".//text()").extract()
        abstract = [x.replace(u"\xa0","").strip() for x in abstract]
        abstract = ' '.join([x for x in abstract if x != ""])
        #print('姓名:',self.tech_name)
        navi = response.xpath('//div[@id="navigation"]/ul/li')
        #print(navi)
        navi_li = dict()
        for x in navi: 
            name = x.xpath('a/span/text()').extract()[0]
            href = x.xpath('a/@href').extract()[0]
            href = response.url+href
            navi_li[name] = href
 
        print('照片:',src_url)
        print('个人简介:',abstract)
        print('导航栏信息:',navi_li)
        print('----------------------')


    def wanted_parse(self,response):
        pass

        
