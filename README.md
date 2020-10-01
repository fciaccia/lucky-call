# lucky-call

This repo contains a possible solution to the problem stated in the pdf named
lucky-call.pdf accessible in the root directory of the repo itself.

The system simulates a lucky-call contest where a RadioServer announces a
special keyword to a group of RadioClients listening to the contest.
Once a specific keyword is announced, all the RadioClients reply to the server
with the keyword plus a random three digit number. Per each call received by
the server the random number announced by the client is added to a variable and
if the cumulative variable is a multiple of 11 the last client is announced as
the winner.

The software architecture is the following:
![architecture](https://github.com/fciaccia/lucky-call/blob/master/doc/architecture.jpg)

To simulate the system python multiprocessing and inter-process communication
with queues are used (not threads, as they are not really concurrent in python
due to the Global Interpreter Lock).

Once the system is initialized, the RadioServer publishes the special keyword
over pub/sub queues where each client is listening (one-to-many). When each
client listening on the subscribed queue receives the special keyword it waits a
random time before sending its request to the server. This random delay
simulates a possible radio propagation delay.

For each client request, the server validates the input and adds the client
random number to a local variable magic_number. If magic_number is a multiple of
11, the client sending the message is announced as the contest winner.

To guarantee consistency and disaster recovery, another process is in charge of
writing the last result computed by the server to a local database (text file).
When the contest starts it always checks if a local db instance is present, in
which case it recovers the execution.

The system is shipped as a python package. You can install it by simply
changing directory to the repo root and running:
```
pip install .
```
assuming you already sourced your virtualenv of choice (optional) and have
python > 3.5.6 and pip installed in your system.

Once the package is installed run:
```
$ luck_call --help
usage: lucky_call [-h] [-f DB_FILE] [-c NUM_CLIENTS]

Radio lucky caller simulation system

optional arguments:
  -h, --help            show this help message and exit
  -f DB_FILE, --db-file DB_FILE
                        Local database filename
  -c NUM_CLIENTS, --num-clients NUM_CLIENTS
                        number of radio clients
```

The systems takes as optional arguments the database file path and the number
of radio clients to simulate.