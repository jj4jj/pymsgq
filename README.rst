pymsgq
======

Description
-----------

A simple wrapper System V msgq interface

Eazy to communicate with native program in Linux platform . :D


Limitations
-----------
no depends


Installation
------------

``pip install pymsgq``

Documentation
-------------

sender(process 1):
1. test_q = Msgq(123456, create=True)
2. test_q.send(msg)

receiver(process 2):
1. test_q = Msgq(123456)
2. mtype,mbuff = test_q.recv()


