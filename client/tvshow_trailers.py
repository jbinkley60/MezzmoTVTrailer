# -*- coding: utf-8 -*-
# #!/usr/bin/python
import os, fnmatch, sys, csv, json, glob
from datetime import datetime, timedelta
import time
import urllib.request, urllib.parse, urllib.error
import http.client
import mimetypes
import subprocess
import string, random, re
from urllib.request import Request, urlopen


trailerdb = ''
tr_config = {}
totcount = dupcount = notrailer = nocountry = badtrailer = 0

# TV Show trailer feed URLs

TVTRAILERS_URL_LIST  = 'http://api.themoviedb.org/3/tv/{}?{}&api_key=a6898792995042896256585082db0842'
TVTRAILERS_URL_CONFIG    = 'http://api.themoviedb.org/3/configuration?api_key=a6898792995042896256585082db0842'
TVTRAILERS_URL_DETAILS   = 'http://api.themoviedb.org/3/tv/{}?api_key=a6898792995042896256585082db0842&append_to_response=videos,releases,casts'
TVTRAILERS_URL_YOUTUBE   = 'https://www.youtube.com/watch?v={}'
TVTRAILERS_URL_BASE      = ''
TVTRAILERS_POSTER_SIZE   = 'w500'
TVTRAILERS_BACKDROP_SIZE = 'original'

version = 'version 1.0.4'

sysarg1 = sysarg2 = sysarg3 = sysarg4 = ''

if len(sys.argv) == 2:
    sysarg1 = sys.argv[1]
if len(sys.argv) == 3:
    sysarg1 = sys.argv[1]   
    sysarg2 = sys.argv[2]

if len(sys.argv) == 4:
    sysarg1 = sys.argv[1]   
    sysarg2 = sys.argv[2]
    sysarg3 = sys.argv[3]
 
if len(sys.argv) == 5:
    sysarg1 = sys.argv[1]   
    sysarg2 = sys.argv[2]
    sysarg3 = sys.argv[3]
    sysarg4 = sys.argv[4]


def checkVersion():

    if sys.version_info[0] < 3:
        print('\nThe Mezzmo TvShow Trailers Channel requires Python version 3 or higher')
        print('Python version: ' + str(sys.version_info[0]) + '.' + str(sys.version_info[1])   \
        + '.' + str(sys.version_info[2]) + ' found.')
        exit()  


def getConfig():

    try: 

        global tr_config, version      
        fileh = open("config.txt")                                     # open the config file

        data = fileh.readline()                                        # Get local channels location
        datab = data.split('#')                                        # Remove comments
        ltrailerloc = datab[0].strip().rstrip("\n")                    # cleanup unwanted characters

        data = fileh.readline()                                        # Get Mezzmo channels location
        dataj = data.split('#')                                        # Remove comments
        mtrailerloc = dataj[0].strip().rstrip("\n")                    # cleanup unwanted characters

        data = fileh.readline()                                        # Get number of trailers to keep
        datac = data.split('#')                                        # Remove comments
        tkeepcount = datac[0].strip().rstrip("\n")                     # cleanup unwanted characters
        if int(tkeepcount) > 100:
            tkeepcount = 100                                           # Max trailers per type is 100

        data = fileh.readline()                                        # Get trailer max resolution
        datae = data.split('#')                                        # Remove comments
        maxres = datae[0].strip().rstrip("\n")                         # cleanup unwanted characters
        if maxres not in ['1080', '720', '480'] :
            maxres = '720'                                             # Default to 720P

        data = fileh.readline()                                        # Logfile location
        if data != '':
            datai = data.split('#')                                    # Remove comments
            logoutfile = datai[0].strip().rstrip("\n")                 # cleanup unwanted characters         
        else:
            logoutfile = 'logfile.txt'                                 # Default to logfile.txt

        data = fileh.readline()                                        # Get output format option
        if data != '':
            datav = data.split('#')                                    # Remove comments
            tformat = datav[0].strip().rstrip("\n").lower()            # cleanup unwanted characters
        else:
            tformat = 'mp4'

        data = fileh.readline()                                        # Get TV Show country
        dataf = data.split('#')                                        # Remove comments
        country = dataf[0].strip().rstrip("\n").lower()                # cleanup unwanted characters
        if country not in ['us', 'fr', 'cn', 'de', 'jp'] :
            country = 'us'                                             # Default to US

        data = fileh.readline()                                        # Get maximum number of trailers to fecth per run
        if data != '':
            datar = data.split('#')                                    # Remove comments
            mfetch = datar[0].strip().rstrip("\n")                     # cleanup unwanted characters
        else:
            mfetch = '20'                                              # 20 trailers per fetch is the default
        if int(mfetch) > 40:
            mfetch = 40                                                # Max trailers per fetch is 40

        fileh.close()                                                  # close the file
        
        tr_config = {
                     'baseloc': ltrailerloc,
                     'ltrailerloc': ltrailerloc + '\\tvshows',
                     'mtrailerloc': mtrailerloc + '\\tvshows',
                     'mcount': tkeepcount,
                     'maxres': maxres,
                     'logoutfile': logoutfile,
                     'tformat': tformat,
                     'country': country,
                     'mfetch': mfetch,
                    }

        if not tformat in ['mkv', 'mp4']:
            tformat = 'mp4'
            mgenlog = 'Invalid output format in config file.  Defaulting to mp4 format'
            genLog(mgenlog)
            print(mgenlog) 

        configuration = [ltrailerloc, mtrailerloc, tkeepcount, maxres, logoutfile, tformat, country, mfetch]
        mgenlog = ("Mezzmo TvShow Trailers Channel Checker Client - " + version)
        print(mgenlog)
        genLog(mgenlog)
        genLog(str(configuration))               # Record configuration to logfile     
        mgenlog = "Finished reading config file."
        genLog(mgenlog)       
        return 
 
    except Exception as e:
        print (e)
        mgenlog = 'There was a problem parsing the config file.'
        genLog(mgenlog)
        print(mgenlog)
        exit()


def checkCommands(sysarg1, sysarg2):                                   # Check for valid commands
   
    if len(sysarg1) > 1 and sysarg1.lower() not in ['trailers', 'csv', 'help', 'backup', 'clean', 'stats']:
        displayHelp(sysarg1)
        exit()
    if len(sysarg1) == 0 or 'help' in sysarg1.lower():
        displayHelp(sysarg1)
        exit()


def displayHelp(sysarg1):                                 #  Command line help menu display

        print('\n=====================================================================================================')
        print('\nThe only valid commands are -  trailers, csv, backup, clean, stats, and help  ')
        print('\nExample:  mezzmo_tvtrailers.py trailers now')      
        print('\ntrailers on\t - Checks for TV Shows currently on-the-air')
        print('trailers air\t - Checks for Upcoming TV Shows airing today')
        print('trailers pop\t - Checks for Popular TV Shows')
        print('trailers top\t - Checks for Top Rated TV Shows ')
        print('trailers all\t - Checks for all for TV Show categories ')
        print('\nclean category\t - Clears trailer database info for TVShows by category and deletes downloaded trailer file')
        print('\t\t   Valid types are: on, air, pop, top, all') 
        print('clean files\t - Analyzes trailer files and database entries for missing files and entries')
        print('\ncsv trailers\t - Creates a CSV file with the trailer information')
        print('csv history\t - Creates a CSV file with the history information')
        print('\nstats\t\t - Generates summary statistics for trailers')
        print('\nbackup\t\t - Creates a time stamped file name backup of the Mezzmo TVShow Trailers Channel database')
        print('\n=====================================================================================================')
        print('\n ')


