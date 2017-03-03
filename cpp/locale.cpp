#include <cstring>
#include <codecvt>
#include <iostream>
#include <locale>
#include <string>
#include <vector>
#include <locale.h>

std::string cvt(const std::wstring& wstr, bool use_active_code_page=false)
{
	if (use_active_code_page) {
		locale_t new_code_page = newlocale(LC_ALL_MASK, "", (locale_t)0);
		locale_t old_code_page = uselocale(new_code_page);

		std::vector<char> str_bytes((wstr.length() + 1) * sizeof(wchar_t));
		size_t ret = wcstombs(str_bytes.data(), wstr.c_str(), str_bytes.size());

		uselocale(old_code_page);
		freelocale(new_code_page);
		return str_bytes.data();
	} else {
		return std::wstring_convert<std::codecvt_utf8<wchar_t>>().to_bytes(wstr);
	}
}

int main(void)
{
	const std::wstring wstr(L"及田吸.mpg");
	std::string str_utf = cvt(wstr, false);
	std::string str_acp = cvt(wstr, true);
	std::cout << str_utf << '\n' << str_acp << std::endl;
	return 0;
}
