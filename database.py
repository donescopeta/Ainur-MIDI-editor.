import sqlite3

class database:
    def __init__(self):
        self.conn = sqlite3.connect(":memory:",check_same_thread=False)
        self.__create_table()

    def __create_table(self):
        self.conn.execute("""
        CREATE TABLE IF NOT EXISTS notes(
             id PRIMARY KEY,
             start real ,
             length real,
             key integer
        );""")

    def insert(self,start,key,length):
        print(key,start,length)
        self.conn.execute("""
            INSERT INTO notes (start,key,length) values(?,?,?);
        """, ( start, key, length ) )

    def getnotes(self, start, range, keys=(0,128)):
        c = self.conn.cursor()
        print(start)
        c.execute("""
                SELECT start, key, length FROM notes
                    WHERE start BETWEEN ? AND ? AND key BETWEEN ? AND ?;
        """,( start, start + range, keys[0], keys[1] ) )
        r = c.fetchall()
        print("fetched from database",start, range, r)
        return set(r)

    def drop(self,*n):
        c = []
        for x in n :
             c += x
        print(c)
        condition =  " OR ".join( ["( key = ? AND start = ? AND length = ? )",] * len(n) )
        self.conn.execute("""
            DELETE FROM notes WHERE ({0})
        """.format(condition), c)
