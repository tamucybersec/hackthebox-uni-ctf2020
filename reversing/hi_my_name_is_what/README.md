# Hi! My name is (what?)

```text
I've been once told that my name is difficult to pronounce and since then I'm using it as a password for everything.
```

## initial review
```c
void main(void)

{
  EVP_PKEY_CTX *ctx;
  __uid_t __uid;
  passwd *ppVar1;
  long lVar2;
  int iVar3;
  size_t sVar4;
  size_t *outlen;
  uchar *in;
  size_t in_stack_ffffffd0;
  int local_28;
  
  puts("Who are you?");
  __uid = geteuid();
  ppVar1 = getpwuid(__uid);
  in = (uchar *)0x0;
  lVar2 = ptrace(PTRACE_TRACEME,0,0);
  if (lVar2 != 0) {
    puts("This doesn\'t seem right");
                    /* WARNING: Subroutine does not return */
    exit(1);
  }
  if (ppVar1 != (passwd *)0x0) {
    ctx = (EVP_PKEY_CTX *)ppVar1->pw_name;
    iVar3 = strcmp((char *)ctx,username);
    if (iVar3 == 0) {
      local_28 = 0;
      while (local_28 < 0x198) {
        if ((*(uint *)(main + local_28) & 0xff) == breakpointvalue) {
          puts("What\'s this now?");
                    /* WARNING: Subroutine does not return */
          exit(1);
        }
        local_28 = local_28 + 1;
      }
      sVar4 = strlen(encrypted_flag);
      outlen = (size_t *)malloc((sVar4 + 1) * 4);
      decrypt(ctx,encrypted_flag,outlen,in,in_stack_ffffffd0);
      *(undefined *)((int)outlen + sVar4) = 0;
      puts((char *)outlen);
    }
    else {
      puts("No you are not the right person");
    }
                    /* WARNING: Subroutine does not return */
    exit(0);
  }
  puts("?");
                    /* WARNING: Subroutine does not return */
  exit(1);
}
```

So, we see a couple anti-debugging features (ptrace, etc) but those aren't super relevant.  If the current executing username matches `~#L-:4;f` then it will decrypt a stored flag and print it.  The decryption involves the username so we can't just binary patch the username check away.  This is problematic because this is not a valid linux username.  So, what can we do?  

## i can so ptrace (alternative title: how you can just overwrite any dynamic library function)

Fun fact: on a Linux system the dynamic linker will check the environmental variable LD_PRELOAD for libraries and then bind those symbols before any other libraries.  What happens if two libraries provide the same symbol?  Well, the one which loads first!  LD_PRELOAD goes before any linked libraries which means that if you preload a shared library which exports a symbol it will override the symbol from the later loading library.  What this means is that we can just overwrite getpwuid so that it returns a struct with an arbitrary username!  

```c
#include <sys/types.h>
#include <stdlib.h>
#include <pwd.h>


long ptrace(int request, pid_t pid,
                   void *addr, void *data) {
	return 0;
}

struct passwd *getpwuid(uid_t uid) {
	struct passwd* ret = malloc(sizeof(struct passwd));
	ret->pw_name = "~#L-:4;f";
	ret->pw_passwd = "a";
	ret->pw_uid = 0;
	ret->pw_gid = 0;
	return ret;
}
```


```text
❯ gcc -m32 preload.c -shared -o preload.so
❯ LD_PRELOAD=$(pwd)/preload.so ./my_name_is
Who are you?
HTB{L00k1ng_f0r_4_w31rd_n4m3}
```