import os
import glob
import pandas as pd
from PTN import parse # parse-torrent-name
from dotenv import load_dotenv
import tmdbsimple as tmdb

base_path_films = r'D:/Movies'

def get_file_types(dir):
    extensions = [] 
    for root, dirs, files in os.walk(dir):
        for file in files:
            root, ext = os.path.splitext(file)
            if ext not in extensions:
                extensions.append(ext)
    return extensions

# function to search for files of chosen types. Returns a list of filenames
def files_to_list(dir, file_types):
    thelist = []
    thedir = []
    # traverse whole directory
    for root, dirs, files in os.walk(dir):
        # select file name
        for file in files:
            # check the extension of files
            if file.endswith(file_types):
                thelist.append(file)
                thedir.append(root)
    return thelist, thedir

# function to parse a list of file names to get the title
def parse_for_title(file_list):
    name_list = []
    for filename in file_list:
        name = parse(filename)['title']
        name_list.append(name)
    return name_list

def get_variable(variable_name):
    """ 
    Retrieves the value of a variable from a .env file, given variable name
    Returns: variable value
    """
    # get env variables from .env file
    load_dotenv()
    # extract variable
    value = os.environ.get(variable_name)
    return value

### Process films
# film_extensions = get_file_types(base_path_films)
# print(film_extensions)     

# review list of extensions and decide what's relevant. Then update search_for_types tuple...
search_for_types = ('.avi', '.mp4', '.mkv', '.divx', '.m4v', '.wmv', '.mov', '.mpg')
# create dataframe to hold all info. filename and name from the files, everything else from TMDb API
media_df = pd.DataFrame(columns=('filename', 'location', 'name', 'release_date', 'overview','genre', 'vote_average', 'vote_count', 'popularity','cast_top5', 'trailer', 'poster'))

# get the list of files
file_list, dir_list = files_to_list(base_path_films, search_for_types)

files_list = []
directory = []
name_list = []
release_date = []
overview= []
vote_average = []
vote_count = []
popularity = []
cast_list = []
trailer = [] 
poster = []
genres = []

no_api_result = []

video_base = 'https://youtu.be/'
img_base = 'https://image.tmdb.org/t/p/w154'

# get tmdb api key
tmdb.API_KEY = get_variable('tmdb_key')
# make api call to create search object
search = tmdb.Search()

# loop through the list of files to get all info into lists
for file, dir in zip(file_list, dir_list):
    # get name
    name = parse(file)['title']
    # search for name
    response = search.movie(query=name)
    # print(response)
    if len(search.results)>0:
        # lets chance picking the first result
        pick = search.results[0]
        files_list.append(file)
        name_list.append(name)
        directory.append(dir)
        release_date.append(pick['release_date'])
        vote_average.append(pick['vote_average'])
        vote_count.append(pick['vote_count'])
        popularity.append(pick['popularity'])
        overview.append(pick['overview'])
        if pick['poster_path'] != None:
            img_url = img_base +pick['poster_path']
        else:
            img_url = 'No poster available'
        poster.append(img_url)
        videos = tmdb.Movies(pick['id']).videos()
        for vid in videos['results']:
            if vid['type'] == 'Trailer':
                if vid['site'] == 'YouTube':
                    trailer_url = video_base + vid['key']
            else:
                trailer_url = 'No trailer available'
        trailer.append(trailer_url)
        credits = tmdb.Movies(pick['id']).credits()
        top5_cast = ''
        for cast in credits['cast'][0:5]:
                top5_cast = top5_cast + f"{cast['name']} as {cast['character']}\n"
        cast_list.append(top5_cast)
        movie = tmdb.Movies(pick['id'])
        response = movie.info()
        this_genres = ''
        for i in range(len(movie.genres)):
            if i == 0:
                this_genres = movie.genres[i]['name']
            else:
                this_genres = this_genres + ', ' + movie.genres[i]['name']
        genres.append(this_genres)
    else:
        no_api_result.append(name)

for i in no_api_result:
    print('Couldn\'t find:')
    print(i)


# add to dataframe
media_df['filename'] = files_list
media_df['name'] = name_list
media_df['release_date'] = release_date
media_df['overview'] = overview
media_df['vote_average'] = vote_average
media_df['vote_count'] = vote_count
media_df['popularity'] = popularity
media_df['trailer'] =  trailer
media_df['poster'] = poster
media_df['genre'] = genres
media_df['cast_top5'] = cast_list
media_df['location'] = directory

#save to csv
media_df.to_csv('media_df.csv')