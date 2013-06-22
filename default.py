# *  Credits:
# *
# *  original Artist Slideshow code by ronie
# *  updates and additions since v1.3.0 by pkscuot
# *
# *  divingmule for script.image.lastfm.slideshow
# *  grajen3 for script.ImageCacher
# *  sfaxman for smartUnicode
# *
# *  code from all scripts/examples are used in script.artistslideshow
# *
# *  Musicbrainz python library by Kenneth Reitz
# *  see resource/musicbrainzngs/copying for copyright and use restrictions
# *  
# *  Last.fm:      http://www.last.fm/
# *  htbackdrops:  http://www.htbackdrops.com/ (depreciated)
# *  fanart.tv:    http://www.fanart.tv
# *  theaudiodb:   http://www.theaudiodb.com


import xbmc, xbmcaddon, os, xbmcgui, xbmcvfs
import codecs, random, re, sys, time, unicodedata, urllib, urllib2, urlparse, socket, shutil
from elementtree import ElementTree as xmltree
if sys.version_info >= (2, 7):
    import json
else:
    import simplejson as json

__addon__        = xbmcaddon.Addon()
__addonname__    = __addon__.getAddonInfo('id')
__addonversion__ = __addon__.getAddonInfo('version')
__addonpath__    = __addon__.getAddonInfo('path').decode('utf-8')
__addonicon__    = xbmc.translatePath('%s/icon.png' % __addonpath__ )
__language__     = __addon__.getLocalizedString

# to be able to import libraries from the artistslideshow addon directory
sys.path.append( os.path.join( __addonpath__, "resources" ) )
sys.path.append( os.path.join( __addonpath__, "resources/dicttoxml" ) )

from dicttoxml import dicttoxml

socket.setdefaulttimeout(10)

LANGUAGES = (
# Full Language name[0]         ISO 639-1[1]   Script Language[2]
    ("Albanian"                   , "sq",            "0"  ),
    ("Arabic"                     , "ar",            "1"  ),
    ("Belarusian"                 , "hy",            "2"  ),
    ("Bosnian"                    , "bs",            "3"  ),
    ("Bulgarian"                  , "bg",            "4"  ),
    ("Catalan"                    , "ca",            "5"  ),
    ("Chinese"                    , "zh",            "6"  ),
    ("Croatian"                   , "hr",            "7"  ),
    ("Czech"                      , "cs",            "8"  ),
    ("Danish"                     , "da",            "9"  ),
    ("Dutch"                      , "nl",            "10" ),
    ("English"                    , "en",            "11" ),
    ("Estonian"                   , "et",            "12" ),
    ("Persian"                    , "fa",            "13" ),
    ("Finnish"                    , "fi",            "14" ),
    ("French"                     , "fr",            "15" ),
    ("German"                     , "de",            "16" ),
    ("Greek"                      , "el",            "17" ),
    ("Hebrew"                     , "he",            "18" ),
    ("Hindi"                      , "hi",            "19" ),
    ("Hungarian"                  , "hu",            "20" ),
    ("Icelandic"                  , "is",            "21" ),
    ("Indonesian"                 , "id",            "22" ),
    ("Italian"                    , "it",            "23" ),
    ("Japanese"                   , "ja",            "24" ),
    ("Korean"                     , "ko",            "25" ),
    ("Latvian"                    , "lv",            "26" ),
    ("Lithuanian"                 , "lt",            "27" ),
    ("Macedonian"                 , "mk",            "28" ),
    ("Norwegian"                  , "no",            "29" ),
    ("Polish"                     , "pl",            "30" ),
    ("Portuguese"                 , "pt",            "31" ),
    ("PortugueseBrazil"           , "pb",            "32" ),
    ("Romanian"                   , "ro",            "33" ),
    ("Russian"                    , "ru",            "34" ),
    ("Serbian"                    , "sr",            "35" ),
    ("Slovak"                     , "sk",            "36" ),
    ("Slovenian"                  , "sl",            "37" ),
    ("Spanish"                    , "es",            "38" ),
    ("Swedish"                    , "sv",            "39" ),
    ("Thai"                       , "th",            "40" ),
    ("Turkish"                    , "tr",            "41" ),
    ("Ukrainian"                  , "uk",            "42" ),
    ("Vietnamese"                 , "vi",            "43" ),
    ("Farsi"                      , "fa",            "13" ),
    ("Portuguese (Brazil)"        , "pb",            "32" ),
    ("Portuguese-BR"              , "pb",            "32" ),
    ("Brazilian"                  , "pb",            "32" ) )

def log(msg, level=xbmc.LOGDEBUG):
    plugin = "Artist Slideshow"
    if type(msg).__name__=='unicode':
        msg = msg.encode('utf-8')
    xbmc.log("[%s] %s" % (plugin, msg.__str__()), level)

def checkDir(path):
    if not xbmcvfs.exists(path):
        xbmcvfs.mkdir(path)

def getCacheThumbName(url, CachePath):
    thumb = xbmc.getCacheThumbName(url)
    thumbpath = os.path.join(CachePath, thumb.encode("utf-8"))
    return thumbpath

def smartUnicode(s):
    if not s:
        return ''
    try:
        if not isinstance(s, basestring):
            if hasattr(s, '__unicode__'):
                s = unicode(s)
            else:
                s = unicode(str(s), 'UTF-8')
        elif not isinstance(s, unicode):
            s = unicode(s, 'UTF-8')
    except:
        if not isinstance(s, basestring):
            if hasattr(s, '__unicode__'):
                s = unicode(s)
            else:
                s = unicode(str(s), 'ISO-8859-1')
        elif not isinstance(s, unicode):
            s = unicode(s, 'ISO-8859-1')
    return s

def smartUTF8(s):
    return smartUnicode(s).encode('utf-8')

def saveURL( url, filename, *args, **kwargs ):
    data = grabURL( url, *args, **kwargs )
    if data:
        try:
            thefile = open( filename, 'wb' )
            thefile.write( data )
            thefile.close()
        except IOError:
            log( 'unable to write data to %s from %s' % (filename, url) )
            return False
    else:
        return False
    return True

