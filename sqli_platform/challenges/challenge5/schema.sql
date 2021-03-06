drop table if exists users;
create table users (
    id integer primary key,
    username text unique not null,
    password text not null
);

drop table if exists notes;
create table notes (
    id integer primary key,
    username text not null,
    title text not null,
    note text not null
);


insert into users (username, password) values 
    ("admin", "kTE956fczynJMM6m"),
    ("dev", "asd"),
    ("amanda", "Summer2019!"),
    ("maja", "345m3io4hj3"),
    ("emil", "viking123");
insert into notes (username, title, note) values 
    ("admin", "Testing Notes", "Hello, World!"),
    ("admin", "Secret Note!", "Top secret note"),
    ("amanda", "Passwords", "emil/viking123"),
    ("amanda", "Lorem Ipsum", "Lorem ipsum dolor sit amet, consectetur adipiscing elit. In ut egestas mi. Vestibulum at metus tincidunt, luctus eros vitae, pellentesque eros. Class aptent taciti sociosqu ad litora torquent per conubia nostra, per inceptos himenaeos. Etiam ac neque facilisis, tincidunt elit et, vestibulum nibh. Nullam tincidunt aliquam ligula et lobortis. Phasellus imperdiet, leo id luctus fringilla, odio ipsum lobortis lectus, nec tristique mi neque sed massa. Donec dictum arcu et massa eleifend blandit. Pellentesque lobortis vulputate rhoncus."),
    ("amanda", "Remember", "Interdum et malesuada fames ac ante ipsum primis in faucibus."),
    ("maja", "Shoppinglist", "milk, bread, coffee"),
    ("emil", "Important", "Remember to walk the dogs on sunday!");
