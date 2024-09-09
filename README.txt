v1.0.5 9/6/2024

- Fixed a bug where the Airing Today and Currently Airing TV Show categories
  were not honoring the configuration trailer keep limit setting.
- Fixed a bug where an exception error would occur if a trailer file being
  deleted, during the limit checking, didn't exist on disk and had a non-ASCII
  character in the file name which couldn't be encoded by the local computer
  code page.  This would cause the number of trailers to exceed the config
  file limit setting.

v1.0.4  8/19/2024

- Updated yt-dlp.exe to eliminate warning messages
- Added automatic yt-dlp.exe update checking/updating to the latest version
- Added setting to limit the maximum number of new trailers per category to 
  fetch per run

v1.0.3  3/29/2024

- Fixed API key issue causing 401 errors from TMDB
- Updated yt-dlp.exe to a new version to fix other You Tube errors
- Updated format parsing to handle newer You Tube formats

v1.0.2  12/18/2023

- Added feature to trim database history table to 1000 lines and the
  logfile to 15000 lines automatically getting to 100% completely
  maintenance free running when running as a scheduled task. 
- Modified the total fetch counter to be for the last 30 days to 
  align to the automatic pruning of the history table.

v1.0.1  12/4/2023

- Improved speed and significant reduction in TMDB API calls by
  changing the method / order for determining existing trailers 
  in the database and origin country
- Added unavailable trailer tracking table which will recheck
  unavailable trailers every 3 days
- Fixed a bug which was causing some trailers to be incorrectly 
  deleted when checking the trailer limits and then rediscovered
- Improved statistics shown at the end of a trailer check run
- Improved logging when TV Show videos exist but none are trailers
- Fixed bug where TV SHows with nonprintable characters in the 
  title could cause an exception error
- Updated the server poster file to be TV Shows instead of Movies

v1.0.0  11/25/2023

- Initial production release

