#pragma once
#include <iostream>
#ifdef STRINGID_EXPORTS
#define STRINGID_API __declspec(dllexport)
#else
#define STRINGID_API __declspec(dllexport)
#endif

extern "C" STRINGID_API uint32_t StrToCRC(int _stride, std::string _str, uint32_t _len);