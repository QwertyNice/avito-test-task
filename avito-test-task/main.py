import asyncio
from datetime import datetime
from typing import Optional
from fastapi import FastAPI
from lxml.html import fromstring
import requests
import uvicorn
from db_connection import DatabaseConnector
from secretinfo import USER, PASSWORD, HOST, DATABASE


app = FastAPI()
db_connector = DatabaseConnector()


@app.on_event("startup")
async def start_consuming():
    # FIXME
    await db_connector.connect(USER, PASSWORD, HOST, DATABASE)
    # await db_connector.show_all_tables()
    # await db_connector.select_id_from_pair_db('Ufa', 'Trad')
    # await db_connector.insert_to_pair_db('Ufa', 'Trad')
    # await db_connector.insert_to_counter_db(1234567890.1, 434, 4)
    asyncio.create_task(db_connector._parse_every_hour())


@app.on_event("shutdown")
async def shutdown():
    await db_connector.disconnect()


@app.get("/add/{region}")
async def read_item(region: str, query: Optional[str] = None):
    # db_query = 'SELECT * FROM ...'
    # if db_query:
    #     pair_id = ... # id пары под индексом ноль
    # else:
    #     requester.prepare_request(region=region)
    #     answer = requester.make_request(params={'q': query})
    #     parser = Parser(answer)
    #     parser.prepare_to_parse()
    #     if not parser.check_valid_region():
    #         pair_id = 'Введен невалидный регион.'
    #     else:
    #         query = parser.check_query(q=query)
    #     # добавляем регион и запрос в SQL
    #     pair_id = ... # присваиваем новому региону и запросу id
    # return {"id": pair_id}
    pass


if __name__ == '__main__':
    # uvicorn.run("main:app", host="127.0.0.1", port=5000, log_level="info")
    pass