def getMezzmoTrailers(sysarg1= '', sysarg2= '', sysarg3 = ''):    #  Get Movie Channel Trailers  
    
    global tr_config
    global dupcount, totcount, notrailer, nocountry, badtrailer

    tcountry = tr_config['country'].upper()
    #print(tcountry)
 
    mtype = []                                                # list of trailers for a given type

    try:
        if not sysarg1.lower() in ['trailers', 'sync']:
            return
        if sysarg2.lower() not in ['air', 'on', 'top', 'pop', 'all']:
            print('\nThe valid trailers options are:  air, on, pop, top and all\n')
            return

        if sysarg2.lower() == 'air':
            mtype = ['airing_today']
        elif sysarg2.lower() == 'on':
            mtype = ['on_the_air']
        elif sysarg2.lower() == 'top':
            mtype = ['top_rated']
        elif sysarg2.lower() == 'pop':
            mtype = ['popular']
        elif sysarg2.lower() == 'all':
            mtype = ['airing_today', 'on_the_air', 'popular', 'top_rated']

        if len(sysarg3) > 0 and sysarg3.isdigit():            # Allow for specifc page fetch
            pages = [str(sysarg3)]
        else:
            pages = getPages()                                # Get list of pages to fetch              
 
        for type in mtype:
            ccount = 0                                        # Category match counter
            for page in pages:
                #print('Page number and counters are: ' + page + '  ' + str(ccount))
                if ccount >= int(tr_config['mfetch']):        # Stop page checking when max fetch reached
                    break
                
                jresponse = urllib.request.urlopen(TVTRAILERS_URL_LIST.format(type, 'page=' + str(page)))
                json_obj = json.load(jresponse)
                #print(str(json_obj))
                jresponse.close()
                
                if json_obj.get('results'):
                    mgenlog = 'Number of TVShows ' + type + ' found: ' + str(len(json_obj['results'])) + \
                    ' Page: ' + str(page)
                    genLog(mgenlog)
                    print(mgenlog)

                    for trailer in json_obj['results']:
                        if ccount >= int(tr_config['mfetch']):        # Stop when max fetch reached
                            mgenlog = 'TVShow category trailer limit reached: ' + type
                            genLog(mgenlog)
                            print(mgenlog)  
                            break

                        cdupe = checkDupe(trailer['id'], trailer['name'], type)  # Check if TV Show already in database
                        #print('Countries are: ' + str(trailer['origin_country']))
                        cmatch = checkCountry(trailer['origin_country'], trailer['id'], trailer['name'])
                        #print('Cmatch value ' + str(cmatch) + ' ' + str(cdupe))
                        item = None
                        if cdupe == 0 and cmatch == 0:
                            print('Trying for trailer: ' + trailer['name'] + '  ' + str(trailer['id']))
                            item = getTrailerDetails(trailer['id'], trailer['name'])
                        elif cmatch == 0:
                            dupcount += 1
                        elif cmatch == 1:
                            nocountry += 1                                  
                        if item != None :                                # Check nondupe trailer and good country
                            checkTrailer(item, type)                     # Update trailer information
                            trbad = checkBad(item)                       # Check if trailer already marked bad              
                            if trbad == 0:
                                trresults = getTrailer(item['uri'])      # Fetch trailer 
                                if trresults[0] == 0:                    # New trailer fetched
                                    trname = checkFormats(trresults[1])  # Check if encoding needs changed
                                    if trname != 0:                      # Trailer file reencoded                           
                                        moveTrailers(trname)             # Move trailer to trailer folder
                                        updateTempHist(item['tmdb_id'], trname, trresults[2], trresults[3])
                                        getArtwork(item['tmdb_id'], item['poster_uri'], item['backdrop_uri'])
                                else:
                                    badtrailer += 1
                                    addbadTrailer(item, type)            # Add to bad trailer table
                                totcount += 1
                                ccount += 1
                            elif trbad > 0:                              # Trailer already marked unavailable
                                badtrailer += 1
                                mgenlog = 'Skipping trailer previously marked unavailable: ' + item['uri']
                                print(mgenlog)
                                genLog(mgenlog)                   
                        else:
                            notrailer += 1
    except Exception as e:
        print (e)
        mgenlog = 'There was an error getting TVShow Trailers Channel listing for: ' + type
        print(mgenlog)
        genLog(mgenlog)           


def getTrailerDetails(id, trname):

    global TVTRAILERS_URL_BASE

    try:
        if TVTRAILERS_URL_BASE == '':
            # retrieve JSON content about themoviedb.org configuration so we can get its base URL
            file = urllib.request.urlopen(TVTRAILERS_URL_CONFIG)
            json_obj = json.load(file)
            file.close()
            if json_obj.get('images'):
                TVTRAILERS_URL_BASE = json_obj['images']['base_url']

        if TVTRAILERS_URL_BASE == '':                # error - could not get base url
            return None
        
        # retrieve JSON content about this movie and parse it
        file = urllib.request.urlopen(TVTRAILERS_URL_DETAILS.format(id))
        json_obj = json.load(file)
        file.close()

        item = {                                        # Movie information dictionary
                 'tmdb_id': id,
                 'title': '',
                 'uri': '',
                 'type': 'video',
                 'description': '',
                 'tagline': '',
                 'release_date': '',
                 'imdb_id': '',
                 'website': '',
                 'poster_uri': '',
                 'backdrop_uri': '',
                 'user_rating': 0,
                 'genre': '',
                 'production_company': '',
                 'content_rating': '',
                 'artist_actor': '',
                 'album_series': '',
                 'composer_director_creator': '',
                 'country': '',
                 'language': ''
               }
        
        # make sure it has a trailer video
        vidlength = len(json_obj.get('videos')['results'])
        print('Number of videos found ' + str(vidlength))
        if vidlength == 0:
            try:
                mgenlog = 'No trailers found for TV Show. Skipping TV Show: ' + trname
                print(mgenlog)
                genLog(mgenlog) 
            except:
                mgenlog = 'No trailers found for TV Show. Skipping TV Show: TMDB ID ' + str(item['tmdb_id'])
                print(mgenlog)
                genLog(mgenlog)  
            return None
        if json_obj.get('videos'):
            videos = json_obj['videos']
            #print(str(videos))
            if videos.get('results'):
                results = videos['results']
                for video in results:
                    if video.get('type') and video['type'] == 'Trailer' and video.get('key') \
                    and (video['site'] == 'YouTube' or video['site'] == None):
                        #item['title'] = json_obj['title']
                        try:
                            item['title'] = json_obj['name']
                            item['uri'] = TVTRAILERS_URL_YOUTUBE.format(video['key'])
                            print(item['uri'])
                            if json_obj.get('overview'):
                                item['description'] = json_obj['overview']
                            if json_obj.get('tagline'):
                                item['tagline'] = json_obj['tagline']
                            if json_obj.get('first_air_date'):
                                item['release_date'] = json_obj['first_air_date']
                            if json_obj.get('origin_country'):
                                countries = json_obj['origin_country']
                                for country in countries:
                                    item['country'] = item['country'] + country + ' ##'
                                item['country'] = item['country'].rstrip('##')
                            if json_obj.get('original_language'):
                                item['language'] = json_obj['original_language']                      
                            if json_obj.get('imdb_id'):
                                item['imdb_id'] = json_obj['imdb_id']
                            if json_obj.get('homepage'):
                                item['website'] = json_obj['homepage']
                            if json_obj.get('poster_path'):
                                item['poster_uri'] = '{}{}{}'.format(TVTRAILERS_URL_BASE, TVTRAILERS_POSTER_SIZE,     \
                                json_obj['poster_path'])
                            if json_obj.get('backdrop_path'):
                                item['backdrop_uri'] = '{}{}{}'.format(TVTRAILERS_URL_BASE, TVTRAILERS_BACKDROP_SIZE, \
                                json_obj['backdrop_path'])
                            if json_obj.get('vote_average'):
                                item['user_rating'] = int((json_obj.get('vote_average') + 0.5)/2.0)
                            if json_obj.get('belongs_to_collection'):
                                item['album_series'] = json_obj.get('belongs_to_collection')['name']
                            if json_obj.get('genres'):
                                genres = json_obj['genres']
                                for genre in genres:
                                    item['genre'] = item['genre'] + genre['name'] + '##'
                                item['genre'] = item['genre'].rstrip('##')
                            if json_obj.get('production_companies'):
                                companies = json_obj['production_companies']
                                for company in companies:
                                    item['production_company'] = item['production_company'] + company['name'] + '##'
                                item['production_company'] = item['production_company'].rstrip('##')
                            if json_obj.get('releases'):
                                releases = json_obj['releases']
                                if releases.get('countries'):
                                    countries = releases['countries']
                                    for country in countries:
                                        if country['iso_3166_1'] == "US":
                                            item['content_rating'] = country['certification']
                                            break
                                    if item['content_rating'] == None and len(countries) > 0:
                                        item['content_rating'] = country[0]['certification']
                            if json_obj.get('casts'):
                                casts = json_obj['casts']
                                if casts.get('cast'):
                                    cast = casts['cast']
                                    acount = 0
                                    for actor in cast:
                                        item['artist_actor'] = item['artist_actor'] + actor['name'] + '##'
                                        acount += 1
                                        if acount > 9:
                                            item['artist_actor'] = item['artist_actor'].rstrip('##')
                                            break
                                    item['artist_actor'] = item['artist_actor'].rstrip('##')
                            if json_obj.get('created_by'):
                                created_bys = json_obj['created_by']
                                for creator in created_bys:
                                    item['composer_director_creator'] = item['composer_director_creator'] +   \
                                    creator['name'] + '##'
                                item['composer_director_creator'] = item['composer_director_creator'].rstrip('##')
                            return item
                        except:
                            mgenlog = 'There was a problem parsing TV Show Trailers Details for: ' + str(id)
                            print(mgenlog)
                            genLog(mgenlog)                             
                            return None
                if len(item['uri']) == 0:
                    #print('Length of item URI is: ' + str(len(item['uri'])))
                    mgenlog = 'No TV Show trailer videos found for TMDB_ID: ' + str(id)
                    print(mgenlog)
                    genLog(mgenlog)
        return None

    except Exception as e:
        print (e)
        mgenlog = 'There was an error getting TV Show Trailers Details for: ' + str(id)
        print(mgenlog)
        genLog(mgenlog)  
                

