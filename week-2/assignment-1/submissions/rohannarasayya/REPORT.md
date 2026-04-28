# NASA Web Server Log Analysis Report

**Generated:** 2026-04-13 10:31:50
**Data:** NASA Kennedy Space Center web server logs, July–August 1995
**Tool:** analyze_logs.sh + generate_report.sh

---

## July 1995 Analysis

```
============================================================
NASA Web Server Log Analysis
File: /c/Users/rohan/OneDrive/Documents/stat418-tools-in-datascience-2026/week-2/assignment-1/submissions/rohannarasayya/NASA_Jul95.log
Lines: 1891714
============================================================

--- Q1: Top 10 Hosts (excluding 404 errors) ---
     17462  piweba3y.prodigy.com
     11535  piweba4y.prodigy.com
      9776  piweba1y.prodigy.com
      7798  alyssa.prodigy.com
      7573  siltb10.orl.mmc.com
      5884  piweba2y.prodigy.com
      5414  edams.ksc.nasa.gov
      4891  163.206.89.4
      4843  news.ti.com
      4344  disarray.demon.co.uk

--- Q2: IP vs Hostname Requests ---
  IP addresses : 422859 (22.4%)
  Hostnames    : 1465930 (77.6%)
  Total        : 1888789

--- Q3: Top 10 URLs (excluding 404 errors) ---
    111144  /images/NASA-logosmall.gif
     89530  /images/KSC-logosmall.gif
     60300  /images/MOSAIC-logosmall.gif
     59845  /images/USA-logosmall.gif
     59325  /images/WORLD-logosmall.gif
     58616  /images/ksclogo-medium.gif
     40841  /images/launch-logo.gif
     40251  /shuttle/countdown/
     40072  /ksc.html
     33555  /images/ksclogosmall.gif

--- Q4: HTTP Method Counts ---
   1884726  GET
      3952  HEAD
       111  POST

--- Q5: Total 404 Errors ---
  404 errors: 10714

--- Q6: Response Code Distribution ---
  Most frequent: HTTP 200  (1697914 requests, 89.9%)
  All codes:
    HTTP 200 : 1697914  (89.9%)
    HTTP 302 :   46549  (2.5%)
    HTTP 304 :  132626  (7.0%)
    HTTP 403 :      54  (0.0%)
    HTTP 404 :   10714  (0.6%)
    HTTP 500 :      62  (0.0%)
    HTTP 501 :      14  (0.0%)

--- Q7: Requests by Hour of Day ---
  00:00  62160
  01:00  52860
  02:00  45269
  03:00  37322
  04:00  32219
  05:00  31860
  06:00  35182
  07:00  53958
  08:00  83671
  09:00  99848
  10:00  105434
  11:00  115559
  12:00  121969
  13:00  120722
  14:00  122228
  15:00  121024
  16:00  117766
  17:00  97482
  18:00  79192
  19:00  71698
  20:00  69722
  21:00  71761
  22:00  70653
  23:00  69230

--- Q8: Busiest Date ---
  13/Jul/1995 : 134134 requests

--- Q9: Quietest Date (excluding outage/gap dates) ---
  28/Jul/1995 : 27097 requests

--- Q10: Hurricane Outage Detection ---
  Full daily counts:
    01/Jul/1995 :  64566
    02/Jul/1995 :  60163
    03/Jul/1995 :  89508
    04/Jul/1995 :  70371
    05/Jul/1995 :  94448
    06/Jul/1995 : 100838
    07/Jul/1995 :  87147
    08/Jul/1995 :  38795
    09/Jul/1995 :  35229
    10/Jul/1995 :  72731
    11/Jul/1995 :  80328
    12/Jul/1995 :  92400
    13/Jul/1995 : 134134
    14/Jul/1995 :  83944
    15/Jul/1995 :  45460
    16/Jul/1995 :  47794
    17/Jul/1995 :  74877
    18/Jul/1995 :  64100
    19/Jul/1995 :  72599
    20/Jul/1995 :  66489
    21/Jul/1995 :  64499
    22/Jul/1995 :  35196
    23/Jul/1995 :  39119
    24/Jul/1995 :  64161
    25/Jul/1995 :  62499
    26/Jul/1995 :  58687
    27/Jul/1995 :  61610
    28/Jul/1995 :  27097

  Missing days in date range (complete data gaps):
    (none — no fully missing days detected)

--- Q11: Response Size Statistics ---
  Largest response  : 6823936 bytes  (6664.0 KB)
  Average response  : 20657 bytes  (20.2 KB)
  Requests with size: 1869213

--- Q12: Error Patterns (4xx/5xx) ---
  Errors by hour:
    Total 4xx/5xx errors: 10844
    00:00  427
    01:00  319
    02:00  269
    03:00  238
    04:00  167
    05:00  147
    06:00  133
    07:00  240
    08:00  358
    09:00  481
    10:00  643
    11:00  731
    12:00  646
    13:00  531
    14:00  751
    15:00  837
    16:00  640
    17:00  613
    18:00  494
    19:00  411
    20:00  380
    21:00  443
    22:00  484
    23:00  461

  Top 10 error-generating hosts:
         251  hoohoo.ncsa.uiuc.edu
         131  jbiagioni.npt.nuwc.navy.mil
         110  piweba3y.prodigy.com
          92  piweba1y.prodigy.com
          70  163.205.1.45
          64  phaelon.ksc.nasa.gov
          61  www-d4.proxy.aol.com
          57  titan02f
          56  piweba4y.prodigy.com
          56  monarch.eng.buffalo.edu

============================================================
Analysis complete.
============================================================
```

