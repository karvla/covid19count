# Preparing node App
FROM ubuntu 
FROM python:3.7

RUN apt-get update
RUN apt-get upgrade -y
RUN apt-get install nodejs -y 
RUN apt-get install npm -y
RUN apt-get install apt-utils -y

WORKDIR /usr/src/app

# Copy pyproject.toml
COPY ./pyproject.toml .

# Copy python script
COPY ./covid19count.py .
COPY ./avaiableRegions.py .

# Copy Web GUI stuff
COPY ./docker/node/html/index.html .
COPY ./docker/node/*.js ./

EXPOSE 8080

RUN pip3 install .

RUN python3 avaiableRegions.py
RUN python3 covid19count.py sweden denmark norway finland

CMD ["node", "app.js"]