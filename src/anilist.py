from ulauncher.api.shared.item.ExtensionResultItem import ExtensionResultItem
from ulauncher.api.shared.action.OpenUrlAction import OpenUrlAction
import requests
import json
import os
import glob
from os.path import exists
import urllib.parse

EXTENSION_DIR = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
THUMBNAILS_DIR = EXTENSION_DIR + '/thumbnails/'

def search(searchKeyword, preferences):
    query = '''
        query ($search: String, $mediaType: MediaType, $isAdult: Boolean) {
        media: Page(perPage: 8) {
            results: media(type: $mediaType, isAdult: $isAdult, search: $search) {
            id
            coverImage {
                medium
            }
            siteUrl
            title {
                romaji,
                english,
                native
            }
            type
            format
            startDate {
                year
            }
            }
        }
        }
    '''

    # Define our query variables and values that will be used in the query request
    variables = {
        'search': searchKeyword,
    }

    if(str2bool(preferences['anime_enabled']) and not str2bool(preferences['manga_enabled'])):
        variables['mediaType'] = 'ANIME'

    if(str2bool(preferences['manga_enabled']) and not str2bool(preferences['anime_enabled'])):
        variables['mediaType'] = 'MANGA'

    if(not str2bool(preferences['adult_enabled'])):
        variables['isAdult'] = False

    url = 'https://graphql.anilist.co'

    # Make the HTTP Api request
    response = requests.post(url, headers={'User-Agent': 'ulauncher-anilauncher'}, json={'query': query, 'variables': variables})

    items = []

    mediaList = response.json()['data']['media']['results']
    for media in mediaList:
        description = "{} | {} | {}"
        description = description.format(media['type'], media['format'], media['startDate']['year'])

        name = media['title'][preferences['title_format']]
        # Fallback if title is not available
        if name == None:
            name = media['title']['romaji']
            
        iconPath = 'images/icon.png'    
        if(str2bool(preferences['cover_enabled'])):
            iconPath = downloadCover(media['coverImage']['medium'], media['id'], str2bool(preferences['statically_enabled']))

        items.append(ExtensionResultItem(icon=iconPath,
                                        name=name,
                                        description=description,
                                        on_enter=OpenUrlAction(media['siteUrl'])))

    return items;

def str2bool(str):
    return json.loads(str.lower())

def downloadCover(url, id, use_cdn):
    if not os.path.exists(THUMBNAILS_DIR):
        os.makedirs(THUMBNAILS_DIR)

    iconPath = THUMBNAILS_DIR + str(id)

    if(not exists(iconPath)):
        parsed_url = urllib.parse.urlparse(url)
        cdn_url = 'https://cdn.statically.io/img/{}/w=80,q=50{}'
        cdn_url = cdn_url.format(parsed_url.netloc, parsed_url.path);
        if(use_cdn):
            r = requests.get(cdn_url)
        else:
            r = requests.get(url)

        with open(iconPath,'wb') as output_file:
            output_file.write(r.content)

    return iconPath

def clear_thumbnails():
    files = glob.glob(THUMBNAILS_DIR + '*')
    
    for f in files:
        os.remove(f)