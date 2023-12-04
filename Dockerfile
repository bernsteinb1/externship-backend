FROM  python:3.11-alpine3.18

WORKDIR ./api

COPY . .

RUN pip install flask
RUN pip install Flask-CORS

EXPOSE 80

CMD ["python3", "api.py"]