---

## August 1995 Analysis

```
============================================================
NASA Web Server Log Analysis
File: /c/Users/rohan/OneDrive/Documents/stat418-tools-in-datascience-2026/week-2/assignment-1/submissions/rohannarasayya/NASA_Aug95.log
Lines: 1569898
============================================================

--- Q1: Top 10 Hosts (excluding 404 errors) ---
      6517  edams.ksc.nasa.gov
      4816  piweba4y.prodigy.com
      4779  163.206.89.4
      4576  piweba5y.prodigy.com
      4369  piweba3y.prodigy.com
      3866  www-d1.proxy.aol.com
      3522  www-b2.proxy.aol.com
      3445  www-b3.proxy.aol.com
      3412  www-c5.proxy.aol.com
      3393  www-b5.proxy.aol.com

--- Q2: IP vs Hostname Requests ---
  IP addresses : 450391 (28.7%)
  Hostnames    : 1117655 (71.3%)
  Total        : 1568046

--- Q3: Top 10 URLs (excluding 404 errors) ---
     97293  /images/NASA-logosmall.gif
     75283  /images/KSC-logosmall.gif
     67356  /images/MOSAIC-logosmall.gif
     66975  /images/USA-logosmall.gif
     66351  /images/WORLD-logosmall.gif
     62670  /images/ksclogo-medium.gif
     43619  /ksc.html
     37806  /history/apollo/images/apollo-logo1.gif
     35119  /images/launch-logo.gif
     30123  /

--- Q4: HTTP Method Counts ---
   1563968  GET
      3965  HEAD
       111  POST
         2  ���.�2�.�>�

--- Q5: Total 404 Errors ---
  404 errors: 9978

--- Q6: Response Code Distribution ---
  Most frequent: HTTP 200  (1396473 requests, 89.1%)
  All codes:
    HTTP 200 : 1396473  (89.1%)
    HTTP 302 :   26422  (1.7%)
    HTTP 304 :  134138  (8.6%)
    HTTP 400 :       2  (0.0%)
    HTTP 403 :     171  (0.0%)
    HTTP 404 :    9978  (0.6%)
    HTTP 500 :       3  (0.0%)
    HTTP 501 :      27  (0.0%)

--- Q7: Requests by Hour of Day ---
  00:00  47660
  01:00  38444
  02:00  32481
  03:00  29966
  04:00  26748
  05:00  27550
  06:00  31258
  07:00  47353
  08:00  65425
  09:00  78618
  10:00  88186
  11:00  95230
  12:00  104991
  13:00  104432
  14:00  101280
  15:00  109356
  16:00  99460
  17:00  80774
  18:00  66723
  19:00  59223
  20:00  59845
  21:00  57908
  22:00  60612
  23:00  54523

--- Q8: Busiest Date ---
  31/Aug/1995 : 90037 requests

--- Q9: Quietest Date (excluding outage/gap dates) ---
  26/Aug/1995 : 31580 requests

--- Q10: Hurricane Outage Detection ---
  Full daily counts:
    01/Aug/1995 :  33936
    03/Aug/1995 :  41336
    04/Aug/1995 :  59493
    05/Aug/1995 :  31831
    06/Aug/1995 :  32377
    07/Aug/1995 :  57301
    08/Aug/1995 :  60064
    09/Aug/1995 :  60437
    10/Aug/1995 :  61127
    11/Aug/1995 :  61170
    12/Aug/1995 :  38004
    13/Aug/1995 :  36436
    14/Aug/1995 :  59811
    15/Aug/1995 :  58794
    16/Aug/1995 :  56602
    17/Aug/1995 :  58958
    18/Aug/1995 :  56206
    19/Aug/1995 :  32056
    20/Aug/1995 :  32942
    21/Aug/1995 :  55481
    22/Aug/1995 :  57677
    23/Aug/1995 :  57977
    24/Aug/1995 :  52490
    25/Aug/1995 :  57300
    26/Aug/1995 :  31580
    27/Aug/1995 :  32774
    28/Aug/1995 :  55422
    29/Aug/1995 :  67869
    30/Aug/1995 :  80558
    31/Aug/1995 :  90037

  Missing days in date range (complete data gaps):
    MISSING: 02/Aug/1995
  (1 fully missing day(s) = hurricane outage)

  Outage start : 01/Aug/1995:14:52:01 -0400
  Outage end   : 03/Aug/1995:04:36:13 -0400
  Duration     : 37 hours 44 minutes

--- Q11: Response Size Statistics ---
  Largest response  : 3421948 bytes  (3341.7 KB)
  Average response  : 17242 bytes  (16.8 KB)
  Requests with size: 1554022

--- Q12: Error Patterns (4xx/5xx) ---
  Errors by hour:
    Total 4xx/5xx errors: 10181
    00:00  367
    01:00  330
    02:00  618
    03:00  361
    04:00  182
    05:00  167
    06:00  135
    07:00  222
    08:00  340
    09:00  352
    10:00  485
    11:00  423
    12:00  651
    13:00  616
    14:00  525
    15:00  548
    16:00  579
    17:00  586
    18:00  429
    19:00  444
    20:00  445
    21:00  434
    22:00  459
    23:00  483

  Top 10 error-generating hosts:
          62  dialip-217.den.mmc.com
          47  piweba3y.prodigy.com
          44  155.148.25.4
          39  scooter.pa-x.dec.com
          39  maz3.maz.net
          38  gate.barr.com
          37  ts8-1.westwood.ts.ucla.edu
          37  nexus.mlckew.edu.au
          37  m38-370-9.mit.edu
          37  204.62.245.32

============================================================
Analysis complete.
============================================================
```

