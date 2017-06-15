FROM alpine

RUN apk add --no-cache python py2-pip git ca-certificates

ADD src /app
ADD requirements.txt /app

WORKDIR /app

RUN pip install -r requirements.txt

CMD [ "python", "app.py" ]
