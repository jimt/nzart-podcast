#! /usr/bin/python3

# read mp3 tags from files and insert each episode in SQLite DB

import os
import sys
import glob
import argparse
import sqlite3
from datetime import date, timedelta
import mutagen
from mutagen.mp3 import MP3
from mutagen.id3 import ID3, TIT2, COMM, TALB, TPE1, TPOS
from mutagen.easyid3 import EasyID3

def convert_seconds(seconds):
    seconds = round(seconds)
    hours = seconds // 3600
    seconds = seconds % 3600
    minutes = seconds // 60
    seconds = seconds % 60
    print(hours, minutes, seconds)
    return f'{hours:02d}:{minutes:02d}:{seconds:02d}'

def last_sunday(year, month):
    print (f'Last Sunday of year: {year}, month: {month}')
    if month == 12:
        month = 1
        year += 1
    else:
        month += 1
    d = date(year, month, 1)
    d += timedelta(days=6-d.weekday()) # First Sunday
    d -= timedelta(days=7) # Last Sunday
    return d

# get the mp3 tags from the file using the mutagen library
# using the pathname as the key, insert the episode into the database
def add_episode(pathname, cur):
    months = ['feb', 'mar', 'apr', 'may', 'jun', 'jul', 'aug', 'sep', 'oct', 'nov', 'dec']
    print("=======", pathname, "=======")
    try:
        mu = MP3(pathname)
        #mu = mutagen.File(pathname)
    except mutagen.mp3.HeaderNotFoundError:
        print("HeaderNotFoundError")
        return
    stats = os.stat(pathname)
    print(mu)
    print('-----')
    print(mu.keys())
    print('-----')
    pathname = os.path.relpath(pathname)
    [year, month] = pathname.split('/')
    month = month.replace('.mp3', '')
    print(f'Try to find episode year: {year}, month: {month}')
    try:
        episode = months.index(month) + 1
        print (f'episode: {episode}')
        pubdate = last_sunday(int(year), episode + 1)
    except ValueError:
        episode = 0
        pubdate = date(int(year), 1, 1)
    pubdate = pubdate.strftime('%a, %d %b %Y 00:00:01 +1200')
    # default 
    ep = {
        'pathname': pathname,
        'title': f'{month.capitalize()} {year} NZART Official Broadcast',
        'album': '',
        'artist': 'Anchor Jim Meachen ZL2BHF',
        'desc': '',
        'pubdate': pubdate,
        'link': 'https://www.nzart.org.nz/news/broadcast/',
        'guid': '',
        'duration': convert_seconds(mu.info.length),
        'series': year,
        'episode': episode,
        'url': '',
        'size': stats.st_size
    }
    # make titles consistent
    #if 'TIT2' in mu.keys():
    #    ep['title'] = mu['TIT2'].text[0]
    if 'TALB' in mu.keys():
        ep['album'] = mu['TALB'].text[0]
    if 'TPE1' in mu.keys():
        ep['artist'] = mu['TPE1'].text[0]
    if 'TPOS' in mu.keys():
        print (mu['TPOS'])
        ep['episode'] = mu['TPOS'].text[0]
    if 'COMM::eng' in mu.keys():
        ep['desc'] = mu['COMM::eng'].text[0]
    elif 'COMM::\x00\x00\x00' in mu.keys():
        ep['desc'] = mu['COMM::\x00\x00\x00'].text[0]
    if year < '2024':
        ep['url'] = f'https://www.nzart.org.nz/assets/broadcast/{pathname}'
    else:
        ep['url'] = f'https://nzart.onnz.net/assets/broadcast/{pathname}'
    if year <= '2020':
        ep['guid'] = ep['url']
    else:
        ep['guid'] = f'NZART Official Broadcast {year} {month.replace('.mp3', '')} {ep['episode']} 00'
    print(ep)
    cur = con.cursor()
    cur.execute('''REPLACE INTO episodes (pathname, title, artist, link, guid, desc, duration,
                    series, episode, url, size, pubdate)
                 VALUES (:pathname, :title, :artist, :link, :guid, :desc, :duration,
                   :series, :episode, :url, :size, :pubdate)''', ep)
    con.commit()

if __name__ == '__main__':
    con = sqlite3.connect("podcast.db")

    os.chdir('/var/www/nzart/html/assets/broadcast')

    parser = argparse.ArgumentParser()
    parser.add_argument("pathname", nargs="*", help="pathname of podcast episode")
    parser.add_argument("-s", "--scan", help="(re)scan all episodes", action="store_true")
    args = parser.parse_args()

    if (len(args.pathname) == 0) and not args.scan:
        print('Must supply either one or more files or use --scan', file=sys.stderr)
        parser.print_help(sys.stderr)
        sys.exit(1)

    if args.scan:
        for file in glob.glob('./**/*.mp3'):
            add_episode(file, con)

    for file in args.pathname:
        add_episode(file, con)
