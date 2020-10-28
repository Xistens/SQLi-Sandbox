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

drop table if exists books;
create table books (
    id integer primary key,
    title text not null,
    description text not null,
    author text not null
);

insert into users (username, password) values 
    ("admin", "{{FLAG}}"),
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

insert into books (title, description, author) values 
    ("Harry Potter and the Philosopher's Stone", "When mysterious letters start arriving on his doorstep, Harry Potter has never heard of Hogwarts School of Witchcraft and Wizardry. They are swiftly confiscated by his aunt and uncle. Then, on Harry’s eleventh birthday, a strange man bursts in with some important news: Harry Potter is a wizard and has been awarded a place to study at Hogwarts. And so the first of the Harry Potter adventures is set to begin.",
    "J.K. Rowling"),
    ("Booktitle", "Nice description", "Tom Hanks"),
    ("test", "description", "author");