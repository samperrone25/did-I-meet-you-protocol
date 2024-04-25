# DIMY
Did I Meet You?

A custom application-layer protocol designed to track the spread of a disease. 
Runs across a centralized server group and many clients.
The clients will periodically communicate with other nearby clients (using UDP broadcasting instead of bluetooth as first proposed), using shamirs secret sharing, to determine whether they have been 'in contact' with each other. 
Contact data will be uploaded and stored in the server where it can then be queried to determine an individuals exposure.

written using the python socket library
