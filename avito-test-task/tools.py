from lxml.html import fromstring
import requests


class Requester:

    def __init__(self):
        self.row_url = 'https://www.avito.ru/{}'

    def prepare_request(self, region):
        self.url = self.row_url.format(region)

    def make_request(self, params=None):
        return requests.get(self.url, params=params).text


class Parser:

    def __init__(self, raw_answer, query, skip_check=False):
        self.raw_answer = raw_answer
        self.__tree = self._prepare_to_parse()
        if not skip_check:
            self.error = None
            self.valid_region = self._check_valid_region()
            if self.valid_region:
                if self._check_valid_query(q=query):
                    self.query = self._correct_mistake_in_query(q=query)
        else:
            self.query = query

    def _prepare_to_parse(self):
        """Функция преобразовывает код страницы в дерево"""
        return fromstring(self.raw_answer)

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

    def _correct_mistake_in_query(self, q):
        """Функция исправляет ошибки в запросе, если они есть"""
        if q:
            q = self.__tree.xpath('//div[starts-with(@class, "index-suggest-")]/input/@value')[0]
        return q