def checkDupe(tmdb_id, tname, mtype):                      # Check if trailer / movie already in database

        db = openTrailerDB()
        found = 0
        
        #mtitle = item['title']

        trcurr = db.execute('SELECT trTitle from tvTrailers WHERE tmdb_id = ?', (tmdb_id,)) 
        trtuple = trcurr.fetchone()
        del trcurr

        if trtuple:
            try:
                mgenlog = 'TV Show already in database, skipping: ' + trtuple[0]
                genLog(mgenlog)
                print(mgenlog)
            except:
                mgenlog = 'TV Show already in database, skipping: TMDB ID - ' + str(tmdb_id)
                genLog(mgenlog)
                print(mgenlog)
            found = 1
        else:
            try:                                            # Handle unprintable characters
                mgenlog = 'New TV Show found: ' + tname
                genLog(mgenlog)
                print(mgenlog)
            except:
                mgenlog = 'New TV Show found - ' + 'TMDB ID - ' + str(tmdb_id)
                genLog(mgenlog)
                print(mgenlog)

        db.close()
        return found


def checkCountry(countries, tmdb_id, tname):               #  Check for matched countries

        global tr_config
        tcountry = tr_config['country'].upper()

        cmatch = 0      
        for country in countries:
            if country.upper() != tcountry:
                cmatch = 1      
                try:                                       #  Handle unprintable  characts
                    mgenlog = 'Origin country is not: ' + tcountry + ' Skipping TV Show: ' + tname
                    print(mgenlog)
                    genLog(mgenlog)
                    break
                except:
                    mgenlog = 'Origin country is not: ' + tcountry + ' Skipping TV Show TMDB ID - ' +    \
                    str(tmdb_id)
                    print(mgenlog)
                    genLog(mgenlog)
                    break

        return cmatch


def checkTrailer(item, mtype):                              # Update detailed trailer information already in database

    try:
        db = openTrailerDB()

        currTime = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        db.execute('INSERT OR IGNORE into tvTemp (dateAdded, tmdb_id, trailerUri, trType, trTitle, trOverview,  \
        trTagline, trRelease_date, trImdb_id, trWebsite, trPoster_path, trBackdrop_path, trUser_rating,         \
        trGenres, trProd_company, trContent_rating, trArtist_actor, trComposer, trLang, trCountry, var1 )       \
        values (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)', (currTime, item['tmdb_id'],    \
        item['uri'], mtype, item['title'],  item['description'], item['tagline'], item['release_date'],         \
        item['imdb_id'], item['website'], item['poster_uri'], item['backdrop_uri'], item['user_rating'],        \
        str(item['genre']), str(item['production_company']), item['content_rating'], str(item['artist_actor']), \
        str(item['composer_director_creator']), item['language'], item['country'], item['album_series'], ))
        db.commit()    

    except Exception as e:
        print (e)
        mgenlog = 'There was an error checking trailer details for: TMDB ID - ' + str(item['tmdb_id'])
        print(mgenlog)
        genLog(mgenlog)
        #return found 


def genLog(mgenlog):                                        #  Write to logfile

        global tr_config
        logoutfile = tr_config['logoutfile']
        fileh = open(logoutfile, "a")                       #  open logf file
        currTime = datetime.now().strftime('%Y-%m-%d %H:%M:%S') 
        data = fileh.write(currTime + ' - ' + mgenlog + '\n')
        fileh.close()


def checkDatabase():

    try:
        global trailerdb

        db = openTrailerDB()

        db.execute('CREATE table IF NOT EXISTS tvTrailers (dateAdded TEXT, tmdb_id INTEGER, trailerUri TEXT,    \
        localTrURL TEXT, mezzmoTrURL TEXT, trType TEXT, trTitle TEXT, trOverview TEXT, trTagline TEXT,         \
        trRelease_date TEXT, trImdb_id TEXT, trWebsite TEXT, trPoster_path TEXT, locPoster_path TEXT,          \
        trBackdrop_path TEXT, locBackdrop_path TEXT, trUser_rating INTEGER, trGenres TEXT, trProd_company TEXT,\
        trContent_rating TEXT, trArtist_actor TEXT, trComposer TEXT, lastchecked TEXT, tr_resol INTEGER,       \
        tr_size INTEGER, trLang TEXT, trCountry TEXT, var1 TEXT, var2 TEXT, var3 TEXT, var4 TEXT)')

        db.execute('CREATE INDEX IF NOT EXISTS trailer_1 ON tvTrailers (dateAdded)')
        db.execute('CREATE UNIQUE INDEX IF NOT EXISTS trailer_2 ON tvTrailers (trailerUri)')
        db.execute('CREATE INDEX IF NOT EXISTS trailer_3 ON tvTrailers (trRelease_date)')
        db.execute('CREATE INDEX IF NOT EXISTS trailer_4 ON tvTrailers (trType)')
        db.execute('CREATE INDEX IF NOT EXISTS trailer_5 ON tvTrailers (tmdb_id)')

        db.execute('CREATE table IF NOT EXISTS tvHistory (dateAdded TEXT, tmdb_id INTEGER, trailerUri TEXT,     \
        localTrURL TEXT, mezzmoTrURL TEXT, trType TEXT, trTitle TEXT, trOverview TEXT, trTagline TEXT,         \
        trRelease_date TEXT, trImdb_id TEXT, trWebsite TEXT, trPoster_path TEXT, locPoster_path TEXT,          \
        trBackdrop_path TEXT, locBackdrop_path TEXT, trUser_rating INTEGER, trGenres TEXT, trProd_company TEXT,\
        trContent_rating TEXT, trArtist_actor TEXT, trComposer TEXT, lastchecked TEXT, tr_resol INTEGER,       \
        tr_size INTEGER, trLang TEXT, trCountry TEXT, var1 TEXT, var2 TEXT, var3 TEXT, var4 TEXT)')

        db.execute('CREATE INDEX IF NOT EXISTS htrailer_1 ON tvHistory (dateAdded)')
        db.execute('CREATE INDEX IF NOT EXISTS htrailer_2 ON tvHistory (trailerUri)')
        db.execute('CREATE INDEX IF NOT EXISTS htrailer_3 ON tvHistory (trRelease_date)')
        db.execute('CREATE INDEX IF NOT EXISTS htrailer_4 ON tvHistory (trType)')
        db.execute('CREATE INDEX IF NOT EXISTS htrailer_5 ON tvHistory (tmdb_id)')

        db.execute('CREATE table IF NOT EXISTS tvTemp (dateAdded TEXT, tmdb_id INTEGER, trailerUri TEXT,        \
        localTrURL TEXT, mezzmoTrURL TEXT, trType TEXT, trTitle TEXT, trOverview TEXT, trTagline TEXT,         \
        trRelease_date TEXT, trImdb_id TEXT, trWebsite TEXT, trPoster_path TEXT, locPoster_path TEXT,          \
        trBackdrop_path TEXT, locBackdrop_path TEXT, trUser_rating INTEGER, trGenres TEXT, trProd_company TEXT,\
        trContent_rating TEXT, trArtist_actor TEXT, trComposer TEXT, lastchecked TEXT, tr_resol INTEGER,       \
        tr_size INTEGER, trLang TEXT, trCountry TEXT, var1 TEXT, var2 TEXT, var3 TEXT, var4 TEXT)')

        db.execute('CREATE INDEX IF NOT EXISTS tetrailer_1 ON tvTemp (dateAdded)')
        db.execute('CREATE INDEX IF NOT EXISTS tetrailer_2 ON tvTemp (trailerUri)')
        db.execute('CREATE INDEX IF NOT EXISTS tetrailer_3 ON tvTemp (trRelease_date)')
        db.execute('CREATE INDEX IF NOT EXISTS tetrailer_4 ON tvTemp (trType)')
        db.execute('CREATE INDEX IF NOT EXISTS tetrailer_5 ON tvTemp (tmdb_id)')
        db.execute('DELETE FROM tvTemp')                                    # Clear temp table on startup

        db.execute('CREATE table IF NOT EXISTS badTrailers (dateAdded TEXT, tmdb_id INTEGER,    \
        trailerUri TEXT, trType TEXT, trTitle TEXT, var1 TEXT, var2 TEXT, var3 TEXT, var4 TEXT)')
        db.execute('CREATE INDEX IF NOT EXISTS badtrailer_1 ON badTrailers (dateAdded)')
        db.execute('CREATE INDEX IF NOT EXISTS badtrailer_2 ON badTrailers (trailerUri)')
        db.execute('CREATE INDEX IF NOT EXISTS badtrailer_3 ON badTrailers (trType)')
        db.execute('CREATE UNIQUE INDEX IF NOT EXISTS badtrailer_4 ON badTrailers (tmdb_id)')
        db.commit()

        hscurr = db.execute('SELECT dateAdded, tmdb_id FROM tvHistory ORDER BY DateAdded ASC')
        hstuples = hscurr.fetchall()
        hstcount = len(hstuples)        
        #print(hstcount)
        if hstcount > 0 and hstcount > 1000:                                # Trim history table to 1000 rows
            for row in range(len(hstuples) - 1000):
                db.execute('DELETE from tvHistory WHERE dateAdded = ? AND tmdb_id = ?',     \
                (hstuples[row][0], hstuples[row][1],)) 

        db.commit()
        db.close()
 
        mgenlog = "Mezzmo TVShow Trailers Channel database check completed."
        print (mgenlog)
        genLog(mgenlog)

    except Exception as e:
        print (e)
        mgenlog = "There was a problem verifying the trailer database file: " + trailerdb
        print(mgenlog)
        exit()   


