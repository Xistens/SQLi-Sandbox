
-- Disable foreign keys so that we can delete the database if it already exists
PRAGMA foreign_keys = OFF;

drop table if exists Track;
drop table if exists Challenge;
drop table if exists Track_item;

PRAGMA foreign_keys = ON;

create table Track (
    track_id integer primary key,
    track_name text unique not null
);

create table Challenge (
    challenge_id integer primary key,
    name text not null unique,
    title text not null unique,
    tags text not null,
    difficulty text not null default "Easy",
    description text not null default "Missing description"
);


create table Track_item (
    item_id integer primary key,
    track_id integer not null references Track(track_id),
    challenge_id integer not null references Challenge(challenge_id),
    track_position integer not null
);

INSERT INTO Track (track_name) VALUES 
    ("Vulnerable Startup"),
    ("Introduction SQL Injection");

