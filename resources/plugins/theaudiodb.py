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
        apikey = '193621276b2d731671156g'
        url = 'http://www.theaudiodb.com/api/v1/json/%s/' % apikey
        secsinweek = int( 7*24*60*60 )
        self.ARTISTURL = url + 'artist-mb.php'
        self.ALBUMURL = url + 'album.php'
        self.ARTISTFILENAME = 'theaudiodbartistbio.nfo'
        self.ALBUMFILENAME = 'theaudiodbartistsalbums.nfo'
        self.IDFILENAME = 'theaudiodbid.nfo'
        self.CACHETIMEFILENAME = 'theaudiodbcachetime.nfo'
        self.CACHEEXPIRE = {}
        self.CACHEEXPIRE['low'] = int( 4*secsinweek )
        self.CACHEEXPIRE['high'] = int( 12*secsinweek )
        self.loglines = []
        self.JSONURL = URL( 'json' )


    def provides( self ):
        return ['bio', 'albums', 'images']


    def getAlbumList( self, album_params ):
        self.loglines = []
        url_params = {}
        albums = []
        json_data = ''
        artistfilepath = os.path.join( album_params['infodir'], self.ARTISTFILENAME )
        idfilepath = os.path.join( album_params['infodir'], self.IDFILENAME )
        audiodbid = self._get_audiodbid( idfilepath, artistfilepath )
        if audiodbid:
            cachefilepath = os.path.join( album_params['infodir'], self.CACHETIMEFILENAME )
            filepath = os.path.join( album_params['infodir'], self.ALBUMFILENAME )
            url_params['i'] = audiodbid
            json_data = self._get_data( filepath, cachefilepath, self.ALBUMURL, url_params )
        if json_data:
            try:
                rawalbums = json_data['album']
            except (IndexError, KeyError, ValueError):
                rawalbums = []
                self.loglines.append( 'Index, Key, or Value Error when reading albums JSON data from ' + self.ALBUMFILENAME )
            except Exception, e:
                rawalbums = []
                self.loglines.extend( ['unexpected error getting albums JSON back from %s' % self.ALBUMFILENAME, e] )
            for album in rawalbums:
                try:
                    albums.append( ( album['strAlbum'] , album['strAlbumThumb'] ) )
                except (IndexError, KeyError, ValueError):
                    self.loglines.append( 'Index, Key, or Value Error when reading album info' )
                except Exception, e:
                    self.loglines.extend( ['unexpected error getting album info', e] )
        return albums, self.loglines

        
    def getBio( self, bio_params ):
        self.loglines = []
        url_params = {}
        bio = ''
        filepath = os.path.join( bio_params['infodir'], self.ARTISTFILENAME )
        cachefilepath = os.path.join( bio_params['infodir'], self.CACHETIMEFILENAME )
        url_params['i'] = bio_params['mbid']
        json_data = self._get_data( filepath, cachefilepath, self.ARTISTURL, url_params )
        if json_data:
            try:
                bio = json_data['artists'][0]['strBiography'+ bio_params['lang'].upper()]
            except (IndexError, KeyError, ValueError):
                self.loglines.append( 'Index, Key, or Value Error when reading JSON data from ' + self.ARTISTFILENAME )
                bio = ''
            except Exception, e:
                bio = ''
                self.loglines.extend( ['unexpected error getting JSON back from %s' % self.ARTISTFILENAME, e] )           
        return bio, self.loglines
        
        
    def getImageList( self, img_params ):
        self.loglines = []
        if not img_params['enabled'] == 'true':
            return [], self.loglines
        url_params = {}
        images = []
        filepath = os.path.join( img_params['infodir'], self.ARTISTFILENAME )
        cachefilepath = os.path.join( img_params['infodir'], self.CACHETIMEFILENAME )
        url_params['i'] = img_params['mbid']
        json_data = self._get_data( filepath, cachefilepath, self.ARTISTURL, url_params )
        if json_data:
            for i in range( 1, 3 ):
                if i == 1:
                    num = ''
                else:
                    num = str( i )
                try:
                    images.append( json_data['artists'][0]['strArtistFanart' + num] )
                except (IndexError, KeyError, ValueError):
                    self.loglines.append( 'Index, Key, or Value Error when getting strArtistFanart' + num )
                except Exception, e:
                    self.loglines.extend( ['unexpected error when getting strArtistFanart' + num, e] ) 
        if images == []:
            return [], self.loglines
        else: 
            return self._remove_exclusions( images, img_params['exclusionsfile'] ), self.loglines
        
        
    def _get_audiodbid( self, idfilepath, filepath ):
        audiodbid = ''
        exists, cloglines = checkPath( idfilepath, False )
        self.loglines.extend( cloglines )
        if not exists:
            exists, cloglines = checkPath( filepath, False )
            self.loglines.extend( cloglines )
            if exists:
                rloglines, rawdata = readFile( filepath )
                self.loglines.extend( rloglines )
                json_data = _json.loads( rawdata )
                try:
                    audiodbid = ( json_data['artists'][0]['idArtist'] )
                except (IndexError, KeyError, ValueError):
                    self.loglines.append( 'Index, Key, or Value Error when reading JSON data from ' + self.ARTISTFILENAME )
                    audiodbid = ''
                except Exception, e:
                    audiodbid = ''
                    self.loglines.extend( ['unexpected error getting JSON back from %s' % self.ARTISTFILENAME, e] )
                if audiodbid:
                    success, wloglines = writeFile( audiodbid, idfilepath )
                    self.loglines.extend( wloglines )
        rloglines, audiodbid = readFile( idfilepath )
        self.loglines.extend( rloglines )
        return audiodbid    


    def _get_cache_time( self, cachefilepath ):
        rawdata = ''
        self.loglines.append( 'getting the cache timeout information for theaudiodb' )
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
            except _json.JSONDecodeError:
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
                self.loglines.append( 'cached artist info found for theaudiodb' )
                return False
            else:
                self.loglines.append( 'outdated cached artist info found for theaudiodb' )
                return self._put_cache_time( cachefilepath )
        else:
            self.loglines.append( 'no theaudiodb cachetime file found, creating it' )
            return self._put_cache_time( cachefilepath )
