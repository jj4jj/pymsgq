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


>>>import msgq

>>>#python(c/c++ or other native program)

>>>#sender(process 1)

>>>mbuf='hello,world!'

>>>test_q = Msgq(123456, create=True)

>>>test_q.send(mbuf, mtype=888888)


>>>#receiver(process 2):

>>>#test_q = Msgq(123456)

>>>#mtype,mbuff = test_q.recv()  #return imediately

>>>mtype,mbuff = test_q.recv(flags=0) #wait until a msg recieved

>>>#return mtype = 888888, mbuff = "hello,world!"


