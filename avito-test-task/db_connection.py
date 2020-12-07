import asyncio
from typing import Optional
import mysql.connector
from secretinfo import USER, PASSWORD, HOST, DATABASE


class DatabaseConnector():

    tables = {'pair': 'CREATE TABLE pair (id INT PRIMARY KEY AUTO_INCREMENT, region VARCHAR(50) NOT NULL, query VARCHAR(30));',
              'counter': 'CREATE TABLE counter (id INT PRIMARY KEY AUTO_INCREMENT, timestamp DECIMAL(11,1), count INT, pair_id INT, FOREIGN KEY (pair_id) REFERENCES pair(id));'}
    
    def __init__(self):
        # FIXME
        # Check db `pair` is created
        # Check db `counter` is created
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

    async def select_id_from_pair_db(self, region: str, query: Optional[str] = None) -> Optional[int]:
        
        cursor = self.conn.cursor()
        with cursor:
            if not query:
                db_query = ("SELECT id FROM pair WHERE region=%s AND query IS %s;")
            else:
                db_query = ("SELECT id FROM pair WHERE region=%s AND query=%s;")
            cursor.execute(db_query, (region, query))
            
            result_list = list(cursor)
            if not result_list:
                return None
            
            pair_id = result_list[0]
            return pair_id
    
    async def insert_to_pair_db(self, region: str, query: Optional[str] = None) -> int:
        cursor = self.conn.cursor()
        with cursor:
            db_query = "INSERT INTO pair (region, query) VALUES (%s, %s);"
            cursor.execute(db_query, (region, query))
            self.conn.commit()
        pair_id = await self.select_id_from_pair_db(region, query)
        return pair_id

    async def insert_to_counter_db(self, timestamp: float, count: int, pair_id: int):
        cursor = self.conn.cursor()
        with cursor:
            assert_query = "SELECT id FROM pair WHERE id=%s;"
            cursor.execute(assert_query, [pair_id])
            assert list(cursor)
            
            db_query = "INSERT INTO counter (timestamp, count, pair_id) VALUES (%s, %s, %s);"
            cursor.execute(db_query, (timestamp, count, pair_id))
            self.conn.commit()