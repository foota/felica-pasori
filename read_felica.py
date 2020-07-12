#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
read_felica.py  by nox
Suicaの履歴を出力するプログラム.
SONY PaSoRi RC-S320
"""

import re
from ctypes import *

VERSION = "0.03"
REVISION = "c"

POLLING_ANY = 0xFFFF
POLLING_SUICA = 0x0003
POLLING_EDY = 0xFE00

SERVICE_SUICA = 0x090F
SERVICE_EDY = 0x170F

# 端末種.
TERMINAL = {
    3: "精算機",
    4: "携帯型端末",
    5: "車載端末",
    7: "券売機",
    8: "券売機",
    9: "入金機",
    18: "券売機",
    20: "券売機等",
    21: "券売機等",
    22: "改札機",
    23: "簡易改札機",
    24: "窓口端末",
    25: "窓口端末",
    26: "改札端末",
    27: "携帯電話",
    28: "乗継精算機",
    29: "連絡改札機",
    31: "簡易入金機",
    70: "VIEW ALTTE",
    72: "VIEW ALTTE",
    199: "物販端末",
    200: "自販機",
}

# 処理.
PROCESS = {
    1: "運賃支払(改札出場)",
    2: "チャージ",
    3: "券購(磁気券購入)",
    4: "精算",
    5: "精算 (入場精算)",
    6: "窓出 (改札窓口処理)",
    7: "新規 (新規発行)",
    8: "控除 (窓口控除)",
    13: "バス (PiTaPa系)",
    15: "バス (IruCa系)",
    17: "再発 (再発行処理)",
    19: "支払 (新幹線利用)",
    20: "入A (入場時オートチャージ)",
    21: "出A (出場時オートチャージ)",
    31: "入金 (バスチャージ)",
    35: "券購 (バス路面電車企画券購入)",
    70: "物販",
    72: "特典 (特典チャージ)",
    73: "入金 (レジ入金)",
    74: "物販取消",
    75: "入物 (入場物販)",
    198: "物現 (現金併用物販)",
    203: "入物 (入場現金併用物販)",
    132: "精算 (他社精算)",
    133: "精算 (他社入場精算)",
}

STATION_CODE = {}


def read_station_code(fname: str) -> None:
    global STATION_CODE
    data = [
        l.strip().split(",")
        for l in open(fname, encoding="utf-8_sig")
        if re.match(r"[\da-fA-F]", l[0])
    ]
    for d in data:
        STATION_CODE[tuple(map(lambda x: int(x, 16), d[0:3]))] = (d[4], d[5])


def read_felica() -> list:
    flib = cdll.felicalib

    flib.pasori_open.restype = c_void_p
    pasori = flib.pasori_open()

    flib.pasori_init.argtypes = (c_void_p,)
    flib.pasori_init(pasori)

    flib.felica_polling.argtypes = (c_void_p, c_int16, c_int8, c_int8)
    flib.felica_polling.restype = c_void_p
    felica = flib.felica_polling(pasori, POLLING_SUICA, 0, 0)  # Suicaを読む.

    if not felica:
        return []

    # 履歴の読み出し.
    data = []
    d = create_string_buffer(16)
    i = 0
    flib.felica_read_without_encryption02.argtypes = (
        c_void_p,
        c_int,
        c_int,
        c_int8,
        c_void_p,
    )
    while flib.felica_read_without_encryption02(felica, SERVICE_SUICA, 0, i, d) == 0:
        data.append(string_at(pointer(d), 16))
        i += 1

    flib.pasori_close.argtypes = (c_void_p,)
    flib.pasori_close(pasori)

    return data


def parse_data(d: bytes, prev: int = -1) -> int:
    global STATION_CODE

    term = d[0]  # 端末種.
    proc = d[1]  # 処理.
    date = d[4:6]  # 日付.
    year = (date[0] >> 1) + 2000  # 年.
    month = ((date[0] & 1) << 3) + (date[1] >> 5)  # 月.
    day = date[1] & (1 << 5) - 1  # 日.
    in_line = d[6]  # 入線区.
    in_sta = d[7]  # 入駅順.
    out_line = d[8]  # 出線区.
    out_sta = d[9]  # 出駅順.
    balance = d[10:12]  # 残高.
    num = d[12:15]  # 連番.
    region = d[15]  # リージョン.

    print("{:4d}年{:02d}月{:02d}日".format(year, month, day), end=" ")
    if proc in (70, 73, 74, 75, 198, 203):  # 物販.
        h = in_line >> 3  # 時.
        m = ((in_line & 7) << 3) + (in_sta >> 5)  # 分.
        s = (in_sta & 0x1F) << 1  # 秒.
        print("{:02d}時{:02d}分{:02d}秒".format(h, m, s), end=" ")
        print("買物", end=" ")
    elif proc in (13, 15, 31, 35):  # バス.
        out_line_ = d[6:8]
        out_sta_ = d[8:10]
        print("バス", end=" ")
    else:
        if region == 0:
            if in_line < 0x80:
                area = 0  # JR線.
            else:
                area = 1  # 関東公営・私鉄.
        else:
            area = 2  # 関西公営・私鉄.
        if in_line not in (0xC7, 0xC8, 0x05):
            if (area, in_line, in_sta) in STATION_CODE:
                print("{}駅".format(STATION_CODE[(area, in_line, in_sta)][1]), end=" ")
            else:
                print("不明", end=" ")
            if (area, out_line, out_sta) in STATION_CODE:
                if not (area == 0 and out_line == 0 and out_sta == 0):
                    print(
                        "{}駅".format(STATION_CODE[(area, out_line, out_sta)][1]),
                        end=" ",
                    )
            else:
                print("不明", end=" ")
    account = (balance[1] << 8) + balance[0]
    charge = prev - account
    if prev < 0:
        print("---円", end=" ")
    elif charge > 0:
        print("{}円".format(charge), end=" ")
    elif charge < 0:
        print("{:+d}円".format(-charge), end=" ")
    print("{}円".format(account), end=" ")
    if term in TERMINAL:
        print(TERMINAL[term], end=" ")
    else:
        print("不明", end=" ")
    if proc in PROCESS:
        print(PROCESS[proc], end=" ")
    else:
        print("不明", end=" ")
    print()

    return account


def main() -> None:
    #read_station_code("stations.csv")
    read_station_code("stationcode.csv")
    data = read_felica()
    if data:
        prev = -1
        for d in data[::-1]:
            prev = parse_data(d, prev)


if __name__ == "__main__":
    main()
