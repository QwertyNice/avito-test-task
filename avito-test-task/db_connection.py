import asyncio
from datetime import datetime
from typing import Optional, Union, Type
import mysql.connector
from tools import Requester, Parser
from secretinfo import USER, PASSWORD, HOST, DATABASE


class DatabaseConnector():
    """Сlass for simulating a MySQL database connection

    All methods of this class are asynchronous. To create a connection to the 
    database, method `connect` is used, and to disconnect `disconnect`. There is 
    also a class attribute `tables` to create the necessary tables.

    """
    tables = {'pair': 'CREATE TABLE pair (id INT PRIMARY KEY AUTO_INCREMENT, ' \
                      'region VARCHAR(50) NOT NULL, query VARCHAR(30));',
              'counter': 'CREATE TABLE counter (id INT PRIMARY KEY ' \
                         'AUTO_INCREMENT, timestamp DECIMAL(11,1), count INT,' \
                         ' pair_id INT, FOREIGN KEY (pair_id) REFERENCES ' \
                         'pair(id));'}
    
    async def connect(self, user: str, password: str, host: str, 
                      database: str) -> None:
        """Connects to the MySQL database server.

        Parameters
        ----------
        user : str
            The user name used to authenticate with the MySQL server.
        password : str
            The password to authenticate the user with the MySQL server.
        host : str
            The host name or IP address of the MySQL server.
        database : str
            The database name to use when connecting with the MySQL server.

        Note
        ----
        Contact your administrator to find out what connection parameters you
        should use to connect (that is, what host, user name, and password
        to use).
        
        """

        self.conn = mysql.connector.connect(user=user, password=password,
                                            host=host, database=database)
        await self._check_tables_exist()
        print(f'Connected to the {database} database')
        

    async def disconnect(self) -> None:
        """"Disconnects from the MySQL database server."""
        db = self.conn.database
        if self.conn:
            self.conn.close()
        print(f'Disconnected from the {db} database')

    async def _parse_loop(self, requester: Type[Requester] = Requester, 
                          parser: Type[Parser] = Parser, 
                          time_loop: int = 3600) -> None:
        """Parses a number of advertisement through in a loop for each record
        in the `pair` table, then and adds it to the `counter` table.

        Parameters
        ----------
        requester : Type[Requester], optional
            User-defined implementation of requester class.
        parser : Type[Requester], optional
            User-defined implementation of parser class.
        time_loop : int, optional
            Time in seconds, through a number of advertisement is being parsed.

        """

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
                    await self.insert_to_counter_table(timestamp=timestamp, 
                                                    count=count, pair_id=tup[0])
                    print(f'Added to counter table: {count=}, {timestamp=}, pair_id={tup[0]}') # DELETE

    async def _check_tables_exist(self) -> None:
        """Checks `pair` and `counter` tables  are exist in the database,
        creates otherwise."""
        cursor = self.conn.cursor()
        with cursor:
            query = ("SHOW TABLES")
            cursor.execute(query)
            remote_tables = [tup[0] for tup in cursor]
            for table in self.tables:
                if not table in remote_tables:
                    cursor.execute(self.tables[table])

    async def select_id_from_pair_table(
        self, region: str, query: Optional[str] = None) -> Optional[int]:
        """Retrieves id of the region and query from the `pair` table.

        Parameters
        ----------
        region : str
            Region which we are looking for id.
        query : str, optional
            Query which we are looking for id.

        Returns
        -------
        int
            Pair id for the region and query.
        
        """

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
    
    async def insert_to_pair_table(self, region: str, 
                                query: Optional[str] = None) -> Optional[int]:
        """Inserts region and query to the `pair` table and retrieves their 
        pair id.

        Parameters
        ----------
        region : str
            Region which is being inserted.
        query : str, optional
            Query which is being inserted.

        Returns
        -------
        int
            Pair id for the region and query.
        
        """
        cursor = self.conn.cursor()
        with cursor:
            db_query = "INSERT INTO pair (region, query) VALUES (%s, %s);"
            cursor.execute(db_query, (region, query))
            self.conn.commit()
        pair_id = await self.select_id_from_pair_table(region, query)
        return pair_id

    async def insert_to_counter_table(self, timestamp: float, 
                                   count: int, pair_id: int) -> None:
        """Inserts timestamp, number of advertisement and id pair to the 
        `counter` table.

        Parameters
        ----------
        timestamp : float
            Timestamp float number which is being inserted.
        count : int
            Number of advertisement which is being inserted.
        pair_id : int
            Pair id for the region and query which is being inserted.

        """

        cursor = self.conn.cursor(buffered=True)
        with cursor:
            assert_query = "SELECT id FROM pair WHERE id=%s;"
            cursor.execute(assert_query, [pair_id])
            assert list(cursor)
            
            db_query = "INSERT INTO counter (timestamp, count, pair_id) " \
                       "VALUES (%s, %s, %s);"
            cursor.execute(db_query, (timestamp, count, pair_id))
            self.conn.commit()

    async def select_ts_from_counter_table(self, pair_id: int, 
                                        start: Union[float, int], 
                                        end: Union[float, int]) -> tuple:
        """Retrieves timestamps and counts from the `counter` table.

        Parameters
        ----------
        pair_id : int
            Pair id for the region and query which is being selected.
        start : float, int
            Start position of the search time interval.
        end : float, int
            End position of the search time interval.

        Returns
        -------
        tuple
            Tuple of tuple with timestamps and tuple with their counts.
            For example: (123456789.0, 222222222.2), (456, 3908) 
        
        """
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
