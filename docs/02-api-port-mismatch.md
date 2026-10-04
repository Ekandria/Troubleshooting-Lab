# INC-002 — API Port Mismatch

## Incident Summary

The API appeared unavailable when the client attempted to connect to the expected port.

The API process itself was running, but Flask had been configured to listen on port `5001` instead of the expected port `5000`.

## Business Impact

The client could not communicate with the API.

In a customer-facing application, this could cause the website to load without data or make backend functionality appear unavailable.

## Reported Symptom

The client attempted:

</> bash

```curl http://localhost:5000/health ```


> curl: (7) Failed to connect to localhost port 5000

## Investigation

### 1. Confirmed the connection failure

The expected API endpoint on port 5000 could not be reached.

### 2. Checked listening ports

The following command was used:

</> bash

``` ss -ltnp ```

The Flask application was found listening on:
> 127.0.0.1:5001

instead of:
> 127.0.0.1:5000

### 3. Tested the actual listening port

The health endpoint was tested using port 5001:

</> bash

```curl -i http://localhost:5001/health ```


> HTTP/1.1 200 OK

This confirmed that the API itself was healthy.

## Root Cause

The API port configuration did not match the port expected by the client.

## Resolution

The Flask configuration was restored to the standard project port:

</> Python

``` app.run(host="0.0.0.0", port=5000) ```

The API was restarted.

## Verification

The health endpoint was tested again:

</> bash

``` curl http://localhost:5000/health ```


> {"status":"healthy"}

The client received:
> HTTP/1.1 200 OK

## Preventive Actions

a. Keep service ports documented

b. Use consistent configuration between clients and services

c. Use environment variables or centralized configuration in larger deployments

d. Verify listening ports after configuration changes

e. Maintain health-check endpoints

## Tools Used

a. Flask

b. curl
c. ss
d. Linux / WSL