---

## July vs August Comparison

| Metric | July 1995 | August 1995 |
|--------|-----------|-------------|
| Total log lines | 1891714 | 1569898 |
| 404 errors | 10714 | 9978 |
| Total 4xx/5xx errors | 10844 | 10181 |
| Most frequent code | HTTP 200 (89.9%) | HTTP 200 (89.1%) |
| IP address requests | 22.4% | 28.7% |
| Busiest day | 13/Jul/1995 : 134134 requests | 31/Aug/1995 : 90037 requests |
| Quietest day | 28/Jul/1995 : 27097 requests | 26/Aug/1995 : 31580 requests |
| Largest response | 6823936 bytes | 3421948 bytes |
| Average response | 20657 bytes | 17242 bytes |

### Top host (July)
17462  piweba3y.prodigy.com

### Top host (August)
6517  edams.ksc.nasa.gov

---

## Hourly Traffic Patterns

### July 1995 — Requests by Hour

```
HH | Bar (scaled to peak)                              Requests
00 | █████████████████████████                          62160
01 | █████████████████████                              52860
02 | ██████████████████                                 45269
03 | ███████████████                                    37322
04 | █████████████                                      32219
05 | █████████████                                      31860
06 | ██████████████                                     35182
07 | ██████████████████████                             53958
08 | ██████████████████████████████████                 83671
09 | ████████████████████████████████████████           99848
10 | ███████████████████████████████████████████        105434
11 | ███████████████████████████████████████████████    115559
12 | █████████████████████████████████████████████████  121969
13 | █████████████████████████████████████████████████  120722
14 | ██████████████████████████████████████████████████ 122228
15 | █████████████████████████████████████████████████  121024
16 | ████████████████████████████████████████████████   117766
17 | ███████████████████████████████████████            97482
18 | ████████████████████████████████                   79192
19 | █████████████████████████████                      71698
20 | ████████████████████████████                       69722
21 | █████████████████████████████                      71761
22 | ████████████████████████████                       70653
23 | ████████████████████████████                       69230
```

