.PHONY: clean start test crawl crawl-proxy

TAG=$(shell git symbolic-ref -q --short HEAD)

all: env/bin/python

env/bin/python:
	virtualenv env -p python3.6 --no-site-packages
	env/bin/pip install --upgrade pip
	env/bin/pip install wheel
	env/bin/pip install -r requirements.txt

crawl: env/bin/python
	env/bin/scrapy crawl --loglevel=INFO MetroLyrics.com

crawl-proxy: env/bin/python
	http_proxy=http://localhost:20020 env/bin/scrapy crawl --loglevel=INFO MetroLyrics.com

clean:
	rm -rfv bin develop-eggs dist downloads eggs env parts .cache .scannerwork
	rm -fv .DS_Store .coverage .installed.cfg bootstrap.py .coverage
	find . -name '*.pyc' -exec rm -fv {} \;
	find . -name '*.pyo' -exec rm -fv {} \;
	find . -depth -name '*.egg-info' -exec rm -rfv {} \;
	find . -depth -name '__pycache__' -exec rm -rfv {} \;