def grabURL( url, *args, **kwargs ):
    req = urllib2.Request(url=url)
    for key, value in kwargs.items():
        req.add_header(key.replace('_', '-'), value)
    for header, value in req.headers.items():
        log('url header %s is %s' % (header, value) )
    try:
        url_data = urllib2.urlopen( req ).read()
    except urllib2.URLError:
        log( 'site unreachable at ' + url )
        return ''
    return url_data

def cleanText(text):
    text = re.sub('<a href="http://www.last.fm/music/.*</a>.','',text)
    text = re.sub('<(.|\n|\r)*?>','',text)
    text = re.sub('&quot;','"',text)
    text = re.sub('&amp;','&',text)
    text = re.sub('&gt;','>',text)
    text = re.sub('&lt;','<',text)
    text = re.sub('User-contributed text is available under the Creative Commons By-SA License and may also be available under the GNU FDL.','',text)
    return text.strip()

def download(src, dst, dst2):
    if (not xbmc.abortRequested):
        tmpname = xbmc.translatePath('special://profile/addon_data/%s/temp/%s' % ( __addonname__ , xbmc.getCacheThumbName(src) ))
        if xbmcvfs.exists(tmpname):
            xbmcvfs.delete(tmpname)
        if not saveURL( src, tmpname ):
            return False
        if os.path.getsize(tmpname) > 999:
            log( 'copying file to transition directory' )
            xbmcvfs.copy(tmpname, dst2)
            log( 'moving file to cache directory' )
            xbmcvfs.rename(tmpname, dst)
            return True
        else:
            xbmcvfs.delete(tmpname)
            return False

def writeFile( data, filename ):
    the_file = open (filename, 'w')
    the_file.write( data )
    the_file.close()

def readFile( filename ):
    if xbmcvfs.exists( filename):
        the_file = open (filename, 'r')
        data = the_file.read()
        the_file.close()
        return data
    else:
        return ''


