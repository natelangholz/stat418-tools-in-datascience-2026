# Analysis: `NASA_Jul95`

Source: `/Users/www1/Desktop/stat418-tools-in-datascience-2026/week-2/assignment-1/submissions/mikewu/data/NASA_Jul95.log`

## Parsing

- Parsed requests: **1891714**
- Skipped bad lines: **1**

## Basic analysis

### Top 10 hosts (404 excluded)

1. `piweba3y.prodigy.com` — 17462 requests
2. `piweba4y.prodigy.com` — 11535 requests
3. `piweba1y.prodigy.com` — 9776 requests
4. `alyssa.prodigy.com` — 7798 requests
5. `siltb10.orl.mmc.com` — 7573 requests
6. `piweba2y.prodigy.com` — 5884 requests
7. `edams.ksc.nasa.gov` — 5414 requests
8. `163.206.89.4` — 4891 requests
9. `news.ti.com` — 4843 requests
10. `disarray.demon.co.uk` — 4344 requests

### IP vs hostname

IPv4 requests: **419140** (**22.16%**).
Hostname requests: **1472574** (**77.84%**).

### Top 10 URLs (404 excluded)

1. `/images/NASA-logosmall.gif` — 111388 requests
2. `/images/KSC-logosmall.gif` — 89639 requests
3. `/images/MOSAIC-logosmall.gif` — 60468 requests
4. `/images/USA-logosmall.gif` — 60014 requests
5. `/images/WORLD-logosmall.gif` — 59489 requests
6. `/images/ksclogo-medium.gif` — 58802 requests
7. `/images/launch-logo.gif` — 40871 requests
8. `/shuttle/countdown/` — 40279 requests
9. `/ksc.html` — 40231 requests
10. `/images/ksclogosmall.gif` — 33585 requests

### HTTP methods

| Method | Count |
| --- | ---: |
| GET | 1887646 |
| HEAD | 3952 |
| POST | 111 |

### 404 errors

**10845** responses with status 404.

### Response codes

Most common status: **200** (1701534 hits, 89.95% of lines).

| Code | Count |
| --- | ---: |
| 200 | 1701534 |
| 304 | 132627 |
| 302 | 46573 |
| 404 | 10845 |
| 500 | 62 |
| 403 | 54 |
| 501 | 14 |
| 400 | 5 |

## Time-based analysis

### Requests by hour

| Hour | Count |
| --- | ---: |
| 00 | 62450 |
| 01 | 53066 |
| 02 | 45297 |
| 03 | 37398 |
| 04 | 32234 |
| 05 | 31919 |
| 06 | 35253 |
| 07 | 54017 |
| 08 | 83750 |
| 09 | 99969 |
| 10 | 105507 |
| 11 | 115720 |
| 12 | 122085 |
| 13 | 120814 |
| 14 | 122479 |
| 15 | 121200 |
| 16 | 118037 |
| 17 | 97609 |
| 18 | 79282 |
| 19 | 71776 |
| 20 | 69809 |
| 21 | 71922 |
| 22 | 70759 |
| 23 | 69362 |

Peak hour: **14**
Quietest hour (with traffic): **5** (31919 requests)
Minimum hour bucket: **5** (31919 requests)

### Busiest day

**13/Jul/1995** with **134203** requests.

### Quietest normal day

Among days with at least half the median daily traffic: **22/Jul/1995** (**35267** requests; median daily **64629**).

## Advanced

### Continuity / gaps (August)

No large gap found between minutes that have at least one request.

### Response sizes

- Largest: **6823936** bytes
- Example line: `derec - - [07/Jul/1995:14:03:32 -0400] "GET /shuttle/countdown/video/livevideo.jpeg HTTP/1.0" 200 6823936`
- Average (numeric bytes only): **20671.06** over 1871988 responses

### Errors (status >= 400) by hour

| Hour | Errors |
| --- | ---: |
| 00 | 432 |
| 01 | 321 |
| 02 | 269 |
| 03 | 240 |
| 04 | 168 |
| 05 | 148 |
| 06 | 134 |
| 07 | 243 |
| 08 | 366 |
| 09 | 483 |
| 10 | 649 |
| 11 | 744 |
| 12 | 658 |
| 13 | 542 |
| 14 | 756 |
| 15 | 844 |
| 16 | 651 |
| 17 | 619 |
| 18 | 507 |
| 19 | 416 |
| 20 | 383 |
| 21 | 448 |
| 22 | 488 |
| 23 | 471 |

### Top hosts for errors

1. `hoohoo.ncsa.uiuc.edu` — 251
2. `jbiagioni.npt.nuwc.navy.mil` — 131
3. `piweba3y.prodigy.com` — 110
4. `piweba1y.prodigy.com` — 92
5. `163.205.1.45` — 70
6. `phaelon.ksc.nasa.gov` — 64
7. `www-d4.proxy.aol.com` — 61
8. `titan02f` — 57
9. `piweba4y.prodigy.com` — 56
10. `monarch.eng.buffalo.edu` — 56
