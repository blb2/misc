// Building with Visual Studio:
//   call "%VS120COMNTOOLS%\vsvars32.bat"
//   call "%VCINSTALLDIR%\vcvarsall.bat" x64
//   cl appname.cpp /EHsc
// Building with Clang:
//   clang++ -std=c++11 -o appname appname.cpp
//   clang++ -std=c++11 -o appname appname.cpp -ObjC++ -framework Foundation
// Building with GCC:
//   g++ -std=c++11 -o appname appname.cpp

#include <cstdio>
#include <string>
#ifdef _WIN32
#include <vector>
#include <windows.h>
#elif defined(__APPLE__)
#ifdef __OBJC__
#import <Foundation/Foundation.h>
#else
#include <cstdint>
#include <vector>
#include <mach-o/dyld.h>
#endif
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
#ifdef __OBJC__
	@autoreleasepool {
		return [[[NSBundle mainBundle] executablePath] cStringUsingEncoding:NSASCIIStringEncoding];
	}
#else
	std::vector<char> pathbuf = { '\0' };
	uint32_t pathbuf_size = 0;

	if (_NSGetExecutablePath(nullptr, &pathbuf_size) == -1) {
		pathbuf.resize(pathbuf_size);
		_NSGetExecutablePath(pathbuf.data(), &pathbuf_size);
	}

	return pathbuf.data();
#endif
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

#if defined(__APPLE__) && defined(__OBJC__)
std::string get_name(const std::string& path)
{
	@autoreleasepool {
		return [[[NSProcessInfo processInfo] processName] cStringUsingEncoding:NSASCIIStringEncoding];
	}
}
#else
std::string get_name(const std::string& path)
{
	return path;
}
#endif

int main(void)
{
	std::string path = get_path();
	std::string name = get_name(path);

	printf("path: %s\n", path.c_str());
	printf("name: %s\n", name.c_str());
	return 0;
}
