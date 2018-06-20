#-*- coding:utf-8 -*-

# Copyright 2017 jj4jj <resc@vip.qq.com> 
#
# Licensed under the MIT License; 
# you may not use this file except in compliance with the License. 
# You may obtain a copy of the License at https://opensource.org/licenses/MIT
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.

""" A simple wrapper System V msgq interface

Eazy to communicate with native program in Linux platform . :D

"""

import ctypes
import os
import errno
libc=ctypes.CDLL('libc.so.6',use_errno=True)
_msgget = libc.msgget
_msgsnd = libc.msgsnd
_msgrcv = libc.msgrcv
_msgctl = libc.msgctl
_ftok = libc.ftok
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
    def __init__(self, key, create=False, max_msg_buff_sz=512*1024, max_msgq_buff_total_sz=1024*1024*16, perms=0666, passive = True):
        flags=perms
        if create:
            flags=IPC_CREAT|perms
        #########################
        nkey = key
        if isinstance(key, str) or isinstance(key, unicode):
            if os.path.exists(key):
                nkey =  _ftok(key, passive and 1 or 2)
            else:
                raise Exception("create msgq error path key:%s" % key)
        self.mqid = _msgget(nkey, flags)
        if self.mqid < 0:
            raise Exception('create msgq error:%s key:%s ftok:%d passive:%s' % (os.strerror(ctypes.get_errno()), str(key), nkey, str(passive)))
        if create:
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

    def send(self, buff, mtype=0, flags=IPC_NOWAIT):
        if mtype == 0:
            mtype = id(self)
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
        ntx = _msgrcv(self.mqid, ctypes.byref(self.msgbuf), ctypes.sizeof(self.msgbuf.mtext), mtype, flags)
        if ntx == -1:
            eno = ctypes.get_errno()
            if eno == errno.ENOMSG or eno == errno.EAGAIN or eno == errno.EINTR:
                return 0,None
            if eno == errno.E2BIG:
                ntx = _msgrcv(self.mqid, ctypes.byref(self.msgbuf), ctypes.sizeof(self.msgbuf.mtext), flags|MSG_NOERROR)
                #error too big msg
                return 0,None
            raise Exception('recv msgq error:%s' % os.strerror(eno))
        return self.msgbuf.mtype,ctypes.string_at(self.msgbuf.mtext, ntx)


if __name__ == '__main__':
    import sys
    if len(sys.argv) == 1:
        print('Usage:%s <send|recv|key_send|key_recv>' % sys.argv[0])
        print('testing send and recv interface')
        sys.exit(-1)
    if sys.argv[1] == 'send':
        test_q = Msgq(123456, True)
        msg = 'hello[\x92\xE5]\0\x56 world!'
        print('case1: send msg(%s) (sz:%d) ret (0/-1):' % (msg,len(msg)), test_q.send(msg, 54321))
        print('case2: send msg(%s) (sz:%d) ret (0/-1):' % (msg,len(msg)), test_q.send(msg))
    elif sys.argv[1] == 'key_send':
        test_q = Msgq('/tmp', True)
        msg = 'hello[\x92\xE5]\0\x56 world!'
        print('case1: send msg(%s) (sz:%d) ret (0/-1):' % (msg,len(msg)), test_q.send(msg, 54321))
        print('case2: send msg(%s) (sz:%d) ret (0/-1):' % (msg,len(msg)), test_q.send(msg))
    elif sys.argv[1] == 'key_recv':
        test_q = Msgq('/tmp', True)
        mtype,mbuff = test_q.recv()
        sz = 0
        if mbuff:
            sz = len(mbuff)
        print('case1: recv ret (msg type,msg buff,sz):', mtype, mbuff,sz)
        mtype,mbuff = test_q.recv()
        sz = 0
        if mbuff:
            sz = len(mbuff)
        print('case2: recv ret (msg type,msg buff,sz):', mtype, mbuff,sz)
    else:
        test_q = Msgq(123456, False)
        mtype,mbuff = test_q.recv()
        sz = 0
        if mbuff:
            sz = len(mbuff)
        print('case1: recv ret (msg type,msg buff,sz):', mtype, mbuff,sz)
        mtype,mbuff = test_q.recv()
        sz = 0
        if mbuff:
            sz = len(mbuff)
        print('case2: recv ret (msg type,msg buff,sz):', mtype, mbuff,sz)


