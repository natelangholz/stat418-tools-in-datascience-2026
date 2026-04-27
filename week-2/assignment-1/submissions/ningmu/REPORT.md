# NASA Web Server Log Analysis Report

**Author:** Christine (ningmu)
**Generated:** 2026-04-19 01:06:19
**Data sources:**
- `data/NASA_Jul95.log`
- `data/NASA_Aug95.log`

---

## Executive Summary

This report analyses NASA Kennedy Space Center web server access logs from
**July 1995** and **August 1995**. The August data contains a noticeable
gap caused by **Hurricane Erin**, which knocked the NASA KSC network
offline for several days.

| Metric          | July 1995    | August 1995  |
|-----------------|--------------|--------------|
| Total requests  | 1891714 | 1569898 |
| 404 errors      | 10714   | 9978   |

---

## July 1995 - Detailed Findings

### 1. Top 10 hosts (excluding 404s)
```
  17462 piweba3y.prodigy.com
  11535 piweba4y.prodigy.com
   9776 piweba1y.prodigy.com
   7798 alyssa.prodigy.com
   7573 siltb10.orl.mmc.com
   5884 piweba2y.prodigy.com
   5414 edams.ksc.nasa.gov
   4891 163.206.89.4
   4843 news.ti.com
   4344 disarray.demon.co.uk
```

### 2. IP addresses vs hostnames
```
IP requests:       419140 (22.16%)
Hostname requests: 1472574 (77.84%)
```

### 3. Top 10 most-requested URLs (excluding 404s)
```
 111388 /images/NASA-logosmall.gif
  89639 /images/KSC-logosmall.gif
  60468 /images/MOSAIC-logosmall.gif
  60014 /images/USA-logosmall.gif
  59489 /images/WORLD-logosmall.gif
  58802 /images/ksclogo-medium.gif
  40871 /images/launch-logo.gif
  40279 /shuttle/countdown/
  40231 /ksc.html
  33585 /images/ksclogosmall.gif
```

### 4. HTTP methods
```
1887646 GET
   3952 HEAD
    111 POST
```

### 5. 404 errors
```
404 errors: 10714 (0.57% of all responses)
```

### 6. Response code distribution
```
1697914 200
 132626 304
  46549 302
  10714 404
    169 234
    168 363
     62 500
     54 403
     19 509
     14 501
     13 527
      9 543
      8 156
      7 308
      4 515
      3 598
      3 374
      3 306
      3 111
      2 378
      2 368
      2 286
      2 263
      1 421
      1 377
      1 305
      1 225
      1 110

Most frequent response code:
  code=200  count=1697914  percentage=89.76%
```

### 7. Activity by hour of day
```
  62450 00
  53066 01
  45297 02
  37398 03
  32234 04
  31919 05
  35253 06
  54017 07
  83750 08
  99969 09
 105507 10
 115720 11
 122085 12
 120814 13
 122479 14
 121200 15
 118037 16
  97609 17
  79282 18
  71776 19
  69809 20
  71922 21
  70759 22
  69362 23

Peak 3 hours:
 122479 14
 122085 12
 121200 15

Quietest 3 hours:
  31919 05
  32234 04
  35253 06
```

### 8. Busiest day
```
 134203 13/Jul/1995
```

### 9. Quietest day
```
  27121 28/Jul/1995
```

### 10. Outage detection
```
Largest gap: 13/Jul/1995 19:48:59  ->  13/Jul/1995 20:11:05
Outage duration: 1326 seconds (0h 22m 6s)
```

### 11. Response size
```
Largest response: 6823936 bytes
Average response: 20657.68 bytes
Total bytes served: 38612759306
```

### 12. Error patterns
```
Errors (4xx/5xx) by hour of day:
    475 00
    356 01
    279 02
    254 03
    169 04
    160 05
    145 06
    254 07
    371 08
    498 09
    654 10
    766 11
    670 12
    542 13
    794 14
    867 15
    677 16
    636 17
    503 18
    426 19
    397 20
    471 21
    506 22
    492 23

Top 10 hosts generating errors (4xx/5xx):
    251 hoohoo.ncsa.uiuc.edu
    131 jbiagioni.npt.nuwc.navy.mil
    110 piweba3y.prodigy.com
     92 piweba1y.prodigy.com
     70 163.205.1.45
     64 phaelon.ksc.nasa.gov
     61 www-d4.proxy.aol.com
     57 titan02f
     56 piweba4y.prodigy.com
     56 monarch.eng.buffalo.edu

Top 10 URLs producing errors:
    667 /pub/winvn/readme.txt
    547 /pub/winvn/release.txt
    286 /history/apollo/apollo-13.html
    230 /shuttle/resources/orbiters/atlantis.gif
    230 /history/apollo/a-001/a-001-patch-small.gif
    215 /history/apollo/pad-abort-test-1/pad-abort-test-1-patch-small.gif
    215 /://spacelink.msfc.nasa.gov
    214 /images/crawlerway-logo.gif
    186 /images/ksclogo-medium.gif
    183 /history/apollo/sa-1/sa-1-patch-small.gif
```

---

## August 1995 - Detailed Findings

