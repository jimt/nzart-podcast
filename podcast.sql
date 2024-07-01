CREATE TABLE episodes (
    pathname TEXT PRIMARY KEY,
    title TEXT,
    artist TEXT,
    link TEXT,
    guid TEXT,
    desc TEXT,
    duration TEXT,
    series INTEGER,
    episode INTEGER,
    url TEXT,
    size INTEGER,
    pubdate TEXT,
    image TEXT DEFAULT "",
    explicit TEXT DEFAULT "false"
)