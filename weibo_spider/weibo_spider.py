from bs4 import BeautifulSoup
import urllib.request as urllib2
import requests
import time
import ssl
import re
from selenium import webdriver

def getHome_Url(name):
    code_name = urllib2.quote(name)
    url = "http://s.weibo.com/weibo/{}&Refer=STopic_box".format(code_name);
    request = urllib2.Request(url)
    html = urllib2.urlopen(request).read()
    soup = BeautifulSoup(html,"lxml",from_encoding='utf-8')
    soup = soup.find_all("script",recursive = True)
    lis = []
    for line in soup:
        line = str(line)
        ans = re.search(r"href=\\\"(.+?)\\\"\starget",line)
        if ans is None:continue
        lis.append(ans)
    if len(lis) == 0 or lis[3] is None:
        return None
    home_url = lis[3].group(1)
    home_url = urllib2.unquote(home_url)
    home_url = home_url.replace("\\","")
    return home_url
#----------------------------------------------------------
#url = "http:{}".format(getHome_Url("王菲"))
#url = "https://weibo.com/xiena?refer_flag=1001030101_&is_hot=1"
driver = webdriver.Chrome()
url = "https://weibo.com/xiena"
driver.get(url)
print(driver.page_source())
#context = ssl._create_unverified_context()
#request = urllib2.Request(url)
#html = urllib2.urlopen(request,context = context)
#soup = BeautifulSoup(html,"lxml")
print(soup)



