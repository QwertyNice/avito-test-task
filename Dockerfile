FROM python:3.8
WORKDIR /code
EXPOSE 8000
COPY avito-test-task /code
RUN pip3 install -r requirements.txt
CMD ["uvicorn", "main:app", "--reload"]