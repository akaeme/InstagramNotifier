import sqlite3


class Database:
    cursor = None

    def __init__(self, db_name):
        self.connection = sqlite3.connect(db_name)
        # Create Table user
        self.connection.execute('''CREATE TABLE IF NOT EXISTS `Users` (
                                `username`	TEXT NOT NULL,
                                `password`	TEXT NOT NULL,
                                PRIMARY KEY(`username`)
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

        self.tables = self.connection.execute('''SELECT name from sqlite_master where type = 'table'; ''')
        self.tables = [table[0] for table in self.tables]

    def insert_user(self, username, password):
        self.connection.execute('INSERT OR IGNORE INTO Users VALUES (?,?);', (username, password))
        self.connection.commit()

    def insert_follow(self, user_id, username, user, full_name='', is_private=False, profile_pic=''):
        self.connection.execute('INSERT OR IGNORE INTO Follow VALUES (NULL,?,?,?,?,?,?);', (user_id, username,
                                                                                            full_name, is_private,
                                                                                            profile_pic, user))
        self.connection.commit()

    def get_from_users(self, username):
        self.cursor = self.connection.execute('SELECT password FROM Users WHERE username = ?;', (username,))
        results = self.cursor.fetchall()
        return results

    def get_from_media(self, username):
        self.cursor = self.connection.execute('SELECT * FROM Media AS M LEFT JOIN (SELECT id, user_id from Follow '
                                              'WHERE user=?) AS Previous ON Previous.id = M.foreign_id WHERE user_id '
                                              'NOT NULL;', (username,))
        results = self.cursor.fetchall()
        return [result[0] for result in results]

    def get_from_follows(self, username):
        self.cursor = self.connection.execute('SELECT user_id FROM Follow WHERE user = ?;', (username,))
        results = self.cursor.fetchall()
        return [result[0] for result in results]
