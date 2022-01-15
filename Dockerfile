FROM python:3

WORKDIR /usr/src/app

RUN pip3 install requests
RUN pip3 install datetime
RUN pip3 install pytelegrambotapi
RUN pip3 install pymongo


COPY config.py  ./
COPY logs ./
COPY main.py ./
COPY message_vars.py ./
COPY mongo_func.py ./

CMD [ "python3", "./main.py" ]

