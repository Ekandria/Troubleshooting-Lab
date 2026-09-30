# INC-003 — API Service Down

## Incident Summary

The website was reachable, but the frontend returned an HTTP 500 error instead of displaying user data.

The frontend process was running correctly, but its backend API dependency was unavailable.

## Business Impact

Users could access the website, but application data could not be loaded.

In a production environment, this could make the application appear partially available while core functionality remained unusable.

## Reported Symptom

The browser returned:

```text
Frontend error: <urlopen error [Errno 111] Connection refused>
500 Internal Server Error

when opening http://localhost:8000


## Investigation

1. Confirmed through Browser DevTools

In Network Tab, by entering localhost Headers the following clues where given in Request URL field:

Request Method: GET
Status Code: 500 Internal Server Error
Remote Address: 127.0.0.1:8000


2. Confirmed the frontend was reachable

The following command was used:

...bash 
curl -i http://localhost:8000

>
  HTTP/1.0 500 Internal Server Error
  Server: BaseHTTP/0.6 Python/3.14.4

Meaning, the frontend responded on port 8000, which showed that the frontend process itself was running.


3. Checked running Python processes

By finding and filtering the running processes:

...bash
pgrep -af python

> 
  117 /usr/bin/python3 /usr/bin/networkd-dispatcher --run-startup-triggers
  266 /usr/bin/python3 /usr/share/unattended-upgrades/unattended-upgrade-shutdown --wait-for-signal
  459 python3 server.py

The frontend process was present (python3 server.py), but the Flask API process was missing.

4. Checked listening ports

Searching our Network Connections to check which ports are actively open and listening:

'''bash
ss -ltnp | grep -E '5000|8000'

> 
  LISTEN 0      5          127.0.0.1:8000      0.0.0.0:*    users:(("python3",pid=459,fd=3))

This confirmed that the frontend was available but the API was not running.

## Root Cause

The Flask API process had stopped.
Because no application was listening on port 5000, the frontend could not retrieve user data and returned HTTP 500 to the browser.

## Resolution

The Flask configuration was restored to the standard project port:

The API virtual environment was activated:

'''bash
cd /mnt/d/DanuStuff/troubleshooting-lab/api

'''bash
source venv/bin/activate

The Flask API was restarted:

'''bash
python app.py.

## Verification

The API was confirmed to be listening again on port 5000 and its health, along with the frontend:

...bash
curl http://localhost:5000/health

>{"status":"healthy"}

The client received:
HTTP/1.1 200 OK

'''bash
curl -i http://localhost:8000

> All the user data were displayed and the client received:
HTTP/1.0 200 OK

All the aforementioned were also verified through Browser DevTools, after reloading the url:

Request URL: http://localhost:8000/
Request Method: GET
Status Code: 200 OK
Remote Address: 127.0.0.1:8000

## Preventive Actions

a. Monitor critical application processes
b. Use service health checks
c. Verify expected listening ports
d. Configure production services to restart automatically after failure
e. Check dependent services when a frontend returns HTTP 500

## Tools Used

a. Browser DevTools
b. curl
c. pgrep
d. ss
e. Linux / WSL
f. Flask
