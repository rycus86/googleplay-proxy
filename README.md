# Google Play Proxy

A simple `Python` [Flask](http://flask.pocoo.org) *REST* server to proxy calls to the *Google Play Store*.

[![Build Status](https://travis-ci.org/rycus86/googleplay-proxy.svg?branch=master)](https://travis-ci.org/rycus86/googleplay-proxy)
[![Build Status](https://img.shields.io/docker/build/rycus86/googleplay-proxy.svg)](https://hub.docker.com/r/rycus86/googleplay-proxy)
[![Coverage Status](https://coveralls.io/repos/github/rycus86/googleplay-proxy/badge.svg?branch=master)](https://coveralls.io/github/rycus86/googleplay-proxy?branch=master)
[![Code Climate](https://codeclimate.com/github/rycus86/googleplay-proxy/badges/gpa.svg)](https://codeclimate.com/github/rycus86/googleplay-proxy)

## Usage

The API is implemented using [googleplay-api](https://github.com/NeroBurner/googleplay-api)
and supports these environment variables:

- `GOOGLE_USERNAME`: a valid *Google* username
- `GOOGLE_PASSWORD`: password for the same *Google* account
- `ANDROID_ID`: a valid *Google Service Framework (GSF)* ID  
  *You can find it using the [Device ID app](https://play.google.com/store/apps/details?id=com.evozi.deviceid) for example*
- `MAX_LOGIN_RETRIES`: the maximum number of retries when login fails  
  *Login can be quite flaky*

To get a reference to the `ApiClient` class use something like:
```python
api = ApiClient(android_id=os.environ.get('ANDROID_ID'),
                username=os.environ.get('GOOGLE_USERNAME'),
                password=os.environ.get('GOOGLE_PASSWORD'),
                max_login_retries=int(os.environ.get('MAX_LOGIN_RETRIES', '10')))
```

The `api.ApiClient` class wraps remote calls with the following methods:

- `login()`:
  Executes the login (with retries) and caches the authentication token for following calls.
- `search(package_prefix)`:
  Searches for applications using `package_prefix` and filters the result list to
  only include apps whose package name starts with that prefix.
- `get_details(package_name)`:
  Returns the details of the application whose package is `package_name`.

The `app` module is responsible for the *REST* presentation layer exposing *JSON* endpoints.
The exposed endpoints are cached using [Flask-Cache](https://pythonhosted.org/Flask-Cache).

Instead of the API a *scraper* can also be used (without authentication)
by setting the `API_TYPE` environment variable to `scraper`.

Programmatically:
```python
api = Scraper(cache_max_age=int(os.environ.get('MAX_CACHE_AGE', 24 * 60 * 60)))
```

The exposed methods are similar to the `ApiClient` class methods:

- `search(package_prefix)`:
  Searches for applications using `package_prefix` and filters the result list to
  only include apps whose package name starts with that prefix.
- `developer(developer_name)`:
  Searches for applications developed by `developer_name`.
  Returns results in the same format as `search`.
- `get_details(package_name)`:
  Returns the details of the application whose package is `package_name`.


Configuration options:

- `HTTP_HOST`: the host (interface) for *Flask* to bind to (default: `127.0.0.1`)
- `HTTP_PORT`: the port to bind to (default: `5000`)
- `CORS_ORIGINS`: comma separated list of *origins* to allow *cross-domain* `GET` requests from
  (default: `http://localhost:?.*`)

To allow connections from other hosts apart from `localhost` set the `HTTP_PORT` environment
variable to `0.0.0.0` or as appropriate.

List of endpoints:

- `/search/<package_prefix>`:
  returns a list of application details whose package starts with the given prefix
- `/developer/<developer_name>`:
  returns a list of application details created by the given developer
- `/details/<package_name>`:
  returns the details of the application with the given package name

## Docker

The web application is built as a *Docker* image too based on *Alpine Linux*
for 3 architectures with the following tags:

- `latest`: for *x86* hosts  
  [![Layers](https://images.microbadger.com/badges/image/rycus86/googleplay-proxy.svg)](https://microbadger.com/images/rycus86/googleplay-proxy "Get your own image badge on microbadger.com")
- `armhf`: for *32-bits ARM* hosts  
  [![Layers](https://images.microbadger.com/badges/image/rycus86/googleplay-proxy:armhf.svg)](https://microbadger.com/images/rycus86/googleplay-proxy:armhf "Get your own image badge on microbadger.com")
- `aarch64`: for *64-bits ARM* hosts  
  [![Layers](https://images.microbadger.com/badges/image/rycus86/googleplay-proxy:aarch64.svg)](https://microbadger.com/images/rycus86/googleplay-proxy:aarch64 "Get your own image badge on microbadger.com")

`latest` is auto-built on [Docker Hub](https://hub.docker.com/r/rycus86/googleplay-proxy)
while the *ARM* builds are uploaded from [Travis](https://travis-ci.org/rycus86/googleplay-proxy).

To run it:
```shell
docker run -d --name="googleplay-proxy" -p 5000:5000                       \
  -e GOOGLE_USERNAME='user' -e GOOGLE_PASSWORD='pass' -e ANDROID_ID='aid'  \
  -e CORS_ORIGINS='http://site.example.com,*.website.com'                  \
  rycus86/googleplay-proxy:latest
```

Or to scrape:
```shell
docker run -d --name="googleplay-proxy" -p 5000:5000                       \
  -e API_TYPE=scrape                                                       \
  -e CORS_ORIGINS='http://site.example.com,*.website.com'                  \
  rycus86/googleplay-proxy:latest
```

Or with *docker-compose* (for a *Raspberry Pi* for example):
```yaml
version: '2'
services:

  googleplay-proxy:
    image: rycus86/googleplay-proxy:armhf
    read_only: true
    expose:
      - "5000"
    restart: always
    environment:
      - HTTP_HOST=0.0.0.0
    env_file:
      - googleplay-secrets.env
```

This way you can keep the secrets in the `env_file` instead of passing them to the *Docker*
client from the command line.
