#v.0.1.0

import sys, xbmc
if sys.version_info >= (2, 7):
    import json as _json
else:
    import simplejson as _json


class objectConfig():
    def __init__( self ):
        self.loglines = []


    def provides( self ):
        return ['bio']
        
        
    def getBio( self, bio_params ):
        self.loglines = []
        bio=''
        response = xbmc.executeJSONRPC ( '{"jsonrpc":"2.0", "method":"Player.GetItem", "params":{"playerid":0, "properties":["artist", "description"]},"id":1}' )
        try:
            bio = _json.loads(response)['result']['item']['description']
        except (IndexError, KeyError, ValueError):
            self.loglines.append( 'Index, Key, or Value error on results from Kodi' )
            bio = ''
        except Exception, e:
            self.loglines.extend( ['unexpected error getting JSON back from Kodi', e] )
            bio = ''
        return bio, self.loglines