class Main:
    def __init__( self ):
        self._parse_argv()
        self._get_settings()
        self._init_vars()
        self._make_dirs()
        if xbmc.getInfoLabel( self.ARTISTSLIDESHOWRUNNING ) == "True":
            log('script already running')
        else:
            self.LastCacheTrim = 0
            self._set_property("ArtistSlideshowRunning", "True")
            if( xbmc.Player().isPlayingAudio() == False and xbmc.getInfoLabel( self.EXTERNALCALL ) == '' ):
                log('no music playing')
                if( self.DAEMON == "False" ):
                    self._set_property("ArtistSlideshowRunning")
            else:
                log('first song started')
                time.sleep(0.5) # it may take some time for xbmc to read tag info after playback started
                self._use_correct_artwork()
                self._trim_cache()
            while (not xbmc.abortRequested):
                time.sleep(0.5)
                if xbmc.getInfoLabel( self.ARTISTSLIDESHOWRUNNING ) == "True":
                    if( xbmc.Player().isPlayingAudio() == True or xbmc.getInfoLabel( self.EXTERNALCALL ) != '' ):
                        if set( self.ALLARTISTS ) <> set( self._get_current_artist() ):
                            self._clear_properties()
                            self.UsingFallback = False
                            self._use_correct_artwork()
                            self._trim_cache()
                        elif(not (self.DownloadedAllImages or self.UsingFallback)):
                            if(not (self.LocalImagesFound and self.PRIORITY == '1')):
                                log('same artist playing, continue download')
                                self._use_correct_artwork()
                    else:
                        time.sleep(2) # doublecheck if playback really stopped
                        if( xbmc.Player().isPlayingAudio() == False and xbmc.getInfoLabel( self.EXTERNALCALL ) == '' ):
                            if ( self.DAEMON == "False" ):
                                self._set_property( "ArtistSlideshowRunning" )
                else:
                    self._clear_properties()
                    break


    def _use_correct_artwork( self ):
        self._clean_dir( self.MergeDir )
        artists = self._get_current_artist()
        self.ALLARTISTS = artists
        self.ARTISTNUM = 0
        self.TOTALARTISTS = len(artists)
        self.MergedImagesFound = False
        for artist in artists:
            log('current artist is %s' % artist)
            self.ARTISTNUM += 1
            self.NAME = artist
            if(self.USEOVERRIDE == 'true'):
                log('using override directory for images')
                self._set_property("ArtistSlideshow", self.OVERRIDEPATH)
                if(self.ARTISTNUM == 1):
                    self._set_cachedir()
                    self._get_artistinfo()
            elif(self.PRIORITY == '1' and not self.LOCALARTISTPATH == ''):
                log('looking for local artwork')
                self._get_local_images()
                if(not self.LocalImagesFound):
                    log('no local artist artwork found, start download')
                    self._start_download()
            elif(self.PRIORITY == '2' and not self.LOCALARTISTPATH == ''):
                log('looking for local artwork')
                self._get_local_images()
                log('start download')
                self._start_download()
            else:
                log('start download')
                self._start_download()
                if(not (self.CachedImagesFound or self.ImageDownloaded)):
                    log('no remote artist artwork found, looking for local artwork')
                    self._get_local_images()
        if(not (self.LocalImagesFound or self.CachedImagesFound or self.ImageDownloaded or self.MergedImagesFound)):
            if (self.USEFALLBACK == 'true'):
                log('no images found for artist, using fallback slideshow')
                log('fallbackdir = ' + self.FALLBACKPATH)
                self.UsingFallback = True
                self._set_property("ArtistSlideshow", self.FALLBACKPATH)


    def _parse_argv( self ):
        try:
            params = dict( arg.split( "=" ) for arg in sys.argv[ 1 ].split( "&" ) )
        except:
            params = {}
        self.WINDOWID = params.get( "windowid", "12006")
        log( 'window id is set to %s' % self.WINDOWID )
        self.ARTISTFIELD = params.get( "artistfield", "" )
        log( 'artist field is set to %s' % self.ARTISTFIELD )
        self.TITLEFIELD = params.get( "titlefield", "" )
        log( 'title field is set to %s' % self.TITLEFIELD )
        self.DAEMON = params.get( "daemon", "False" )
        if self.DAEMON == "True":
            log('daemonizing')


    def _get_settings( self ):
        self.LASTFM = __addon__.getSetting( "lastfm" )
        try:
            self.minwidth = int(__addon__.getSetting( "minwidth" ))
        except:
            self.minwidth = 0
        try:
            self.minheight = int(__addon__.getSetting( "minheight" ))
        except:
            self.minheight = 0
        self.HDASPECTONLY = __addon__.getSetting( "hd_aspect_only" )
        self.FANARTTV = __addon__.getSetting( "fanarttv" )
        self.THEAUDIODB = __addon__.getSetting( "theaudiodb" )
        self.HTBACKDROPS = __addon__.getSetting( "htbackdrops" )
        self.ARTISTINFO = __addon__.getSetting( "artistinfo" )
        self.LANGUAGE = __addon__.getSetting( "language" )
        for language in LANGUAGES:
            if self.LANGUAGE == language[2]:
                self.LANGUAGE = language[1]
                log('language = %s' % self.LANGUAGE)
                break
        self.LOCALARTISTPATH = __addon__.getSetting( "local_artist_path" ).decode("utf-8")
        self.PRIORITY = __addon__.getSetting( "priority" )
        self.USEFALLBACK = __addon__.getSetting( "fallback" )
        self.FALLBACKPATH = __addon__.getSetting( "fallback_path" ).decode("utf-8")
        self.USEOVERRIDE = __addon__.getSetting( "slideshow" )
        self.OVERRIDEPATH = __addon__.getSetting( "slideshow_path" ).decode("utf-8")
        self.RESTRICTCACHE = __addon__.getSetting( "restrict_cache" )
        try:
            self.maxcachesize = int(__addon__.getSetting( "max_cache_size" )) * 1000000
        except:
            self.maxcachesize = 1024 * 1000000
        self.NOTIFICATIONTYPE = __addon__.getSetting( "show_progress" )
        if self.NOTIFICATIONTYPE == "2":
            self.PROGRESSPATH = __addon__.getSetting( "progress_path" ).decode("utf-8")
            log('set progress path to %s' % self.PROGRESSPATH)
        else:
            self.PROGRESSPATH = ''
        if __addon__.getSetting( "fanart_folder" ):
            self.FANARTFOLDER = __addon__.getSetting( "fanart_folder" ).decode("utf-8")
            log('set fanart folder to %s' % self.FANARTFOLDER)
        else:
            self.FANARTFOLDER = 'extrafanart'


    def _init_vars( self ):
        self.WINDOW = xbmcgui.Window( int(self.WINDOWID) )
        self._set_property( "ArtistSlideshow.CleanupComplete" )
        if( self.ARTISTFIELD == '' ):
            self.SKINARTIST = ''
        else:
            self.SKINARTIST = "Window(%s).Property(%s)" % ( self.WINDOWID, self.ARTISTFIELD )
        if( self.TITLEFIELD == '' ):
            self.SKINTITLE = ''
        else:
            self.SKINTITLE = "Window(%s).Property(%s)" % ( self.WINDOWID, self.TITLEFIELD )
        self.ARTISTSLIDESHOW = "Window(%s).Property(%s)" % ( self.WINDOWID, "ArtistSlideshow" )
        self.ARTISTSLIDESHOWRUNNING = "Window(%s).Property(%s)" % ( self.WINDOWID, "ArtistSlideshowRunning" )
        self.EXTERNALCALL = "Window(%s).Property(%s)" % ( self.WINDOWID, "ArtistSlideshow.ExternalCall" )
        self.EXTERNALCALLSTATUS = xbmc.getInfoLabel( self.EXTERNALCALL )
        log( 'external call is set to ' + xbmc.getInfoLabel( self.EXTERNALCALL ) )
        self.NAME = ''
        self.ALLARTISTS = []
        self.LocalImagesFound = False
        self.CachedImagesFound = False
        self.ImageDownloaded = False
        self.DownloadedAllImages = False
        self.UsingFallback = False
        self.BlankDir = xbmc.translatePath('special://profile/addon_data/%s/transition' % __addonname__ ).decode("utf-8")
        self.MergeDir = xbmc.translatePath('special://profile/addon_data/%s/merge' % __addonname__ ).decode("utf-8")
        self.InitDir = xbmc.translatePath('%s/resources/black' % __addonpath__ ).decode("utf-8")
        LastfmApiKey = 'afe7e856e4f4089fc90f841980ea1ada'
        HtbackdropsApiKey = '96d681ea0dcb07ad9d27a347e64b652a'
        fanarttvApiKey = '7a93c84fe1c9999e6f0fec206a66b0f5'
        theaudiodbApiKey = '193621276b2d731671156g'
        self.LastfmURL = 'http://ws.audioscrobbler.com/2.0/?autocorrect=1&api_key=' + LastfmApiKey
        self.HtbackdropsQueryURL = 'http://htbackdrops.com/api/' + HtbackdropsApiKey + '/searchXML?default_operator=and&fields=title&aid=1'
        self.HtbackdropsDownloadURL = 'http://htbackdrops.com/api/' + HtbackdropsApiKey + '/download/'
        self.fanarttvURL = 'http://api.fanart.tv/webservice/artist/%s/' % fanarttvApiKey
        self.fanarttvOPTIONS = '/json/artistbackground/'
        self.theaudiodbURL = 'http://www.theaudiodb.com/api/v1/json/%s/' % theaudiodbApiKey
        self.theaudiodbARTISTURL = 'artist-mb.php?i='
        self.theaudiodbALBUMURL = 'album.php?i='

    def _make_dirs( self ):
        checkDir(xbmc.translatePath('special://profile/addon_data/%s' % __addonname__ ).decode("utf-8"))
        checkDir(xbmc.translatePath('special://profile/addon_data/%s/temp' % __addonname__ ).decode("utf-8"))
        checkDir(xbmc.translatePath('special://profile/addon_data/%s/ArtistSlideshow' % __addonname__ ).decode("utf-8"))
        checkDir(xbmc.translatePath('special://profile/addon_data/%s/transition' % __addonname__ ).decode("utf-8"))

    def _set_cachedir( self ):
        CacheName = xbmc.getCacheThumbName(self.NAME).replace('.tbn', '')
        #CacheName = self.NAME
        self.CacheDir = xbmc.translatePath('special://profile/addon_data/%s/ArtistSlideshow/%s/' % ( __addonname__ , CacheName, )).decode("utf-8")
        checkDir(self.CacheDir)


    def _start_download( self ):
        self.CachedImagesFound = False
        self.DownloadedFirstImage = False
        self.DownloadedAllImages = False
        self.ImageDownloaded = False
        self.FirstImage = True
        cached_image_info = False
        min_refresh = 9.9
        if not self.NAME:
            log('no artist name provided')
            return
        if(self.PRIORITY == '2' and self.LocalImagesFound):
            pass
            #self.CacheDir was successfully set in _get_local_images
        else:
            self._set_cachedir()
        log('cachedir = %s' % self.CacheDir)

        files = os.listdir(self.CacheDir)
        for file in files:
            if file.lower().endswith('tbn') or (self.PRIORITY == '2' and self.LocalImagesFound):
                self.CachedImagesFound = True

        if self.CachedImagesFound:
            log('cached images found')
            cached_image_info = True
            last_time = time.time()
            if self.ARTISTNUM == 1:
                self._set_property("ArtistSlideshow", self.CacheDir)
                if self.ARTISTINFO == "true":
                    self._get_artistinfo()
        else:
            last_time = 0
            if self.ARTISTNUM == 1:
                for cache_file in ['artistimageshtbackdrops.nfo', 'artistimageslastfm.nfo']:
                    filename = os.path.join( self.CacheDir, cache_file.decode("utf-8") )
                    if xbmcvfs.exists( filename ):
                        if time.time() - os.path.getmtime(filename) < 1209600:
                            log('cached %s found' % filename)
                            cached_image_info = True
                        else:
                           log('outdated %s found' % filename)
                           cached_image_info = False
                if self.NOTIFICATIONTYPE == "1":
                    self._set_property("ArtistSlideshow", self.InitDir)
                    if not cached_image_info:
                        command = 'XBMC.Notification(%s, %s, %s, %s)' % (smartUTF8(__language__(30300)), smartUTF8(__language__(30301)), 5000, smartUTF8(__addonicon__))
                        xbmc.executebuiltin(command)
                elif self.NOTIFICATIONTYPE == "2":
                    if not cached_image_info:
                        self._set_property("ArtistSlideshow", self.PROGRESSPATH)
                    else:
                        self._set_property("ArtistSlideshow", self.InitDir)
                else:
                      self._set_property("ArtistSlideshow", self.InitDir)
        sourcelist = []
        sourcelist.append( ['lastfm', self.LASTFM] )
        sourcelist.append( ['fanarttv', self.FANARTTV] )
        sourcelist.append( ['theaudiodb', self.THEAUDIODB] )
        sourcelist.append( ['htbackdrops', self.HTBACKDROPS] )
        imagelist = []
        for source in sourcelist:
            log( ' checking the source %s with a value of %s.' % (source[0], source[1]) )
            if source[1] == "true":
                imagelist.extend( self._get_images(source[0]) )
        log('downloading images')
        for url in imagelist:
            if( self._playback_stopped_or_changed() ):
                self._set_property("ArtistSlideshow", self.CacheDir)
                self._clean_dir( self.BlankDir )
                return
            path = getCacheThumbName(url, self.CacheDir)
            path2 = getCacheThumbName(url, self.BlankDir)
            if not xbmcvfs.exists(path):
                if download(url, path, path2):
                    log('downloaded %s to %s' % (url, path) )
                    self.ImageDownloaded=True
            if self.ImageDownloaded:
                if( self._playback_stopped_or_changed() and self.ARTISTNUM == 1 ):
                    self._set_property("ArtistSlideshow", self.CacheDir)
                    self._clean_dir( self.BlankDir )
                    return
                if not self.CachedImagesFound:
                    self.CachedImagesFound = True
                    if self.ARTISTINFO == "true" and self.ARTISTNUM == 1:
                        self._get_artistinfo()
                wait_elapsed = time.time() - last_time
                if( wait_elapsed > min_refresh ):
                    if( not (self.FirstImage and not self.CachedImagesFound) ):
                        self._wait( min_refresh - (wait_elapsed % min_refresh) )
                    if( not self._playback_stopped_or_changed() and self.ARTISTNUM == 1 ):
                        self._refresh_image_directory()
                    last_time = time.time()
                self.FirstImage = False

        if self.ImageDownloaded:
            log('finished downloading images')
            self.DownloadedAllImages = True
            if( self._playback_stopped_or_changed() ):
                self._set_property("ArtistSlideshow", self.CacheDir)
                self._clean_dir( self.BlankDir )
                return
            log( 'cleaning up from refreshing slideshow' )
            wait_elapsed = time.time() - last_time
            if( wait_elapsed < min_refresh ):
                self._wait( min_refresh - wait_elapsed )
            if( not self._playback_stopped_or_changed() ):
                if self.ARTISTNUM == 1:
                    self._refresh_image_directory()
                    if self.NOTIFICATIONTYPE == "1" and not cached_image_info:
                        command = 'XBMC.Notification(%s, %s, %s, %s)' % (smartUTF8(__language__(30304)), smartUTF8(__language__(30305)), 5000, smartUTF8(__addonicon__))
                        xbmc.executebuiltin(command)
                if self.TOTALARTISTS > 1:
                    self._merge_images()
            if( xbmc.getInfoLabel( self.ARTISTSLIDESHOW ).decode("utf-8") == self.BlankDir and self.ARTISTNUM == 1):
                self._wait( min_refresh )
                if( not self._playback_stopped_or_changed() ):
                    self._refresh_image_directory()
            self._clean_dir( self.BlankDir )

        if not self.ImageDownloaded:
            log('no images downloaded')
            self.DownloadedAllImages = True
            if not self.CachedImagesFound:
                if self.ARTISTNUM == 1:
                    log('clearing ArtistSlideshow property')
                    self._set_property("ArtistSlideshow", self.InitDir)
                    if self.NOTIFICATIONTYPE == "1" and not cached_image_info:
                        command = 'XBMC.Notification(%s, %s, %s, %s)' % (smartUTF8(__language__(30302)), smartUTF8(__language__(30303)), 10000, smartUTF8(__addonicon__))
                        xbmc.executebuiltin(command)
                    if( self.ARTISTINFO == "true" and not self._playback_stopped_or_changed() ):
                        self._get_artistinfo()
        elif self.TOTALARTISTS > 1:
            self._merge_images()


    def _wait( self, wait_time ):
        waited = 0
        while( waited < wait_time ):
            time.sleep(0.1)
            waited = waited + 0.1
            if( self._playback_stopped_or_changed() ):
                self._set_property("ArtistSlideshow", self.InitDir)
                self.Abort = True
                return


    def _clean_dir( self, dir_path ):
        try:
            old_files = os.listdir( dir_path )
        except:
            old_files = []
        for old_file in old_files:
            xbmcvfs.delete( '%s/%s' % (dir_path, old_file) )
            log( 'deleting file %s/%s' % (dir_path, old_file) )


    def _refresh_image_directory( self ):
        if( xbmc.getInfoLabel( self.ARTISTSLIDESHOW ).decode("utf-8") == self.BlankDir):
            self._set_property("ArtistSlideshow", self.CacheDir)
            log( 'switching slideshow to ' + self.CacheDir )
        else:
            self._set_property("ArtistSlideshow", self.BlankDir)
            log( 'switching slideshow to ' + self.BlankDir )


    def _split_artists( self, response):
        return response.replace('ft.',' / ').replace('feat.',' / ').split(' / ')


    def _get_featured_artists( self, data ):
        the_split = data.replace('ft.','feat.').split('feat.')
        if len( the_split ) > 1:
            return self._split_artists( the_split[-1] )
        else:
            return []
    

    def _get_current_artist( self ):
        featured_artists = ''
        artists = []
        if( xbmc.Player().isPlayingAudio() == True ):
            response = xbmc.executeJSONRPC ( '{"jsonrpc":"2.0", "method":"Player.GetItem", "params":{"playerid":0, "properties":["artist"]},"id":1}' )
            try:
                artists = json.loads(response)['result']['item']['artist']
            except KeyError:
                artists = []
            if not artists:
                log( 'No artist name returned from JSON call, assuming this is an internet stream' )
                try:
                    playing_song = xbmc.Player().getMusicInfoTag().getTitle()
                    playingartist = playing_song[0:(playing_song.find('-'))-1]
                except RuntimeError:
                    playingartist = ''
                artists = self._split_artists( playingartist )
            try:
                featured_artists = self._get_featured_artists( xbmc.Player().getMusicInfoTag().getTitle() )
            except RuntimeError:
                featured_artists = []
        elif( not xbmc.getInfoLabel( self.SKINARTIST ) == '' ):
            response = xbmc.getInfoLabel( self.SKINARTIST )
            artists = self._split_artists( response )
            featured_artists = self._get_featured_artists( xbmc.getInfoLabel( self.SKINTITLE ) )
        if featured_artists:
            for one_artist in featured_artists:
                artists.append( one_artist.strip(' ()') )
        return artists


    def _playback_stopped_or_changed( self ):
        if ( set(self.ALLARTISTS) <> set(self._get_current_artist()) or self.EXTERNALCALLSTATUS != xbmc.getInfoLabel(self.EXTERNALCALL) ):
            return True
        else:
            return False


    def _get_local_images( self ):
        self.LocalImagesFound = False
        if not self.NAME:
            log('no artist name provided')
            return
        self.CacheDir = os.path.join( self.LOCALARTISTPATH, self.NAME, self.FANARTFOLDER )
        log('cachedir = %s' % self.CacheDir)
        try:
            files = os.listdir(self.CacheDir)
        except OSError:
            files = []
        for file in files:
            if(file.lower().endswith('tbn') or file.lower().endswith('jpg') or file.lower().endswith('jpeg') or file.lower().endswith('gif') or file.lower().endswith('png')):
                self.LocalImagesFound = True
        if self.LocalImagesFound:
            log('local images found')
            if self.ARTISTNUM == 1:
                self._set_property("ArtistSlideshow", self.CacheDir)
                if self.ARTISTINFO == "true":
                    self._get_artistinfo()
            if self.TOTALARTISTS > 1:
               self._merge_images()


    def _merge_images( self ):
        self.MergedImagesFound = True
        files = os.listdir(self.CacheDir)
        for file in files:
            if(file.lower().endswith('tbn') or file.lower().endswith('jpg') or file.lower().endswith('jpeg') or file.lower().endswith('gif') or file.lower().endswith('png')):
                xbmcvfs.copy(os.path.join(self.CacheDir, file), os.path.join(self.MergeDir, file))
        if self.ARTISTNUM == self.TOTALARTISTS:
            self._wait( 9.8 )
            self._set_property("ArtistSlideshow", self.MergeDir)


    def _trim_cache( self ):
        if( self.RESTRICTCACHE == 'true' and not self.PRIORITY == '2' ):
            now = time.time()
            cache_trim_delay = 0   #delay time is in seconds
            if( now - self.LastCacheTrim > cache_trim_delay ):
                log(' trimming the cache down to %s bytes' % self.maxcachesize )
                cache_root = xbmc.translatePath( 'special://profile/addon_data/%s/ArtistSlideshow/' % __addonname__ ).decode("utf-8")
                os.chdir( cache_root )
                folders = os.listdir( cache_root )
                folders.sort( key=lambda x: os.path.getmtime(x), reverse=True )
                cache_size = 0
                first_folder = True
                for folder in folders:
                    if( self._playback_stopped_or_changed() ):
                        break
                    cache_size = cache_size + self._get_folder_size( cache_root + folder )
                    log( 'looking at folder %s cache size is now %s' % (folder, cache_size) )
                    if( cache_size > self.maxcachesize and not first_folder ):
                        self._clean_dir( cache_root + folder )
                        log( 'deleted files in folder %s' % folder )
                    first_folder = False
                self.LastCacheTrim = now


    def _get_folder_size( self, start_path ):
        total_size = 0
        for dirpath, dirnames, filenames in os.walk( start_path ):
            for f in filenames:
                fp = os.path.join( dirpath, f )
                total_size += os.path.getsize( fp )
        return total_size


    def _get_images( self, site ):
        if site == "lastfm":
            self.url = self.LastfmURL + '&method=artist.getImages&artist=' + urllib.quote_plus( smartUTF8(self.NAME) )
            log( 'asking for images from: %s' %self.url )
        elif site == 'fanarttv':
            mbid = self._get_musicbrainz_id()
            log( 'the returned mbid was ' + mbid )
            if mbid:
                self.url = self.fanarttvURL + mbid + self.fanarttvOPTIONS
                log( 'asking for images from: %s' %self.url )
            else:
                return []
        elif site == 'theaudiodb':
            mbid = self._get_musicbrainz_id()
            log( 'the returned mbid was ' + str(mbid) )
            if mbid:
                self.url = self.theaudiodbURL + self.theaudiodbARTISTURL + mbid
                log( 'asking for images from: %s' %self.url )
            else:
                return []
        elif site == "htbackdrops":
            self.url = self.HtbackdropsQueryURL + '&keywords=' + self.NAME.replace('&','%26').replace(' ', '+') + '&dmin_w=' + str( self.minwidth ) + '&dmin_h=' + str( self.minheight )
            log( 'asking for images from: %s' %self.url )
        images = self._get_data(site, 'images')
        return images


    def _get_musicbrainz_info( self, mboptions, mbsearch, type, query_times ):
        mbbase = 'http://www.musicbrainz.org/ws/2/'
        theartist = self.NAME
        mb_data = []
        offset = 0
        do_loop = True
        elapsed_time = query_times['current'] - query_times['last']
        if elapsed_time < 1:
            self._wait( 1 - elapsed_time )
        elif self._playback_stopped_or_changed():
            return []        
        query_start = time.time()
        while do_loop:
            if mbsearch:
                mbquery = mbbase + mboptions + urllib.quote_plus( smartUTF8(mbsearch), ':' )
            else:
                mbquery = mbbase + mboptions + '&offset=' + str(offset)
            log( 'getting results from musicbrainz using: ' + mbquery)
            for x in range(1, 5):
                json_data = json.loads( grabURL(mbquery, User_Agent=__addonname__  + '/' + __addonversion__  + '( https://github.com/pkscout/artistslideshow )') )
                if self._playback_stopped_or_changed():
                    return []       
                if not json_data:
                    wait_time = random.randint(2,5)
                    log('site unreachable, waiting %s seconds to try again.' % wait_time)
                    self._wait( wait_time )
                else:
                    try:
                        mb_data.extend( json_data[type] )
                    except KeyError:
                        pass
                    break
            offset = offset + 100
            try:
                total_items = int(json_data[type[:-1] + '-count'])
            except KeyError:
                total_items = 0
            if (not mbsearch) and (total_items - offset > 0):
                log( 'getting more data from musicbrainz' )
                query_elapsed = time.time() - query_start
                if query_elapsed < 1:
                    self._wait(1 - query_elapsed)
                elif self._playback_stopped_or_changed():
                    return []        
            else:
                do_loop = False
        return mb_data


    def _parse_musicbrainz_info( self, type, mbid, playing_thing, query_times ):
        if self._playback_stopped_or_changed():
            return False
        log( "checking this artist's " + type + "s against currently playing " + type )
        mboptions = type + '?artist=' + mbid + '&limit=100&fmt=json'
        for thing in self._get_musicbrainz_info( mboptions, '', type + 's', query_times ):
            title = smartUTF8( thing['title'] )
            playing_title = smartUTF8( playing_thing )[:playing_thing.find('(')-2]
            log( 'comparing musicbrainz %s: %s with local %s: %s' % (type, title, type, playing_title) )
            if title.lower().startswith( playing_title.lower() ):
                log( 'found matching %s, this should be the right artist' % type )
                return True
        return False


    def _get_musicbrainz_id ( self ):
        theartist = self.NAME
        log( 'Looking for musicbrainz ID in the XBMC JSON response' )
        response = xbmc.executeJSONRPC ( '{"jsonrpc":"2.0", "method":"Player.GetItem", "params":{"playerid":0, "properties":["musicbrainzartistid"]},"id":1}' )
        try:
            mbid = json.loads(response)['result']['item']['muiscbrainzartistid']
        except (IndexError, KeyError):
            mbid = ''
        if not mbid:
            cached_mb_info = False
            log( 'no musicbrainz ID found in XBMC JSON response' )
        else:
            cached_mb_info = True
            log( 'musicbrainz ID found in XBMC JSON response' )
            return mbid
        if self._playback_stopped_or_changed():
            return ''
        if not cached_mb_info:
            log( 'Looking for musicbrainz ID in the musicbrainz.nfo file' )
            filename = os.path.join( self.CacheDir, 'musicbrainz.nfo' )
            if xbmcvfs.exists( filename ):
                mbid = readFile( filename )
                if not mbid:
                    log( 'no musicbrainz ID found in musicbrainz.nfo file' )
                    cached_mb_info = False
                else:
                    log( 'musicbrainz ID found in musicbrainz.nfo file' )
                    cached_mb_info = True
                    return str( mbid )
            else:
                log( 'no musicbrainz.nfo file found' )
                cached_mb_info = False         
        if self._playback_stopped_or_changed():
            return ''
        if not cached_mb_info:
            log( 'querying musicbrainz.com for musicbrainz ID. This is about to get messy.' )
            badSubstrings = ["the ", "a ", "an "]
            searchartist = theartist
            for badSubstring in badSubstrings:
                if searchartist.lower().startswith(badSubstring):
                    searchartist = searchartist.replace(badSubstring, "")
            mboptions = 'artist/?fmt=json&query=' 
            mbsearch = 'artist:%s' % searchartist
            query_times = {'last':0, 'current':time.time()}
            log( 'parsing musicbrainz response for muiscbrainz ID' )
            for artist in self._get_musicbrainz_info( mboptions, mbsearch, 'artist', query_times ):
                mbid=''
                if self._playback_stopped_or_changed():
                    return ''
                aliases = []
                try:
                    all_names = artist['aliases']
                except KeyError:
                    all_names = []
                if all_names:
                    for one_name in all_names:
                        aliases.append( one_name['name'].lower() )
                if artist['name'].lower() == theartist.lower() or theartist.lower() in aliases:
                    mbid = artist['id']
                    log( 'found a potential musicbrainz ID: ' + mbid )
                    try:
                        playing_album = xbmc.Player().getMusicInfoTag().getAlbum()
                    except RuntimeError:
                        playing_album = ''
                    if playing_album:
                        query_times = {'last':query_times['current'], 'current':time.time()}
                        cached_mb_info = self._parse_musicbrainz_info( 'release', mbid, playing_album, query_times )
                    if not cached_mb_info:
                        try:
                            playing_song = xbmc.Player().getMusicInfoTag().getTitle()
                        except RuntimeError:
                            playing_song = ''
                        if theartist == playing_song[0:(playing_song.find('-'))-1]:
                            playing_song = playing_song[(playing_song.find('-'))+2:]
                        if playing_song:
                            query_times = {'last':query_times['current'], 'current':time.time()}
                            cached_mb_info = self._parse_musicbrainz_info( 'work', mbid, playing_song, query_times )
                    if cached_mb_info:
                        break
                    else:
                        log( 'no matching song/album found from this artist. trying the next artist' )
            if cached_mb_info:
                log( 'musicbrainzid is %s. writing out to cache file.' % mbid )
                writeFile( mbid, filename )
                return mbid
            else:
                log( 'No musicbrainz ID found for %s.' % theartist )
                return ''            

                                
    def _get_artistinfo( self ):
        log( 'checking for local artist bio data' )
        bio = self._get_local_data( 'bio' )
        if bio == []:
            mbid = self._get_musicbrainz_id()
            log( 'the returned mbid was ' + mbid )
            if mbid:
                self.url = self.theaudiodbURL + self.theaudiodbARTISTURL + mbid
                log( 'trying to get artist bio from ' + self.url )
                bio = self._get_data( 'theaudiodb', 'bio' )
        if bio == []:
            self.url = self.LastfmURL + '&method=artist.getInfo&artist=' + urllib.quote_plus( smartUTF8(self.NAME) )
            log( 'trying to get artist bio from ' + self.url )
            bio = self._get_data('lastfm', 'bio')
        if bio == []:
            self.biography = ''
        else:
            self.biography = cleanText(bio[0])
        self.albums = self._get_local_data( 'albums' )
        if self.albums == []:
            theaudiodb_id = readFile( os.path.join(self.CacheDir, 'theaudiodbid.nfo') )
            if theaudiodb_id:
                self.url = self.theaudiodbURL + self.theaudiodbALBUMURL + theaudiodb_id
                log( 'trying to get artist albumns from ' + self.url )
                self.albums = self._get_data('theaudiodb', 'albums')
        if self.albums == []:
            self.url = self.LastfmURL + '&method=artist.getTopAlbums&artist=' + urllib.quote_plus( smartUTF8(self.NAME) )
            log( 'trying to get artist albums from ' + self.url )
            self.albums = self._get_data('lastfm', 'albums')
        self.similar = self._get_local_data( 'similar' )
        if self.similar == []:
            self.url = self.LastfmURL + '&method=artist.getSimilar&artist=' + urllib.quote_plus( smartUTF8(self.NAME) )
            self.similar = self._get_data('lastfm', 'similar')
        self._set_properties()


    def _get_local_data( self, item ):
        data = []
        filenames = []
        local_path = os.path.join( self.LOCALARTISTPATH, self.NAME, 'override' )
        if item == "similar":
            filenames.append( os.path.join( local_path, 'artistsimilar.nfo' ) )
        elif item == "albums":
            filenames.append( os.path.join( local_path, 'artistsalbums.nfo' ) )
        elif item == "bio":
            filenames.append( os.path.join( local_path, 'theaudiodbartistbio.nfo' ) )
            filenames.append( os.path.join( local_path, 'artistbio.nfo' ) )
        found_xml = True
        for filename in filenames:
            log( 'checking filename ' + filename )
            try:
                xmldata = xmltree.parse(filename).getroot()
            except:
                log('invalid or missing local xml file for %s' % item)
                found_xml = False
            if found_xml:
                break
        if not found_xml:
            return []
        if item == "bio":
            for element in xmldata.getiterator():
                if element.tag == "content":
                    bio = element.text
                    if not bio:
                        bio = ''
                    data.append(bio)
        elif( item == "similar" or item == "albums" ):
            for element in xmldata.getiterator():
                if element.tag == "name":
                    name = element.text
                    name.encode('ascii', 'ignore')
                elif element.tag == "image":
                    image_text = element.text
                    if not image_text:
                        image = ''
                    else:
                        image = os.path.join( local_path, item, image_text )
                    data.append( ( name , image ) )
        if data == '':
            log('no %s found in local xml file' % item)
        return data


    def _get_data( self, site, item ):
        data = []
        ForceUpdate = True
        if item == "images":
            if site == "lastfm":
                filename = os.path.join( self.CacheDir, 'artistimageslastfm.nfo')
            elif site == "fanarttv":
                filename = os.path.join( self.CacheDir, 'artistimagesfanarttv.nfo')
            elif site == "theaudiodb":
                filename = os.path.join( self.CacheDir, 'theaudiodbartistbio.nfo')
                id_filename = os.path.join( self.CacheDir, 'theaudiodbid.nfo')
            elif site == "htbackdrops":
                filename = os.path.join( self.CacheDir, 'artistimageshtbackdrops.nfo')
        elif item == "bio":
            if site == "theaudiodb":
                filename = os.path.join( self.CacheDir, 'theaudiodbartistbio.nfo')
                id_filename = os.path.join( self.CacheDir, 'theaudiodbid.nfo')
            elif site == "lastfm":
                filename = os.path.join( self.CacheDir, 'artistbio.nfo')
        elif item == "similar":
            filename = os.path.join( self.CacheDir, 'artistsimilar.nfo')
        elif item == "albums":
            if site == "theaudiodb":
                filename = os.path.join( self.CacheDir, 'theaudiodbartistsalbums.nfo')
            elif site == "lastfm":
                filename = os.path.join( self.CacheDir, 'artistsalbums.nfo')
        if xbmcvfs.exists( filename ):
            if time.time() - os.path.getmtime(filename) < 1209600:
                log('cached artist %s info found' % item)
                ForceUpdate = False
            else:
                log('outdated cached info found for %s ' % item)
        if ForceUpdate:
            log('downloading artist %s info from %s' % (item, site))
            if site == 'fanarttv' or site == 'theaudiodb':
                #converts the JSON response to XML
                json_data = json.loads( grabURL( self.url ) )
                if json_data:
                    if site == 'fanarttv':
                        try:
                            json_data = dict(map(lambda (key, value): ('artistImages', value), json_data.items()))
                        except AttributeError:
                            return_data
                    writeFile( dicttoxml( json_data ).encode('utf-8'), filename )
                    json_data = ''
                else:
                    return data
            elif not saveURL( self.url, filename ):
                return data
        try:
            xmldata = xmltree.parse(filename).getroot()
        except:
            log('invalid or missing xml file')
            xbmcvfs.delete(filename)
            return data
        if item == "images":
            if site == "lastfm":
                for element in xmldata.getiterator():
                    if element.tag == "size":
                        if element.attrib.get('name') == "original":
                            width = element.attrib.get('width')
                            height = element.attrib.get('height')
                            if ( int(width) >= self.minwidth ) and ( int(height) >= self.minheight ):
                                if(self.HDASPECTONLY == 'true'):
                                    aspect_ratio = float(width)/float(height)
                                    if(aspect_ratio > 1.770 and aspect_ratio < 1.787):
                                        data.append(element.text)
                                else:
                                    data.append(element.text)
            elif site == "fanarttv":
                for element in xmldata.getiterator():
                    if element.tag == "url":
                        data.append(element.text)
            elif site == "theaudiodb":
                for element in xmldata.getiterator():
                    if element.tag.startswith( "strArtistFanart" ):
                        if element.text:
                            data.append(element.text)
                    if element.tag == 'idArtist' and not xbmcvfs.exists( id_filename ):
                        writeFile( element.text, id_filename )
            elif site == "htbackdrops":
                for element in xmldata.getiterator():
                    if element.tag == "id":
                        data.append(self.HtbackdropsDownloadURL + str( element.text ) + '/fullsize')
        elif item == "bio":
            if site == "theaudiodb":
                for element in xmldata.getiterator():
                    if element.tag == "strBiography" + self.LANGUAGE.upper():
                        bio = element.text
                        if not bio:
                            bio = ''
                        data.append(bio)            
                    if element.tag == 'idArtist' and not xbmcvfs.exists( id_filename ):
                        writeFile( element.text, id_filename )
            if site == "lastfm":
                for element in xmldata.getiterator():
                    if element.tag == "content":
                        bio = element.text
                        if not bio:
                            bio = ''
                        data.append(bio)
        elif item == "similar":
            if site == "lastfm":
                for element in xmldata.getiterator():
                    if element.tag == "name":
                        name = element.text
                        name.encode('ascii', 'ignore')
                    elif element.tag == "image":
                        if element.attrib.get('size') == "mega":
                            image = element.text
                            if not image:
                                image = ''
                            data.append( ( name , image ) )
        elif item == "albums":
            if site == "theaudiodb":
                match = False
                for element in xmldata.getiterator():
                    if element.tag == "strAlbum":
                        name = element.text
                        name.encode('ascii', 'ignore')
                        match = True
                    elif element.tag == "strAlbumThumb" and match:
                        image = element.text
                        if not image:
                            image = ''
                        data.append( ( name , image ) )            
                        match = False
            if site == "lastfm":
                match = False
                for element in xmldata.getiterator():
                    if element.tag == "name":
                        if match:
                            match = False
                        else:
                            name = element.text
                            name.encode('ascii', 'ignore')
                            match = True
                    elif element.tag == "image":
                        if element.attrib.get('size') == "extralarge":
                            image = element.text
                            if not image:
                                image = ''
                            data.append( ( name , image ) )
        if data == '':
            log('no %s found on %s' % (item, site))
        return data


    def _set_properties( self ):
      self._set_property("ArtistSlideshow.ArtistBiography", self.biography)
      for count, item in enumerate( self.similar ):
          self._set_property("ArtistSlideshow.%d.SimilarName" % ( count + 1 ), item[0])
          self._set_property("ArtistSlideshow.%d.SimilarThumb" % ( count + 1 ), item[1])
      for count, item in enumerate( self.albums ):
          self._set_property("ArtistSlideshow.%d.AlbumName" % ( count + 1 ), item[0])
          self._set_property("ArtistSlideshow.%d.AlbumThumb" % ( count + 1 ), item[1])


    def _clear_properties( self ):
        self._set_property( "ArtistSlideshow", self.InitDir )
        self._clean_dir( self.MergeDir )
        self._set_property( "ArtistSlideshow.ArtistBiography" )
        for count in range( 50 ):
            self._set_property( "ArtistSlideshow.%d.SimilarName" % ( count + 1 ) )
            self._set_property( "ArtistSlideshow.%d.SimilarThumb" % ( count + 1 ) )
            self._set_property( "ArtistSlideshow.%d.AlbumName" % ( count + 1 ) )
            self._set_property( "ArtistSlideshow.%d.AlbumThumb" % ( count + 1 ) )

    #sets a property (or clears it if no value is supplied)
    #does not crash if e.g. the window no longer exists.
    def _set_property( self, property_name, value=""):
      try:
        self.WINDOW.setProperty(property_name, value)
      except:
        pass
        log(" *************** Exception: Couldn't set propery " + property_name + " value " + value)


if ( __name__ == "__main__" ):
    log('script version %s started' % __addonversion__)
    slideshow = Main()
    try:
        slideshow._set_property("ArtistSlideshow.CleanupComplete", "True")
    except:
        pass

log('script stopped')