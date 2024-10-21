# Mezzmo TV Show Trailers Channel
Add a channel to your Mezzmo server to view movie trailers from <a href="https://www.themoviedb.org/">TMDB</a>.  


## Features:

- Get current TMDB TV Show trailer information for Popular, Airing Today, Currently Airing and Top Rated TV Shows
- Download TV Show trailers and TV Show artwork for local playback through your Mezzmo server
- User selectable feature of 480P, 720P or 1080P quality trailers (if available, otherwise best quality available)
- Automatically move trailers to designated location (i.e. NAS, local disk etc.)
- Option for how many TV Shows to keep for each category (1-100) or unlimited
- Automatic skipping of TV Shows with no trailer files
- Configuration setting for the TV Shows preferred origin country
- Automatic Kodi database search for existing episodes and actor information
- Option to set output trailer output format to mp4 or mkv 
- Full detailed logfile
- Full Mezzmo TV Show Trailer channel statistics
- CSV export of trailer information and checker history 
- Command line backups of Mezzmo TV Show Trailers Channel database
- User ability to clear trailer information by TV Show category
- Client software now available in both native Python and Windows x64 formats  
<br/>

## Installation and usage:

-  Download the Mezzmo TV Show Trailers Channel release zipfile
-  Ensure you have Python installed on Windows. Minimum version 3.x or use the Windows x64 exe version
-  Unzip file into an empty folder on your system
-  The zipfile contains 2 folders, client and server
-  The client folder stays on your local workstation and contains the trailer downloader
-  The server folder goes onto your Mezzmo server in the Mezzmo Channels folder
-  The Mezzmo channels folder is typically located at c:\ProgramData\Conceiva\Mezzmo\Plugins\   
-  Edit the config.text client file with the location of your trailer folder and preferred output format
-  It is <b>highly suggested</b> not to use the same trailer folder as the <a href="https://github.com/jbinkley60/MezzmoTrailerChecker/wiki">Mezzmo Trailer Checker</a>  
-  Open a command window and run tvshow_trailers.py trailers now<br/>
   See optional command line arguments below.
-  The client will build the database, check folder locations and download the Now Playing movie trailers
-  Next install the <a href="http://www.mezzmo.com/wiki/doku.php?id=adding_channels">Mezzmo TV Show Trailers Channel</a> into Mezzmo
-  Open the Mezzmo TV Show Trailers Channel in the Mezzmo GUI and set the trailer path location <br>
   in Properties->Settings       

<br>
   
## Command line arguments:  (Limit 1 at a time)

- <b>trailers on</b>	-  Checks for TV Shows currently on-the-air <br>
- <b>trailers air</b>   -  Checks for Upcoming TV Shows airing today <br>
- <b>trailers pop</b>   -  Checks for Popular TV Shows <br>
- <b>trailers top</b>   -  Checks for Top Rated Shows <br>
- <b>trailers all</b>   -  Checks for all for TV Show categories <br>
- <b>clean category</b> -  Clears trailer database info for TV Shows by category and deletes downloaded trailer file <br>
- <b>clean files</b>    -  Analyzes trailer files and database entries for missing files and entries <br>  
- <b>csv trailers</b>   -  Creates a CSV file with the trailer information in the Mezzmo TV Show Trailers Channel<br> 
- <b>csv history</b>    -  Creates a CSV file with the history information in the Mezzmo TV Show Trailers Channel<br>
- <b>stats</b>          -  Creates a time stamped file name backup of the Mezzmo TV Shows Trailers Channel database <br>
- <b>backup</b>         -  Creates a time stamped file name backup of the Mezzmo Trailer Checker database <br> 
          
          

           
<br/><img src="https://github.com/Conceiva/MovieTrailer/assets/63779136/1f65376d-2a70-4337-a0c7-a4899164b0a8" width="40%" height="40%">