def updateTempHist(tmdb_id, trname, trsize, trres):                       # Update temp table

    try:
        global tr_config, trailerdb                                       # Get config information
        db = openTrailerDB()

        newmtrailer = tr_config['mtrailerloc'] + '\\trailers\\' + trname  # Mezzmo trailer name
        newctrailer = tr_config['ltrailerloc'] + '\\trailers\\' + trname  # Local trailer name 
        resolution =  int(trres.strip('p'))                               # Resolution as number 
        db.execute('UPDATE tvTemp SET LocalTrURL=?, mezzmoTrURL=?, tr_resol=?, tr_size=? WHERE tmdb_id=?', \
        (newctrailer, newmtrailer, resolution, trsize, tmdb_id,)) 
        db.commit()
        db.execute('INSERT INTO tvTrailers SELECT * FROM tvTemp WHERE tmdb_id=?', (tmdb_id,))
        db.execute('INSERT INTO tvHistory SELECT * FROM tvTemp WHERE tmdb_id=?', (tmdb_id,))
        db.commit()
        db.execute('DELETE FROM tvTemp WHERE tmdb_id=?', (tmdb_id,))
        db.commit()

    except Exception as e:
        print (e)
        mgenlog = "There was a problem updating the temp table: " + trailerdb
        print(mgenlog)
        genLog(mgenlog)


def addbadTrailer(item, mtype):                     # Mark trailers bad for 7 days

        db = openTrailerDB()

        currTime = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        db.execute('INSERT OR IGNORE into badTrailers (dateAdded, tmdb_id, trailerUri, trType, trTitle) \
        values (?, ?, ?, ?, ?)', (currTime, item['tmdb_id'], item['uri'], mtype, item['title'],))
        db.commit()
        db.close()         

def checkBad(item):                                 # Check if trailer already marked unavailable

    try:
        db = openTrailerDB()
        bdcurr = db.execute('SELECT count (*) from badTrailers WHERE trailerUri = ?', (item['uri'],))        
        bdtuple = bdcurr.fetchone()
        del bdcurr
        db.close()
        return bdtuple[0]

    except Exception as e:
        print (e)
        mgenlog = "There was problem a checking for unavailable trailers: " + item['uri']
        print(mgenlog)
        genLog(mgenlog)
        return 0


def getPages():                                     # Return page list based upon config setting

    global tr_config    
    mcount = int(tr_config['mcount'])               # Number of TVShow Trailers to keep

    if mcount > 0 and mcount <= 20:
        pages = ['1', '2']
    elif mcount <= 30: 
        pages = ['1', '2', '3']
    elif mcount <= 40: 
        pages = ['1', '2', '3', '4']
    elif mcount <= 50: 
        pages = ['1', '2', '3', '4', '5']
    elif mcount <= 60: 
        pages = ['1', '2', '3', '4', '5', '6']
    elif mcount <= 70: 
        pages = ['1', '2', '3', '4', '5', '6', '7']
    elif mcount <= 80: 
        pages = ['1', '2', '3', '4', '5', '6', '7', '8']
    elif mcount <= 90: 
        pages = ['1', '2', '3', '4', '5', '6', '7', '8', '9']
    else: 
        pages = ['1', '2', '3', '4', '5', '6', '7', '8', '9', '10']

    return pages
  

def checkFormats(trailfile):                                             # Check / modify output formats

    try:

        global tr_config
        tformat = tr_config['tformat']

        if tformat in trailfile and 'mp4' in tformat:                            # No adjustment needed
            mgenlog = "Format conversion not required for: " + trailfile
            print(mgenlog)
            genLog(mgenlog)        
            return trailfile
 
        new_name = trailfile.replace('.mp4', '.mkv')                              # New trailer name

        curr_trailer = 'temp\\' + trailfile                                       # Current trailer path and file name
        new_trailer = 'temp\\' +  new_name                                        # Converted trailer path and file name
        mgenlog = "Format conversion to " + tformat + ' beginning for trailer ' + trailfile
        print(mgenlog)
        genLog(mgenlog)
        #print('Format file names: ' + trailer_name + '  ' + convert_name)
        frcommand = 'ffmpeg.exe -i ' +  curr_trailer + ' -vcodec copy -acodec copy -y ' + new_trailer + ' >nul 2>nul'
        #print(frcommand)
        os.system(frcommand)
        #print('Trailer file names: ' + curr_trailer + '  ' + new_trailer)
        delcommand = "del " + '"' + curr_trailer + '"'                           # Remove old trailer from disk    
        #print(delcommand)
        os.system(delcommand)
        mgenlog = "Format conversion successful to: " + new_name
        print(mgenlog)
        genLog(mgenlog)
        return new_name

    except Exception as e:
        print (e)
        mgenlog = "There was a problem adjusting the output formats."
        print(mgenlog)
        genLog(mgenlog)  
        return 0


def openTrailerDB():

    global trailerdb
    
    try:
        from sqlite3 import dbapi2 as sqlite
    except:
        from pysqlite2 import dbapi2 as sqlite
                       
    db = sqlite.connect(trailerdb)

    return db


