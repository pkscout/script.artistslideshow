import os, xbmc, xbmcvfs

def checkDir(path):
    if not xbmcvfs.exists(path):
        xbmcvfs.mkdirs(path)

def getCacheThumbName(url, CachePath):
    thumb = xbmc.getCacheThumbName(url)
    thumbpath = os.path.join(CachePath, thumb.encode('utf-8'))
    return thumbpath

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
    return (True, log_lines)

def readFile( filename ):
    if xbmcvfs.exists( filename):
        try:
            the_file = open (filename, 'r')
            data = the_file.read()
            the_file.close()
        except IOError:
            lw.log( 'unable to read data from ' + filename, xbmc.LOGDEBUG )
            return ''
        except Exception, e:
            lw.log( 'unknown error while reading data from ' + filename, xbmc.LOGDEBUG )
            lw.log( e, xbmc.LOGDEBUG )
            return ''
        return data
    else:
        return ''
