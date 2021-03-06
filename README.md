# SMTPutt

## Installation

### Windows (as a Service)

* pip install pywin32
* [path to python dir]\scripts\pywin32_postinstall.py -install
* [path to smtputt] python smtputtsvc.py install

## Configuration

Configuration is stored in an ini file, with the following sections:

### \[relay\]

* remoteserver
  Address of the relay server SMTPutt should forward received messages to.
* remoteport (optional, default 25)
  SMTP port on the remote server.
* remoteuser (optional)
  Username used to login to the remote server.
* remotepassword (optional)
  Password used to login to the remote server.
* remotessl (optional, default false)
  "true" if TLS should be used to login to the remote server, otherwise "false".

### \[server\]

* listenhost (optional, default 0.0.0.0)
  Local address on which SMTPutt should listen for incoming messages.
* listenport (optional, default 25)
  Local port on which SMTPutt should listen for incoming messages.
* authmodule (optional)
  Module path for the module used to authorize sending mail through the SMTPutt relay.
* authrequired (optional, default False)
  Whether authorization is required to send mail through the SMTPutt relay.
* mynetworks (optional, default 127.0.0.1)
  A comma-separated list of network addresses (in CIDR form e.g. 0.0.0.0/0) from which the server should accept mail.

### \[fixer\]

* fromaddress (optional)
  E-mail address which should replace the From: address on messages forwarded through SMTPutt.

## Authorizers

The following are authorizers that may be specified in the authmodule= line in the configuration file.

Configuration options for authorizers should be placed in the \[server\] section.

### smtputt.authorizers.ldap

### smtputt.authorizers.dictauth

This authorizer compares the username and password to a static dictionary provided in the configuration.

#### Configuration

* authdict
  Dictionary of users in the format user1:password1,user2:password2