### 1. Top 10 hosts (excluding 404s)
```
   6519 edams.ksc.nasa.gov
   4816 piweba4y.prodigy.com
   4779 163.206.89.4
   4576 piweba5y.prodigy.com
   4369 piweba3y.prodigy.com
   3866 www-d1.proxy.aol.com
   3522 www-b2.proxy.aol.com
   3445 www-b3.proxy.aol.com
   3412 www-c5.proxy.aol.com
   3393 www-b5.proxy.aol.com
```

### 2. IP addresses vs hostnames
```
IP requests:       446494 (28.44%)
Hostname requests: 1123404 (71.56%)
```

### 3. Top 10 most-requested URLs (excluding 404s)
```
  97410 /images/NASA-logosmall.gif
  75337 /images/KSC-logosmall.gif
  67448 /images/MOSAIC-logosmall.gif
  67068 /images/USA-logosmall.gif
  66444 /images/WORLD-logosmall.gif
  62778 /images/ksclogo-medium.gif
  43687 /ksc.html
  37826 /history/apollo/images/apollo-logo1.gif
  35138 /images/launch-logo.gif
  30347 /
```

### 4. HTTP methods
```
1565812 GET
   3965 HEAD
    111 POST
```

### 5. 404 errors
```
404 errors: 9978 (0.64% of all responses)
```

### 6. Response code distribution
```
1396473 200
 134138 304
  26422 302
   9978 404
    171 403
     93 234
     92 363
     30 598
     27 501
     19 509
     12 527
      3 543
      3 515
      3 500
      3 110
      2 530
      2 400
      2 372
      2 308
      2 263
      1 440
      1 381
      1 374
      1 156
      1 104

Most frequent response code:
  code=200  count=1396473  percentage=88.95%
```

### 7. Activity by hour of day
```
  47862 00
  38531 01
  32508 02
  29995 03
  26756 04
  27587 05
  31287 06
  47386 07
  65443 08
  78695 09
  88309 10
  95344 11
 105143 12
 104536 13
 101394 14
 109465 15
  99527 16
  80834 17
  66809 18
  59315 19
  59944 20
  57985 21
  60673 22
  54570 23

Peak 3 hours:
 109465 15
 105143 12
 104536 13

Quietest 3 hours:
  26756 04
  27587 05
  29995 03
```

### 8. Busiest day
```
  90125 31/Aug/1995
```

### 9. Quietest day
```
  31608 26/Aug/1995
```

### 10. Outage detection (Hurricane Erin)
```
Largest gap: 01/Aug/1995 14:52:01  ->  03/Aug/1995 04:36:13
Outage duration: 135852 seconds (37h 44m 12s)
```

### 11. Response size
```
Largest response: 3421948 bytes
Average response: 17241.67 bytes
Total bytes served: 26793705507
```

### 12. Error patterns
```
Errors (4xx/5xx) by hour of day:
    405 00
    345 01
    622 02
    370 03
    182 04
    174 05
    139 06
    228 07
    342 08
    362 09
    500 10
    447 11
    688 12
    631 13
    539 14
    562 15
    590 16
    599 17
    436 18
    457 19
    469 20
    443 21
    467 22
    492 23

Top 10 hosts generating errors (4xx/5xx):
     62 dialip-217.den.mmc.com
     47 piweba3y.prodigy.com
     44 155.148.25.4
     39 scooter.pa-x.dec.com
     39 maz3.maz.net
     38 gate.barr.com
     37 ts8-1.westwood.ts.ucla.edu
     37 nexus.mlckew.edu.au
     37 m38-370-9.mit.edu
     37 204.62.245.32

Top 10 URLs producing errors:
   1337 /pub/winvn/readme.txt
   1185 /pub/winvn/release.txt
    682 /shuttle/missions/STS-69/mission-STS-69.html
    319 /images/nasa-logo.gif
    251 /shuttle/missions/sts-68/ksc-upclose.gif
    209 /elv/DELTA/uncons.htm
    200 /history/apollo/sa-1/sa-1-patch-small.gif
    166 /://spacelink.msfc.nasa.gov
    160 /images/crawlerway-logo.gif
    154 /history/apollo/a-001/a-001-patch-small.gif
```

---

## July vs August Comparison

| Metric          | July         | August       |
|-----------------|--------------|--------------|
| Total requests  | 1891714 | 1569898 |
| 404 errors      | 10714   | 9978   |

### ASCII Visualization: Activity Comparison
```
Monthly Request Volume:

July:     ██████████████████████████████████████░░  1891714
August:   ███████████████████████████████░░░░░░░░░  1569898
          |---------|---------|---------|---------|
          0        500k     1000k    1500k    2000k

404 Error Comparison:

July:     █████████████████████░░░░░░░░░░░░░░░░░░░  10714
August:   ████████████████████░░░░░░░░░░░░░░░░░░░░  9978
          |---------|---------|---------|---------|
          0         5k       10k      15k      20k
```

### ASCII chart - daily request volume (detail)

