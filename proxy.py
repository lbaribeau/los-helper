import urllib2, socket, os

socket.setdefaulttimeout(10)

# read the list of proxy IPs in proxyList
proxyList = [''] # there are two sample proxy ip

def is_bad_proxy(pip):    
    try:        
        os.environ['http_proxy'] = pip 
        os.environ['HTTP_PROXY'] = pip
        os.environ['https_proxy'] = pip
        os.environ['HTTPS_PROXY'] = pip

        # proxy_handler = urllib2.ProxyHandler({'http': pip})    
        # # opener = urllib2.build_opener(proxy_handler)
        # # opener.addheaders = [('User-agent', 'Mozilla/5.0')]
        # # urllib2.install_opener(opener)
        req=urllib2.Request('http://www.google.com')  # change the url address here
        sock=urllib2.urlopen(req)
    except urllib2.HTTPError, e:        
        print 'Error code: ', e.code
        return e.code
    except Exception, detail:

        print "ERROR:", detail
        return 1
    return 0

for item in proxyList:
    if is_bad_proxy(item):
        print "Bad Proxy", item
    else:
        print item, "is working"