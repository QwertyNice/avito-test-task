import asyncio
import mysql.connector
from secretinfo import USER, PASSWORD, HOST, DATABASE


class DatabaseConnector():

    def __init__(self):
        # FIXME
        # Check db `region_query` is created
        # Check db `timestamps` is created
        pass

    async def connect(self, user, password, host, database):
        self.conn = mysql.connector.connect(user=user, password=password,
                                            host=host, database=database)

    async def disconnect(self):
        if self.conn:
            self.conn.close()

    async def select_db(self):
        cursor = self.conn.cursor()
        with cursor:
            query = ("SELECT * FROM region_query")
            while True:
                cursor.execute(query)
                res = []
                for i in cursor:
                    res.append(i)
                print(res)
                await asyncio.sleep(2)