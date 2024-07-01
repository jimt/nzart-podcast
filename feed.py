#!/usr/bin/python3

# use the python-feedgen library to generate an ATOM feed
# from the episodes found in the SQLite podcast.db database

import sqlite3
from feedgen.feed import FeedGenerator

fg = FeedGenerator()
fg.load_extension("podcast", rss=True, atom=False)
fg.id("https://www.nzart.org.nz/news/broadcast/")
fg.title("NZART Official Broadcast")
fg.author({"name": "NZART podcast", "email": "podcast@nzart.onnz.net"})
fg.language("en")
fg.link(href="https://www.nzart.org.nz/news/broadcast/", rel="alternate")
fg.logo("https://nzart.onnz.net/assets/forms/NZART-1400x1400.png")
fg.podcast.itunes_image("https://nzart.onnz.net/assets/forms/NZART-1400x1400.png")
fg.podcast.itunes_owner("Jim Tittsler ZL2IA", "podcast@nzart.onnz.net")
fg.podcast.itunes_author("Jim Meachen ZL2BHF")
fg.podcast.itunes_summary(
    "The official podcast of the New Zealand Association of Radio Transmitters with news and information for radio amateurs"
)
fg.subtitle(
    "The official podcast of the New Zealand Association of Radio Transmitters with news and information for radio amateurs"
)
fg.link(href="https://nzart.onnz.net/assets/broadcast/podcast.rss", rel="self")
fg.language("en")
fg.contributor({"name": "Jim Meachen ZL2BHF", "email": "zl6a@nzart.org.nz"})
fg.copyright("Copyright 2024 New Zealand Association of Radio Transmitters")
fg.category(term="Technology", scheme="https://www.itunes.com")
fg.podcast.itunes_category("Technology")
fg.podcast.itunes_explicit("no")

con = sqlite3.connect("podcast.db")
cur = con.cursor()
cur.execute("SELECT * FROM episodes ORDER BY series DESC, episode DESC")

for row in cur.fetchall():
    (
        pathname,
        title,
        artist,
        link,
        guid,
        desc,
        duration,
        series,
        episode,
        url,
        size,
        pubdate,
        image,
        explicit,
    ) = row
    fe = fg.add_entry()
    fe.id(url)
    fe.guid(guid, permalink=guid.startswith("http"))
    fe.title(title)
    fe.author(name=artist, email="zl6a@nzart.org.nz")
    fe.category()
    fe.link(href=link)
    fe.description(desc)
    # fe.duration(duration)
    fe.published(pubdate)
    fe.podcast.itunes_season(series)
    fe.podcast.itunes_episode(episode)
    fe.podcast.itunes_duration(duration)
    fe.podcast.itunes_explicit("no")
    fe.enclosure(url, str(size), "audio/mpeg")

fg.rss_file("/var/www/nzart/html/assets/broadcast/podcast.rss")
