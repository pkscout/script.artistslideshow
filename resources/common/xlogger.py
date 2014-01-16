import xbmc, unicodedata

__log_preamble__ = ''

#this class creates an object used to log stuff to the xbmc log file
class Logger():
    def __init__(self, preamble=''):
        global __log_preamble__
        __log_preamble__ = preamble


    def _output( self, line, loglevel ):
        if type(line).__name__=='unicode':
            line = line.encode('utf-8')
        xbmc.log("%s %s" % (__log_preamble__, line.__str__()), loglevel)
 

    def log( self, loglines, loglevel=xbmc.LOGDEBUG ):
        for line in loglines:
            try:
                str_line = line.__str__()
            except Exception, e:
                str_line = ''
                self._output( 'error parsing logline', loglevel )
                self._output( e, loglevel )
            if str_line:
                self._output( str_line, loglevel )