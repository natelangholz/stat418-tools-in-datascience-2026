# Assignment 1 Report: NASA Web Server Log Analysis

Generated on: Tue Apr 21 15:38:49     2026

## Overview

This report analyzes the NASA July and August 1995 web server logs using bash, grep, awk, sed, sort, uniq, and other command-line tools.

## Executive Summary

- July total requests: **1891715**
- August total requests: **1569898**
- July 404 errors: **10845**
- August 404 errors: **10056**
- July IP-based requests: **22.16%**
- August IP-based requests: **28.44%**
- July peak hour: **14:00**
- August peak hour: **15:00**
- July busiest day: **13/Jul/1995**
- August busiest day: **31/Aug/1995**

## July vs August Comparison

| Metric | July | August |
|---|---:|---:|
| Total requests | 1891715 | 1569898 |
| 404 errors | 10845 | 10056 |
| IP request % | 22.16 | 28.44 |
| Peak hour | 14 | 15 |
| Busiest day | 13/Jul/1995 | 31/Aug/1995 |

## Hurricane Outage

The longest gap in the August log appears to run from **01/Aug/1995 14:52:01** to **03/Aug/1995 04:36:13**.

- Gap length (seconds): **135852**
- Gap length (hours): **37.74**

This is a data-driven way to identify the outage period from the log timestamps.

## July Details

### Top 10 Hosts (July, excluding 404s)

| Count | Value |
|---:|---|
| 17462 | piweba3y.prodigy.com |
| 11535 | piweba4y.prodigy.com |
| 9776 | piweba1y.prodigy.com |
| 7798 | alyssa.prodigy.com |
| 7573 | siltb10.orl.mmc.com |
| 5884 | piweba2y.prodigy.com |
| 5414 | edams.ksc.nasa.gov |
| 4891 | 163.206.89.4 |
| 4843 | news.ti.com |
| 4344 | disarray.demon.co.uk |

### Top 10 Requests (July, excluding 404s)

| Count | Value |
|---:|---|
| 111388 | /images/NASA-logosmall.gif |
| 89639 | /images/KSC-logosmall.gif |
| 60468 | /images/MOSAIC-logosmall.gif |
| 60014 | /images/USA-logosmall.gif |
| 59489 | /images/WORLD-logosmall.gif |
| 58802 | /images/ksclogo-medium.gif |
| 40871 | /images/launch-logo.gif |
| 40279 | /shuttle/countdown/ |
| 40231 | /ksc.html |
| 33585 | /images/ksclogosmall.gif |

### Request Types (July)

| Count | Value |
|---:|---|
| 1887646 | GET |
| 3952 | HEAD |
| 111 | POST |
| 6 | UNKNOWN |

### Response Codes (July)

| Count | Value |
|---:|---|
| 1701534 | 200 |
| 132627 | 304 |
| 46573 | 302 |
| 10845 | 404 |
| 62 | 500 |
| 54 | 403 |
| 14 | 501 |
| 5 | 400 |

### Hourly Activity (July)

```text
00 | #########################                          62450
01 | #####################                              53066
02 | ##################                                 45297
03 | ###############                                    37398
04 | #############                                      32234
05 | #############                                      31919
06 | ##############                                     35253
07 | ######################                             54017
08 | ##################################                 83750
09 | ########################################           99969
10 | ###########################################        105507
11 | ###############################################    115720
12 | #################################################  122085
13 | #################################################  120814
14 | ################################################## 122479
15 | #################################################  121200
16 | ################################################   118037
17 | #######################################            97609
18 | ################################                   79282
19 | #############################                      71776
20 | ############################                       69809
21 | #############################                      71922
22 | ############################                       70759
23 | ############################                       69362
```

## August Details

### Top 10 Hosts (August, excluding 404s)

| Count | Value |
|---:|---|
| 6517 | edams.ksc.nasa.gov |
| 4816 | piweba4y.prodigy.com |
| 4779 | 163.206.89.4 |
| 4576 | piweba5y.prodigy.com |
| 4369 | piweba3y.prodigy.com |
| 3866 | www-d1.proxy.aol.com |
| 3522 | www-b2.proxy.aol.com |
| 3445 | www-b3.proxy.aol.com |
| 3412 | www-c5.proxy.aol.com |
| 3393 | www-b5.proxy.aol.com |

### Top 10 Requests (August, excluding 404s)

| Count | Value |
|---:|---|
| 97410 | /images/NASA-logosmall.gif |
| 75337 | /images/KSC-logosmall.gif |
| 67448 | /images/MOSAIC-logosmall.gif |
| 67068 | /images/USA-logosmall.gif |
| 66444 | /images/WORLD-logosmall.gif |
| 62778 | /images/ksclogo-medium.gif |
| 43688 | /ksc.html |
| 37826 | /history/apollo/images/apollo-logo1.gif |
| 35138 | /images/launch-logo.gif |
| 30347 | / |

### Request Types (August)

| Count | Value |
|---:|---|
| 1565812 | GET |
| 3965 | HEAD |
| 111 | POST |
| 10 | UNKNOWN |

### Response Codes (August)

| Count | Value |
|---:|---|
| 1398988 | 200 |
| 134146 | 304 |
| 26497 | 302 |
| 10056 | 404 |
| 171 | 403 |
| 27 | 501 |
| 10 | 400 |
| 3 | 500 |

### Hourly Activity (August)

```text
00 | #####################                              47862
01 | #################                                  38531
02 | ##############                                     32508
03 | #############                                      29995
04 | ############                                       26756
05 | ############                                       27587
06 | ##############                                     31287
07 | #####################                              47386
08 | #############################                      65443
09 | ###################################                78695
10 | ########################################           88309
11 | ###########################################        95344
12 | ################################################   105143
13 | ###############################################    104536
14 | ##############################################     101394
15 | ################################################## 109465
16 | #############################################      99527
17 | ####################################               80834
18 | ##############################                     66809
19 | ###########################                        59315
20 | ###########################                        59944
21 | ##########################                         57985
22 | ###########################                        60673
23 | ########################                           54570
```

## Interesting Findings / Anomalies

- August contains a very large timestamp gap, which is consistent with the hurricane outage prompt in the assignment.
- The report compares request volume, 404 counts, request composition, and peak traffic timing across both months.
- ASCII charts were included to keep the report reproducible and terminal-friendly.

