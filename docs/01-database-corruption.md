# INC-001 — SQLite Database Corruption

## Incident Summary

The application's SQLite database became unreadable when attempting to access the `users` table.

The database structure could still be partially inspected, but normal queries returned a corruption error.

## Business Impact

The application could not reliably retrieve user records.

In a customer-facing application, this could cause missing data, application errors, or unavailable functionality.

## Reported Symptom

The following query failed:

```bash
sqlite3 app.db "SELECT COUNT(*) FROM users;"


> Error: stepping, database disk image is malformed (11)

## Investigation

1. Preserved the original database

Before attempting repairs, a backup was created:

...bash
cp app.db app_corrupt_backup.db

This allowed troubleshooting to continue without modifying the only copy of the damaged database.


2. Confirmed SQLite could still read database metadata

The file was checked with:

...bash
file app.db
sqlite3 app.db ".dbinfo"

SQLite recognized the file and could read database metadata.


The users table structure was also partially accessible:

...bash
sqlite3 app.db "PRAGMA table_info(users);"

However, attempting to read table rows still produced:

>database disk image is malformed


3. Attempted standard SQLite recovery

SQLite's built-in recovery command was tested:

...bash
sqlite3 app.db ".recover" > recovered.sql
sqlite3 recovered.db < recovered.sql

The recovered database passed:

...bash
sqlite3 recovered.db "PRAGMA integrity_check;"

>ok

However, no user records were recovered.


4. Inspected the database pages

The database file was inspected using xxd:

...bash
xxd -s 4096 -l 256 app.db
xxd -s 8192 -l 256 app.db

The investigation showed that the page assigned to the unique email index contained an incorrect SQLite B-tree page type.
A separate working copy was created before attempting a repair.

## Root Cause

An internal SQLite index page contained an invalid page type. More specifically page 3 was supposed to be an index leaf page, not a table leaf page.
This caused SQLite to report the database as malformed when attempting to access the users table.

## Resolution

The repair was tested on a copy of the database rather than the original, which was create with the following method:

...bash
cp app.db app_test.db

Then, some changes had to be made to that copy, in oreder to be the final, correct database.

First, we removed the extra trailing bytes:

...bash
truncate -s 12288 app_test.db

After the xxd inspection, the database reported:

page size = 4096 bytes
page count = 3

So:
4096 × 3 = 12288 bytes


Then we corrected the first byte of page 3, that tells SQLite what kind of B-tree page it is.

...bash
printf '\x0a' | dd of=app_test.db bs=1 seek=8192 count=1 conv=notrunc

## Verification

The repaired database passed:

...bash
sqlite3 app_test.db "PRAGMA integrity_check;"

>ok

The table could then be queried successfully:

...bash
sqlite3 app_test.db "SELECT COUNT(*) FROM users;"

The corruption error was no longer present.
Test records were subsequently inserted and retrieved successfully, confirming that both reads and writes were working.

The original damaged database did not yield recoverable user rows through SQLite's .recover command.
For the lab environment, the database structure was restored and test data was recreated.

## Preventive Actions

a. Keep regular database backups
b. Never perform experimental repairs on the only copy of a database
c. Test repairs on a duplicate file
d. Verify database integrity after recovery
e. Investigate filesystem or storage problems if unexplained corruption occurs.

## Tools Used

a. SQLite CLI
b. file
c. xxd
d. cp
e. truncate
f. Linux / WSL
