// Building with Visual Studio:
//   call "%VS120COMNTOOLS%\vsvars32.bat"
//   call "%VCINSTALLDIR%\vcvarsall.bat" x64
//   cl appname.cpp /EHsc
// Building with Clang:
//   clang++ -std=c++11 -o appname appname.cpp
// Building with GCC:
//   g++ -std=c++11 -o appname appname.cpp

#include <cstdio>
#include <string>
#ifdef _WIN32
#include <vector>
#include <windows.h>
#elif defined(__APPLE__)
#else
#include <unistd.h>
#include <limits.h>
#endif

#ifdef _WIN32
static const char s_path_sep = '\\';
std::string get_path(void)
{
	std::vector<char> pathbuf;

	do {
		pathbuf.resize(pathbuf.size() + MAX_PATH);
		GetModuleFileNameA(nullptr, pathbuf.data(), (DWORD)pathbuf.size());
	} while (GetLastError() == ERROR_INSUFFICIENT_BUFFER);

	return pathbuf.data();
}
#elif defined(__APPLE__)
static const char s_path_sep = '/';
std::string get_path(void)
{
	return "";
}
#else
static const char s_path_sep = '/';
std::string get_path(void)
{
	const char* paths[] = {
		"/proc/self/exe",
		"/proc/curproc/file",
		"/proc/curproc/exe",
	};

	char pathbuf[PATH_MAX];
	for (const char* path : paths) {
		ssize_t len = readlink(path, pathbuf, sizeof(pathbuf));
		if (len != -1) {
			pathbuf[len] = '\0';
			return pathbuf;
		} else {
			perror("readlink");
		}
	}

	return std::to_string(getpid());
}
#endif

std::string get_name(const std::string& path)
{
	return path;
}

int main(void)
{
	std::string path = get_path();
	std::string name = get_name(path);

	printf("path: %s\n", path.c_str());
	printf("name: %s\n", name.c_str());
	return 0;
}
