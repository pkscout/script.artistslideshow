import requests
    
__timeout__    = 10
__headers__    = ''
__returntype__ = 'text'


class URL():
    def __init__( self, returntype='text', headers='', timeout=10 ):
        global __timeout__, __headers__, __returntype__
        __timeout__ = timeout
        __headers__ = headers
        __returntype__ = returntype

    
    def Get( self, url, **kwargs ):
        params, data = self._unpack_args( kwargs )
        return self._urlcall( url, params, '', 'get' )
    
    
    def Post( self, url, **kwargs ):
        params, data = self._unpack_args( kwargs )
        return self._urlcall( url, params, data, 'post' ) 
    
    
    def Delete( self, url, **kwargs ):
        params, data = self._unpack_args( kwargs )
        return self._urlcall( url, params, data, 'delete' )
    
    
    def _urlcall( self, url, params, data, urltype ):
        loglines = []
        urldata = ''
        try:
            if urltype == "get":
                urldata = requests.get( url, params=params, timeout=__timeout__ )
            elif urltype == "post":
                urldata = requests.post( url, params=params, data=data, headers=__headers__, timeout=__timeout__ )
            elif urltype == "delete":
                urldata = requests.delete( url, params=params, data=data, headers=__headers__, timeout=__timeout__ )
            loglines.append( "the url is: " + urldata.url )
        except requests.exceptions.ConnectionError, e:
            loglines.append( 'site unreachable at ' + url )
            loglines.append( e )
        except requests.exceptions.Timeout, e:
            loglines.append( 'timeout error while downloading from ' + url )
            loglines.append( e )
        except requests.exceptions.HTTPError, e:
            loglines.append( 'HTTP Error while downloading from ' + url )
            loglines.append( e )
        except requests.exceptions.RequestException, e:
            loglines.append( 'unknown error while downloading from ' + url )
            loglines.append( e )
        if urldata:
            success = True
            if __returntype__ == 'text':
                data = urldata.text()
            elif __returntype__ == 'binary':
                data = urldata.content()
            elif __returntype__ == 'json':
                data = urldata.json()
                if data == None:
                    data = []
        else:
            success = False
            data = ''
        loglines.append( '-----URL OBJECT RETURNED-----' )
        loglines.append( data )
        return success, loglines, data
    
    
    def _unpack_args( self, kwargs ):
        try:
            params = kwargs['params']
        except:
            params = {}
        try:
            data = kwargs['data']
        except:
            if __returntype__ == 'json':
                data = []
            else:
                data = ''
    	return params, data