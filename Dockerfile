FROM python:3.7-alpine

RUN apk --no-cache add git

WORKDIR ./

COPY requirements.txt start_server.py ./
RUN apk --no-cache add gcc musl-dev
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

COPY server/ server/
COPY migrations/ migrations/
COPY characters/ characters/

CMD python ./start_server.py -s

