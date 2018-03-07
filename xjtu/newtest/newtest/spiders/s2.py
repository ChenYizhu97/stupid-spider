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
    contact = scrapy.Field()
    direction = scrapy.Field()
    wanted = scrapy.Field()
    project = scrapy.Field()



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
            'http://gr.xjtu.edu.cn/web/hrcao',
            ]
    prefix = "http://gr.xjtu.edu.cn"
    item_lists = list()
    def parse(self,response):
        tech_name = "remain"
        newtech_item = tech_item()
        self.item_lists.append(newtech_item)
        sel = response.xpath('//div[re:test(div/div/@class,"portlet-topper")]')[0]
        sel = sel.xpath('.//div[@align="left"]')
        src = sel.xpath('.//img/@src').extract()[0]
        src_url = self.prefix+src
        abstract = sel.xpath(".//text()").extract()
        abstract = [x.replace(u"\xa0","").strip() for x in abstract]
        abstract = ' '.join([x for x in abstract if x != ""])
        #---填充信息---
        newtech_item['name'] = tech_name
        newtech_item['img'] = src_url
        newtech_item['abstract'] = abstract
        #---填充信息完---
        navi = response.xpath('//div[@id="navigation"]/ul/li')
        for x in navi: 
            name = x.xpath('a/span/text()').extract()[0]
            href = x.xpath('a/@href').extract()[0]
            href = self.prefix+href
            #navi_li[name] = href
            ans = self.dispatch(name,href,newtech_item)
            if ans is not None:
                yield ans
        
    def dispatch(self,name,href,item):
        meta = {"item":item}
        if re.search("人才|招生",name) is not None:
            #print(name,href)
            return Request(href,callback=self.wanted_parse,meta = meta)
        elif re.search("项目|科研|结果|成果",name) is not None:
            return Request(href,callback=self.project_parse,meta = meta)
        elif re.search("方向|领域",name) is not None:
            return Request(href,callback=self.direction_parse,meta = meta)
        elif re.search("联系|方式|地址",name) is not None:
            return Request(href,callback=self.contact_parse,meta = meta)
        
        
        
    def wanted_parse(self,response):
        item = response.meta['item']
        item['wanted'] = self.page_parse(response)

    def direction_parse(self,response):
        item = response.meta['item']
        item['direction'] = self.page_parse(response)
    
    def project_parse(self,response):
        item = response.meta['item']
        item['project'] = self.page_parse(response)

    def contact_parse(self,response):
        item = response.meta['item']
        item['contact'] = self.page_parse(response)
        

    def page_parse(self,response):
        ans = dict()
        portlets = response.xpath('//div[@class="portlet"]')
        rereobj = re.compile(u'\xa0|\x0a|\x09|\3000')
        for x in portlets:
            name = x.xpath('div[@class="portlet-topper"]//text()').extract()
            name = ' '.join(name).strip()
            content = x.xpath('div[@class="portlet-content"]//text()').extract()
            content = ' '.join([rereobj.subn('',y)[0] for y in content])
            flag = x.xpath('.//script[contains(@type,"java")]')
            if len(flag) != 0:
                continue
            ans[name] = content
            #name_content = ' >\n'.join((name,content))

        return ans
       
    def closed(self,reason):
        print(self.item_lists)


        
