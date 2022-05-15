from ulauncher.api.shared.item.ExtensionResultItem import ExtensionResultItem
from ulauncher.api.shared.action.OpenUrlAction import OpenUrlAction
import requests
import json

def search(searchKeyword, preferences):
    query = '''
        query ($search: String, $mediaType: MediaType, $isAdult: Boolean) {
        media: Page(perPage: 8) {
            results: media(type: $mediaType, isAdult: $isAdult, search: $search) {
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
        'search': searchKeyword
    }

    if(str2bool(preferences['anime_enabled']) and not str2bool(preferences['manga_enabled'])):
        variables['mediaType'] = 'ANIME'

    if(str2bool(preferences['manga_enabled']) and not str2bool(preferences['anime_enabled'])):
        variables['mediaType'] = 'MANGA'

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

        items.append(ExtensionResultItem(icon='images/icon.png',
                                        name=name,
                                        description=description,
                                        on_enter=OpenUrlAction(media['siteUrl'])))

    return items;

def str2bool(str):
    return json.loads(str.lower())