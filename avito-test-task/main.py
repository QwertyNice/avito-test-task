from typing import Optional
import requests
from fastapi import FastAPI
from lxml.html import fromstring
import uvicorn
from datetime import datetime
import asyncio
from secretinfo import USER, PASSWORD, HOST, DATABASE
from db_connection import DatabaseConnector


class Requester:

    def __init__(self):
        self.row_url = 'https://www.avito.ru/{}'

    def prepare_request(self, region):
        self.url = self.row_url.format(region)

    def make_request(self, params=None):
        return requests.get(self.url, params=params).text


class Parser:

    def __init__(self, row_answer, query, skip_check=False):
        # TODO случай skip_check = True
        self.row_answer = row_answer
        self.error = None
        self.__tree = self._prepare_to_parse()
        self.valid_region = self._check_valid_region()
        if self.valid_region:
            if self._check_valid_query(q=query):
                self.query = self.correct_mistake_in_query(q=query)
        # FIXME Вернуть правильно невалидный query
        else:
            self.query = query

    def _prepare_to_parse(self):
        """Функция преобразовывает код страницы в дерево"""
        return fromstring(self.row_answer)

    def _check_valid_region(self):
        """Функция проверяет, правильно ли пользователь ввел регион"""
        answer = self.__tree.xpath('//div[@class="b-404"]/h1/text()')
        if answer:
            self.error = 'Введен невалидный регион'
        return not answer

    def _check_valid_query(self, q):
        """Функция проверяет, правильно ли пользователь ввел запрос"""
        return self.parse_count(q=q) != 0

    def parse_count(self, q):
        """Функция парсит преобразованное дерево и выводит количество обьявлений"""
        if q:
            count = self.__tree.xpath(
                '//span[starts-with(@class, "page-title-count")]/text()')
            if count:
                count = int(count[0].replace(' ', ''))
            else:
                count = 0
                # FIXME Исправить синтаксичесическую часть предложения
                self.error = 'Введен невалидный запрос или количество объявлений по нему ноль'
            return count
        else:
            count = self.__tree.xpath(
                '//span[starts-with(@class, "category-with-counters-count")]/text()')
            count = int(count[0].replace(',', ''))
            return count

    def correct_mistake_in_query(self, q):
        """Функция исправляет ошибки в запросе, если они есть"""
        if q:
            q = self.__tree.xpath('//div[starts-with(@class, "index-suggest-")]/input/@value')[0]
        return q


app = FastAPI()

# db_connector = DatabaseConnector()


@app.on_event("startup")
async def start_consuming():
    # FIXME
    await db_connector.connect(USER, PASSWORD, HOST, DATABASE)
    asyncio.create_task(db_connector.select_db())


@app.on_event("shutdown")
async def shutdown():
    await db_connector.disconnect()


@app.get("/add/{region}")
async def read_item(region: str, query: Optional[str] = None):
    db_query = 'SELECT * FROM ...'
    if db_query:
        pair_id = ... # id пары под индексом ноль
    else:
        requester.prepare_request(region=region)
        answer = requester.make_request(params={'q': query})
        parser = Parser(answer)
        parser.prepare_to_parse()
        if not parser.check_valid_region():
            pair_id = 'Введен невалидный регион.'
        else:
            query = parser.check_query(q=query)
        # добавляем регион и запрос в SQL
        pair_id = ... # присваиваем новому региону и запросу id
    return {"id": pair_id}


if __name__ == '__main__':
    # uvicorn.run("main:app", host="127.0.0.1", port=5000, log_level="info")
    # uvicorn main:app --reload
    # CREATE TABLE pair (id INT PRIMARY KEY AUTO_INCREMENT, region VARCHAR(50) NOT NULL, query VARCHAR(30));
    # CREATE TABLE timestamp (id INT PRIMARY KEY AUTO_INCREMENT, timestamp DECIMAL(11,1), count INT, pair_id INT, FOREIGN KEY (pair_id) REFERENCES pair(id));
    pass