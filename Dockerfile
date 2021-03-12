
FROM alpine:3.7
RUN apk add --no-cache python3 py3-pip

# Temporarily install files for Python C extension compiles.
RUN apk add --no-cache --virtual .build-deps python3-dev gcc musl-dev

# Copy app files.
COPY . /app/
WORKDIR /app/
RUN pip3 install --upgrade pip
RUN pip3 install .

COPY "smtputt/config/smtputt.ini.dist" "/etc/smtputt.ini"

# Remove temporarily installed files.
RUN apk del .build-deps

ENV SERVER_AUTHMODULES ""
ENV SERVER_AUTHREQUIRED "false"
ENV AUTH_LDAP_URL ""
ENV AUTH_LDAP_DNFORMAT ""
ENV RELAY_SMTP_URL ""

EXPOSE 25

CMD python3 -m smtputt \
    -o server authmodules ${SERVER_AUTHMODULES} \
    -o server authrequired ${SERVER_AUTHREQUIRED} \
    -o smtputt.authorization.ldap ldapurl ${AUTH_LDAP_URL} \
    -o smtputt.authorization.ldap ldapdnformat ${AUTH_LDAP_DNFORMAT} \
    -o smtputt.relays.smtp smtpurl ${RELAY_SMTP_URL}
