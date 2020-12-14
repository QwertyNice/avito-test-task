from typing import Optional, Union, Type
from lxml.html import fromstring, HtmlElement
import requests


class Requester:
    """Class for getting the source code of the page.

    This class sends a request to the Avito website (https://www.avito.ru/) 
    with region and query. It contains the attributes, which are listed below.

    Parameters
    ----------
    region : str
        Russian region for advertisement search.
    params : dict, optional
        Additional parameters for searching request.

    Attributes
    ----------
    answer : str
        Source code of the page as a text.
    _raw_url : str
        The Avito URL without any parameters.
    _url : str
        The Avito URL with required attribute `region`.

    Note
    ----
    1) Make sure you entered the correct region. For example "moscow" -
       - incorrect, "moskva" - correct;
    2) `q` is only parameter in `params` for this class.

    """

    def __init__(self, region: str, params: Optional[dict] = None):
        self._raw_url = 'https://www.avito.ru/{}'
        self._url = self._prepare_request(region=region)
        self.answer = self._make_request(params=params)

    def _prepare_request(self, region: str) -> str:
        """Prepares URL for the request by inserting the attributes below.

        Parameters
        ----------
        region : str
            Russian region for advertisement search.

        Returns
        -------
        str
            The URL prepared for parsing.

        """

        return self._raw_url.format(region)

    def _make_request(self, params: Optional[dict] = None) -> str:
        """Makes the request wuth parameters below.

        Parameters
        ----------
        params : dict, opional
            Additional parameters for searching request.

        Returns
        -------
        str
            Source code of the page as a text.
        
        """

        return requests.get(self._url, params=params).text


class Parser:
    """Class for pasrsing the source code and getting the number of 
    advertisement.

    This class performs some preparations before parsing. First, the validity 
    of the entered region is checked, if successful, then the validity of the 
    entered query is checked.   It contains the attributes, which are listed 
    below.

    Parameters
    ----------
    raw_answer : str
        Source code of the page as a text.
    query : str, optional
        Query which we are looking for the number of advertisement.
    skip_check : bool, optional
        A flag used to parse source code without checking validity (default 
        is False)

    Attributes
    ----------
    raw_answer : str
        Source code of the page as a text.
    error : str, optional
        If the region or query is entered incorrectly, then this attribute 
        contains the error message text, otherwise None.
    valid_region : bool
        If this attribute is true, then the region is entered correctly.
    query : str, optional
        Correct existing query in avito page.

    Note
    ----
    If `query` is not passed (is None), then this class will parse all 
    advertisement in this region.
    """

    def __init__(self, raw_answer: str, query: Optional[str] = None, 
                 skip_check: bool = False):
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

    def _prepare_to_parse(self) -> Type[HtmlElement]:
        """Converts the page source code into HtmlElement tree.

        Returns
        -------
        type[HtmlElement]
            Source code HtmlElement tree.
        
        """

        return fromstring(self.raw_answer)

    def _check_valid_region(self) -> bool:
        """Checks if the user entered the correct region.

        Returns
        -------
        bool
            True if region is correct, False otherwise.
        
        """

        answer = self.__tree.xpath('//div[@class="b-404"]/h1/text()')
        if answer:
            self.error = "Invalid region is entered"
        return not answer

    def _check_valid_query(self, q: Optional[str] = None) -> bool:
        """Checks if the user entered the correct query.

        Parameters
        ----------
        q : str, optional
            Query which we are looking for the number of advertisement.

        Returns
        -------
        bool
            True if query is correct, False otherwise.
        
        """

        return self.parse_count(q=q) != 0

    def parse_count(self, q: Optional[str] = None) -> int:
        """Parses the source code HtmlElement tree and gets a number of adv

        Parameters
        ----------
        q : str, optional
            Query which we are looking for the number of advertisement.

        Returns
        -------
        int
            The number of advertisement.
        
        """

        if q:
            count = self.__tree.xpath(
                '//span[starts-with(@class, "page-title-count")]/text()')
            if count:
                count = int(count[0].replace(' ', ''))
            else:
                count = 0
                self.error = "Invalid query is entered or the number of " \
                             "advertisement is zero"
            return count
        
        else:
            count = self.__tree.xpath(
                '//span[starts-with(@class, "category-with-counters-count")]/text()')
            count = int(count[0].replace(',', ''))
            return count

    def _correct_mistake_in_query(self, 
                                  q: Optional[str] = None) -> Optional[str]:
        """Corrects errors in the query, if they exist.

        Parameters
        ----------
        q : str, optional
            Query which we are looking for the number of advertisement.

        Returns
        -------
        str, optional
            The syntax corrected query.
        
        """
        
        if q:
            q = self.__tree.xpath('//div[starts-with(@class, ' \
                '"index-suggest-")]/input/@value')
            if q:
                q = q[0]
            else:
                q = self.__tree.xpath('//div[starts-with(@class, "category-' \
                    'select-select")]/select/option[@selected]/text()')[0]
        return q