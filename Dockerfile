FROM python:3.7-alpine AS python

RUN apk --no-cache add git

WORKDIR /tsuserver3cc-musicautoscan/OLEAO-ServerCC/

COPY requirements.txt start_server.py ./
RUN apk --no-cache add gcc musl-dev
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

COPY --from=mwader/static-ffmpeg:4.1.4-2 /ffmpeg /ffprobe /usr/local/bin/
COPY server/ server/
COPY migrations/ migrations/
COPY characters/ characters/
COPY config/ config/
COPY base/sounds/music/ base/sounds/music/

CMD ffmpeg
CMD ffprobe 
CMD python ./start_server.py -s