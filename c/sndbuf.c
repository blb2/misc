#include <stdio.h>
#include <sys/socket.h>
#include <netinet/in.h>
#include <unistd.h>

int main(void)
{
	int s = socket(AF_INET, SOCK_STREAM, IPPROTO_TCP);
	if (s >= 0) {
		int sndbuf = 0;
		socklen_t sndbuf_size = sizeof(sndbuf);

		if (getsockopt(s, SOL_SOCKET, SO_SNDBUF, &sndbuf, &sndbuf_size) >= 0)
			printf("sndbuf: %d\n", sndbuf);

		close(s);
	}

	return 0;
}
