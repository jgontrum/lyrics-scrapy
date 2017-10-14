FROM python:3.6
MAINTAINER Johannes Gontrum <gontrum@me.com>

RUN pip install virtualenv

COPY . /app
RUN cd /app && make clean && make

CMD ["bash", "-c", "cd /app && make crawl-proxy"]
