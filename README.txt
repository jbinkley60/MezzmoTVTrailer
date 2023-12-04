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