**July 1995:**
```
01/Jul/1995     64714 ████████████████████████████
02/Jul/1995     60265 ██████████████████████████
03/Jul/1995     89584 ████████████████████████████████████████
04/Jul/1995     70452 ███████████████████████████████
05/Jul/1995     94575 ██████████████████████████████████████████
06/Jul/1995    100960 █████████████████████████████████████████████
07/Jul/1995     87233 ███████████████████████████████████████
08/Jul/1995     38867 █████████████████
09/Jul/1995     35272 ███████████████
10/Jul/1995     72860 ████████████████████████████████
11/Jul/1995     80407 ███████████████████████████████████
12/Jul/1995     92536 █████████████████████████████████████████
13/Jul/1995    134203 ████████████████████████████████████████████████████████████
14/Jul/1995     84103 █████████████████████████████████████
15/Jul/1995     45532 ████████████████████
16/Jul/1995     47854 █████████████████████
17/Jul/1995     74981 █████████████████████████████████
18/Jul/1995     64282 ████████████████████████████
19/Jul/1995     72738 ████████████████████████████████
20/Jul/1995     66593 █████████████████████████████
21/Jul/1995     64629 ████████████████████████████
22/Jul/1995     35267 ███████████████
23/Jul/1995     39199 █████████████████
24/Jul/1995     64259 ████████████████████████████
25/Jul/1995     62699 ████████████████████████████
26/Jul/1995     58849 ██████████████████████████
27/Jul/1995     61680 ███████████████████████████
28/Jul/1995     27121 ████████████
```

**August 1995:**
```
01/Aug/1995     33996 ██████████████████████
03/Aug/1995     41388 ███████████████████████████
04/Aug/1995     59557 ███████████████████████████████████████
05/Aug/1995     31893 █████████████████████
06/Aug/1995     32420 █████████████████████
07/Aug/1995     57362 ██████████████████████████████████████
08/Aug/1995     60157 ████████████████████████████████████████
09/Aug/1995     60458 ████████████████████████████████████████
10/Aug/1995     61248 ████████████████████████████████████████
11/Aug/1995     61246 ████████████████████████████████████████
12/Aug/1995     38071 █████████████████████████
13/Aug/1995     36480 ████████████████████████
14/Aug/1995     59878 ███████████████████████████████████████
15/Aug/1995     58847 ███████████████████████████████████████
16/Aug/1995     56653 █████████████████████████████████████
17/Aug/1995     58988 ███████████████████████████████████████
18/Aug/1995     56246 █████████████████████████████████████
19/Aug/1995     32094 █████████████████████
20/Aug/1995     32963 █████████████████████
21/Aug/1995     55540 ████████████████████████████████████
22/Aug/1995     57762 ██████████████████████████████████████
23/Aug/1995     58097 ██████████████████████████████████████
24/Aug/1995     52552 ██████████████████████████████████
25/Aug/1995     57321 ██████████████████████████████████████
26/Aug/1995     31608 █████████████████████
27/Aug/1995     32823 █████████████████████
28/Aug/1995     55496 ████████████████████████████████████
29/Aug/1995     67988 █████████████████████████████████████████████
30/Aug/1995     80641 █████████████████████████████████████████████████████
31/Aug/1995     90125 ████████████████████████████████████████████████████████████
```

---

## July vs August - Headline Comparisons

- **August had fewer total requests than July** (1569898 vs
  1891714), largely because of the Hurricane Erin outage: an
  entire day of log data (02/Aug/1995) is missing, plus partial
  coverage on 01/Aug and 03/Aug.
- **Despite lower August volume, the 404 error rate was slightly
  higher** than in July (see section 5 of each month). So the drop in
  traffic was not matched by a proportional drop in bad requests.
- The busiest single day shifted from mid-July (**13/Jul/1995**) to
  the last day of August (**31/Aug/1995**), which is consistent with
  traffic ramping back up after the outage.

---

## Interesting Findings & Anomalies

- **Hurricane Erin outage.** See section 10 for August - the largest gap
  in log timestamps identifies the outage window and its duration.
- **GIF-heavy traffic.** The most-requested URLs in both months are small
  GIF images (NASA/KSC logos, countdown clock, etc.). This reflects the
  pre-CDN era: every HTML page pulled several tiny images.
- **Most requests are successful.** Code 200 dominates, typically
  accompanied by 304 (Not Modified) responses - a sign of active
  client-side caching.
- **GET is essentially the only method used**, which matches a read-only
  public documentation / mission site.
- **Daytime peak (US east coast).** Activity rises sharply during US
  daytime hours and is quietest in the early-morning hours (UTC-0400).

---

## Caveats

- Some log rows are malformed (binary garbage in the request field, or
  missing spaces). My analyses filter these out where possible
  (e.g. `$4 ~ /^\[/` for timestamps, `$9 ~ /^[1-5][0-9][0-9]$/`
  for status codes, and `$6 ~ /^[A-Z]+$/` for HTTP methods).
- **Response-code distribution may contain rare three-digit values**
  (e.g. 234, 363, 527, 543) that are not real HTTP status codes.
  Some malformed log entries appear to shift fields, so unusual
  three-digit values may reflect parsing noise rather than valid HTTP
  status codes. The figures for the common codes (200, 304, 302, 404,
  403, 500) are unaffected.

