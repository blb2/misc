#include <stddef.h>
#include <stdio.h>
#include <stdlib.h>

int main(int argc, char* argv[])
{
	int i;

	for (i = 1; i != argc; i++) {
		char* path = realpath(argv[i], NULL);
		if (path) {
			printf("%s -> %s\n", argv[i], path);
			free(path);
		} else {
			perror(argv[i]);
		}
	}

	return 0;
}
