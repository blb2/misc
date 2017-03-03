#include <stdio.h>
#include <string.h>
#include <unistd.h>
#include <stropts.h>
#include <sys/socket.h>
#include <sys/ioctl.h>
#include <net/if.h>
#include <netinet/in.h>
#include <arpa/inet.h>

int main(void)
{
	struct if_nameindex* p_ifs = if_nameindex();
	if (p_ifs)
	{
		int s = socket(AF_INET, SOCK_DGRAM, IPPROTO_UDP);
		if (s >= 0)
		{
			int i;
			for (i = 0; p_ifs[i].if_index != 0 && p_ifs[i].if_name; i++)
			{
				char ip[INET_ADDRSTRLEN] = "?";

				struct ifreq req;
				memset(&req, 0, sizeof(req));

				strncpy(req.ifr_name, p_ifs[i].if_name, IFNAMSIZ);

				if (ioctl(s, SIOCGIFADDR, &req) >= 0)
					inet_ntop(AF_INET, &((struct sockaddr_in*)&req.ifr_addr)->sin_addr, ip, INET_ADDRSTRLEN);

				printf("i=%d idx=%d name=%s ip=%s\n", i, p_ifs[i].if_index, p_ifs[i].if_name, ip);
			}

			close(s);
		}

		if_freenameindex(p_ifs);
	}

	return 0;
}
