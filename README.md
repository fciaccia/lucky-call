# lucky-call

## Architecture
This repo contains a possible solution to the problem stated in the pdf named
lucky-call.pdf accessible in the /doc directory of the repo itself.

The system simulates a lucky-call contest where a RadioServer announces a
special keyword to a group of RadioClients listening to the contest. Once a
specific keyword is announced, all the RadioClients reply to the server with the
keyword plus a random three digit number. Per each call received by the server,
the random number announced by the client is added to a variable and, if the
cumulative variable is a multiple of 11, the last client is announced as the
winner.

The software architecture is the following:
![architecture](https://github.com/fciaccia/lucky-call/blob/master/doc/architecture.jpg)

To simulate the such a contest, python multiprocessing and inter-process
communication with queues are used (not threads, as they are not really
concurrent in python due to the Global Interpreter Lock).

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

## Install and run
The system is shipped as a python package. You can install it by checking out
the repo, changing to the repo root directory, and running:
```
pip install .
```
assuming you already sourced your virtualenv of choice (optional), have python >
3.5.6 and pip installed in your system.

Once the package is installed, run:
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

The systems takes as optional arguments the database file path and the number of
radio clients to simulate. An example run (with database recovery) is:
```
(.venv) ❯ lucky_call -c 5
Recovering Database
Started RadioClient  46036
Started RadioClient  46037
Started RadioClient  46038
Started RadioClient  46040
Started RadioServer
Client 46036 received word lucky
Client 46036 sleeping random delay 0.910
Client 46037 received word lucky
Client 46037 sleeping random delay 0.355
Client 46038 received word lucky
Client 46038 sleeping random delay 0.454
Client 46040 received word lucky
Client 46040 sleeping random delay 0.854
Started RadioClient  46039
Client 46039 received word lucky
Client 46039 sleeping random delay 0.744
Received message from caller 46037 with number 917
And our winner is 46037 with magic number 3839! Congratulations!
```

It could also happen that nobody wins the contest. This happens when the server
times-out after all clients have sent their request and the magic_number never
summed to a multiple of 11. An execution of that kind looks like the following:
```
(.venv) ❯ lucky_call -c 2
Started RadioClient  46634
Started RadioClient  46635
Started RadioServer
Client 46634 received word lucky
Client 46634 sleeping random delay 0.453
Client 46635 received word lucky
Client 46635 sleeping random delay 0.573
Received message from caller 46634 with number 920
Received message from caller 46635 with number 672
Sorry but nobody won today! Better luck next time.
```

To simulate disaster recovery it is possible to either write a fake db prior to
running the program, or actually interrupting it during execution (after all
clients have initialized).

The db looks like this:
```
46687 2 520
```
where the first number is the last client process id, the second is the number
of client that made requests before the crash, and the third is the
magic_number.


## Possible improvements
This is a toy example that simulates the lucky-call scenario using python
multiprocessing. To make this an actual system, a pub/sub scheme using
established protocols and message brokers could be used (e.g. MQTT protocol with
mosquitto message broker). Another alternative would be to implement a REST API.
Also, python multiprocessing is hard to debug, and other kind of architectural
implementation could be considered (e.g. gevent).

From an architecture point of view, the server could benefit from scaling
horizontally (adding other processes/servers) if the computational workload
needed to serve each client request was heavier than a simple sum. However, in
presence of single shared variable such as the magic_number, with multiple
consumers both reading and writing, special attention should be put into
guaranteeing correct concurrent access (e.g. with a mutex). For more complex
data types and record to be maintained, an actual database would necessary.

The system is also missing unit-testing, which would benefit code
maintainability.

<!---
## Contest fairness
Given that between 100 and 999 we have 81 multiples of 11 we obtain that the
probability for one of the random client numbers of being a multiple of 11 is
81/900 ~ 9%. However, given the time constraints and my current mastery of the
probability calculus domain I cannot provide a rigorous mathematical estimation
of the probability that the sum of those random number is a multiple of 11. I
can say however that the events are not un-related, thus a conditional
probability has to be computed.

The model implemented introduces additional variability thanks to the random
delay that the clients wait for, before sending the request to the server.
-->
