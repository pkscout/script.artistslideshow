-----How to use this addon:

You must have a compatible skin (or update your skin using the instructions below).

There are three groupings of settings: Download, Slideshow, and Advanced.

Download
-Download images from last.fm (default true)
 (self expanitory)
-Download images from htbackdrops.com (default false)
 (self expanitory)
-Minimal image width and height: (default 0,0)
 any images smaller than the set dimensions will not be downloaded.
-Download only 16:9 images: (default false)
 will discard any images that aren't really, really close to a 16:9 aspect ratio.
-Download additional artist info: (default false)
 includes information like the artist's bio and artists similar to the one to which you are
 listening.  includes option to select download language.  skin must support this extra
 information, or nothing will be displayed.

Slideshow
-Local artist folder: (default none)
 path to a directory that has artist images.  Images must be organized in artist/extrafanart/
-Fallback slideshow folder: (default none)
 path to a directory of images that should be used if no local or remote images can be found.
-Priority: (default remote first)
 three options: remote first, local first, both
  remote first will try and download images from remote sites.  if none found will use local
  images. if none found will use fallback slideshow
  local first will use local images.  if none found will try and download remote images. if none
  found will use fallback slideshow
  both will check for local images first.  if they exist the downloaded images will be placed in
  the same directory as the local images.  if not remote images will be stored in normal cache dir.
-Override slideshow folder: (default none)
 path to a directory of images that should be used intead of artist artwork. With this set no
 artwork will ever be downloaded.
 
Advanced
-Limit size of download cache: (default false)
 if enabled, the download cache will be trimmed (oldest first) to keep the size below the specified
 minimum
-Maximum cache size (in megabytes): (default 1024mb)
 if Limit size of download cache is set to true, this allows the user to specify the maximum size
 of the cache (from 128mb to 4096mb)


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
	<timeperimage>10000</timeperimage>
	<fadetime>2000</fadetime>
	<randomize>true</randomize>
	<animation effect="fade" start="0" end="100" time="300">Visible</animation>
	<animation effect="fade" start="100" end="0" time="300">Hidden</animation>
</control>

You can also start this script at startup instead:
- RunScript(script.artistslideshow,daemon=True)
this will keep the script running all the time.

The script provides these properties to the skin:

Window(Visualisation).Property(ArtistSlideshow)
 This is the path to the directory containing the downloaded images for the currently playing
 artist

Window(Visualisation).Property(ArtistSlideshow.ArtistBiography)
 Artist biography from last.fm

Window(Visualisation).Property(ArtistSlideshow.%d.SimilarName)
Window(Visualisation).Property(ArtistSlideshow.%d.SimilarThumb)
 Similar artists

Window(Visualisation).Property(ArtistSlideshow.%d.AlbumName)
Window(Visualisation).Property(ArtistSlideshow.%d.AlbumThumb)
 Albums by the artist

Window(Visualisation).Property(ArtistSlideshowRunning)
 This one is used internally by the script to check if it is already running.
 There's no need to use this property in your skin.
 
Window(Visualisation).Property(ArtistSlideshow.CleanupComplete)
 This one is used internally by the script to tell an external script that it
 is done running and is exiting.

 
----How to call this addon from another addon

To use this addon to provide the background for another addon, your addon must create a window that uses a multimage control the same as above.  That window must have an infolabel in which the currently playing artist is stored.  It is the responsibility of the calling addon to change that infolabel when the artist changes.

The created window can call this addon by using:

RunScript(script.artistslideshow,windowid=<somenumber>&artistfield=<infolabelname>)

where <somenumber> is the number of the window the calling addon created and <infolabelname> if the name of the infolabel where the currently playing artist is being stored.

Artistslideshow should be called only once when you first instantiate the window with the specified windowid.  When your script exits you should set the artist infolabel you defined in the call to empty.  ArtistSlideshow will set the window property Artistslideshow.CleanupComplete to True when it is done with cleanup and exiting.  You should check that this property is True before destroying the Window with the windowid used to call ArtistSlideshow.