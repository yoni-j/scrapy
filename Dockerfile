# Use the official Python image.
# https://hub.docker.com/_/python
FROM --platform=linux/amd64 python:3.11-buster

# Install manually all the missing libraries
RUN apt-get update && \
    apt-get install -y gconf-service libasound2 libatk1.0-0 libcairo2 libcups2 libfontconfig1 libgdk-pixbuf2.0-0 libgtk-3-0 libnspr4 libpango-1.0-0 libxss1 fonts-liberation libappindicator1 libnss3 lsb-release xdg-utils && \
    rm -rf /var/lib/apt/lists/*

# Install ChromeDriver using chromedriver-autoinstaller
RUN wget -q -O - https://dl-ssl.google.com/linux/linux_signing_key.pub | apt-key add -

RUN sh -c 'echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" >>
/etc/apt/sources.list.d/google-chrome.list'

RUN apt-get -y update

RUN apt-get install -y google-chrome-stable

# install chromedriver

RUN apt-get install -yqq unzip

RUN wget -O /tmp/chromedriver.zip http://chromedriver.storage.googleapis.com/`curl -sS
chromedriver.storage.googleapis.com/LATEST_RELEASE`/chromedriver_linux64.zip

RUN unzip /tmp/chromedriver.zip chromedriver -d /usr/local/bin/

# set display port to avoid crash

ENV DISPLAY=:99

# Set up the working directory
WORKDIR /app

# Copy only the files needed for installing dependencies
COPY /src/requirements.txt .

# Install Python dependencies with pip
RUN pip install --no-cache-dir -r requirements.txt

COPY /src .

# Install gunicorn
RUN pip install gunicorn

# Run the web service on container startup. Here we use the gunicorn
# webserver, with one worker process and 8 threads.
# For environments with multiple CPU cores, increase the number of workers
# to be equal to the cores available.
CMD exec gunicorn --bind :8080 --workers 1 --threads 8 main:app