from typing import Optional
import requests
from fastapi import FastAPI
from lxml.html import fromstring
import uvicorn
from datetime import datetime
import asyncio


class Requester:
    # FIXME
    
    def __init__(self):
        self.row_url = 'https://www.avito.ru/{}'

    def prepare_request(self, region, query):
        self.url = self.row_url.format(region)

    def make_request(self, params=None):
        return requests.get(self.url, params=params)


class Parser:

    def __init__(self, row_answer):
        self.row_answer = row_answer

    def prepare_to_parse(self):
        """Функция преобразовывает код страницы в дерево"""
        self.tree = fromstring(self.row_answer.text)

    def __check_vaild_request(self):
        """Функция проверяет, правильно ли пользователь ввел регион"""
        self.__answer = self.tree.xpath('//div[@class="b-404"]/h1/text()')
        return not self.__answer

    def parse(self):
        """Функция парсит преобразованное дерево и выводит количество обьявлений"""
        # FIXME
        if self.__check_vaild_request():
            count = self.tree.xpath(
                '//span[starts-with(@class, "page-title-count")]/text()')
            if count:
                count = int(count[0].replace(' ', ''))
                return count
            else:
                count = self.tree.xpath(
                '//span[starts-with(@class, "category-with-counters-count")]/text()')
                return int(count[0].replace(',', ''))
        else:
            self.__answer = 'Введен неверный регион!'
            return self.__answer


app = FastAPI()


@app.on_event("startup")
async def start_consuming():
    # asyncio.create_task(...)
    pass


@app.get("/add/{region}")
def read_item(region: str, query: Optional[str] = None):
    a = Requester()
    a.prepare_request(region=region, query=query)
    answer = a.make_request(params={'q':query})
    parser = Parser(answer)
    parser.prepare_to_parse()
    count = parser.parse()
    return {"id": None, "count": count, "timestamp": datetime.now().timestamp()}


if __name__ == '__main__':
    # uvicorn.run("main:app", host="127.0.0.1", port=5000, log_level="info")
    pass