# SMTPutt

## Installation

### Windows (as a Service)

* pip install pywin32
* [path to python dir]\scripts\pywin32_postinstall.py -install
* [path to smtputt] python smtputtsvc.py install

## Configuration

Configuration is stored in an ini file, with the following sections:

### \[server\]

* listenhost (optional, default 0.0.0.0)
  Local address on which SMTPutt should listen for incoming messages.
* listenport (optional, default 25)
  Local port on which SMTPutt should listen for incoming messages.
* fixermodules (optional)
  Module paths for modules which will be applied to "fix" any mail passing through the SMTPutt relay.
* relaymodules (optional)
  Modules which will be used to relay incoming mail. SMTPutt is rather useless without any relay modules.
* authmodules (optional)
  Module paths for modules used to authorize sending mail through the SMTPutt relay. Modules will be tried in order until one succeeds.
* authrequired (optional, default False)
  Whether authorization is required to send mail through the SMTPutt relay.
* mynetworks (optional, default 127.0.0.1)
  A comma-separated list of network addresses (in CIDR form e.g. 0.0.0.0/0) from which the server should accept mail.

Individual module configurations should be placed in the ini file under a section named for their module path. e.g. configuration for smtputt.authorizers.ldap should go in a section named \[smtputt.authorizers.ldap\].

## Authorizers

The following are authorizers that may be specified in the authmodule= line in the configuration file.

### smtputt.authorizers.ldap

This authorizer attempts to simply bind to an LDAP server provided with the credentials provided to the SMTP server.

#### Configuration

* ldaphost
  Hostname of the LDAP server to validate against.

* ldapport (optional)
  Port to connect to said LDAP server on.

* ldapdnformat
  DN format to use for usernames to bind to LDAP server. %u is replaced with the username provided to the SMTP server.

* ldapssl (optional, default false)
  'true' if TLS should be used to connect to LDAP server, otherwise 'false'.

### smtputt.authorizers.dictauth

This authorizer compares the username and password to a static dictionary provided in the configuration.

#### Configuration

* authdict
  Dictionary of users in the format user1:password1,user2:password2

## Relays

### smtputt.relays.smtp

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

## Fixers

### smtputt.fixers.fromdate

#### Configuration

* fromdate

### smtputt.fixers.fromaddress

#### Configuration

* fromaddress
  E-mail address which should replace the From: address on messages forwarded through SMTPutt.
