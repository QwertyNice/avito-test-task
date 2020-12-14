## Requirements

Python 3.8
MySQL server 8.0

* <a href="https://fastapi.tiangolo.com/">FastApi</a>
* <a href="https://lxml.de/">lxml</a>
* <a href="https://dev.mysql.com/doc/connector-python/en/">mysql-connector-python</a>
* <a href="https://requests.readthedocs.io/en/master/">requests</a>
* <a href="https://www.uvicorn.org/">Uvicorn</a>

## Installation

If you already have <a href="https://dev.mysql.com/doc/refman/8.0/en/">MySQL server</a> and don't want to use <a href="https://www.docker.com/">Docker</a> do the following steps:

Clone the repository from GitHub. Then create a virtual environment, and install all the dependencies.
```console
git clone https://github.com/QwertyNice/avito-test-task.git
python3 -m venv env
source env/bin/activate
cd avito-test-task/
python -m pip install -r requirements.txt

---> 100%
```