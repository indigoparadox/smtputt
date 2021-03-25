
FROM alpine:3.13
RUN apk add --no-cache python3 py3-pip

# Temporarily install files for Python C extension compiles.
RUN apk add --no-cache --virtual .build-deps python3-dev gcc musl-dev

# Copy app files.
COPY . /app/
WORKDIR /app/
RUN pip3 install --upgrade pip
RUN pip3 install .

# Remove temporarily installed files.
RUN apk del .build-deps

ENV SMTPUTT_CONFIG_PATH "/config/smtputt.ini"

EXPOSE 25

CMD python3 -m smtputt -c ${SMTPUTT_CONFIG_PATH}