def getArtwork(tmdb_id, posterUrl, backDropUrl):                         #  Get trailer artwork 

    global tr_config

    try:
        #print(tr_config['ltrailerloc'])
        newmposter = 'file://' + tr_config['mtrailerloc'] +   \
        '\\artwork\\' +  str(tmdb_id) + '_poster.jpg'                    # Mezzmo poster name
        newlposter = tr_config['ltrailerloc'] + '\\artwork\\'   \
        + str(tmdb_id) + '_poster.jpg'                                   # Local poster name
        newmbackd = 'file://' + tr_config['mtrailerloc'] +    \
        '\\artwork\\' + str(tmdb_id) + '_backdrop.jpg'                   # Mezzmo backdrop name
        newlbackd = tr_config['ltrailerloc'] + '\\artwork\\'    \
        + str(tmdb_id) + '_backdrop.jpg'                                 # Local backdrop name

        mgenlog = 'Fetching trailer artwork'
        genLog(mgenlog)
        print(mgenlog)
   
        resource = urllib.request.urlopen(posterUrl)
        output = open(newlposter,"wb")
        output.write(resource.read())
        output.close()    

        resource = urllib.request.urlopen(backDropUrl)
        output = open(newlbackd,"wb")
        output.write(resource.read())
        output.close() 

        db = openTrailerDB()
        db.execute('UPDATE tvTrailers SET trPoster_path=?, trBackdrop_path=?, \
        locPoster_path=?, locBackdrop_path=? WHERE tmdb_id=?', (newmposter,  \
        newmbackd, newlposter, newlbackd, tmdb_id,)) 

        db.commit()
        db.close() 

        mgenlog = 'Trailer artwork fetching successful'
        genLog(mgenlog)    
        print(mgenlog)

    except Exception as e:
        print (e)
        mgenlog = 'There was a problem fetching the trailer artwork'
        genLog(mgenlog)
        print(mgenlog)


def getTrailer(trailer, imdbtitle = ''):                   # Download You Tube \ IMDB trailers

    try:
        global tr_config
        maxres = int(tr_config['maxres'])                  # Get max resolution
        tr_cmd = fmt = ''
        formats = str(getFormats(trailer, imdbtitle))     # Get available trailer formats
        #print('Formats result is: ' + str(formats))
        #print('Trailer info: ' + imdbtitle + ' ' + str(maxres)) 
        if 'Error' in formats:                             # You Tube / IMDB error getting formats file
            return 'Error'
        elif 'imdb' in imdbtitle and '1080p' in formats and maxres >= 1080:         # 1080 available for IMDB   
            tr_cmd = "yt-dlp.exe -f 1080p -q --check-formats --windows-filenames " + trailer
            fmt = '1080p' 
        elif 'imdb' in imdbtitle and '720p' in formats and maxres >= 720:           # 720 available for IMDB   
            tr_cmd = "yt-dlp.exe -f 720p -q --check-formats --windows-filenames " + trailer
            fmt = '720p' 
        elif 'imdb' in imdbtitle and '480p' in formats and maxres >= 480:           # 480 available for IMDB   
            tr_cmd = "yt-dlp.exe -f 480p -q --check-formats --windows-filenames " + trailer
            fmt = '480p' 
        elif 'imdb' in imdbtitle and 'SD' in formats:                               # SD available for IMDB   
            tr_cmd = "yt-dlp.exe -f SD -q --check-formats --windows-filenames " + trailer
            fmt = '360p'        
        elif '137 mp4' in formats and '140 m4a' in formats and maxres >= 1080:      # 1080P available
            tr_cmd = "yt-dlp.exe -f 137+140 -q --check-formats --restrict-filenames " + trailer
            fmt = '1080p'
        elif '137     mp4' in formats and '140     m4a' in formats and maxres >= 1080:      # 1080P available
            tr_cmd = "yt-dlp.exe -f 137+140 -q --check-formats --restrict-filenames " + trailer
            fmt = '1080p'  
        elif '137 mp4' in formats and '139 m4a' in formats  and maxres >= 1080:     # 1080P available
            tr_cmd = "yt-dlp.exe -f 137+139 -q --check-formats --restrict-filenames " + trailer
            fmt = '1080p'
        elif '137     mp4' in formats and '139     m4a' in formats  and maxres >= 1080:     # 1080P available
            tr_cmd = "yt-dlp.exe -f 137+139 -q --check-formats --restrict-filenames " + trailer
            fmt = '1080p'  
        elif '22  mp4' in formats and maxres >= 720:                                # 720P available
            tr_cmd = "yt-dlp.exe -f 22 -q --restrict-filenames " + trailer
            fmt = '720p'
        elif '22      mp4' in formats and maxres >= 720:                            # 720P available
            tr_cmd = "yt-dlp.exe -f 22 -q --restrict-filenames " + trailer
            fmt = '720p'  
        elif  '135 mp4' in formats and '140 m4a' in formats and maxres >= 480:      # 480P available
            tr_cmd = "yt-dlp.exe -f 135+140 -q --check-formats --restrict-filenames " + trailer
            fmt = '480p'
        elif  '135     mp4' in formats and '140     m4a' in formats and maxres >= 480:      # 480P available
            tr_cmd = "yt-dlp.exe -f 135+140 -q --check-formats --restrict-filenames " + trailer
            fmt = '480p'  
        elif  '135 mp4' in formats and '139 m4a' in formats and maxres >= 480:      # 480P available
            tr_cmd = "yt-dlp.exe -f 135+139 -q --check-formats --restrict-filenames " + trailer
            fmt = '480p'
        elif  '135     mp4' in formats and '139     m4a' in formats and maxres >= 480:      # 480P available
            tr_cmd = "yt-dlp.exe -f 135+139 -q --check-formats --restrict-filenames " + trailer
            fmt = '480p'  
        elif '18  mp4' in formats:                                                  # 360P available
            tr_cmd = "yt-dlp.exe -f 18 -q --restrict-filenames " + trailer
            fmt = '360p'
        elif '18      mp4' in formats:                                              # 360P available
            tr_cmd = "yt-dlp.exe -f 18 -q --restrict-filenames " + trailer
            fmt = '360p'
        else:
            return 'Error'                                 # No acceptable format available 
        
        #print (tr_cmd)

        if 'imdb' in imdbtitle:
            tsource = 'IMDB'
        else:
            tsource = 'You Tube'
        mgenlog = 'Attempting fetch ' + tsource + ' trailer at: ' + fmt + ' - ' + trailer
        genLog(mgenlog)
        print(mgenlog)

        fetch_result = subprocess.call(tr_cmd, shell=True)
        if fetch_result == 0:
            mgenlog = 'Fetched ' + tsource + ' trailer at: ' + fmt + ' - ' + trailer
            genLog(mgenlog)
            print(mgenlog)
            trfile = renameFiles(imdbtitle)                  # Cleanup trailer name and move to temp folder
            return [fetch_result, trfile[0], trfile[1], fmt]
                                                             # Return trailer file info and status
                                                             # trfile[0] = new trailer file name
                                                             # trfile[1] = new trailer file size
        elif fetch_result == 1:
            mgenlog = "A Youtube / IMDB fetching error occured for: " + trailer
            print(mgenlog)
            genLog(mgenlog)
            return [fetch_result, '0', '0', '0']
    
    except Exception as e:
        print (e)
        mgenlog = 'There was a problem getting the formats information'
        genLog(mgenlog)
        print(mgenlog)


def getFormats(trailer,imdbtitle = ''):             # Get available You Tube Trailer formats

    try:
        global tr_config

        formats = []
        tr_cmd = "yt-dlp.exe -F " + trailer + " > output.txt"
        fetch_result = subprocess.call(tr_cmd, shell=True)
        if fetch_result == 0:
            fileh = open("output.txt")             # open formats file
            data = fileh.readlines()   
            for x in range(6, len(data)):
                if 'imdb' in imdbtitle:
                    formats.append(data[x][:5].strip())    # List of available formats
                elif data[x][13:14] == ' ' :               # New format
                    formats.append(data[x][:14].strip())   # List of available formats
                else:                                      # Old format
                    formats.append(data[x][:7].strip())    # List of available formats
            fileh.close()  
            return formats
        else:
            mgenlog = "There was no video format data available for this trailer: " + trailer
            print(mgenlog)
            genLog(mgenlog) 
            return 'Error'

    except Exception as e:
        print (e)
        mgenlog = "There was a problem getting the trailer formats: " + trailer
        print(mgenlog)
        genLog(mgenlog) 


