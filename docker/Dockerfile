# Preparing node App
FROM ubuntu 
FROM python:3.7

RUN apt-get update
RUN apt-get upgrade -y
RUN apt-get install nodejs -y 
RUN apt-get install npm -y
RUN apt-get install apt-utils -y
RUN curl -sSL https://raw.githubusercontent.com/python-poetry/poetry/master/get-poetry.py | python3

# Disables pip caching
ENV PIP_NO_CACHE_DIR=false

# Install poetry and configure to not use a virtualenv
RUN python3 -m pip install poetry
RUN poetry config virtualenvs.create false

WORKDIR /usr/src/app

# Copy pyproject.toml
COPY ./pyproject.toml .

# Copy python script
COPY ./covid19count.py .
COPY ./poetry.lock .

# Copy Web GUI stuff
COPY ./docker/node/html/index.html .
COPY ./docker/node/*.js ./

# Install dependencies (including dev dependencies)
RUN python3 -m poetry install --no-root

RUN python3 covid19count.py listregions --outfile=regions.txt
RUN python3 covid19count.py plot sweden denmark norway finland --outfile=output.png

# Expose port 8080
EXPOSE 8080

CMD ["node", "app.js"]
