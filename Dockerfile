FROM  python:3.11-alpine3.18

WORKDIR ./api

COPY ../../../../../../Desktop .

RUN pip install flask

EXPOSE 5105

CMD ["python3", "api.py"]

