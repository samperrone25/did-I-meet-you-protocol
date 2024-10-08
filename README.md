# DIMY (Did I Meet You?)  
An application-layer protocol designed to track the spread of a disease. A simplification of the protocol described in [https://arxiv.org/abs/2103.05873](https://arxiv.org/abs/2103.05873).  

## How it works  
1) Clients generate ephemeral IDs every 15 seconds.  
2) These IDs are split into 5 shares using [Shamir's Secret Sharing](https://en.wikipedia.org/wiki/Shamir%27s_secret_sharing) scheme such that 3 shares would be needed to reconstruct the ID. A share is broadcast (UDP) every 3 seconds.  
3) When a client receives 3+ shares from another, they will reconstruct an EphID and verify it with a hash provided in prior share broadcasts.  
4) The two clients now know each other's EphIDs. Each client combines their private random exponent (used on an elliptic curve to create their EphID) with the other EphID to complete a [Diffie-Hellman key exchange](https://en.wikipedia.org/wiki/Diffie%E2%80%93Hellman_key_exchange) and arrive at a shared secret for the encounter, an encounter ID (EncID).  
5) This EncID is encoded into a Daily Bloom Filter (DBF) and deleted.  
6) Every 90 seconds, a DBF is stored, and a new one is created.  
7) Every 9 minutes, all DBFs are combined into another Bloom Filter called the Query Bloom Filter (QBF) and deleted. The QBF is sent to the backend server (TCP) and compared with the server's Contact Bloom Filter (CBF), which contains the encounters of all COVID-positive clients. The result is shown to the client.  
8) When a client gets COVID, they can upload their QBFs for merging with the CBF.  

## To Run  
`python3 Dimy2.py [seconds_until_covid_diagnosis] ## for client`  
`python3 DimyServer.py ## for server`
