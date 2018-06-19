#/usr/local/bin/python3
import signal
from bs4 import BeautifulSoup
import requests
import sys
import getpass
from halo import Halo
from lyricline.constants import ( TOKEN )

def handle_signal(signal, frame):
    sys.exit(0)

signal.signal(signal.SIGINT, handle_signal)

defaults = {
    'request': {
        'token': TOKEN,
        'base_url': 'https://api.genius.com'
    },
    'message': {
        'search_fail': 'The lyrics for this song were not found!',
        'wrong_input': 'Wrong number of arguments.\n' \
                       'Use two parameters to perform a custom search ' \
                       'or none to get the song currently playing on Spotify.'
    }
}

def exit():
    sys.exit(0)

def request_song_info(song_title, artist_name):
    base_url = defaults['request']['base_url']
    headers = {
        'Authorization': 'Bearer {}'.format(TOKEN)
    }
    data = {
        'q': '{} {}'.format(song_title, artist_name)
    }
    search_url = base_url + '/search'
    response = requests.get(search_url, data=data, headers=headers)

    return response

def scrape_song_url(url):
    page = requests.get(url)
    html = BeautifulSoup(page.text, 'html.parser')
    lyrics = html.find('div', class_='lyrics').get_text()

    return lyrics

def lyric_by_verse(lyrics):
    current_verse = []
    for line in lyrics.split("\n"):
        if line == '':
            if len(current_verse) > 0:
                yield str.join("\n", current_verse)
                current_verse = [] 
            continue
        elif line: 
            current_verse.append("\t\t" + line.strip())

def handle_input(index, number_verses):
    should_exit = False
    new_index = index
    prompt = "{}/{} [n/p/e]".format(new_index, number_verses)
    next_step = getpass.getpass(prompt)

    if len(next_step) < 1:
        return new_index, should_exit

    if next_step.lower()[0] == 'n':
        if new_index == number_verses:
            print("\t-- end of lyrics --")
        else:
            new_index = new_index + 1
    if next_step.lower()[0] == 'p':
        if new_index == 0:
            print("\t-- start of lyrics --")
        else:
            new_index = new_index - 1
    if next_step.lower()[0] == 'e':
        exit()

    return new_index, should_exit

def main():
    if len(sys.argv) < 3:
        print("Too few arguments. Require song title followed by artist name.")
        sys.exit(0)

    song_info = sys.argv
    song_title, artist_name = song_info[1], song_info[2]
    print('{} by {}'.format(song_title, artist_name))

    # Search for matches in request response
    spinner = Halo(text='Loading...', spinner='dots')
    spinner.start()
    response = request_song_info(song_title, artist_name)
    json = response.json()
    remote_song_info = None

    for hit in json['response']['hits']:
        if artist_name.lower() in hit['result']['primary_artist']['name'].lower():
            remote_song_info = hit
            break

    # Extract lyrics from URL if song was found
    if not remote_song_info:
        spinner.stop()
        print(defaults['message']['search_fail'])
    
    song_url = remote_song_info['result']['url']
    lyrics = scrape_song_url(song_url)

    spinner.stop()
    should_exit_input = False 
    verse_index = 0
    lyric_array = [ x for x in lyric_by_verse(lyrics) ]
    while not should_exit_input:
        print(lyric_array[verse_index]) 
        verse_index, should_exit_input = handle_input(verse_index, len(lyric_array) - 1)
    
    sys.exit(0)

