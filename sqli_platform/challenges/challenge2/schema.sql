drop table if exists users;
create table users (
    id integer primary key,
    username text unique not null,
    password text not null
);


insert into users (username, password) values 
    ("admin", "rcLYWHCxeGUsA9tH3GNV"),
    ("dev", "asd"),
    ("amanda", "Summer2019!"),
    ("maja", "345m3io4hj3"),
    ("awe32Flage32x", "{{FLAG}}"),
    ("emil", "viking123");

