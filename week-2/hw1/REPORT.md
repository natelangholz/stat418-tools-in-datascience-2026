# NASA Web Server Log Analysis Report
**Data:** NASA Kennedy Space Center HTTP logs, July–August 1995  
**Analyzed:** 2026-04-13

---

## Overview

This report analyzes web server access logs from NASA's Kennedy Space Center
website during July and August 1995 — a historically significant period
coinciding with several shuttle missions and a major hurricane.

---

## 1. Top 10 Hosts

### July 1995
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

### August 1995
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

---

## 2. IP vs Hostname

### July 1995
  Total requests : 1891715
  IP addresses   : 419140 (22.16%)
  Hostnames      : 1472575 (77.84%)

### August 1995
  Total requests : 1569898
  IP addresses   : 446494 (28.44%)
  Hostnames      : 1123404 (71.56%)

---

## 3. Top 10 Requested URLs

### July 1995
```
 111144 /images/NASA-logosmall.gif
  89530 /images/KSC-logosmall.gif
  60300 /images/MOSAIC-logosmall.gif
  59845 /images/USA-logosmall.gif
  59325 /images/WORLD-logosmall.gif
  58616 /images/ksclogo-medium.gif
  40841 /images/launch-logo.gif
  40251 /shuttle/countdown/
  40072 /ksc.html
  33555 /images/ksclogosmall.gif
```

### August 1995
```
  97293 /images/NASA-logosmall.gif
  75283 /images/KSC-logosmall.gif
  67356 /images/MOSAIC-logosmall.gif
  66975 /images/USA-logosmall.gif
  66351 /images/WORLD-logosmall.gif
  62670 /images/ksclogo-medium.gif
  43619 /ksc.html
  37806 /history/apollo/images/apollo-logo1.gif
  35119 /images/launch-logo.gif
  30123 /
```

---

## 4. HTTP Request Types

### July 1995
```
1887646 GET
   3952 HEAD
    111 POST
      2 1/history/apollo/images/
      1 
      1 
```

### August 1995
```
1565812 GET
   3965 HEAD
    111 POST
      1 huttle/countdown/
      1 ?
```

---

## 5. Total 404 Errors

| Month | 404 Errors |
|-------|------------|
| July  | 10714 |
| August | 9978 |

---

## 6. Most Frequent Response Code

### July 1995
```
1697914 200
 132626 304
  46549 302
  10714 404
    611 <berend@blazemonger.pc.cc.cmu.edu>"
  Most frequent: 200 at 89.76% of all responses
```

### August 1995
```
1396473 200
 134138 304
  26422 302
   9978 404
    624 <berend@blazemonger.pc.cc.cmu.edu>"
  Most frequent: 200 at 88.95% of all responses
```

---

## 7. Peak and Quiet Hours

### July 1995
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
```

### August 1995
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
```

---

## 8. Busiest Day

| Month | Busiest Day |
|-------|-------------|
| July  | 13/Jul/1995 - 134203 requests |
| August | 31/Aug/1995 - 90125 requests |

---

## 9. Quietest Day

### July 1995
```
  27121 28/Jul/1995
  35267 22/Jul/1995
  35272 09/Jul/1995
  38867 08/Jul/1995
  39199 23/Jul/1995
```

### August 1995
```
  31608 26/Aug/1995
  31893 05/Aug/1995
  32094 19/Aug/1995
  32420 06/Aug/1995
  32823 27/Aug/1995
```

---

## 10. Hurricane Outage (August 1995)

```
Possible gap: 03/Aug/1995:04 (only 16 requests)
Possible gap: 03/Aug/1995:05 (only 43 requests)
Possible gap: 03/Aug/1995:06 (only 70 requests)
Possible gap: 03/Aug/1995:07 (only 58 requests)
Possible gap: 03/Aug/1995:09 (only 22 requests)
Possible gap: 03/Aug/1995:10 (only 57 requests)
```

> Hurricane Erin made landfall in Florida in August 1995, causing a data
> collection outage at Kennedy Space Center. The gaps above show hours
> where fewer than 100 requests were logged, indicating the outage window.

---

## 11. Response Sizes

### July 1995
  Largest : 6823936 bytes
  Average : 20658 bytes

### August 1995
  Largest : 3421948 bytes
  Average : 17242 bytes

---

## 12. Error Patterns by Hour

### July 1995
```
   1011 15
    982 14
    904 16
    876 11
    776 17
```

### August 1995
```
    797 12
    732 13
    675 16
    674 17
    673 15
```

---

## Summary: July vs August Comparison

| Metric | July 1995 | August 1995 |
|--------|-----------|-------------|
| Total Requests | 1891714 | 1569898 |
| 404 Errors | 10714 | 9978 |
| Busiest Day | 13/Jul/1995 - 134203 requests | 31/Aug/1995 - 90125 requests |
---

## Key Findings

1. **Prodigy.com dominates traffic** — piweba hosts from Prodigy were the
   top requesters in both months, suggesting automated or heavy residential use.

2. **Images drive the majority of requests** — NASA logo and KSC logo GIFs
   appear in nearly every top-10 URL list, reflecting the image-heavy web
   design of 1995.

3. **HTTP 200 accounts for ~90% of responses** — the server was healthy
   and serving content successfully the vast majority of the time.

4. **Hurricane Erin caused a measurable outage in August** — gaps in
   hourly request counts confirm the data collection interruption.

5. **Traffic drops significantly on weekends** — quietest days tend to
   fall on Saturdays and Sundays, reflecting the professional/academic
   user base of the mid-1990s web.

