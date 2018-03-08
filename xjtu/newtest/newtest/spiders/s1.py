import scrapy
import sys
from scrapy.http import Request
from scrapy.selector import HtmlXPathSelector
import re
import urllib
import os
import pymysql
#print(sys.path)

class tech_item(scrapy.Item):
    name = scrapy.Field()
    img = scrapy.Field()
    college = scrapy.Field()
    abstract = scrapy.Field()
    contact = scrapy.Field()
    direction = scrapy.Field()
    wanted = scrapy.Field()
    project = scrapy.Field()

class S1Spider(scrapy.spiders.Spider):
    
    #类属性
    name = "s1"
    allowed_domains = ["xjtu.edu.cn"]
    start_urls = [
            "http://gr.xjtu.edu.cn/web/guest"
            ]
    college_list = dict()
    alpha_list = dict()
    cnt = 0
    prefix = "http://gr.xjtu.edu.cn"
    item_lists = list()
    conn = None
    

    def __init__(self,category = 0,*args,**kwargs):
        super(S1Spider,self).__init__(*args,*kwargs)
        self.college_idx = int(category)
        self.init()

    def init(self):
        print('尝试连接数据库...')
        try:
            self.conn = pymysql.connect(host='127.0.0.1', port=3306, user='root'
                       , passwd='csf123mlp', db='Spider', charset='utf8')
            print('数据库已连接!')
        except:
            print('数据库连接失败!')            

        #debug代码
        #newitem = tech_item()
        #newitem['name'] = '蔡少斐'
        #newitem['college'] = '软件学院'
        #self.item_lists.append(newitem)
        #self.closed(1)

    def parse(self,response):
        current_url = response.url
        if current_url == "http://gr.xjtu.edu.cn/web/guest":
            items = response.xpath('//td[@width="20%"]/a')
            for idx,x in enumerate(items):
                if idx != self.college_idx+25:
                    continue
                #if idx < 25: continue
                #if idx > 51:
                    #break
                name = x.xpath('text()').extract()[0]
                href = x.xpath('@href').extract()[0]
                self.college_list[name] = href
                yield Request(href,callback=self.parse,meta={'college':name})
        elif current_url.startswith('http://gr.xjtu.edu.cn/web/guest/home'):
            items = response.xpath('//td[@align="center"]/a')
            for idx,x in enumerate(items):
                alpha = x.xpath('text()').extract()[0]
                href = x.xpath('@href').extract()[0]
                yield Request(href,callback=self.alpha_parse,meta = response.meta)
            
    
    def alpha_parse(self,response):
        current_url = response.url
        if current_url.startswith('http://gr.xjtu.edu.cn/web/guest/home'):
            items = response.xpath('//td[@width="25%"]//a')
            for idx,x in enumerate(items):
                name = x.xpath('text()').extract()[0]
                href = x.xpath('@href').extract()[0]
                self.cnt += 1
                #print('idx:',self.cnt)
                college = response.meta['college']
                yield Request(href,callback = self.dimension_parse,meta = {'name':name,'college':college})

    def dimension_parse(self,response):
        tech_name = response.meta['name']
        college_name = response.meta['college']
        newtech_item = tech_item()
        src_url = ""
        abstract = ""
        self.item_lists.append(newtech_item)
        sel = response.xpath('//div[re:test(div/div/@class,"portlet-topper")]')
        if len(sel) != 0:
            sel = sel[0]
        #print(tech_name)
            sel = sel.xpath('.//div[@align="left"]')
            src = sel.xpath('.//img/@src').extract()
            if len(src) != 0:
                src_url = self.prefix+src[0]
        #print(src_url)
            abstract = sel.xpath(".//text()").extract()
            abstract = [x.replace(u"\xa0","").strip() for x in abstract]
            abstract = ' '.join([x for x in abstract if x != ""])
        #---填充信息---
        newtech_item['name'] = tech_name
        newtech_item['img'] = src_url
        newtech_item['abstract'] = abstract
        newtech_item['college'] = college_name
        #---填充信息完---
        navi = response.xpath('//div[@id="navigation"]/ul/li')
        for x in navi: 
            name = x.xpath('a/span/text()').extract()
            if len(name) == 0:
                continue
            name = name[0]
            href = x.xpath('a/@href').extract()[0]
            href = self.prefix+href
            #navi_li[name] = href
            ans = self.dispatch(name,href,newtech_item)
            if ans is not None:
                yield ans
        
    def dispatch(self,name,href,item):
        meta = {"item":item}
        print('爬取中...','姓名:',item['name'],'板块:',name)
        if re.search("人才|招生|本科生|研究生|学生",name) is not None:
            #print(name,href)
            return Request(href,callback=self.wanted_parse,meta = meta)
        elif re.search("项目|科研|结果|成果",name) is not None:
            return Request(href,callback=self.project_parse,meta = meta)
        elif re.search("方向|领域|",name) is not None:
            return Request(href,callback=self.direction_parse,meta = meta)
        elif re.search("联系|方式|地址|沟通",name) is not None:
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
    
    def unquote(self):
        for item in self.item_lists:
            for key,content in item.items():
                if type(content) != type(''):
                    continue
                content = content.replace('\"','\\\"')
                content = content.replace('\'','\\\'')
                if len(content) >10000:
                    content = content[0:10000]
                item[key] = content
            if len(item['img']) > 1000:
                item['img'] = ''

    def insert_dict(self,table,fid,dic):
        sql = 'insert into {}(fid,tag,content) values({},%s,%s)'.format(table,fid)
        cursor = self.conn.cursor()
        for tag,content in dic.items():
            #print(fid,tag,content,type(fid),sql)
            if len(content) > 10000:
                content = content[0:10000]
            print('写入表:',table,'长度:',len(content))
            cursor.execute(sql,(tag,content))
        cursor.close()

    def clear(self):
        cursor = self.conn.cursor()
        cursor.execute('delete from Tech_Base')
        cursor.execute('delete from Tech_Contact')
        cursor.execute('delete from Tech_Direction')
        cursor.execute('delete from Tech_Project')
        cursor.execute('delete from Tech_Wanted')
        self.conn.commit()
        cursor.close()

    def closed(self,reason):
        #self.clear()
        self.unquote() #清洗引号
        cursor = self.conn.cursor()
        for item in self.item_lists:
            iname = item.get('name','')
            icollege = item.get('college','')
            iimg = item.get('img','')
            iabstract = item.get('abstract','')
            iproject = item.get('project',dict())
            iwanted = item.get('wanted',dict())
            icontact = item.get('contact',dict())
            idirection = item.get('direction',dict())
            fsql = "select id from Tech_Base where college = %s and name = %s"
            cursor.execute(fsql,(icollege,iname))
            fo = cursor.fetchone()
            if fo is not None:
                #delete
                sql = "delete from Tech_Base where college = %s and name = %s"
                cursor.execute(sql,(icollege,iname))
                print("提示:删除条目... 姓名:",iname)
            sql = '''insert into Tech_Base(name,college,img,abstract)
            values(%s,%s,%s,%s)'''
            cursor.execute(sql,(iname,icollege,iimg,iabstract))
            print('提示:生成条目... 姓名:',iname)
            cursor.execute(fsql,(icollege,iname))
            fo = cursor.fetchone()
            fid = int(fo[0])
            self.insert_dict('Tech_Contact',fid,icontact)
            self.insert_dict('Tech_Project',fid,iproject)
            self.insert_dict('Tech_Wanted',fid,iwanted)
            self.insert_dict('Tech_Direction',fid,idirection)

        self.conn.commit()
        print('提示:提交数据库...')
        cursor.close()
        print('提示:断开连接！')
        self.conn.close()
        
