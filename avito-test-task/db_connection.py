import asyncio
import mysql.connector
from secretinfo import USER, PASSWORD, HOST, DATABASE


class DatabaseConnector():

    tables = {'pair': 'CREATE TABLE pair (id INT PRIMARY KEY AUTO_INCREMENT, region VARCHAR(50) NOT NULL, query VARCHAR(30));',
              'timestamp': 'CREATE TABLE timestamp (id INT PRIMARY KEY AUTO_INCREMENT, timestamp DECIMAL(11,1), count INT, pair_id INT, FOREIGN KEY (pair_id) REFERENCES pair(id));'}
    
    def __init__(self):
        # FIXME
        # Check db `pair` is created
        # Check db `timestamps` is created
        pass

    async def connect(self, user, password, host, database):
        self.conn = mysql.connector.connect(user=user, password=password,
                                            host=host, database=database)
        await self._check_tables_exist()
        

    async def disconnect(self):
        if self.conn:
            self.conn.close()

    async def parse_every_hour(self):
        # FIXME
        cursor = self.conn.cursor()
        with cursor:
            query = ("SELECT * FROM pair")
            while True:
                cursor.execute(query)
                res = []
                for i in cursor:
                    res.append(i)
                print(res)
                await asyncio.sleep(2)

    async def show_all_tables(self):
        '''Just checks and prints all existing tables in db'''
        cursor = self.conn.cursor()
        with cursor:
            query = ("SHOW TABLES")
            cursor.execute(query)
            print(list(cursor))

    async def _check_tables_exist(self):
        cursor = self.conn.cursor()
        with cursor:
            query = ("SHOW TABLES")
            cursor.execute(query)
            remote_tables = [tup[0] for tup in cursor]
            for table in self.tables:
                if not table in remote_tables:
                    cursor.execute(self.tables[table])

    async def add_pair_to_db(self, region, query):
        pass