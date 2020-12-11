import asyncio
from datetime import datetime
from typing import Optional, Union
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
async def start_consuming() -> None:
    await db_connector.connect(USER, PASSWORD, HOST, DATABASE)
    asyncio.create_task(db_connector._parse_loop(time_loop=15))


@app.on_event("shutdown")
async def shutdown() -> None:
    await db_connector.disconnect()


@app.get("/add/{region}")
async def add_pair(region: str, query: Optional[str] = None) -> dict:
    pair_id = await db_connector.select_id_from_pair_db(region=region, 
                                                        query=query)
    
    if pair_id:
        return {"id": pair_id}
    requester = Requester(region=region, params={'q': query})
    parser = Parser(raw_answer=requester.answer, query=query, skip_check=False)
    
    if parser.error:
        return {"id": parser.error}

    # Проверяем есть ли такой id после исправления ошибок в запросе
    pair_id = await db_connector.select_id_from_pair_db(region=region, 
                                                        query=parser.query)
    if pair_id:
        return {"id": pair_id}
    
    pair_id = await db_connector.insert_to_pair_db(region=region, 
                                                   query=parser.query)
    return {"id": pair_id}


@app.get("/stat/{id}")
async def show_stats(id: int, start: Union[str, float, int] = None, 
                     end: Union[str, float, int] = None) -> dict:
    try:
        start_ts = datetime.fromisoformat(start).timestamp() if start else 0
    except ValueError:
        start_ts = float(start.replace(',', '.'))
    
    try:
        end_ts = datetime.fromisoformat(end).timestamp() if end else 9999999999
    except ValueError:
        end_ts = float(end.replace(',', '.'))
    timestamp_tuple, count_tuple = await db_connector.select_ts_from_counter_db(
        pair_id=id, start=start_ts, end=end_ts)
    return {"id": id, "timestamp": timestamp_tuple, "count": count_tuple}


if __name__ == '__main__':
    # uvicorn.run("main:app", host="127.0.0.1", port=5000, log_level="info")
    pass
    "http://127.0.0.1:8000/stat/45?start=2020-12-09T16:23:56&end=2020-12-09T17:23:56"