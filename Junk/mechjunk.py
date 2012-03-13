import mechanize, cookielib, urlparse, re

availableUserAgents = {
    'old':      'Mozilla/5.0 (X11; U; Linux i686; en-US; rv:1.9.0.1) Gecko/2008071615 Fedora/3.0.1-1.fc9 Firefox/3.0.1',
    'ie9':      'Mozilla/5.0 (Windows; U; MSIE 9.0; Windows NT 9.0; en-US)',
    'ie8':      'Mozilla/5.0 (compatible; MSIE 8.0; Windows NT 5.1; Trident/4.0; .NET CLR 1.1.4322; .NET CLR 2.0.50727)',
    'ff':       'Mozilla/5.0 (Windows NT 6.2; rv:9.0.1) Gecko/20100101 Firefox/9.0.1',
    'chrome':   'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/535.2 (KHTML, like Gecko) Chrome/18.6.872.0 Safari/535.2 UNTRUSTED/1.0 3gpp-gba UNTRUSTED/1.0',
    'safari':   'Mozilla/5.0 (Macintosh; U; Intel Mac OS X 10_6_8; de-at) AppleWebKit/533.21.1 (KHTML, like Gecko) Version/5.0.5 Safari/533.21.1',
    'opera':    'Opera/9.80 (Windows NT 6.1; U; es-ES) Presto/2.9.181 Version/12.00'
}
    
class BrowserInstance(object):
    def __init__(self, uagent="old"):
        self.b = mechanize.Browser()
        self.cj = cookielib.LWPCookieJar()
        self.b.set_cookiejar(self.cj)
        self.b.set_handle_equiv(True)
        self.b.set_handle_gzip(False)
        self.b.set_handle_redirect(True)
        self.b.set_handle_referer(True)
        self.b.set_handle_robots(False)
        self.b.set_handle_refresh(mechanize._http.HTTPRefreshProcessor(), max_time=1)
        self.b.addheaders = [('User-agent', availableUserAgents[uagent])]

b = BrowserInstance().b
b.open("http://ducot.netdocuments.com")
b.select_form(nr=0)
b['username'] = 'nd.automated-drone_150'
b['password'] = 'snoopy'
b.submit()

r = b.click_link(text='Search')
b.open(r)

b.select_form(nr=0)
b['criteria'] = '"DRONEFOLDER_150"'
b.submit()

r = b.click_link(text="DRONEFOLDER_150")
b.open(r)

linkDict = {}
for link in b.links():
    linkDict.setdefault(link.text, link)

for k in linkDict.keys():
    print linkDict[k].text

r = b.click_link(text="doc_150_5_1330709380")
b.open(r)

a = b.response().read()

print a

result = re.search('cFilePath: </span><b>(.*)</b>', a)
print result.groups()
result = re.search('File extension:</span> <b>.(\w+)</b>', a)
print result.groups()[0]

##r = b.click_link(text="Download")
##b.open(r)
##
##a = b.response().read()
##
##print len(a)
##
##with open("temp.png", "wb") as f:
##    f.write(a)

