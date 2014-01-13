import ntpath, os, socket, urllib, urllib2, xbmc, xbmcvfs

socket.setdefaulttimeout(10)

def checkDir(path):
    if not xbmcvfs.exists(path):
        xbmcvfs.mkdirs(path)

def pathLeaf(path):
    path, filename = ntpath.split(path)
    return {"path":path, "filename":filename}

def saveURL( url, filename, *args, **kwargs ):
    data, log_lines = grabURL( url, *args, **kwargs )
    if data:
        success, log_lines2 = writeFile( data, filename )
        log_lines.extend( log_lines2 )
        if success:
            return True, log_lines
        else:
            return False, log_lines
    else:
        return False, log_lines

def grabURL( url, *args, **kwargs ):
    log_lines = []
    req = urllib2.Request( url=url )
    log_lines.append( 'url is ' + url )
    for key, value in kwargs.items():
        req.add_header(key.replace('_', '-'), value)
    for header, value in req.headers.items():
        log_lines.append( 'url header %s is %s' % (header, value) )
    params = ''
    for arg in args:
        if params:
           join = '&'
        else:
            join = ''
        try:
            params = params + join + urllib.urlencode( arg )
        except Exception, e:
            log_lines.append( 'unknown error urlencoding args' )
            log_lines.append( e )
    try:
        if params:
            log_lines.append( 'the POST params are: ' + params )
            url_data = urllib2.urlopen( req, params ).read()        
        else:
            url_data = urllib2.urlopen( req ).read()
    except urllib2.URLError, urllib2.HTTPError:
        log_lines.append( 'site unreachable at ' + url )
        return '', log_lines
    except socket.error:
        log_lines.append( 'timeout error while downloading from ' + url )
        return '', log_lines
    except Exception, e:
        log_lines.append( 'unknown error while downloading from ' + url )
        log_lines.append( e )
        return '', log_lines
    return url_data, log_lines    

def writeFile( data, filename ):
    log_lines = []
    if type(data).__name__=='unicode':
        data = data.encode('utf-8')
    try:
        thefile = open( filename, 'wb' )
        thefile.write( data )
        thefile.close()
    except IOError, e:
        log_lines.append( 'unable to write data to ' + filename )
        log_lines.append( e )
        return (False, log_lines)
    except Exception, e:
        log_lines.append( 'unknown error while writing data to ' + filename )
        log_lines.append( e )
        return (False, log_lines)
    log_lines.append( 'successfuly wrote data to ' + filename )
    return True, log_lines

def readFile( filename ):
    log_lines = []
    if xbmcvfs.exists( filename):
        try:
            the_file = open (filename, 'r')
            data = the_file.read()
            the_file.close()
        except IOError:
            log_lines.append( 'unable to read data from ' + filename )
            return '', log_lines
        except Exception, e:
            log_lines.append( 'unknown error while reading data from ' + filename )
            log_lines.append( e )
            return '', log_lines
        return data, log_lines
    else:
        return '', log_lines
