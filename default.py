from kodi_six import xbmc
import resources.lib.artistslideshow as ArtistSlideshow

if ( __name__ == "__main__" ):
    slideshow = ArtistSlideshow.Main()
    slideshow.run()
xbmc.log( '[Artist Slideshow] script stopped', xbmc.LOGNOTICE )