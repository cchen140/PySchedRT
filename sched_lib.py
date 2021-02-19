'''
MIT License

Copyright (c) 2021 CY Chen (cyer@cychen.me)

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
'''

import os
import sys
import ctypes
import struct
from ctypes.util import find_library

'''
struct sched_attr {
	__u32 size;

	__u32 sched_policy;
	__u64 sched_flags;

	/* SCHED_NORMAL, SCHED_BATCH */
	__s32 sched_nice;

	/* SCHED_FIFO, SCHED_RR */
	__u32 sched_priority;

	/* SCHED_DEADLINE (nsec) */
	__u64 sched_runtime;
	__u64 sched_deadline;
	__u64 sched_period;
};

int sched_setattr(pid_t pid,
		const struct sched_attr *attr,
		unsigned int flags)
{
	return syscall(__NR_sched_setattr, pid, attr, flags);
}

int sched_getattr(pid_t pid,
		struct sched_attr *attr,
		unsigned int size,
		unsigned int flags)
{
	return syscall(__NR_sched_getattr, pid, attr, size, flags);
}
'''

class sched_attr(ctypes.Structure):
    _fields_ = (
        ('size', ctypes.c_uint32),
        ('sched_policy', ctypes.c_uint32),
        ('sched_flags', ctypes.c_uint64),
        ('sched_nice', ctypes.c_int32),
        ('sched_priority', ctypes.c_uint32),
        ('sched_runtime', ctypes.c_uint64),
        ('sched_deadline', ctypes.c_uint64),
        ('sched_period', ctypes.c_uint64),
    )

    def __repr__(self):
        return f'size: {self.size}\r\n'\
               f'sched_policy: {self.sched_policy}\r\n'\
               f'sched_flags: {self.sched_flags}\r\n'\
               f'sched_priority: {self.sched_priority}\r\n'\
               f'sched_runtime: {self.sched_runtime}\r\n'\
               f'sched_deadline: {self.sched_deadline}\r\n'\
               f'sched_period: {self.sched_period}'


SCHED_DEADLINE = 6

def sched_setattr(period, deadline, runtime, policy):
    SYS_SCHED_SETATTR = 380
    c_sched_attr_p = ctypes.POINTER(sched_attr)
    libc = ctypes.CDLL(find_library('c'), use_errno=True)
    syscall = libc.syscall
    syscall.argtypes = [ctypes.c_int, ctypes.c_int, c_sched_attr_p, ctypes.c_uint]
    syscall.restype = ctypes.c_int
    
    DEFAULT_BUF_SIZE = 1 * 1024 * 1024  # 1MB
    buf = ctypes.create_string_buffer(DEFAULT_BUF_SIZE)
    bufp = ctypes.cast(buf, c_sched_attr_p)
    bufp[0].size = 48 #ctypes.sizeof(c_sched_attr_p)
    bufp[0].sched_flags = 0
    bufp[0].sched_nice = 0
    bufp[0].sched_priority = 0
    bufp[0].sched_policy = SCHED_DEADLINE
    bufp[0].sched_runtime = runtime
    bufp[0].sched_period = period
    bufp[0].sched_deadline = deadline

    ret = 0
    ret = syscall(SYS_SCHED_SETATTR, 0, bufp, 0)
    if ret < 0:
        errno = ctypes.get_errno()
        print("Error Code = {}".format(errno))
    return ret


def sched_getattr():
    SYS_SCHED_GETATTR = 381
    c_sched_attr_p = ctypes.POINTER(sched_attr)
    libc = ctypes.CDLL(find_library('c'), use_errno=True)
    syscall = libc.syscall
    syscall.argtypes = [ctypes.c_int, ctypes.c_int, c_sched_attr_p, ctypes.c_uint, ctypes.c_uint]
    syscall.restype = ctypes.c_int

    DEFAULT_BUF_SIZE = 1 * 1024 * 1024  # 1MB
    buf = ctypes.create_string_buffer(DEFAULT_BUF_SIZE)
    bufp = ctypes.cast(buf, c_sched_attr_p)
    #print(bufp[0])
    ret = 0
    ret = syscall(SYS_SCHED_GETATTR, 0, bufp, 48*8, 0) # 48*8
    if ret < 0:
        errno = ctypes.get_errno()
        print("Error: {}".format(errno))
        return None
    else:
        return bufp[0]


def gettid():
    SYS_GETTID = 224
    libc = ctypes.CDLL(find_library('c'), use_errno=True)
    syscall = libc.syscall
    syscall.argtypes = [ctypes.c_int]
    syscall.restype = ctypes.c_int
    ret = syscall(224)  #224, 178
    #print(ret)
    return ret

if __name__=="__main__":
    print(gettid())
    sched_setattr(5000000, 5000000, 1000000, SCHED_DEADLINE)
    print(sched_getattr())
