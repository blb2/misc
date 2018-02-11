#include <assert.h>
#include <stddef.h>
#include <stdio.h>
#include <string.h>
#include <sys/socket.h>
#include <netdb.h>
#include <netinet/in.h>
#include <arpa/inet.h>

char ipv4[INET_ADDRSTRLEN], ipv6[INET6_ADDRSTRLEN];

void showaddrinfo(struct addrinfo* addr, const char* header)
{
	puts(header);

	int addr_num = 0;
	for (struct addrinfo* curr = addr; curr; curr = curr->ai_next, addr_num++) {
		printf("addr[%d]:\n", addr_num);

		puts(" flags:");
		{
			if ((curr->ai_flags & AI_PASSIVE) != 0)
				printf("  AI_PASSIVE\n");
			if ((curr->ai_flags & AI_CANONNAME) != 0)
				printf("  AI_CANONNAME\n");
			if ((curr->ai_flags & AI_NUMERICHOST) != 0)
				printf("  AI_NUMERICHOST\n");
			if ((curr->ai_flags & AI_V4MAPPED) != 0)
				printf("  AI_V4MAPPED\n");
			if ((curr->ai_flags & AI_ALL) != 0)
				printf("  AI_ALL\n");
			if ((curr->ai_flags & AI_ADDRCONFIG) != 0)
				printf("  AI_ADDRCONFIG\n");
		}

		puts(" family:");
		{
			const char* family;
			switch (curr->ai_family) {
				case AF_INET:
					family = "ipv4";
					break;
				case AF_INET6:
					family = "ipv6";
					break;
				case AF_UNIX:
					family = "unix";
					break;
				default:
					family = NULL;
			}

			if (family)
				printf("  %s\n", family);
		}

		puts(" socktype:");
		{
			const char* type;
			switch (curr->ai_socktype) {
				case SOCK_STREAM:
					type = "stream";
					break;
				case SOCK_DGRAM:
					type = "datagram";
					break;
				case SOCK_RAW:
					type = "raw";
					break;
				case SOCK_SEQPACKET:
					type = "seqpacket";
					break;
				default:
					type = NULL;
			}

			if (type)
				printf("  %s\n", type);
		}

		puts(" protocol:");
		{
			const char* protocol;
			switch (curr->ai_protocol) {
				case IPPROTO_TCP:
					protocol = "tcp";
					break;
				case IPPROTO_UDP:
					protocol = "udp";
					break;
				case IPPROTO_RAW:
					protocol = "raw";
					break;
				case IPPROTO_IP:
					protocol = "ip";
					break;
				case IPPROTO_IPV6:
					protocol = "ipv6";
					break;
				case IPPROTO_ICMP:
					protocol = "icmp";
					break;
				default:
					protocol = NULL;
			}

			if (protocol)
				printf("  %s\n", protocol);
		}

		puts(" canonical:");
		{
			if (curr->ai_canonname)
				printf("  %s\n", curr->ai_canonname);
		}

		puts(" addr:");
		{
			switch (curr->ai_family) {
				case AF_INET: {
					struct sockaddr_in* s = (struct sockaddr_in*)curr->ai_addr;
					assert(s->sin_family == curr->ai_family);
					printf("  family: %d\n", s->sin_family);
					printf("  addr: %s\n", inet_ntop(s->sin_family, &s->sin_addr, ipv4, sizeof(ipv4)));
					printf("  port: %d\n", ntohs(s->sin_port));
					break;
				}
				case AF_INET6: {
				   struct sockaddr_in6* s = (struct sockaddr_in6*)curr->ai_addr;
				   assert(s->sin6_family == curr->ai_family);
				   printf("  family: %d\n", s->sin6_family);
				   printf("  addr: %s\n", inet_ntop(s->sin6_family, &s->sin6_addr, ipv6, sizeof(ipv6)));
				   printf("  port: %d\n", ntohs(s->sin6_port));
				   break;
				}
			}
		}

		printf(" addrlen=%d\n", curr->ai_addrlen);
	}

	puts("");
}

int main(void)
{
	struct addrinfo hints;
	struct addrinfo* addr;

	memset(&hints, 0, sizeof(hints));
	hints.ai_flags    = AI_PASSIVE | AI_NUMERICSERV;
	hints.ai_family   = AF_INET;
	hints.ai_protocol = IPPROTO_TCP;
	hints.ai_socktype = SOCK_STREAM;

	if (getaddrinfo(NULL, "80", &hints, &addr) == 0) {
		showaddrinfo(addr, "NULL + 80");
		freeaddrinfo(addr);
	}

	memset(&hints, 0, sizeof(hints));
	hints.ai_flags = AI_CANONNAME;

	if (getaddrinfo("heapify.org", "http", &hints, &addr) == 0) {
		showaddrinfo(addr, "heapify.org + http");
		freeaddrinfo(addr);
	}

	memset(&hints, 0, sizeof(hints));
	hints.ai_flags  = AI_NUMERICHOST;
	hints.ai_family = AF_UNSPEC;

	if (getaddrinfo("8.8.8.8", "domain", &hints, &addr) == 0) {
		showaddrinfo(addr, "8.8.8.8 + domain");
		freeaddrinfo(addr);
	}

	return 0;
}
