import asyncio
from datetime import datetime
from typing import Optional
from fastapi import FastAPI
from lxml.html import fromstring
import requests
import uvicorn
from db_connection import DatabaseConnector
from secretinfo import USER, PASSWORD, HOST, DATABASE
from tools import Requester, Parser


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
    # asyncio.create_task(db_connector._parse_every_hour())


@app.on_event("shutdown")
async def shutdown():
    await db_connector.disconnect()


@app.get("/add/{region}")
async def add_pair(region: str, query: Optional[str] = None):
    pair_id = await db_connector.select_id_from_pair_db(region=region, query=query)
    
    if pair_id:
        return {"id": pair_id}
    requester = Requester()
    requester.prepare_request(region=region)
    answer = requester.make_request(params={'q': query})
    parser = Parser(raw_answer=answer, query=query, skip_check=False)
    
    if parser.error:
        return {"id": parser.error}

    # Проверяем есть ли такой id после исправления ошибок в запросе
    pair_id = await db_connector.select_id_from_pair_db(region=region, query=parser.query)
    if pair_id:
        return {"id": pair_id}
    
    pair_id = await db_connector.insert_to_pair_db(region=region, query=parser.query)
    return {"id": pair_id}


@app.get("/stat/{id}")
async def show_stats(id: int, start: Optional[float] = None, end: Optional[float] = None):
    return {"id": id, "start": start, "end": end}


if __name__ == '__main__':
    # uvicorn.run("main:app", host="127.0.0.1", port=5000, log_level="info")
    pass