def checkFolders():                                # Check folders and files

    try:
        global tr_config, trailerdb
        baseloc = tr_config['baseloc']
        trailerloc = tr_config['ltrailerloc']
        if not os.path.exists('temp'):             #  Check temp files location
            os.makedirs('temp')
        command = 'del temp\*.mp* >nul 2>nul'      #  Delete temp files if exist 
        os.system(command)                         #  Clear temp files
        command = 'del *.mp4 >nul 2>nul'           #  Remove old converted files
        os.system(command)                         #  Clear converted files
        if not os.path.exists(baseloc):            #  Check trailer files base location
            mgenlog = 'Local trailer file location does not exist.  Mezzmo TVShow Trailer Channel exiting.'  
            genLog(mgenlog)
            print(mgenlog)            
            sys.exit()
        if not os.path.exists(trailerloc):         #  Check TVShow Trailers file location
            os.makedirs(trailerloc)
            mgenlog = 'Local trailer file location does not exist.  Local file location created.'  
            genLog(mgenlog)
            print(mgenlog)            
        ltrailersloc = os.path.join(trailerloc, "trailers")        
        if not os.path.exists(ltrailersloc):       #  Check trailer files location       
            os.makedirs(ltrailersloc)
            mgenlog = 'Trailers folder location did not exist.  Trailers folder created.'  
            genLog(mgenlog)
            print(mgenlog)
        trailerdb = os.path.join(trailerloc, "trailers\\mezzmo_tvtrailers.db")                
        backuploc = os.path.join(trailerloc, "trailers\\backup")
        if not os.path.exists(backuploc):          #  Check trailers backup files location
            os.makedirs(backuploc)
            mgenlog = 'Trailer backup file location did not exist.  Backup folder created.'  
            genLog(mgenlog)
            print(mgenlog)
        ltrailersloc = os.path.join(trailerloc, "artwork")        
        if not os.path.exists(ltrailersloc):       #  Check artwork files location       
            os.makedirs(ltrailersloc)
            mgenlog = 'Trailers artwork folder location did not exist.  Trailers artwork folder created.'  
            genLog(mgenlog)
            print(mgenlog)    
        if not os.path.isfile('./ffmpeg.exe'):
            mgenlog = 'ffmpeg.exe not found in Mezzmo TVShow Trailers Channel folder.  Mezzmo TVShow Trailers Channel exiting.'
            genLog(mgenlog)
            print(mgenlog)            
            sys.exit()
        if not os.path.isfile('./yt-dlp.exe'):
            mgenlog = 'ytp-dl.exe not found in Mezzmo TVShow Trailers Channel folder.  Mezzmo TVShow Trailers Channel exiting.'
            genLog(mgenlog)
            print(mgenlog)            
            sys.exit()
  

    except Exception as e:
        print (e)
        mgenlog = 'There was a problem checking folders'
        genLog(mgenlog)
        print(mgenlog)    


def checkLimits(sysarg1):                             # Check category limits

    try:

        #if sysarg1.lower() NOT IN ['trailer']:
        #    return

        global tr_config
        trailerloc = tr_config['ltrailerloc']         # Get locatal path to trailer lcoation
        mcount = tr_config['mcount']                  # Number of TVShow Trailers to keep

        if int(mcount) == 0:                          # Unlimited retention
            mgenlog = 'Checking TV Show keep limits.  Unlimited selected.  Skipping.'
            genLog(mgenlog)    
            return

        db = openTrailerDB()

        mgenlog = 'Checking Checking TV keep limits'
        genLog(mgenlog)
        print('\n' + mgenlog)

        mtype = ['now_playing', 'upcoming', 'popular', 'top_rated']

        for type in mtype:
            dbcurr = db.execute('SELECT dateAdded, tmdb_id, localTrURL, trTitle, locPoster_path,   \
            locBackdrop_path FROM tvTrailers WHERE dateAdded NOT IN (SELECT dateAdded FROM         \
            tvTrailers WHERE trType = ? ORDER BY dateAdded DESC LIMIT ? ) and trType = ?',         \
            (type, mcount, type,))

            dbtuple = dbcurr.fetchall()                   # TVShows over keep limit
            del dbcurr
            if len(dbtuple) > 0:                          # Remove extra TVShows and trailer files
                rmcount = 0
                for tv in range(len(dbtuple)):
                    delcommand = "del " + '"' + dbtuple[tv][2] + '"'       
                    print(delcommand)
                    os.system(delcommand)                 # Remove trailer from disk
                    if dbtuple[tv][4]:                    # Delete poster file
                        delcommand = "del " + dbtuple[tv][4] + " >nul 2>nul"
                        os.system(delcommand) 
                    if dbtuple[tv][5]:                    # Delete backdrop file
                        delcommand = "del " + dbtuple[tv][5] + " >nul 2>nul"
                        os.system(delcommand)   
                    db.execute('DELETE FROM tvTrailers WHERE tmdb_id=?', (dbtuple[tv][1],))
                    mgenlog = type + ' TV Show removed: ' + dbtuple[tv][3]
                    genLog(mgenlog)
                    rmcount += 1
                db.commit()
                mgenlog = type + ' TVShow Trailers removed: ' + str(rmcount)
                genLog(mgenlog)
                print(mgenlog)
            del dbtuple
        newtime = (datetime.now() + timedelta(days=-3)).strftime('%Y-%m-%d %H:%M:%S')
        bdcurr = db.execute('SELECT trailerUri FROM badTrailers WHERE dateAdded < ?', (newtime,))
        bdtuples = bdcurr.fetchall()

        bdcount = 0
        for bad in range(len(bdtuples)):                # Remove aged trailers for recheck after 3 days
            db.execute('DELETE FROM badTrailers WHERE trailerUri=?', (bdtuples[bad][0],))
            mgenlog = 'Trailer reset from unavailable for recheck: ' + str(bdtuples[bad][0],)
            genLog(mgenlog)
            bdcount += 1
        db.commit()
        
        if bdcount > 0:
            mgenlog = 'Trailers reset from unavailable for rechecking: ' + str(bdcount)
            genLog(mgenlog)
            print(mgenlog)

        db.close()
        mgenlog = 'Checking TV Show keep limits completed. '  
        genLog(mgenlog)
        print(mgenlog + '\n')

        return

    except Exception as e:
        print (e)
        mgenlog = "There was a problem checking limits "
        print(mgenlog)
        genLog(mgenlog) 


def renameFiles(imdbtitle = ''):                    # Rename trailer file names / move to temp folder

        global tr_config

        listOfFiles = os.listdir('.')
        pattern = "*.mp4"
        for x in listOfFiles:
            if fnmatch.fnmatch(x, pattern):
                #print (x)
                filestat = os.stat(x)
                fsize = filestat.st_size            # Get trailer size in bytes
                rpos = x.find('[')
                newname = x[:rpos - 1]
                # Remove file name characters which cannot be reencoded
                newname = newname.replace(' ' ,'_')
                imdbtitle = imdbtitle.replace(' ' ,'_').replace(',' ,'_')
                newname = re.sub(r'[^\x61-\x7a,\x5f,^\x41-\x5a,^\x30-\x39]',r'', newname) 
                imdbtitle = re.sub(r'[^\x61-\x7a,\x5f,^\x41-\x5a,^\x30-\x39]',r'', imdbtitle)  
                if rpos >= 10:                    # Trim extra characters
                    newname = newname[:rpos - 1]  + ".mp4"
                elif len(newname) < 10:
                    tempname = ''.join(random.choices(string.ascii_letters, k=12))
                    newname = "trailer_" + tempname + ".mp4"
                command = "rename " + '"' + x + '" "' + newname + '"'
                os.system(command)                  # Rename trailer file to trimmed newname
                command = "move " + '"' + newname + '" temp >nul 2>nul'
                #print('The file name is: ' + newname + ' ' + str(rpos))
                os.system(command)                  # Move to temp folder till done fetching all
                return [newname, str(fsize)]        # Return new trailer name and info


def moveTrailers(trfile):                           # Move trailers to trailer location

    try:
        global tr_config                            # Get local path to trailer lcoation
        trailerloc = tr_config['ltrailerloc'] + '\\trailers'

        command = "move temp\\" + trfile + " " + trailerloc + " >nul 2>nul"
        #print(command)
        os.system(command)
    except Exception as e:
        print (e)
        mgenlog = 'There was a problem moving trailers to the trailer folder.'
        genLog(mgenlog)
        print(mgenlog)


