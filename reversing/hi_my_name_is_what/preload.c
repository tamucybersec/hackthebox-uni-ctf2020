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