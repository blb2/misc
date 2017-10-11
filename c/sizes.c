#include <stdio.h>

#ifdef _MSC_VER
#define fmt "%Iu"
#else
#define fmt "%zu"
#endif

int main(void)
{
	printf("short\t\t" fmt "\n", sizeof(short));
	printf("int\t\t" fmt "\n", sizeof(int));
	printf("long\t\t" fmt "\n", sizeof(long));
	printf("long long\t" fmt "\n", sizeof(long long));
	printf("void*\t\t" fmt "\n", sizeof(void*));
	printf("char\t\t" fmt "\n", sizeof(char));
	printf("wchar_t\t\t" fmt "\n", sizeof(wchar_t));
	return 0;
}