def checkCsv(sysarg1 = '', sysarg2 = ''):           # Generate CSV files

        if len(sysarg1) == 0 or sysarg1.lower() not in 'csv':
            return
        elif sysarg2.lower() not in ['trailers', 'history']:
            print('\nThe valid csv options are:  trailers or history\n')
            return
  
        mgenlog = 'CSV file export beginning for - ' + sysarg1
        genLog(mgenlog)
            
        db = openTrailerDB()
        fpart = datetime.now().strftime('%H%M%S')
        if sysarg2.lower() == 'trailers':
            curm = db.execute('SELECT * FROM tvTrailers ORDER BY dateAdded ASC')
            filename = 'meztrailers_' + fpart + '.csv'
        elif sysarg2.lower() == 'history':
            curm = db.execute('SELECT * FROM tvHistory')
            filename = 'mezhistory_' + fpart + '.csv'          
    
        headers = [i[0] for i in curm.description]      
        recs = curm.fetchall()   
        writeCSV(filename, headers, recs)
        del curm
        db.close()
        mgenlog = 'CSV file export completed to - ' + filename
        genLog(mgenlog)
        print(mgenlog)


def writeCSV(filename, headers, recs):

    try:
        csvFile = csv.writer(open(filename, 'w', encoding = 'utf-8'),
                         delimiter=',', lineterminator='\n',
                         quoting=csv.QUOTE_ALL)
        csvFile.writerow(headers)     # Add the headers and data to the CSV file.
        for row in recs:
            recsencode = []
            for item in range(len(row)):
                if isinstance(row[item], int) or isinstance(row[item], float):  # Convert to strings
                    recitem = str(row[item])
                else:
                    recitem = row[item]

                if "##" in str(recitem):
                    recitem = recitem.replace('##', ', ')
                recsencode.append(recitem) 
            csvFile.writerow(recsencode)               

    except Exception as e:
        print (e)
        mgenlog = 'An error occurred creating the CSV file.'
        genLog(mgenlog)
        print(mgenlog)


def checkFinish(sysarg1, sysarg2):                           # Successfully finished

    if sysarg1.lower() in ['trailers']:                      # Display for trailers
        mgenlog = 'Mezzmo TVShow Trailers Channel completed successfully.' 
        print('\n' + mgenlog)
        genLog(mgenlog)


def getTotals():                                             # Gets checked download totals

    try:
        db = openTrailerDB()
        currDate = datetime.now().strftime('%Y-%m-%d')
        dateMatch = currDate + '%'
        dqcurr = db.execute('SELECT count (*) from tvHistory WHERE dateAdded LIKE ?', (dateMatch,))
        daytuple = dqcurr.fetchone()
        newtime = (datetime.now() + timedelta(days=-30)).strftime('%Y-%m-%d %H:%M:%S')
        dqcurr = db.execute('SELECT count (*) from tvHistory WHERE dateAdded > ?', (newtime,))
        htottuple = dqcurr.fetchone()
        db.close()
        return [daytuple[0], htottuple[0]]

    except Exception as e:
        print (e)
        mgenlog = 'An error occurred generating totals.'
        genLog(mgenlog)
        print(mgenlog)
        if db != None:
            db.close()

def makeBackups():                                   # Make database backups

    try:
        from sqlite3 import dbapi2 as sqlite
    except:
        from pysqlite2 import dbapi2 as sqlite
    
    try:
        if len(sysarg1) == 0 or sysarg1.lower() not in 'backup':
            return

        global tr_config                            # Get locatal path to trailer lcoation
        trailerloc = tr_config['ltrailerloc']

        DB = trailerloc + '\\trailers\\backup\\mezzmo_trailers_' +             \
        datetime.now().strftime('%m%d%Y-%H%M%S') + '.db'
        #print(DB)
        dbout = sqlite.connect(DB)
        dbin = openTrailerDB()

        with dbout:
            dbin.backup(dbout, pages=100)
        dbout.close()
        dbin.close()
        mgenlog = 'Mezzmo Trailer Checker backup successful: ' + str(DB)
        genLog(mgenlog)
        print(mgenlog) 

    except Exception as e:
        print (e)
        mgenlog = 'An error occurred creating a Mezzmo Movie Trailers Channel backup.'
        genLog(mgenlog)
        print(mgenlog)      

                                  

def cleanTrailers(sysarg1 = '', sysarg2 = '', sysarg3 = ''): # Clean show TVShow Trailers from DB


        if sysarg1.lower() not in ['clean']:
            return
        elif sysarg2.lower() not in ['air', 'on', 'top', 'pop', 'all', 'files']: 
            return

        if sysarg2.lower() == 'air':
            mtype = 'airing_today'
        elif sysarg2.lower() == 'on':
            mtype = 'on_the_air'
        elif sysarg2.lower() == 'top':
            mtype = 'top_rated'
        elif sysarg2.lower() == 'pop':
            mtype = 'popular'
        elif sysarg2.lower() == 'all':
            mtype = 'all'
        elif sysarg2.lower() == 'files':
            checkFiles()    
            return

        global tr_config
        ltrailerloc = tr_config['ltrailerloc']       # Get local path to trailer lcoation
        mtrailerloc = tr_config['mtrailerloc']       # Get Mezzmo path to trailer lcoation

        if sysarg2.lower() not in ['files']:
            db = openTrailerDB()
            if mtype == 'all':
                dbcurr = db.execute('SELECT tmdb_id, localTrURL, trTitle, locPoster_path,  \
                locBackdrop_path from tvTrailers ')            
            else:
                dbcurr = db.execute('SELECT tmdb_id, localTrURL, trTitle, locPoster_path,  \
                locBackdrop_path from tvTrailers WHERE trType=? ', (mtype,))
            dbtuples = dbcurr.fetchall() 
            if len(dbtuples) == 0:
                mgenlog = 'No trailers found with movie type: ' + str(mtype)
                print('\n')
                genLog(mgenlog)
                print(mgenlog)
                db.close()
                return
            else:
                mgenlog = 'Number of TVShow Trailers to clean: ' + str(len(dbtuples))
                genLog(mgenlog)
                print('\n' + mgenlog  + '\n')
                for n in range(len(dbtuples)):
                    print(str(dbtuples[n][2]))
                choice = input('\nDo you want to delete these TVShow Trailers (Y/N) ?  \n')
                if 'n' in choice.lower():
                    mgenlog = 'TVShow Trailers will not be cleaned with status: ' + str(mtype)
                    genLog(mgenlog)
                    print(mgenlog)                
                    db.close()
                    return 
                else:
                    delcount = 0
                    for x in range(len(dbtuples)):
                        command = "del " + dbtuples[x][1] + " >nul 2>nul"        # Delete trailer file
                        os.system(command)
                        if dbtuples[x][3]:
                            command = "del " + dbtuples[x][3] + " >nul 2>nul"    # Delete poster file
                            os.system(command) 
                        if dbtuples[x][4]:
                            command = "del " + dbtuples[x][4] + " >nul 2>nul"    # Delete backdrop file
                            os.system(command)         
                        db.execute('DELETE FROM tvTrailers WHERE tmdb_id=?', (dbtuples[x][0],))
                        delcount += 1
                        mgenlog = 'Successfully cleaned TVShow Trailer: ' + dbtuples[x][2]
                        genLog(mgenlog)
                        print(mgenlog)   
                    db.commit()
                    db.close()
                    mgenlog = 'Number of TVShow Trailers successfully cleaned: ' + str(delcount)
                    genLog(mgenlog)
                    print('\n' + mgenlog)  


def checkUpdate(sysarg1):                             # Check for yt-dlp.exe update

    try:
        if len(sysarg1) > 1 and sysarg1.lower() != 'trailers':
            return        
        command = "yt-dlp.exe -U >nul 2>nul"
        #print(command)
        os.system(command)
        mgenlog = 'Checking for yt-dlp.exe update completed.'
        genLog(mgenlog)
        print(mgenlog)
    except Exception as e:
        print (e)
        mgenlog = 'There was a problem checking for a yt-dlp.exe update.'
        genLog(mgenlog)
        print(mgenlog)
        exit()  


def checkLogfile():                                   # Checks / trims the size of the logfile

        global tr_config
        logoutfile = tr_config['logoutfile']
        fileh = open(logoutfile, "r+")                #  open log file
        flines = fileh.readlines()
        fcount = len(flines)
        if fcount > 16000:
            fileh.seek(0)
            fileh.truncate()
            fileh.writelines(flines[fcount - 15000:])
        fileh.close()
        mgenlog = 'The number of lines in the logfile is: ' + str(len(flines))
        genLog(mgenlog)  


