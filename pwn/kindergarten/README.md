# Kindergarten

Kids must follow the rules!
1. No cheating!   ❌
2. No swearing!   ❌
3. No 🚩 sharing! ❌

Is everything clear? (y/n)
> y

Alright! Do you have any more questions? (y/n)
> y
Feel free to ask!
>> test
Very interesting question! Let me think about it..

Alright! Do you have any more questions? (y/n)
> y
Feel free to ask!
>> asdf
Very interesting question! Let me think about it..

Alright! Do you have any more questions? (y/n)
> n
Have a nice day!!
Bad system call (core dumped)

## Analysis

The program begins by reading in some input, asking if everything is clear.  
We can put shellcode here and then figure out how to execute it.  There is a 
limit on the input, to 0x60 (96 decimal) bytes.  Most syscalls are also 
off-limits via seccomp.  I can still use read and write, but not system, for 
instance.  Given the limits on size and syscalls, custom shellcode is 
necessary.

There is a final opportunity for a "question" that gives me an opportunity to 
overflow and take control, after it prompts, "enough questions for today."  
Decompilation shows that this can be used to overflow.

There is a hidden function in the binary, `kids_are_not_allowed_here`, that 
will execute memory into which I earlier entered shellcode.  Overflowing 
appropriately from this last prompt will allow code execution.

## Shellcode

This is the shellcode that is used.  The separate section is used to allocate 
space for the `flag.txt` string and the `call` ensures the address is on the 
stack.  Commented shellcode can be found in the repo in `dump.asm`.

Because it uses multiple sections, most tools that convert shellcode to the 
`\x` format will pitch a fit or get it wrong.  Use the `bin2sc.sh` in the repo 
instead.

## Exploiting

Enter the encoded shellcode in the first prompt, then overflow in the final 
question with 136 bytes, followed by the address of 
`kids_are_not_allowed_here`.  The function should emit a message along the 
lines of, "What are you doing here?  Kids are not allowed here."  The 
shellcode should then execute and dump the contents of `flag.txt`.  The full 
`exploit.py` can be found in the repo.

## Errors

If you receive `SIGSYS`, you probably broke my shellcode.  If you receive a 
segfault, then it may be a bug in gdbserver on newer kernels, or you may not 
have flag.txt in the directory.  Be sure to run `exploit.py` in tmux.
