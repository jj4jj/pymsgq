#-*- coding:utf-8 -*-
"""
python msgq with libc system V interface
eazy to communicate with native App in Linux platform
"""
import ctypes
import os
import errno
libc=ctypes.CDLL('libc.so.6',use_errno=True)
_msgget = libc.msgget
_msgsnd = libc.msgsnd
_msgrcv = libc.msgrcv
_msgctl = libc.msgctl
###########################################
IPC_CREAT=512
IPC_NOWAIT=2048
IPC_STAT=2
IPC_SET=1
#msgqbuf
def _msgbuf(size):
    class __msgbuf(ctypes.Structure):
        _pack_ = 1
        _fields_ = [
                ('mtype', ctypes.c_long, 8*8),
                ('mtext', ctypes.c_byte*size,),
                ]
    return __msgbuf()
#msgdsbuf
DS_STRUCT_SIZE = 120
DS_STRUCT_DUMMY_OFFSET_SIZE = 88
DS_STRUCT_DUMMY_PADDING_SIZE = DS_STRUCT_SIZE - DS_STRUCT_DUMMY_OFFSET_SIZE - 8
class _msgdsbuf(ctypes.Structure):
    _pack_ = 1
    _fields_ = [
            ('dummy_1', ctypes.c_byte*DS_STRUCT_DUMMY_OFFSET_SIZE),
            ('msg_qbytes', ctypes.c_long, 8*8),
            ('dummy_2', ctypes.c_byte*DS_STRUCT_DUMMY_PADDING_SIZE)
            ]

class Msgq(object):
    def __init__(self, key, create = False, max_msg_buff_sz=512*1024, max_msgq_buff_total_sz = 1024*1024*16):
        flags = IPC_CREAT
        if create:
            flags = IPC_CREAT|0666
        self.mqid = _msgget(key, flags)
        if self.mqid < 0:
            raise Exception('create msgq error:%s' % os.strerror(ctypes.get_errno()))
        ds = _msgdsbuf() 
        err = _msgctl(self.mqid, IPC_STAT, ctypes.byref(ds))
        if err < 0:
            raise Exception('get msgq stat error:%s' % os.strerror(ctypes.get_errno()))
        if ds.msg_qbytes < max_msgq_buff_total_sz:
            ds.msg_qbytes = max_msgq_buff_total_sz
            err = _msgctl(self.mqid, IPC_SET, ctypes.byref(ds))
            if err < 0:
                raise Exception('set msgq buffer error:%s' % os.strerror(ctypes.get_errno()))
        self.msgbuf = _msgbuf(max_msg_buff_sz)
        self.max_msg_size = max_msg_buff_sz

    def send(self, buff, mtype, flags=IPC_NOWAIT):
        self.msgbuf.mtype = mtype
        if len(buff) >  self.max_msg_size:
            raise Exception('send msgq buff too big (>%d) !' % self.max_msg_size)
        nc = 0
        for c in buff: 
            self.msgbuf.mtext[nc] = ctypes.c_byte(ord(c))
            nc += 1
        err = _msgsnd(self.mqid, ctypes.byref(self.msgbuf), nc, flags)
        if err < 0:
            eno = ctypes.get_errno()
            if eno == errno.EAGAIN:
                return -1
            if eno == errno.EINTR:
                return -2
            raise Exception('send msgq error:%s' % os.strerror(cyptes.get_errno()))
        return err

    def recv(self, mtype=0, flags=IPC_NOWAIT):
        self.msgbuf.mtype = mtype
        err = _msgrcv(self.mqid, ctypes.byref(self.msgbuf), ctypes.sizeof(self.msgbuf.mtext), flags)
        if err == -1:
            eno = ctypes.get_errno()
            if eno == errno.ENOMSG or eno == errno.EAGAIN or eno == errno.EINTR:
                return 0,
            if err == errno.E2BIG:
                err = _msgrcv(self.mqid, ctypes.byref(self.msgbuf), ctypes.sizeof(self.msgbuf.mtext), flags|MSG_NOERROR)
                #error too big msg
                return 0,
            raise Exception('recv msgq error:%s' % os.strerror(eno))
        return self.msgbuf.mtype,err,self.msgbuf.mtext


if __name__ == '__main__':
    import sys
    if len(sys.argv) == 1:
        print 'Usage:%s <send|recv>'
        print 'testing send and recv interface'
        sys.exit(-1)
    if sys.argv[1] == 'send':
        test_q = Msgq(123456, True)
        print 'send ret:',test_q.send('hello', 54321)
    else:
        test_q = Msgq(123456, False)
        print 'recv ret:',test_q.recv()

