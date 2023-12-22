import sqlite3


class RecommendationsDB:

    def __init__(self, db_file):
        self.conn = sqlite3.connect(db_file, check_same_thread=False)
        self.cursor = self.conn.cursor()

    def is_exist(self, tablename):
        """Check if a table exists"""
        query = "SELECT count(name) FROM sqlite_master WHERE type='table' and name=?"
        result = self.cursor.execute(query, (tablename,))
        return result.fetchone()[0]

    def get_all_recs(self, username):
        """Get recommendations"""
        result = self.cursor.execute(f'SELECT * from {username}')
        return result.fetchall()

    def add_recs(self, username, data):
        """Add recommendations to the database"""
        self.cursor.execute(f'''CREATE TABLE {username} (
                        ID INTEGER PRIMARY KEY,
                        Title text NOT NULL,
                        Genres text NOT NULL,
                        PlanToWatch text NOT NULL,
                        Synopsis text NOT NULL,
                        Link text NOT NULL)''')

        for i in data:
            self.cursor.execute(f'INSERT INTO {username} VALUES (?, ?, ?, ?, ?, ?)', (data[i]['id'],
                                                                                      data[i]['Title'],
                                                                                      data[i]['Genres'],
                                                                                      data[i]['Plan To Watch'],
                                                                                      data[i]['Synopsis'],
                                                                                      data[i]['Link']))
        return self.conn.commit()

    def del_table(self, tablename):
        """Delete table"""
        self.conn.execute(f'DROP TABLE {tablename}')
        return self.conn.commit()

    def close(self):
        """Close the connection."""
        self.conn.close()


recs_db = RecommendationsDB('../recs_db.db')
