import os
import glob
import pandas as pd
from PTN import parse # parse-torrent-name

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
    # traverse whole directory
    for root, dirs, files in os.walk(dir):
        # select file name
        for file in files:
            # check the extension of files
            if file.endswith(file_types):
                thelist.append(file)
    return thelist

# function to parse a list of file names to get the title
def parse_for_title(file_list):
    name_list = []
    for filename in file_list:
        name = parse(filename)['title']
        name_list.append(name)
    return name_list


### Process films
film_extensions = get_file_types(base_path_films)
print(film_extensions)     

# review list of extensions and decide what's relevant. Then update search_for_types tuple...
search_for_types = ('.avi', '.mp4', '.mkv', '.divx', '.m4v', '.wmv', '.mov', '.mpg')
# create dataframe to hold all info. filename and name from the files, everything else from TMDb API
media_df = pd.DataFrame(columns=('filename', 'name', 'year', 'genre', 'rating', 'cast', 'trailer', 'poster', 'api_result'))

file_list = files_to_list(base_path_films, search_for_types)
name_list = parse_for_title(file_list)


# add to dataframe
media_df['filename'] = file_list
media_df['name'] = name_list
media_df.to_csv('media_df.csv')