#include "pch.h"
#include <iostream>

void mix(uint32_t& a, uint32_t& b, uint32_t& c)
{
    a -= b; a -= c; a ^= c >> 13;
    b -= c; b -= a; b ^= a << 8;
    c -= a; c -= b; c ^= b >> 13;
    a -= b; a -= c; a ^= c >> 12;
    b -= c; b -= a; b ^= a << 16;
    c -= a; c -= b; c ^= b >> 5;
    a -= b; a -= c; a ^= c >> 3;
    b -= c; b -= a; b ^= a << 10;
    c -= a; c -= b; c ^= b >> 15;
}

char ToUp(char c)
{
    if (c < 'a' || c > 'z')
    {
        return c;
    }
    return (char)(c + 'A' - 'a');
}

void case1(uint32_t& a, uint32_t& b, uint32_t& c, int _stride, std::string _str) {
    a += ToUp(_str[0 * _stride]);
}

void case2(uint32_t& a, uint32_t& b, uint32_t& c, int _stride, std::string _str) {
    a += (uint32_t)ToUp(_str[1 * _stride]) << 8;
    case1(a, b, c, _stride, _str);
}

void case3(uint32_t& a, uint32_t& b, uint32_t& c, int _stride, std::string _str) {
    a += (uint32_t)ToUp(_str[2 * _stride]) << 16;
    case2(a, b, c, _stride, _str);
}

void case4(uint32_t& a, uint32_t& b, uint32_t& c, int _stride, std::string _str) {
    a += (uint32_t)ToUp(_str[3 * _stride]) << 24;
    case3(a, b, c, _stride, _str);
}

void case5(uint32_t& a, uint32_t& b, uint32_t& c, int _stride, std::string _str) {
    b += ToUp(_str[4 * _stride]);
    case4(a, b, c, _stride, _str);
}

void case6(uint32_t& a, uint32_t& b, uint32_t& c, int _stride, std::string _str) {
    b += (uint32_t)ToUp(_str[5 * _stride]) << 8;
    case5(a, b, c, _stride, _str);
}

void case7(uint32_t& a, uint32_t& b, uint32_t& c, int _stride, std::string _str) {
    b += (uint32_t)ToUp(_str[6 * _stride]) << 16;
    case6(a, b, c, _stride, _str);
}

void case8(uint32_t& a, uint32_t& b, uint32_t& c, int _stride, std::string _str) {
    b += (uint32_t)ToUp(_str[7 * _stride]) << 24;
    case7(a, b, c, _stride, _str);
}

void case9(uint32_t& a, uint32_t& b, uint32_t& c, int _stride, std::string _str) {
    c += (uint32_t)ToUp(_str[8 * _stride]) << 8;
    case8(a, b, c, _stride, _str);
}

void case10(uint32_t& a, uint32_t& b, uint32_t& c, int _stride, std::string _str) {
    c += (uint32_t)ToUp(_str[9 * _stride]) << 16;
    case9(a, b, c, _stride, _str);
}

void case11(uint32_t& a, uint32_t& b, uint32_t& c, int _stride, std::string _str) {
    c += (uint32_t)ToUp(_str[10 * _stride]) << 24;
    case10(a, b, c, _stride, _str);
}

// Credits to the guys from Ubi Montreal
// Based on Gear::Hash::Dobbs that shouldn't give names collisions.
uint32_t StrToCRC(int _stride, std::string _str, uint32_t _len)
{
    /* Set up the internal state */
    uint32_t Len = _len;
    uint32_t len = Len;
    uint32_t a = 0x9e3779b9; // the golden ratio; an arbitrary value
    uint32_t b = a;
    uint32_t c = 0;


    /*---------------------------------------- handle most of the key */
    while (len >= 12)
    {
        a += ToUp(_str[0 * _stride]) + ((uint32_t)(ToUp(_str[1 * _stride])) << 8) + ((uint32_t)(ToUp(_str[2 * _stride])) << 16) + ((uint32_t)(ToUp(_str[3 * _stride])) << 24);
        b += ToUp(_str[4 * _stride]) + ((uint32_t)(ToUp(_str[5 * _stride])) << 8) + ((uint32_t)(ToUp(_str[6 * _stride])) << 16) + ((uint32_t)(ToUp(_str[7 * _stride])) << 24);
        c += ToUp(_str[8 * _stride]) + ((uint32_t)(ToUp(_str[9 * _stride])) << 8) + ((uint32_t)(ToUp(_str[10 * _stride])) << 16) + ((uint32_t)(ToUp(_str[11 * _stride])) << 24);
        mix(a, b, c);
        //                _str += 12*_stride;
        _str = _str.substr(12 * _stride);
        len -= 12;
    }

    /*------------------------------------- handle the last 11 bytes */
    c += Len;
    switch (len)              /* all the case statements fall through */
    {
        case 11: case11(a, b, c, _stride, _str); break;
        case 10: case10(a, b, c, _stride, _str); break;
        case 9: case9(a, b, c, _stride, _str); break;
        /* the first byte of c is reserved for the length */
        case 8: case8(a, b, c, _stride, _str); break;
        case 7: case7(a, b, c, _stride, _str); break;
        case 6: case6(a, b, c, _stride, _str); break;
        case 5: case5(a, b, c, _stride, _str); break;
        case 4: case4(a, b, c, _stride, _str); break;
        case 3: case3(a, b, c, _stride, _str); break;
        case 2: case2(a, b, c, _stride, _str); break;
        case 1: case1(a, b, c, _stride, _str); break;
        /* case 0: nothing left to add */
    }

    mix(a, b, c);

    return c;
}

