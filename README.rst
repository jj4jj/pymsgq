pymsgq
======

Description
-----------

A simple System V msgq python interface for Linux IPC

Eazy to communicate with native program in Linux platform . :D


Limitations
-----------
no depends


Installation
------------

``pip install pymsgq``

Documentation
-------------


::
 	
    #sender(process 1 ,  python/c/c++ or other native program)
    mbuf='hello,world!'
    test_q = Msgq(123456, create=True)
    test_q.send(mbuf, mtype=888888)

::

    #receiver(process 2):
    test_q = Msgq(123456)
    mtype,mbuf = test_q.recv(flags=0) #wait until a msg recieved
    #mtype,mbuf = test_q.recv()  #this call return imediately
    #call will return mtype = 888888, mbuf = "hello,world!"



