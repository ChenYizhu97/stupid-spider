import urllib.request as sed
import ssl
from bs4 import BeautifulSoup as BS
if __name__  == '__main__':
    ctx = ssl._create_unverified_context()
    '''Httphandler = sed.HTTPHandler(debuglevel=1)
    Httpshandler = sed.HTTPSHandler(debuglevel=1)
    opener = sed.build_opener(Httphandler,Httpshandler)
    sed.install_opener(opener)
    '''
    url = 'https://baike.baidu.com/item/Scala/2462287?fr=aladdin'

    res = sed.urlopen(url,context=ctx).read().decode('utf-8')
    soup = BS(
        res,
        'html.parser'
    )
    res = soup.find_all('div',class_='lemma-summary')
    for i in res:
        r = i.findAll('a')
        for i in r:
            if(i.has_attr('href')):
                print(sed.unquote(i['href']))