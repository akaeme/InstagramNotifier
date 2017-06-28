import sqlite3


class Database:
    cursor = None

    def __init__(self, db_name):
        self.connection = sqlite3.connect(db_name)
        # Create Table user
        self.connection.execute('''CREATE TABLE IF NOT EXISTS `Users` (
                                `username_insta`	TEXT NOT NULL,
                                `password_insta`	TEXT NOT NULL,
                                `email`	            TEXT NOT NULL,
                                `password_fb`	    TEXT NOT NULL,
                                PRIMARY KEY(`username_insta`)
                            );''')
        # Create Table Follow
        self.connection.execute('''CREATE TABLE IF NOT EXISTS `Follow` (
                            `id`	INTEGER NOT NULL PRIMARY KEY,
                            `user_id`	INTEGER NOT NULL,
                            `username`	TEXT NOT NULL UNIQUE,
                            `full_name`	TEXT,
                            `is_private`	INTEGER,
                            `profile_pic`	TEXT,
                            `user`	TEXT,
                            FOREIGN KEY(`user`) REFERENCES `Users`(`username`)
                        );''')
        # Create Table Media
        self.connection.execute('''CREATE TABLE IF NOT EXISTS `Media` (
                                `id`	INTEGER NOT NULL PRIMARY KEY,
                                `last_media_id`	INTEGER NOT NULL,
                                `media_count`	INTEGER NOT NULL,
                                `foreign_id`	INTEGER NOT NULL,
                                `last_media`	TEXT NOT NULL,
                                `width`	INTEGER NOT NULL,
                                `height`	INTEGER NOT NULL,
                                `location`	TEXT,
                                FOREIGN KEY(`foreign_id`) REFERENCES `Follow`(`id`)
                            );''')
        # Create Table Notify
        self.connection.execute('''CREATE TABLE IF NOT EXISTS `Notify` (
                                `id`	INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
                                `foreign_id`	INTEGER NOT NULL,
                                `thread_id`	INTEGER NOT NULL,
                                `thread_type`	TEXT NOT NULL,
                                `image_flag`	INTEGER NOT NULL DEFAULT 1,
                                FOREIGN KEY(`foreign_id`) REFERENCES 'Follow'('id')
                            );''')

        self.tables = self.connection.execute('''SELECT name from sqlite_master where type = 'table'; ''')
        self.tables = [table[0] for table in self.tables]

    def insert_user(self, username, password, email, password_fb):
        self.connection.execute("INSERT OR IGNORE INTO Users VALUES (?,?,?,?);", (username, password, email, password_fb
                                                                                  )
                                )
        self.connection.commit()

    def insert_follow(self, user_id, username, user, full_name='', is_private=False, profile_pic=''):
        self.connection.execute("INSERT OR IGNORE INTO Follow VALUES (NULL,?,?,?,?,?,?);", (user_id, username,
                                                                                            full_name, is_private,
                                                                                            profile_pic, user))
        self.connection.commit()

    def insert_notify(self, foreign_id, thread_id, thread_type, image_flag):
        # thread_type 0 - User
        # thread_type 1 - group
        # image_flag  1 - True
        # image_flag  0 - False
        self.connection.execute("INSERT OR IGNORE INTO Notify VALUES (NULL,?,?,?,?);",
                                (foreign_id, thread_id, thread_type, image_flag))
        self.connection.commit()

    def get_from_users(self, username, service):
        if service == 'instagram':
            try:
                self.cursor = self.connection.execute("SELECT password_insta FROM Users WHERE username_insta = ?;",
                                                      (username,))
            except sqlite3.Error:
                pass
        else:
            try:
                self.cursor = self.connection.execute("SELECT password_fb FROM Users WHERE email = ?;",
                                                      (username,))
            except sqlite3.Error:
                pass
        results = self.cursor.fetchall()
        return results

    def get_from_follows(self, username):
        try:
            self.cursor = self.connection.execute("SELECT user_id, username FROM Follow WHERE user = ?;", (username,))
        except sqlite3.Error:
            pass
        results = self.cursor.fetchall()
        return results

    def get_from_follows_find(self, username, username_follow):
        try:
            self.cursor = self.connection.execute("SELECT Follow.id FROM Users JOIN Follow ON Users.username_insta="
                                                  "Follow.user WHERE Users.username_insta=? AND Follow.username = ?;"
                                                  "", (username, username_follow))
        except sqlite3.Error:
            pass
        results = self.cursor.fetchall()
        results = [r[0] for r in results]
        return results

    def get_from_media(self, username):
        try:
            self.cursor = self.connection.execute("SELECT last_media_id,media_count,user_id,last_media,width,height,"
                                                  "location FROM Media AS M JOIN (SELECT id, user_id from Follow "
                                                  "WHERE user=?) AS Previous ON Previous.id = "
                                                  "M.foreign_id;", (username,))
        except sqlite3.Error:
            pass
        columns = [d[0] for d in self.cursor.description]
        data = [dict(zip(columns, row)) for row in self.cursor.fetchall()]
        return data

    def get_from_notify(self, username, username_follow):
        try:
            self.cursor = self.connection.execute("SELECT thread_id, thread_type, image_flag FROM Notify AS N JOIN "
                                                  "(Select Follow.id FROM Users JOIN Follow ON Users.username_"
                                                  "insta=Follow.user WHERE Users.username_insta=? and "
                                                  "Follow.username=?) AS previous ON "
                                                  "N.foreign_id=previous.id", (username, username_follow))
        except sqlite3.Error:
            pass
        columns = ['thread_id', 'thread_type', 'image_flag']
        data = [dict(zip(columns, row)) for row in self.cursor.fetchall()]
        return data
