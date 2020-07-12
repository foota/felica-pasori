# felica-pasori
Programs for the USB NFC Reader SONY PaSoRi RC-S320

## Preparation

* Microsoft Windows 10 / x64
* SONY PaSoRi RC-S320
  * Install the driver from https://www.sony.co.jp/Products/felica/consumer/download/old2_felicaportsoftware.html

## Build

* Get 'felicalib-0.4.2' from https://github.com/tmurakam/felicalib/releases
* Build using VS2019 with src/FelicaLib.sln [optional: for x64 environment]
  * Replace 'afxres.h' to 'winres.h' in 'felicalib.rc'
  * Replace 'Release/Win32' to 'Release/x64' in the Configuration Manager
  * Build 'felicalib'
* Add 'felicalib.dll' to your system path
* Get 'StationCode.xls' from http://www.denno.net/SFCardFan/index.php
  * Convert from Excel format to CSV (UTF-8) format
  * Rename to 'stationcode.csv'

## Usage

* python read_felica.py

## Files

* README.md
  * This file
* read_felica.py
  * Display the Suica record by the NFC Reader PaSoRi
* get_stationcode.py
  * Script file for web scraping, if you cannot get 'StationCode.xls' from http://www.denno.net/SFCardFan/index.php
