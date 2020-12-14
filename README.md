## Requirements

* Python 3.8
* MySQL server 8.0
* <a href="https://fastapi.tiangolo.com/">FastApi</a>
* <a href="https://lxml.de/">lxml</a>
* <a href="https://dev.mysql.com/doc/connector-python/en/">mysql-connector-python</a>
* <a href="https://requests.readthedocs.io/en/master/">requests</a>
* <a href="https://www.uvicorn.org/">Uvicorn</a>

## Installation and run

* If you already have <a href="https://dev.mysql.com/doc/refman/8.0/en/">MySQL server</a> and don't want to use <a href="https://www.docker.com/">Docker</a> do the following steps:

Clone the repository from GitHub. Then create a virtual environment, and install all the dependencies.
```console
$ git clone https://github.com/QwertyNice/avito-test-task.git
$ python3 -m venv env
$ source env/bin/activate
$ cd avito-test-task/avito-test-task/
$ python -m pip install -r requirements.txt
$ uvicorn main:app --reload

---> 100%
```

* If you already have <a href="https://dev.mysql.com/doc/refman/8.0/en/">MySQL server</a> and <a href="https://www.docker.com/">Docker</a> do the following steps:

Clone the repository from GitHub. Then build image with docker command.
```console
$ git clone https://github.com/QwertyNice/avito-test-task.git
$ cd avito-test-task/
$ docker build -t web_api_image .
$ docker run -d --name web_api_container -p 8000:8000 --network=host web_api_image

---> 100%
```

* If you don't have <a href="https://dev.mysql.com/doc/refman/8.0/en/">MySQL server</a> and have <a href="https://www.docker.com/">Docker</a> do the following steps:

Clone the repository from GitHub. Then build images with docker-compose command.
```console
$ git clone https://github.com/QwertyNice/avito-test-task.git
$ cd avito-test-task/
$ docker-compose up -d

---> 100%
```

## Example

Imagine you want to add region `Moscow` and query `Car`.
Open your browser at <a href="http://127.0.0.1:8000/add/moskva?query=car">http://127.0.0.1:8000/add/moskva?query=car</a>.

You will see the JSON response as:

```JSON
{"id": 1}
```

If you want to check number of advertisement for query `Car` and region `Moscow` (with id=1) after a while, open your browser at <a href="http://127.0.0.1:8000/stat/1">http://127.0.0.1:8000/stat/1</a>.
If you want to check for time period between `16:20:45 14.12.2020` and `14:40:11 15.12.2020`, open your browser at <a href="http://127.0.0.1:8000/stat/1?start=2020-12-14T16:20:45&end=2020-12-15T14:40:11">http://127.0.0.1:8000/stat/1?start=2020-12-14T16:20:45&end=2020-12-15T14:40:11</a> or use corresponding timestamps.

You will see the JSON response as:

```JSON
{"id": 1, "timestamp": [123456789.0, 12345999.2], "count": [56907, 56992]}
```


