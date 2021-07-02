# Response Cache API

Cache responses from different API servers using Redis. Possible authentication by api key.

## Requirements

* python >=3.7

## Installation

Install using pip:

```shell
pip install -r requirements.txt
```

## Configuration

You must complete the connection to Redis in *.env* and optionally add api keys.

## Usage

To cache response just "GET" the address of your script installation:

```
http://domain.tld/api/v1/cache?api_key=key1&ttl=0&url=http://httpbin.org/delay/1
```

default `ttl` = 0 is no cache, -1 is forever ttl, >0 is ttl in seconds<br/>
`api_key` is optional, not required if not set in a config<br/>
`url` must be correct http/https url

There are 3 ways to use the api key, with a parameter in the query, with the header and with a cookie.

An automatic documentation can be found at `http://domain.tld/docs` where `domain.tld`is the address where the script is
installed.

You can also make POST form requests. All data from POST goes to the page being requested.

I use [uvicorn](https://www.uvicorn.org/) to run the application, but you can use any other ASGI server. <br />
Below are some examples of the commands I use.

### Production

```shell
uvicorn main:app --env-file ".env" --host 127.0.0.1 --port 8000 --workers 2 --no-access-log --proxy-headers
```

### Development

```shell
uvicorn main:app --reload --env-file ".env"
```