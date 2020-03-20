# Preparing node App
FROM ubuntu 
FROM python:3.7

RUN apt-get update
RUN apt-get upgrade -y
RUN apt-get install nodejs -y 
RUN apt-get install npm -y
RUN apt-get install apt-utils -y
RUN curl -sSL https://raw.githubusercontent.com/python-poetry/poetry/master/get-poetry.py | python3

WORKDIR /usr/src/app

# Copy pyproject.toml
COPY ./pyproject.toml .

# Copy python script
COPY ./covid19count.py .
COPY ./avaiableRegions.py .
COPY ./poetry.lock .

# Copy Web GUI stuff
COPY ./docker/node/html/index.html .
COPY ./docker/node/*.js ./

EXPOSE 8080

RUN poetry install .
RUN poetry shell .

RUN python3 save_regions.py
RUN python3 covid19count.py sweden denmark norway finland

CMD ["node", "app.js"]
