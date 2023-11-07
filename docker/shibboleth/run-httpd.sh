#!/bin/bash

# Start Shibboleth in the foreground
./usr/sbin/shibd

# Start Apache in the foreground
exec /usr/sbin/httpd -D FOREGROUND

