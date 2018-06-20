#/usr/local/bin/python3
import argparse
import requests
import sys
from bs4 import BeautifulSoup
from lyricline.spinn import Spinner
from lyricline.constants import ( TOKEN )

BASE_URL = 'https://api.genius.com'

def exit():
    clear_last_line = '\x1b[2K'
    sys.stdout.write(clear_last_line)
    sys.stdout.write('\rExiting...\n')
    sys.stdout.flush()
    sys.exit(0)

def request_song_info(song_title, artist_name):
    headers = {
        'Authorization': 'Bearer {}'.format(TOKEN)
    }
    data = {
        'q': '{} {}'.format(song_title, artist_name)
    }
    search_url = BASE_URL + '/search'
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

def get_search():
    title = input("Song title: ")
    artist = input("Artist: ")
    return (title, artist)

def handle_input(index, number_verses):
    should_exit = False
    new_index = index
    next_song = None

    prompt = "{}/{} [n/p/e/s] ".format(new_index, number_verses)
    next_step = input(prompt)

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
        raise SystemExit() 
    if next_step.lower()[0] == 's':
        next_song = get_search()

    return new_index, should_exit, next_song

def search(song_title, artist_name):

    # Search for matches in request response
    spinner = Spinner(message='Loading...')
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
        print("The lyrics for this song were not found!")
        return get_search() 

    song_url = remote_song_info['result']['url']
    lyrics = scrape_song_url(song_url)
    spinner.stop()

    full_title = hit['result']['full_title']
    print('{}'.format(full_title))

    should_exit_input = False 
    last_verse_index = -1
    verse_index = 0
    lyric_array = [ x for x in lyric_by_verse(lyrics) ]
    while not should_exit_input:
        if last_verse_index != verse_index:
            print(lyric_array[verse_index]) 
        last_verse_index = verse_index
        verse_index, should_exit_input, next_song = handle_input(verse_index, len(lyric_array) - 1)
        
        if next_song:
           return next_song 

def main():
    try:
        song_title, artist_name = get_search()
        while song_title or artist_name:
            song_title, artist_name = search(song_title, artist_name)    
    except SystemExit:
        exit()
    sys.exit(0)

