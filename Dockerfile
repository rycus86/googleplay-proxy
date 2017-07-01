FROM alpine

RUN apk add --no-cache python py2-pip git ca-certificates

ADD requirements.txt /tmp/requirements.txt
RUN pip install -r /tmp/requirements.txt

RUN adduser -S webapp
USER webapp

ADD src /app
WORKDIR /app

CMD [ "python", "app.py" ]
