import asyncio
from datetime import datetime
from typing import Optional, Union, Type
import mysql.connector
from tools import Requester, Parser
from secretinfo import USER, PASSWORD, HOST, DATABASE


class DatabaseConnector():

    tables = {'pair': 'CREATE TABLE pair (id INT PRIMARY KEY AUTO_INCREMENT, ' \
                      'region VARCHAR(50) NOT NULL, query VARCHAR(30));',
              'counter': 'CREATE TABLE counter (id INT PRIMARY KEY ' \
                         'AUTO_INCREMENT, timestamp DECIMAL(11,1), count INT,' \
                         ' pair_id INT, FOREIGN KEY (pair_id) REFERENCES ' \
                         'pair(id));'}
    
    async def connect(self, user: str, password: str, host: str, 
                      database: str) -> None:
        self.conn = mysql.connector.connect(user=user, password=password,
                                            host=host, database=database)
        await self._check_tables_exist()
        

    async def disconnect(self) -> None:
        if self.conn:
            self.conn.close()

    async def _parse_loop(self, requester: Type[Requester] = Requester, 
                          parser: Type[Parser] = Parser, 
                          time_loop: int = 3600) -> None:
        
        query = "SELECT id, region, query FROM pair"
        while True:
            await asyncio.sleep(time_loop)
            cursor = self.conn.cursor(buffered=True)
            
            with cursor:
                cursor.execute(query)
                for tup in cursor:
                    requester_instance = requester(region=tup[1].lower(),
                                                   params={'q': tup[2]})
                    parser_instance = parser(
                                    raw_answer=requester_instance.answer, 
                                    query=tup[2], skip_check=True)
                    count = parser_instance.parse_count(q=tup[2])
                    timestamp = round(datetime.now().timestamp(), 1)
                    await self.insert_to_counter_db(timestamp=timestamp, 
                                                    count=count, pair_id=tup[0])
                    print(f'Added to counter db: {count=}, {timestamp=}, pair_id={tup[0]}') # DELETE

    async def _check_tables_exist(self) -> None:
        cursor = self.conn.cursor()
        with cursor:
            query = ("SHOW TABLES")
            cursor.execute(query)
            remote_tables = [tup[0] for tup in cursor]
            for table in self.tables:
                if not table in remote_tables:
                    cursor.execute(self.tables[table])

    async def select_id_from_pair_db(
        self, region: str, query: Optional[str] = None) -> Optional[int]:
        
        cursor = self.conn.cursor()
        with cursor:
            if not query:
                db_query = "SELECT id FROM pair WHERE region=%s AND " \
                            "query IS %s;"
            else:
                db_query = "SELECT id FROM pair WHERE region=%s AND query=%s;"

            cursor.execute(db_query, (region, query))
            result_list = list(cursor)

            if not result_list:
                return None
            
            pair_id = result_list[0][0]
            return pair_id
    
    async def insert_to_pair_db(self, region: str, 
                                query: Optional[str] = None) -> Optional[int]:
        cursor = self.conn.cursor()
        with cursor:
            db_query = "INSERT INTO pair (region, query) VALUES (%s, %s);"
            cursor.execute(db_query, (region, query))
            self.conn.commit()
        pair_id = await self.select_id_from_pair_db(region, query)
        return pair_id

    async def insert_to_counter_db(self, timestamp: float, 
                                   count: int, pair_id: int) -> None:
        cursor = self.conn.cursor(buffered=True)
        with cursor:
            assert_query = "SELECT id FROM pair WHERE id=%s;"
            cursor.execute(assert_query, [pair_id])
            assert list(cursor)
            
            db_query = "INSERT INTO counter (timestamp, count, pair_id) " \
                       "VALUES (%s, %s, %s);"
            cursor.execute(db_query, (timestamp, count, pair_id))
            self.conn.commit()

    async def select_ts_from_counter_db(self, pair_id: int, 
                                        start: Union[float, int], 
                                        end: Union[float, int]) -> tuple:
        db_query = "SELECT timestamp, count FROM counter WHERE " \
                   "timestamp >= %s AND timestamp <= %s AND pair_id=%s"
        cursor = self.conn.cursor()
        with cursor:
            cursor.execute(db_query, (start, end, pair_id))
            generator = zip(*cursor)
            try:
                timestamp_tuple = next(generator)
                count_tuple = next(generator)
            except StopIteration:
                timestamp_tuple = tuple()
                count_tuple = tuple()
            return timestamp_tuple, count_tuple
