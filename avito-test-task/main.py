import asyncio
from datetime import datetime
from typing import Optional, Union
from fastapi import FastAPI
from lxml.html import fromstring
import requests
from db_connection import DatabaseConnector
from secretinfo import USER, PASSWORD, HOST, DATABASE
from tools import Requester, Parser


app = FastAPI()
db_connector = DatabaseConnector()


@app.on_event("startup")
async def start_consuming() -> None:
    """Connects to the database then starts concurrent task with parse loop."""
    await db_connector.connect(USER, PASSWORD, HOST, DATABASE)
    asyncio.create_task(db_connector._parse_loop(time_loop=3600))


@app.on_event("shutdown")
async def shutdown() -> None:
    """Disconnects from the database then shutdown."""
    await db_connector.disconnect()


@app.get("/add/{region}")
async def add_pair(region: str, query: Optional[str] = None) -> dict:
    """Takes a query and a region, registers them in the database.

    Parameters
    ----------
    region : str
        Region which is being inserted.
    query : str, optional
        Query which is being inserted.

    Returns
    -------
    dict
        Pair id for the region and query.
    
    """

    pair_id = await db_connector.select_id_from_pair_table(region=region, 
                                                           query=query)
    
    if pair_id:
        return {"id": pair_id}
    requester = Requester(region=region, params={'q': query})
    parser = Parser(raw_answer=requester.answer, query=query, skip_check=False)
    
    if parser.error:
        return {"id": parser.error}

    # Check again if such pair id is in database after correcting syntax errors 
    # in the query
    pair_id = await db_connector.select_id_from_pair_table(region=region, 
                                                           query=parser.query)
    if pair_id:
        return {"id": pair_id}
    
    pair_id = await db_connector.insert_to_pair_table(region=region, 
                                                      query=parser.query)
    return {"id": pair_id}


@app.get("/stat/{id}")
async def show_stats(id: int, start: Union[str, float, int] = None, 
                     end: Union[str, float, int] = None) -> dict:
    """Takes id of the query + region and the interval for which the counters
    should be displayed. 

    Parameters
    ----------
    id : int
        Pair id for the region and query which is being selected.
    start : str, float, int, optional
        Start position of the search time interval.
    end : str, float, int, optional
        End position of the search time interval.

    Returns
    -------
    dict
        Returns a tuple of counters and tuple of their corresponding timestamps.
    
    Note
    -------
    1) The start/end argument should look like:
        a) Float timestamp: 123456789.0;
        b) Int timestamp: 222222222;
        c) Str timestamp: YYYY-MM-DDTHH:MM:SS (splits by `T`).
    2) If start argument is None, searching in the database returns all 
    timestamps from the beginning;
    3) If end argument is None, searching in the database returns all 
    timestamps up to the end;
    4) Start and end arguments split by `&`. 
    For example: /stat/2?start=2020-12-09T16:23:56&end=2020-12-09T17:23:56
    
    """
    
    try:
        start_ts = datetime.fromisoformat(start).timestamp() if start else 0
    except ValueError:
        start_ts = float(start.replace(',', '.'))
    
    try:
        end_ts = datetime.fromisoformat(end).timestamp() if end else 9999999999
    except ValueError:
        end_ts = float(end.replace(',', '.'))
    timestamp_tuple, count_tuple = await \
    db_connector.select_ts_from_counter_table(pair_id=id, 
                                              start=start_ts, end=end_ts)
    return {"id": id, "timestamp": timestamp_tuple, "count": count_tuple}
