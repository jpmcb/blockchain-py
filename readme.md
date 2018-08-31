# Python Blockchain API
----------
A simple, Python blockchain API. This blockchain can run on your personal computer, a server, or anywhere. Nodes may be registered and the chain will be resolved among the various chains. `GET` requests may be made to the server running the API to mine blocks are return proof of work.

#### API Routes:

`/mine` : Mines a new block into the chain. Reterns a receipt with proof of work

`chain` : Returns the entire blockchain

`/transaction/new` : Enters a new "transaction" from a sender address and enters it into the block queue. The next block that is mined will hold these transactions

`/nodes/register` : Registers a address with the server hosting the blockchain

`/nodes/resolve` : Resolves various block chains and the mined blocks within them


Inspiration from Daniel van Flymen[https://hackernoon.com/learn-blockchains-by-building-one-117428612f46]