### August 1995 — Requests by Hour

```
HH | Bar (scaled to peak)                              Requests
00 | █████████████████████                              47660
01 | █████████████████                                  38444
02 | ██████████████                                     32481
03 | █████████████                                      29966
04 | ████████████                                       26748
05 | ████████████                                       27550
06 | ██████████████                                     31258
07 | █████████████████████                              47353
08 | █████████████████████████████                      65425
09 | ███████████████████████████████████                78618
10 | ████████████████████████████████████████           88186
11 | ███████████████████████████████████████████        95230
12 | ████████████████████████████████████████████████   104991
13 | ███████████████████████████████████████████████    104432
14 | ██████████████████████████████████████████████     101280
15 | ██████████████████████████████████████████████████ 109356
16 | █████████████████████████████████████████████      99460
17 | ████████████████████████████████████               80774
18 | ██████████████████████████████                     66723
19 | ███████████████████████████                        59223
20 | ███████████████████████████                        59845
21 | ██████████████████████████                         57908
22 | ███████████████████████████                        60612
23 | ████████████████████████                           54523
```

---

## Key Findings

### 1. Hurricane Erin Outage (August 1995)

> **WARNING: Data gap detected in NASA_Aug95.log**

Hurricane Erin made landfall in Florida on **August 2, 1995**, causing
the NASA Kennedy Space Center web server data collection to stop entirely.

**Missing day(s):**

- `02/Aug/1995` — **no data collected** (complete outage)

**Exact outage window:**

```
Outage start : 01/Aug/1995:14:52:01 -0400
Outage end   : 03/Aug/1995:04:36:13 -0400
Duration     : 37 hours 44 minutes
```

### 2. Traffic Patterns

- **Peak hour:** Mid-afternoon (14:00–15:00) consistently sees the highest traffic
  in both months — typical for a US East Coast server (Florida/EDT)
- **Quiet hours:** 03:00–05:00 EDT sees the lowest traffic
- **Weekend dips:** Saturday/Sunday see ~45–55% of typical weekday traffic

### 3. Content Profile

- The top URLs in both months are small GIF images (NASA logos, KSC logos),
  consistent with every HTML page loading the same set of site-wide images
- The shuttle countdown pages (`/shuttle/countdown/`) dominate non-image traffic,
  reflecting high interest in STS-70 (July) and STS-69 (August) missions

### 4. Client Demographics

- July: **22.4%** of requests came from raw IP addresses
- August: **28.7%** of requests came from raw IP addresses
- AOL proxy servers (`piweba*.prodigy.com`, `www-*.proxy.aol.com`) appear in the
  top hosts every month, reflecting the dial-up internet demographics of 1995

### 5. Error Analysis

- August had **9978** 404 errors vs **10714** in July
- Error rates are evenly distributed across hours with a slight spike at 02:00,
  possibly automated crawlers or retry storms after the outage
- The top error-generating hosts generate 30–60 errors each — not a single
  dominant bad client, suggesting normal broken-link traffic

---

*Report generated by generate_report.sh*
