# NASA Web Logs — Combined Report

_Generated: 2026-04-21 06:19:57Z (UTC)_

## Summary

July parsed lines: **1891714**. August parsed lines: **1569898** (ratio August/July = **0.830x**).
Net change (Aug - Jul): **-321816** requests (**-17.01%**).

## Comparison

| Metric | July | August |
| --- | ---: | ---: |
| Parsed requests | 1891714 | 1569898 |
| 404 errors | 10845 | 10056 |
| IP share | 22.16% | 28.44% |
| Peak hour (count) | 14 (122479) | 15 (109465) |
| Busiest day (count) | 13/Jul/1995 (134203) | 31/Aug/1995 (90125) |
| Largest response (bytes) | 6823936 | 3421948 |

## Hour-of-day (ASCII)

### July

```
00 |#################### 62450
01 |################# 53066
02 |############### 45297
03 |############ 37398
04 |########### 32234
05 |########## 31919
06 |############ 35253
07 |################## 54017
08 |########################### 83750
09 |################################# 99969
10 |################################## 105507
11 |###################################### 115720
12 |######################################## 122085
13 |####################################### 120814
14 |######################################## 122479
15 |######################################## 121200
16 |####################################### 118037
17 |################################ 97609
18 |########################## 79282
19 |####################### 71776
20 |####################### 69809
21 |####################### 71922
22 |####################### 70759
23 |####################### 69362
```

### August

```
00 |################# 47862
01 |############## 38531
02 |############ 32508
03 |########### 29995
04 |########## 26756
05 |########## 27587
06 |########### 31287
07 |################# 47386
08 |######################## 65443
09 |############################# 78695
10 |################################ 88309
11 |################################### 95344
12 |###################################### 105143
13 |###################################### 104536
14 |##################################### 101394
15 |######################################## 109465
16 |#################################### 99527
17 |############################## 80834
18 |######################## 66809
19 |###################### 59315
20 |###################### 59944
21 |##################### 57985
22 |###################### 60673
23 |#################### 54570
```

## Highlights

- **Traffic volume:** August has **-321816** fewer parsed requests than July (-17.01% change).
- **Error trend:** 404 count changed from **10845** (Jul) to **10056** (Aug), difference **-789** (-7.28%).
- **Client mix:** IP-share rises from **22.16%** in July to **28.44%** in August.
- **Peak load shifts:** peak hour moves from **14** (Jul) to **15** (Aug).
- **Anomaly note:** August shows a long logging gap; see the August continuity section for exact timestamps.

## July — full analysis

#### Analysis: `NASA_Jul95`

Source: `/Users/www1/Desktop/stat418-tools-in-datascience-2026/week-2/assignment-1/submissions/mikewu/data/NASA_Jul95.log`

##### Parsing

- Parsed requests: **1891714**
- Skipped bad lines: **1**

##### Basic analysis

###### Top 10 hosts (404 excluded)

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

###### IP vs hostname

IPv4 requests: **419140** (**22.16%**).
Hostname requests: **1472574** (**77.84%**).

###### Top 10 URLs (404 excluded)

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

###### HTTP methods

| Method | Count |
| --- | ---: |
| GET | 1887646 |
| HEAD | 3952 |
| POST | 111 |

###### 404 errors

**10845** responses with status 404.

###### Response codes

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

##### Time-based analysis

###### Requests by hour

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

###### Busiest day

**13/Jul/1995** with **134203** requests.

###### Quietest normal day

Among days with at least half the median daily traffic: **22/Jul/1995** (**35267** requests; median daily **64629**).

##### Advanced

###### Continuity / gaps (August)

No large gap found between minutes that have at least one request.

###### Response sizes

- Largest: **6823936** bytes
- Example line: `derec - - [07/Jul/1995:14:03:32 -0400] "GET /shuttle/countdown/video/livevideo.jpeg HTTP/1.0" 200 6823936`
- Average (numeric bytes only): **20671.06** over 1871988 responses

###### Errors (status >= 400) by hour

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

###### Top hosts for errors

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

## August — full analysis

#### Analysis: `NASA_Aug95`

Source: `/Users/www1/Desktop/stat418-tools-in-datascience-2026/week-2/assignment-1/submissions/mikewu/data/NASA_Aug95.log`

##### Parsing

- Parsed requests: **1569898**
- Skipped bad lines: **0**

##### Basic analysis

###### Top 10 hosts (404 excluded)

