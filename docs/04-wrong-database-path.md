# INC-004 — API Using Incorrect Database File

## Incident Summary

The Troubleshooting Lab website returned an HTTP 500 Internal Server Error even though both the frontend and API services were running.

The API health endpoint returned HTTP 200, but the `/users` endpoint returned HTTP 500.

Investigation showed that the API was configured to connect to the wrong SQLite database file.

SQLite automatically created the missing database file, allowing the database connection itself to succeed. However, the newly created database was empty and did not contain the expected `users` table.

---

## Business Impact

Users could reach the application, but user data could not be displayed.

The application appeared to be online because the frontend and API processes were running, but functionality that depended on the database was unavailable.

---

## Reported Symptoms

The main website returned:

>
   Frontend error: HTTP Error 500: INTERNAL SERVER ERROR


Throught Browser's Inspect, at Network Tab and by entering localhost Headers the following clues where given in Request URL field:

Request Method: GET
Status Code: 500 Internal Server Error
Remote Address: 127.0.0.1:8000

## Investigation

1. Checked Running Services

'''bash
ss -ltnp | grep -E '5000|8000'

>
  LISTEN 0      5          127.0.0.1:8000      0.0.0.0:*    users:(("python3",pid=1622,fd=3))
  LISTEN 0      128          0.0.0.0:5000      0.0.0.0:*    users:(("python",pid=1607,fd=3))

Both applications were listening.

'''bash
pgrep -af python

>

   117 /usr/bin/python3 /usr/bin/networkd-dispatcher --run-startup-triggers
   266 /usr/bin/python3 /usr/share/unattended-upgrades/unattended-upgrade-shutdown --wait-for-signal
   1607 python app.py
   1622 python3 server.py

Both applications were working.

2. Tested API Health

The API health endpoint was tested directly:

'''bash
curl -i http://localhost:5000/health

>
   HTTP/1.1 200 OK

   {"status":"healthy"}

This confirmed that Flask was running and responding to HTTP requests.

3. Tested the Failing API Endpoint

The /users endpoint was tested directly:

'''bash
curl -i http://localhost:5000/users

>
   HTTP/1.1 500 INTERNAL SERVER ERROR

This isolated the problem to functionality used by /users, rather than the API service as a whole.

4. Inspected the API Error Log

The Flask traceback showed:

> 
   sqlite3.OperationalError: no such table: users

The error occurred while executing:
SELECT id, name, email FROM users

This showed that the request reached the database layer, but the database being accessed did not contain the expected table.

5. Inspected the Database Files

The database directory contained:
app.db          12K
app_missing.db    0

The expected database was checked:
sqlite3 app.db ".tables"

Result:
users

The database being used by the API was then checked:
sqlite3 app_missing.db ".tables"

No tables were returned.
This confirmed that app_missing.db was an empty SQLite database.

## Root Cause

The API database configuration pointed to:

'''Python
DATABASE = Path(__file__).parent.parent / "database" / "app_missing.db"


instead of the correct database:

'''Python
DATABASE = Path(__file__).parent.parent / "database" / "app.db"


Because SQLite can automatically create a database file when the specified file does not exist, the connection did not fail immediately.
Instead, SQLite created an empty app_missing.db.
The API therefore started normally and /health continued to work, but /users failed because the new database did not contain the users table.

## Resolution

The database configuration was restored to:

'''Python
DATABASE = Path(__file__).parent.parent / "database" / "app.db"


The Flask API was restarted.

The accidentally created empty database file was removed:

'''bash
rm database/app_missing.db

## Verification

The API health endpoint was tested:

'''bash
curl -i http://localhost:5000/health

>
   HTTP/1.1 200 OK

The users endpoint was tested:

'''bash
curl -i http://localhost:5000/users

>
   HTTP/1.1 200 OK

The expected user data was returned.

Finally, the frontend was tested:

'''bash
curl -i http://localhost:8000

and verified through the browser.

>
   HTTP/1.1 200 OK

The user list was displayed normally again.

## Preventive Actions

a. Validate database paths during application startup.
b. Log the database file being used by the application.
c. Verify that required tables exist before accepting traffic.
d. Use configuration variables rather than hard-coded database paths in larger deployments.
e. Expand health checks to test critical dependencies when appropriate.
f. Investigate endpoint-specific failures even when a general health endpoint reports the service as healthy.

## Tools Used

a. Browser DevTools
b. curl
c. pgrep
d. ss
e. Linux / WSL
f. Flask logs/traceback
g. sqlite CLI
