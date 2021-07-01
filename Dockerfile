FROM python:3.8

RUN apt-get update

RUN apt-get -y install git

WORKDIR /tsuserver3cc-musicautoscan/OLEAO-ServerCC/

COPY requirements.txt start_server.py ./
RUN apt-get -y install gcc
RUN apt-get -y install musl-dev
RUN pip install --upgrade pip
RUN pip install -r requirements.txt
RUN pip install ffprobe3
RUN pip install ffprobe
RUN pip install ffmpeg-python
RUN pip install ffmpeg

COPY server/ server/
COPY migrations/ migrations/
COPY characters/ characters/
COPY config/ config/
COPY base/sounds/music/ base/sounds/music/
COPY /usr/local/lib/python3.8/dist-packages/ffprobe/ ./ffprobe/

CMD python ./start_server.py -s