1. `edams.ksc.nasa.gov` — 6517 requests
2. `piweba4y.prodigy.com` — 4816 requests
3. `163.206.89.4` — 4779 requests
4. `piweba5y.prodigy.com` — 4576 requests
5. `piweba3y.prodigy.com` — 4369 requests
6. `www-d1.proxy.aol.com` — 3866 requests
7. `www-b2.proxy.aol.com` — 3522 requests
8. `www-b3.proxy.aol.com` — 3445 requests
9. `www-c5.proxy.aol.com` — 3412 requests
10. `www-b5.proxy.aol.com` — 3393 requests

###### IP vs hostname

IPv4 requests: **446494** (**28.44%**).
Hostname requests: **1123404** (**71.56%**).

###### Top 10 URLs (404 excluded)

1. `/images/NASA-logosmall.gif` — 97410 requests
2. `/images/KSC-logosmall.gif` — 75337 requests
3. `/images/MOSAIC-logosmall.gif` — 67448 requests
4. `/images/USA-logosmall.gif` — 67068 requests
5. `/images/WORLD-logosmall.gif` — 66444 requests
6. `/images/ksclogo-medium.gif` — 62778 requests
7. `/ksc.html` — 43687 requests
8. `/history/apollo/images/apollo-logo1.gif` — 37826 requests
9. `/images/launch-logo.gif` — 35138 requests
10. `/` — 30347 requests

###### HTTP methods

| Method | Count |
| --- | ---: |
| GET | 1565812 |
| HEAD | 3965 |
| POST | 111 |

###### 404 errors

**10056** responses with status 404.

###### Response codes

Most common status: **200** (1398988 hits, 89.11% of lines).

| Code | Count |
| --- | ---: |
| 200 | 1398988 |
| 304 | 134146 |
| 302 | 26497 |
| 404 | 10056 |
| 403 | 171 |
| 501 | 27 |
| 400 | 10 |
| 500 | 3 |

##### Time-based analysis

###### Requests by hour

| Hour | Count |
| --- | ---: |
| 00 | 47862 |
| 01 | 38531 |
| 02 | 32508 |
| 03 | 29995 |
| 04 | 26756 |
| 05 | 27587 |
| 06 | 31287 |
| 07 | 47386 |
| 08 | 65443 |
| 09 | 78695 |
| 10 | 88309 |
| 11 | 95344 |
| 12 | 105143 |
| 13 | 104536 |
| 14 | 101394 |
| 15 | 109465 |
| 16 | 99527 |
| 17 | 80834 |
| 18 | 66809 |
| 19 | 59315 |
| 20 | 59944 |
| 21 | 57985 |
| 22 | 60673 |
| 23 | 54570 |

Peak hour: **15**
Quietest hour (with traffic): **4** (26756 requests)
Minimum hour bucket: **4** (26756 requests)

###### Busiest day

**31/Aug/1995** with **90125** requests.

###### Quietest normal day

Among days with at least half the median daily traffic: **26/Aug/1995** (**31608** requests; median daily **56653**).

##### Advanced

###### Continuity / gaps (August)

Gap between minutes that still have requests: **01/Aug/1995 14:52** then **03/Aug/1995 04:36** (~37.73 hours apart by minute index).

Longest stretch with **zero lines** every clock hour: Aug 01 15:00 to Aug 03 03:59 (37 hours).

###### Response sizes

- Largest: **3421948** bytes
- Example line: `163.205.156.16 - - [03/Aug/1995:15:51:23 -0400] "GET /statistics/1995/Jul/Jul95_reverse_domains.html HTTP/1.0" 200 3421948`
- Average (numeric bytes only): **17244.97** over 1555720 responses

###### Errors (status >= 400) by hour

| Hour | Errors |
| --- | ---: |
| 00 | 368 |
| 01 | 332 |
| 02 | 618 |
| 03 | 364 |
| 04 | 185 |
| 05 | 168 |
| 06 | 135 |
| 07 | 223 |
| 08 | 341 |
| 09 | 363 |
| 10 | 494 |
| 11 | 436 |
| 12 | 653 |
| 13 | 619 |
| 14 | 528 |
| 15 | 560 |
| 16 | 582 |
| 17 | 587 |
| 18 | 431 |
| 19 | 444 |
| 20 | 448 |
| 21 | 437 |
| 22 | 465 |
| 23 | 486 |

###### Top hosts for errors

1. `dialip-217.den.mmc.com` — 62
2. `piweba3y.prodigy.com` — 47
3. `155.148.25.4` — 44
4. `scooter.pa-x.dec.com` — 39
5. `maz3.maz.net` — 39
6. `gate.barr.com` — 38
7. `ts8-1.westwood.ts.ucla.edu` — 37
8. `nexus.mlckew.edu.au` — 37
9. `m38-370-9.mit.edu` — 37
10. `204.62.245.32` — 37
