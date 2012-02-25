-----How to use this addon:

You must have a compatible skin (or update your skin using the instructions below).

There are two groupings of settings: Download and Slideshow.

Download
-Download images from last.fm (self expanitory)
-Download images from htbackdrops.com (self expanitory)
-Minimal image width and height: any images smaller than the set dimensions will not be downloaded.
-Download only 16:9 images: will discard any images that aren't really, really close to a 16:9 aspect ratio.
-Download additional artist info: includes information like the artist's bio and artists similar to the one to which you are listening.  Your skin must support this extra information, or nothing will be displayed.

Slideshow
-Local artist folder: path to a directory that has artist images.  Images must be organized in artist/extrafanart/
-Prioritize local artwork: if set to true, the addon will use your local artwork if found.  If none is found, the addon will attempt to download remote artwork.
-Fallback slideshow folder: path to a directory of images that should be used if no local or remote images can be found.
-Override slideshow folder: path to a directory of images that should be used intead of artist artwork. With this set no artwork will ever be downloaded.
-Fade time after all images loaded: when the addon starts downloading images, it shows the first one while it downloads all the others.  When it refreshes the directory it fades out and back in.  For the most seamless experience, set this to the same fade time as your skin uses.
-Refresh slideshow after every image download: if set to true, the slideshow will refresh after every image instead of after all the images are downloaded.  This is really only useful for slow connections.


-----How to use this addon in your skin:

In MusicVisualisation.xml:

- 1) Set the default control to 999:
<defaultcontrol>999</defaultcontrol>

- 2) Add a button to start the script:
<control type="button" id="999">
	<posx>-10</posx>
	<posy>-10</posy>
	<width>1</width>
	<height>1</height>
	<onfocus>RunScript(script.artistslideshow)</onfocus>
</control>

- 3) Add a multiimage conrol:
<control type="multiimage">
	<posx>0</posx>
	<posy>0</posy>
	<width>1280</width>
	<height>720</height>
	<imagepath background="true">$INFO[Window(Visualisation).Property(ArtistSlideshow)]</imagepath>
	<aspectratio>keep</aspectratio>
	<timeperimage>5000</timeperimage>
	<fadetime>2000</fadetime>
	<randomize>true</randomize>
	<animation effect="fade" start="0" end="100" time="300">Visible</animation>
	<animation effect="fade" start="100" end="0" time="300">Hidden</animation>
</control>


You can also start this script at startup instead:
- RunScript(script.artistslideshow,daemon=True)
this will keep the script running all the time.


The script provides these properties to the skin:

- Window(Visualisation).Property(ArtistSlideshow)
This is the path to the directory containing the downloaded images for the currently playing artist

- Window(Visualisation).Property(ArtistSlideshowRefresh)
DEPRECIATED.  No longer needed as of v.?????
This can be used to fade out/fade in the slideshow when the path is refreshed.
The path will refresh after all images for a certain artist have been downloaded.
This is needed since xbmc will not automatically pick up any new images after the multiimage control has been loaded.

- Window(Visualisation).Property(ArtistSlideshowRunning)
This one is used internally by the script to check if it is already running.
There's no need to use this property in your skin.

- Window(Visualisation).Property(ArtistSlideshow.ArtistBiography)
Artist biography from last.fm

- Window(Visualisation).Property(ArtistSlideshow.%d.SimilarName)
- Window(Visualisation).Property(ArtistSlideshow.%d.SimilarThumb)
Similar artists

- Window(Visualisation).Property(ArtistSlideshow.%d.AlbumName)
- Window(Visualisation).Property(ArtistSlideshow.%d.AlbumThumb)
Albums by the artist

