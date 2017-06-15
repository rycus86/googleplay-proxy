FROM alpine

RUN apk add --no-cache python py2-pip ca-certificates

ADD src/main /app
ADD requirements.txt /app

WORKDIR /app

RUN pip install -r requirements.txt

CMD [ "python", "app.py" ]
