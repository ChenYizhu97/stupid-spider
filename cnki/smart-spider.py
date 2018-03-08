from selenium import webdriver
from selenium.webdriver.support.select import Select
from time import sleep
#每个老师爬取所有论文会出现验证码，解决比较麻烦。
#每个老师只爬被引用次数最多的20篇(内)论文，出错重启
#注释掉的为爬取所有论文所需代码
'''
def getNextPage(driver,str):
    try:
        tmp = browser.find_elements_by_xpath(str)
        for i in tmp:
            if i.text == '下一页':
                print(i.text)
                return i
        return None
    except :
        print('asdsa')
        return None
'''
def atomic(browser,teacher):
    url = 'http://kns.cnki.net/kns/brief/default_result.aspx'
    browser.get(url)
    browser.implicitly_wait(6)
    text = browser.find_element_by_id('txt_1_value1')
    text.clear()
    #搜索老师论文
    text.send_keys(teacher)
    option = Select(browser.find_element_by_id('txt_1_sel'))
    #按作者搜索
    option.select_by_index(3)
    button = browser.find_element_by_id('btnSearch')
    button.submit()
    #停两秒，等待分类栏加载完
    sleep(3)
    #选择机构->XJTU
    link = browser.find_element_by_id('alink3')
    link.click()
    sleep(0.5)
    try:
        linkm = browser.find_elements_by_xpath('//a[@name="groupPager"]')
        for lm in linkm:
            if lm.text == '>>':
                break
        lm.click()
        sleep(0.5)
    except:
        pass
    try:
        linkt = browser.find_element_by_xpath('//span[@title1="点击显示 ‘西安交通大学’ 的分组结果"]')
    except:
        return ['']
    linkt.click()
    #等待论文加载
    sleep(1)
    #按被引用排序
    browser.switch_to.frame(1)
    links = browser.find_element_by_xpath('//table[@class="taxis"]//td[@align="left"]/span[4]/a')
    links.click()
    sleep(1)
    '''
    next = getNextPage(browser,'//a[@title="键盘的“← →”可以实现快速翻页"]')
    j = 0
    while next:
        j =(j + 1)%6+1.5
        items = browser.find_elements_by_xpath('//table[@class="GridTableContent"]//tr[@bgcolor]')
        for i in items:
            sequence = i.find_element_by_xpath('./td[1]').text
            title = i.find_element_by_xpath('./td[2]/a').get_attribute('href')
            author = i.find_element_by_xpath('./td[3]').text
            source = i.find_element_by_xpath('./td[4]').text
            data = i.find_element_by_xpath('./td[5]').text
            tag = i.find_element_by_xpath('./td[6]').text
            num = i.find_element_by_xpath('./td[7]').text
            print(sequence,title,author,source,data,num)
        next.click()
        print(next.text)
        print('------------------')
        sleep(j)
        next = getNextPage(browser, '//a[@title="键盘的“← →”可以实现快速翻页"]')
    '''
    items = browser.find_elements_by_xpath('//table[@class="GridTableContent"]//tr[@bgcolor]')
    l=[]
    for i in items:
        item = []
        item.append(i.find_element_by_xpath('./td[1]').text)
        item.append(i.find_element_by_xpath('./td[2]').text)
        item.append(i.find_element_by_xpath('./td[2]/a').get_attribute('href'))
        item.append(i.find_element_by_xpath('./td[3]').text)
        item.append(i.find_element_by_xpath('./td[4]').text)
        item.append(i.find_element_by_xpath('./td[5]').text)
        item.append(i.find_element_by_xpath('./td[6]').text)
        item.append(i.find_element_by_xpath('./td[7]').text)
        l.append(item)
    return l

if __name__ == '__main__':
    browser = webdriver.Chrome()
    index = 0
    with open('namelist.txt') as namlist:
        teachers = namlist.read().split(',')
        print(len(teachers))
        with open('results.txt','a') as res:
            while(index < len(teachers)):
                try:
                    results = atomic(browser,teachers[index])
                    sleep(1)
                    res.write(teachers[index] + '\n')
                    for item in results:
                        for col in item:
                            res.write(col+',')
                        res.write('\n')
                    res.flush()
                    index += 1
                    print('开始爬取第：'+str(index)+' 位老师: '+teachers[index])
                except:
                    print('本次爬取出现异常，重新爬取第: '+str(index)+' 位老师: '+teachers[index])
                    continue
    browser.close()