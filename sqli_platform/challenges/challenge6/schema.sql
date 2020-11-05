drop table if exists users;
create table users (
    id integer primary key,
    username text unique not null,
    password text not null
);


insert into users (username, password) values 
    ("admin", "{{FLAG}}"),
    ("dev", "asd"),
    ("amanda", "Summer2019!"),
    ("maja", "345m3io4hj3"),
    ("emil", "viking123");

