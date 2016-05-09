#v.0.1.0

import os, time, sys, random, xbmc
from ..common.url import URL
from ..common.fileops import readFile, writeFile, deleteFile, checkPath
if sys.version_info >= (2, 7):
    import json as _json
else:
    import simplejson as _json


class objectConfig():
    def __init__( self ):
        self.APIKEY = '7a93c84fe1c9999e6f0fec206a66b0f5'
        secsinweek = int( 7*24*60*60 )
        self.URL = 'http://webservice.fanart.tv/v3/music/'
        self.FILENAME = 'fanarttvartistimages.nfo'
        self.CACHETIMEFILENAME = 'fanarttvcachetime.nfo'
        self.CACHEEXPIRE = {}
        self.CACHEEXPIRE['low'] = int( 4*secsinweek )
        self.CACHEEXPIRE['high'] = int( 12*secsinweek )
        self.loglines = []
        self.JSONURL = URL( 'json' )


    def provides( self ):
        return ['images']
        
        
    def getImageList( self, img_params ):
        self.loglines = []
        if not img_params['enabled'] == 'true':
            return [], self.loglines
        url_params = {}
        images = []
        filepath = os.path.join( img_params['infodir'], self.FILENAME )
        cachefilepath = os.path.join( img_params['infodir'], self.CACHETIMEFILENAME )
        url = self.URL + img_params['mbid']
        url_params['api_key'] = self.APIKEY
        if img_params['clientapikey']:
            url_params['client_key'] = img_params['clientapikey']
        json_data = self._get_data( filepath, cachefilepath, url, url_params )
        if json_data:
            try:
                image_list = json_data['artistbackground']
            except (IndexError, KeyError, ValueError):
                self.loglines.append( 'Index, Key, or Value Error getting backgrounds from ' + self.FILENAME )
                image_list = []
            except Exception, e:
                image_list = []
                self.loglines.extend( ['unexpected error getting backgrounds from %s' % self.FILENAME, e] )
            if img_params['getall'] == 'true':
                try:
                    image_list.extend( json_data['artistthumb'] )
                except (IndexError, KeyError, ValueError):
                    self.loglines.append( 'Index, Key, or Value Error getting thumbs from ' + self.FILENAME )
                except Exception, e:
                    image_list = []
                    self.loglines.extend( ['unexpected error getting thumbs from %s' % self.FILENAME, e] )
            for image in image_list:
                try:
                    images.append( image['url'] )
                except (IndexError, KeyError, ValueError):
                    self.loglines.append( 'Index, Key, or Value Error when reading JSON data from list of images' )
                    image_list = []
                except Exception, e:
                    bio = []
                    self.loglines.extend( ['unexpected error getting JSON back from list of images', e] )
        if images == []:
            return [], self.loglines
        else: 
            return self._remove_exclusions( images, img_params['exclusionsfile'] ), self.loglines


    def _get_cache_time( self, cachefilepath ):
        rawdata = ''
        self.loglines.append( 'getting the cache timeout information for fanarttv' )
        exists, cloglines = checkPath( cachefilepath, False )
        self.loglines.extend( cloglines )
        if exists:
            success = True
        else:
            success = self._put_cache_time( cachefilepath )
        if success:
            rloglines, rawdata = readFile( cachefilepath ) 
            self.loglines.extend( rloglines )
        if rawdata:
            return int( rawdata )
        else:
            return 0


    def _get_data( self, filepath, cachefilepath, url, url_params ):
        json_data = ''
        if self._update_cache( filepath, cachefilepath ):
            success, uloglines, json_data = self.JSONURL.Get( url, params=url_params )
            self.loglines.extend( uloglines )
            if success:
                success, wloglines = writeFile( _json.dumps( json_data ).encode( 'utf-8' ), filepath )
                self.loglines.extend( wloglines )
        exists, cloglines = checkPath( filepath, False )
        self.loglines.extend( cloglines )
        if exists:
            rloglines, rawdata = readFile( filepath )
            self.loglines.extend( rloglines )
            try:
                json_data = _json.loads( rawdata )
            except ValueError:
                success, dloglines = deleteFile( filepath )
                self.loglines.extend( dloglines )
                self.loglines.append( 'Deleted old cache file. New file will be download on next run.' )
                json_data = ''
        return json_data


    def _put_cache_time( self, cachefilepath ):
        cachetime = random.randint( self.CACHEEXPIRE['low'], self.CACHEEXPIRE['high'] )
        success, wloglines = writeFile( str( cachetime ), cachefilepath )
        self.loglines.append( wloglines)
        return success


    def _remove_exclusions( self, image_list, exclusionfilepath ):
        images = []
        rloglines, rawdata = readFile( exclusionfilepath )
        self.loglines.extend( rloglines )
        if not rawdata:
            return image_list
        exclusionlist = rawdata.split()
        for image in image_list:
            for exclusion in exclusionlist:
                if not exclusion.startswith( xbmc.getCacheThumbName( image ) ):
                    images.append( image )
        return images


    def _update_cache( self, filepath, cachefilepath ):
        exists, cloglines = checkPath( filepath, False )
        self.loglines.extend( cloglines )
        if exists:
            if time.time() - os.path.getmtime( filepath ) < self._get_cache_time( cachefilepath ):
                self.loglines.append( 'cached artist info found for fanarttv' )
                return False
            else:
                self.loglines.append( 'outdated cached artist info found for fanarttv' )
                return self._put_cache_time( cachefilepath )
        else:
            self.loglines.append( 'no fanarttv cachetime file found, creating it' )
            return self._put_cache_time( cachefilepath )
