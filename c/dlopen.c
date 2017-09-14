#include <stdio.h>
#include <dlfcn.h>

int main(int argc, char* argv[])
{
	int i;

	for (i = 1; i != argc; i++) {
		const char* path = argv[i];
		void* p = dlopen(path, RTLD_LAZY | RTLD_LOCAL);
		if (p) {
			printf("loaded: %s\n", path);
			dlclose(p);
		} else {
			perror(path);
			printf("dlerror:\n%s\n", dlerror());
		}
	}

	return 0;
}
