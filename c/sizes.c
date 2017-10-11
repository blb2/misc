#include <stdio.h>

int main(void)
{
	printf("short\t\t%zu\n", sizeof(short));
	printf("int\t\t%zu\n", sizeof(int));
	printf("long\t\t%zu\n", sizeof(long));
	printf("long long\t%zu\n", sizeof(long long));
	printf("void*\t\t%zu\n", sizeof(void*));
	return 0;
}
