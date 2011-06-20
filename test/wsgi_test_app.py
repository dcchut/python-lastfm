from urlparse import urlunparse
import os
import sys
import re
if sys.version < '2.6':
    import md5
    def md5hash(string):
        return md5.new(string).hexdigest()
else:
    from hashlib import md5
    def md5hash(string):
        return md5(string).hexdigest()
"""
A simple WSGI application for testing.
"""

CACHE_PATH = os.path.join(os.path.dirname(__file__), 'data')
_app_was_hit = False

def success():
    return _app_was_hit

def test_app(environ, start_response):
    """Simplest possible application object"""
    url =  urlunparse((
                       environ['wsgi.url_scheme'],
                       environ['HTTP_HOST'],
                       environ['PATH_INFO'],
                       '',
                       environ['QUERY_STRING'],
                       ''
                       ))
    status = '200 OK'
    response_headers = [('Content-type','text/xml')]
    start_response(status, response_headers)

    global _app_was_hit
    _app_was_hit = True
    
#    old_key = md5hash(url)
    
    url_without_apikey = re.sub(r'(api_key=[^&]+.)','', url) 
    key = md5hash(url_without_apikey)
    data_file = os.path.join(CACHE_PATH, "%s.xml" % key)
    
#    old_file = os.path.join(CACHE_PATH, "%s.xml" % old_key)
#    if os.path.exists(old_file):
#        assert not os.path.exists(data_file)
##        print 'RENME'
#        os.rename(old_file, data_file)
    
#    print old_file
#    print data_file
#    print url
#    print url_without_apikey
    
#    assert False
    try:
        filedata = open(data_file).read()
    except IOError:
        #print "\nintercepted: %s" % url
        #print "old_key:", old_key 
        import wsgi_intercept
        wsgi_intercept.remove_wsgi_intercept('ws.audioscrobbler.com', 80)
        import urllib2
        filedata = urllib2.urlopen(url).read()
        wsgi_intercept.add_wsgi_intercept('ws.audioscrobbler.com', 80, create_wsgi_app)
        open(data_file, "w").write(filedata)
    return [filedata]

def create_wsgi_app():
    global _app_was_hit
    _app_was_hit = False
    return test_app

if __name__ == "__main__":
    from wsgi_intercept.urllib2_intercept import install_opener
    install_opener()
    import wsgi_intercept
    wsgi_intercept.add_wsgi_intercept('ws.audioscrobbler.com', 80, create_wsgi_app)
    import urllib2
    print urllib2.urlopen('http://ws.audioscrobbler.com/2.0/?album=Supersonic&api_key=152a230561e72192b8b0f3e42362c6ff&artist=Oasis&method=album.getInfo').read()