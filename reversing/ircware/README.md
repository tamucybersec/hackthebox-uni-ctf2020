# ircware

```text
During a routine check on our servers we found this suspicious binary, but when analyzing it we couldn't get it to do anything. We assume it's dead malware but maybe something interesting can still be extracted from it?
```

## initial review

### entry

```c
undefined  [16] entry(void)

{
  int iVar1;
  
                    /* rax = 0x13e, getrandom */
  syscall();
  s_NICK_ircware_0000_00601018._13_4_ = s_NICK_ircware_0000_00601018._13_4_ & 0x7070707;
  s_NICK_ircware_0000_00601018._13_4_ = s_NICK_ircware_0000_00601018._13_4_ | 0x30303030;
  iVar1 = connect_localhost_8000(0x601025,4,0);
  if (-1 < iVar1) {
    write_empty_line?();
    write_empty_line?();
    write_empty_line?();
    do {
      read?();
      command_handler();
    } while( true );
  }
  syscall();
  syscall();
  return CONCAT88(DAT_00601068,0x3c);
}
```

Not a lot in the entry function.  It connects to a local server on port 8000 and then does some read/write on that socket but doesn't seem to actually write much.  

### command_handler


```c
void command_handler(void)

{
	  ...
      lVar5 = DAT_00601179;
      pcVar9 = pcVar13;
      pcVar11 = s_PRIVMSG_#secret_:@pass_00601161;
	  ...
      pcVar9 = pcVar13;
      pcVar11 = s_PRIVMSG_#secret_:@flag_00601128;
      do {
        pcVar12 = pcVar11;
        if (lVar5 == 0) break;
        lVar5 = lVar5 + -1;
        pcVar12 = pcVar11 + 1;
        cVar1 = *pcVar9;
        cVar2 = *pcVar11;
        pcVar9 = pcVar9 + 1;
        pcVar11 = pcVar12;
      } while (cVar1 == cVar2);
      if (lVar5 == 0) {
        if (_DAT_00601008 == 0) {
          FUN_00400485(pcVar12,s_Requires_password_006010c2,&DAT_006021a9,DAT_006010d4);
          return;

}
```

I've stripped large parts of this function out because they weren't super useful decompilation and this contains the relevant bits.  The important things to notice here are that:

1. This is IRC -- the PRIMSG #secret is a dead giveaway.  I just guessed at this point that it wanted an IRC server so I ran one and joined the #secret channel.  
2. the is a @flag command but it requires a password
3. there is a @pass function

The implication here is that this is an IRC bot and we need to give it the correct password before it will give us the flag.  

## so what's the password?

```text
                             LAB_00400401                                    XREF[1]:     0040043c(j)  
        00400401 8a 06           MOV        AL,byte ptr [RSI]=>DAT_006021c0                  = ??
        00400403 88 03           MOV        byte ptr [RBX]=>DAT_00601147,AL                  = "JJ3DSCP"
                                                                                             = 52h
        00400405 3c 00           CMP        AL,0x0
        00400407 74 35           JZ         LAB_0040043e
        00400409 3c 0a           CMP        AL,0xa
        0040040b 74 31           JZ         LAB_0040043e
        0040040d 3c 0d           CMP        AL,0xd
        0040040f 74 2d           JZ         LAB_0040043e
        00400411 48 3b 15        CMP        RDX,qword ptr [DAT_00601159]                     = 08h
                 41 0d 20 00
        00400418 77 4c           JA         LAB_00400466
        0040041a 3c 41           CMP        AL,0x41
        0040041c 72 0e           JC         LAB_0040042c
        0040041e 3c 5a           CMP        AL,0x5a
        00400420 77 0a           JA         LAB_0040042c
        00400422 04 11           ADD        AL,0x11
        00400424 3c 5a           CMP        AL,0x5a
        00400426 76 04           JBE        LAB_0040042c
        00400428 2c 5a           SUB        AL,0x5a
        0040042a 04 40           ADD        AL,0x40
                             LAB_0040042c                                    XREF[3]:     0040041c(j), 00400420(j), 
                                                                                          00400426(j)  
        0040042c 38 07           CMP        byte ptr [RDI]=>s_RJJ3DSCP_00601150,AL           = "RJJ3DSCP"
        0040042e 75 36           JNZ        LAB_00400466
        00400430 48 ff c2        INC        RDX
        00400433 48 ff c3        INC        RBX
        00400436 48 ff c6        INC        RSI
        00400439 48 ff c7        INC        RDI
        0040043c eb c3           JMP        LAB_00400401
                             LAB_0040043e                                    XREF[3]:     00400407(j), 0040040b(j), 
                                                                                          0040040f(j)  
        0040043e 48 89 ce        MOV        RSI,RCX
        00400441 48 3b 15        CMP        RDX,qword ptr [DAT_00601159]                     = 08h
                 11 0d 20 00
        00400448 75 1c           JNZ        LAB_00400466
        0040044a 48 ff 05        INC        qword ptr [DAT_00601008]
                 b7 0b 20 00
        00400451 48 8d 35        LEA        RSI,[s_Accepted_00601092]                        = "Accepted"
                 3a 0c 20 00
        00400458 48 8b 0d        MOV        RCX,qword ptr [DAT_0060109b]                     = 0000000000000009h
                 3c 0c 20 00
        0040045f e8 21 00        CALL       FUN_00400485                                     undefined FUN_00400485()
                 00 00
        00400464 eb 1e           JMP        LAB_00400484
                             LAB_00400466                                    XREF[3]:     00400418(j), 0040042e(j), 
                                                                                          00400448(j)  
        00400466 48 c7 05        MOV        qword ptr [DAT_00601008],0x0
                 97 0b 20 
                 00 00 00 
        00400471 48 8d 35        LEA        RSI,[s_Rejected_006010a3]                        = "Rejected"
                 2b 0c 20 00
        00400478 48 8b 0d        MOV        RCX,qword ptr [DAT_006010ac]                     = 0000000000000009h
                 2d 0c 20 00
        0040047f e8 01 00        CALL       FUN_00400485                                     undefined FUN_00400485()
                 00 00
```

So the core flow of this segment of assembly is a fancy string comparison.  It loads the byte it is currently operating on (so 0th, 1st, 2nd, until it goes through 8 of them), mutates it based on a condition, and then compares it against `RJJ3DSCP`.  I will put these mutations in the form of a python script because that's how I solved it and I don't want to explain it with english lol.  

```python
from string import printable

def mutate(c):
	if c < 0x41:
		return c
	if c > 0x5a:
		return c
	c += 0x11
	if c <= 0x5a:
		return c
	c -= 0x5a
	c += 0x40
	return c

comp = "RJJ3DSCP"

for i in range(8):
	for j in printable:
		if chr(mutate(ord(j))) == comp[i]:
			print(j,end='')
```
That script solves for ASS3MBLY which definitely looks meaningful.  Let's try telling it to the bot!  

```text
* Now talking on #secret
* #secret :No topic is set
* ircware_7040 (ircware@127.0.0.1) has joined
<sky> @pass ASS3MBLY
<ircware_7040> Accepted
<sky> @flag
<ircware_7040> HTB{m1N1m411st1C_fL4g_pR0v1d3r_b0T}
```