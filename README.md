# DIMY-assignment

A custom application-layer protocol designed to track the spread of a disease. 
It is to be ran on one centralized server and multiple clients. 
The clients will periodically communicate with other nearby clients (using UDP broadcasting instead of bluetooth as first proposed), using shamirs secret sharing, to determine whether they have been 'in contact' with each other. This data will be periodically uploaded to the server which can then be queried to determine an individuals exposure.

written using the python socket library