def checkFiles():                                     # Check for orphaned trailer or missing files

        global tr_config
        trailerloc = tr_config['ltrailerloc'] + '\\trailers' 

        db = openTrailerDB()

        nofiles = []
        notrailers = []

        mgenlog = 'Beginning missing trailer file analysis'
        genLog(mgenlog)
        print(mgenlog)

        listOfFiles = os.listdir(trailerloc)          # Get list of trailer files
        pattern = "*.m*"
        for x in listOfFiles:                         # Check for matching trailer entry
            if fnmatch.fnmatch(x, pattern):
                #print(x)
                dbcurr = db.execute('SELECT localTrURL FROM tvTrailers WHERE localTrURL \
                LIKE ?', ('%' + x,))
                dbtuple = dbcurr.fetchone()
                if not dbtuple:                       # If not found add to list
                    notrailers.append(x)
        if len(notrailers) == 0:                      # None found
            mgenlog = 'No missing trailers found.  All trailers matched.'
            genLog(mgenlog)
            print(mgenlog)
        else:
            mgenlog = 'Number of TVShow Trailers to clean: ' + str(len(notrailers))
            genLog(mgenlog)
            print('\n' + mgenlog  + '\n')
            for n in range(len(notrailers)):
                print(str(notrailers[n]))
            choice = input('\nDo you want to delete these TVShow Trailers (Y/N) ?  \n')
            if 'n' in choice.lower():
                mgenlog = 'TVShow Trailers will not be cleaned'
                genLog(mgenlog)
                print(mgenlog)                
            else:
                delcount = 0
                for x in range(len(notrailers)):                
                    command = 'del "' + trailerloc + '\\' + notrailers[x] + '" >nul 2>nul'
                    #print(command)
                    os.system(command)  
                    delcount += 1
                    mgenlog = 'Successfully cleaned TVShow Trailer entry: ' + notrailers[x]
                    genLog(mgenlog)
                    print(mgenlog)   
                db.commit()
                mgenlog = 'Number of TVShow Trailer entries successfully cleaned: ' + str(delcount)
                genLog(mgenlog)
                print('\n' + mgenlog)

        mgenlog = 'Beginning missing trailer entry analysis'
        genLog(mgenlog)
        print('\n' + mgenlog)     
 
        dbcurr = db.execute('SELECT localTrURL, tmdb_id FROM tvTrailers')
        dbtuple = dbcurr.fetchall()                   # Get entries with missing info
        if len(dbtuple) > 0:                          # Get all trailer files 
            for x in range(len(dbtuple)):
                rpos = dbtuple[x][0].rfind('\\')
                trname = dbtuple[x][0][rpos + 1:]
                if trname not in listOfFiles:
                    nofiles.append(dbtuple[x][0])
        if len(nofiles) == 0:                         # None found
            mgenlog = 'No missing trailers entries found.  All trailer entries matched.'
            genLog(mgenlog)
            print(mgenlog)
        else:
            mgenlog = 'Number of TVShow Trailers entries to clean: ' + str(len(nofiles))
            genLog(mgenlog)
            print(mgenlog  + '\n')
            for n in range(len(nofiles)):
                print(str(nofiles[n]))
            choice = input('\nDo you want to delete these TVShow Trailer entries (Y/N) ?  \n')
            if 'n' in choice.lower():
                mgenlog = 'TVShow Trailer entries will not be cleaned'
                genLog(mgenlog)
                print(mgenlog)                
            else:
                delcount = 0
                for x in range(len(nofiles)):                
                    db.execute('DELETE FROM tvTrailers WHERE localTrURL=?', (nofiles[x],))
                    delcount += 1
                    mgenlog = 'Successfully cleaned TVShow Trailer entry: ' + nofiles[x]
                    genLog(mgenlog)
                    print(mgenlog)   
                db.commit()
                mgenlog = 'Number of TVShow Trailer entries successfully cleaned: ' + str(delcount)
                genLog(mgenlog)
                print('\n' + mgenlog) 

        db.close()


def displayStats(sysarg1):                            # Display statistics    

    try:

        if sysarg1.lower() not in ['trailers', 'stats']:
            return
  
        global totcount, dupcount, notrailer, nocountry, badtrailer
        global tr_config
        trailerloc = tr_config['ltrailerloc'] + '\\trailers'
        mtrailerloc = tr_config['mtrailerloc']

        print ('\n\n\t ************  Mezzmo TVShow Trailers Channel Stats  *************\n')

        daytotal, grandtotal =  getTotals()

        if sysarg1.lower() in ['trailers']:
            print ("Mezzmo TVShow Trailers checked: \t\t" + str(totcount + badtrailer + notrailer))
            print ("Mezzmo TVShow Trailers existing skipped: \t" + str(dupcount))
            print ("Mezzmo TVShow Trailers unavailable: \t\t" + str(badtrailer))
            print ("Mezzmo TVShow Trailers fetched: \t\t" + str(totcount))
            print ("Mezzmo TVShows with no trailers: \t\t" + str(notrailer - dupcount - nocountry))
            print ("Mezzmo TVShows country mismatch: \t\t" + str(nocountry))

        if sysarg1.lower() in ['trailers', 'stats']:
            print ("\nMezzmo TVShow Trailers fetched today: \t\t" + str(daytotal))
            print ("Mezzmo TVShow Trailers fetched last 30 days: \t" + str(grandtotal))

        if sysarg1.lower() in ['stats']:
            db = openTrailerDB()
            dqcurr = db.execute('SELECT count (*) from tvTrailers WHERE trType LIKE ?', ('%airing_today%',))
            airtuple = dqcurr.fetchone()
            dqcurr = db.execute('SELECT count (*) from tvTrailers WHERE trType LIKE ?', ('%on_the_air%',))
            nowtuple = dqcurr.fetchone()
            dqcurr = db.execute('SELECT count (*) from tvTrailers WHERE trType LIKE ?', ('%popular%',))
            poptuple = dqcurr.fetchone()
            dqcurr = db.execute('SELECT count (*) from tvTrailers WHERE trType LIKE ?', ('%top_rated%',))
            toptuple = dqcurr.fetchone()
            dqcurr = db.execute('SELECT count (*) from tvTrailers WHERE mezzmoTrURL LIKE ?', ('%.mp4',))
            mp4format = dqcurr.fetchone()
            dqcurr = db.execute('SELECT count (*) from tvTrailers WHERE mezzmoTrURL LIKE ?', ('%.mkv',))
            mkvformat = dqcurr.fetchone()
            db.close()

            foldersize = filecount = 0
            for element in os.scandir(trailerloc):
                if '.m' in str(element):
                    foldersize+=os.stat(element).st_size
                    filecount += 1
            storagegb = round((float(foldersize) / 1073741824),2)
            avgsize = round((float(foldersize) / 1048576 / filecount),2) 

            print ("\nMezzmo TVShow Trailers Airing Today: \t\t" + str(airtuple[0]))
            print ("Mezzmo TVShow Trailers On Now: \t\t\t" + str(nowtuple[0]))
            print ("Mezzmo TVShow Trailers Popular:  \t\t" + str(poptuple[0]))
            print ("Mezzmo TVShow Trailers Top Rated: \t\t" + str(toptuple[0]))
            print ("\nMezzmo local trailers mp4 format: \t\t" + str(mp4format[0]))
            print ("Mezzmo local trailers mkv format: \t\t" + str(mkvformat[0]))
            print ("\nLocal trailer files in folder: \t\t\t" + str(filecount))
            print ("Total size of local trailers: \t\t\t" + str(storagegb) + 'GB')
            print ("Average trailer file size: \t\t\t" + str(avgsize) + 'MB')
            print ("\n\n")

    except Exception as e:
        print (e)
        mgenlog = "There was a problem displaying statistics "
        print(mgenlog)
        genLog(mgenlog) 


checkVersion()                                               # Ensure Python version 3+
checkCommands(sysarg1, sysarg2)                              # Check for valid commands
getConfig()                                                  # Process config file
checkUpdate(sysarg1)                                         # Check for new vesion of yt-dlp.exe
checkFolders()                                               # Check trailer and temp folder locations
checkDatabase()                                              # Check trailer database
checkLogfile()                                               # Checks the size of the logfile
checkLimits(sysarg1)                                         # Check limits of trailers to keep 
getMezzmoTrailers(sysarg1, sysarg2, sysarg3)                 # Get TVShow Channel Trailers
checkCsv(sysarg1, sysarg2)
cleanTrailers(sysarg1, sysarg2, sysarg3)
makeBackups()
displayStats(sysarg1)
checkFinish(sysarg1, sysarg2)


