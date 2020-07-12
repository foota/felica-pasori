#!/usr/bin/env python
# -*- coding: utf-8 -*-

import re
import time
import urllib.request
import sys

PATTERN = r"<tr><td>([\d,a-f,A-F]+)</td><td>(.*)</td><td>(.*)</td><td>(.*)</td><td>(.*)</td><td>(.*)</td><td>(.*)</td></tr>"
CSV_FILE = "stationcode.csv"
WAIT_TIME = 5


def get_lastpage(url: str) -> int:
    r = urllib.request.urlopen(url).read().decode("euc-jp")
    m = re.search(r'"last page"\>\[(\d+)\]', r)
    time.sleep(WAIT_TIME)
    if m:
        return int(m.group(1))
    return 0


def main() -> None:
    url = "http://www.denno.net/SFCardFan/index.php?pageID={}"
    f = open(CSV_FILE, "w", encoding="utf-8")
    lastpage = get_lastpage(url.format(1))
    print("num of pages: {}".format(lastpage))
    for page in range(lastpage):
        print("page: {}".format(page + 1))
        r = (
            urllib.request.urlopen(url.format(page + 1))
            .read()
            .decode("euc-jp")
            .split("\n")
        )
        for line in r:
            m = re.search(PATTERN, line)
            if m:
                f.write(
                    ",".join(["{}".format(m.group(i + 1)) for i in range(7)]) + "\n"
                )
        time.sleep(WAIT_TIME)
    f.close()


if __name__ == "__main__":
    main()
