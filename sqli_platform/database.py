#!/usr/bin/python3
import sqlite3
import os
from flask import flash
from sqli_platform import app_log
from sqli_platform.utils.challenge import place_flag_schema


class Database(object):
    """
    This class handles all communication with sqlite.

    Args:
        app:        The application context. (Type: Class application.Application)
        configs:    (list)  List containing configurations of all challenges
        basedir:    (str)   The application's root path
    """

    def __init__(self, app, configs: list, basedir: str):
        self._app = app
        self._configs = configs
        self._basedir = basedir
        self._binds = {}
        self._setup_main()
        self._setup_binds()


    def _setup_main(self):
        """
        Setup the sqlite connection for the main application
        """
        url = f"{self._basedir}/databases/database.db"
        db = sqlite3.connect(url, check_same_thread=False)
        self._init_db(db, f"{self._basedir}/schemas/main.sql")
        bind = {"main": db}
        self._binds.update(bind)


    def _setup_binds(self) -> dict:
        """
        Create sqlite3 connections from challenge configs
        
        Args:
            configs:    (list) List containing configurations of all challenges
            basedir:    (str) Path to the application's root directory
        """
        #self._app.app_log.debug("Generating binds")
        binds = {}
        for conf in self._configs:
            path = conf["path"].replace(".", "/")
            c = conf["config"]
            drive = c["database"]["drivername"]
            url = f'{self._basedir}{path}/{c["name"]}.db'
            db = sqlite3.connect(url, check_same_thread=False)
            binds[c['name']] = db
            schema = f"{self._basedir}{path}/schema.sql"
            place_flag_schema(schema, c["name"])
            self._init_db(db, schema)


            # Add challenge information to db
            tags = ", ".join(c.get("tags", ""))
            difficulty = c["difficulty"].lower().capitalize()
            description = c.get("description", "")
            rowid = self.sql_insert(
                "main", 
                "INSERT INTO Challenge (name, title, tags, difficulty, description) VALUES (?, ?, ?, ?, ?)", 
                [c["name"], c["title"], tags, difficulty, description]
            )

            # Add track information to db
            self.sql_insert(
                "main",
                "INSERT INTO Track_item (track_id, challenge_id, track_position) VALUES (?, ?, ?)",
                [c["track"]["track_id"], rowid, c["track"]["position_in_track"]]
            )
        self._binds.update(binds)


    def get_db(self, name: str):
        """
        Gets the database connection for <name>

        Args:
            name:   (str) The database connection name (challenge name or "main" for main app)
        Return:
            db:     (sqlite3.Connection): The database connection
        """
        db = self._binds[name]

        # Use namedtuple's. Access them by index or key
        db.row_factory = sqlite3.Row
        return db


    def _init_db(self, db, schema: str):
        """
        Initializes a new database from schema.
        
        Args:
            schema: (str) The path to / name of the schema to use for the database.
        """
        with self._app.app_context():
            with self._app.open_resource(schema, mode="r") as f:
                db.cursor().executescript(f.read())
            db.commit()


    def get_tracks(self):
        """
        Query to get Track information

        TODO:
            - Refactor and move out of here?
        """
        return self.sql_query("main",
            """
            SELECT
                t.track_name,
                c.name,
                c.title,
                c.tags,
                c.difficulty,
                c.description,
                TI.track_position
            FROM 
                Track_Item TI
                JOIN challenge c ON c.challenge_id=TI.challenge_id
                JOIN track t ON t.track_id=TI.track_id
            ORDER BY t.track_id DESC
            """
        )

    def sql_query(self, name: str, query: str, args: tuple = (), one: bool = False):
        """
        A helper function that combines getting the cursor,
        executing and fetching for results.

        Args:
            name: Name of the database
            query: The SQL query to be performed
            args: The arguments to be used in the query
            one: A boolean flag to tell if we should get one or more values.
        
        Returns:
            A tuple or list with the returned rows
            sqlite3.Row If one == True else List off Sqlite3.Row
        """
        try:
            app_log.debug(query)
            with self.get_db(name) as conn:
                cur = conn.execute(query, args)
                rv = cur.fetchall()
        except sqlite3.OperationalError as e:
            app_log.error(e)
            rv = {}
        except sqlite3.Warning as e:
            app_log.error(e)
            rv = {}
            flash(f"Database error: {e}", "danger")
        return (rv[0] if rv else None) if one else rv


    def sql_insert(self, name: str, query: str, args: tuple = ()):
        try:
            app_log.debug(query)
            cur = self.get_db(name).execute(query, args)
            cur.execute("COMMIT")
            return cur.lastrowid
        except sqlite3.IntegrityError:
            app_log.error(name, query, args)
        except sqlite3.OperationalError:
            app_log.error(name, query, args)
