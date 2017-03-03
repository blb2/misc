#include <stdio.h>
#include <fcntl.h>
#include <unistd.h>

int main(void)
{
	int fd = open("/tmp/mylockfile", O_WRONLY | O_CREAT, S_IRWXU | S_IRWXG | S_IRWXO);
	if (fd >= 0) {
		if (lockf(fd, F_TLOCK, 0) < 0) {
			perror("lockf");
		} else {
			puts("lockf succeeded");
			sleep(10);
			lockf(fd, F_ULOCK, 0);
		}

		close(fd);
	} else {
		perror("open");
	}

	return 0;
}
