# NASA Web Server Log Analysis Report

Generated on: Tue Apr 21 02:29:36 PDT 2026

## Overview

This report summarizes the NASA web server logs from July and August 1995.

## Summary comparison

| Metric | July | August |
|---|---:|---:|
| Total requests | 1891714 | 1569898 |
| 404 errors | 10845 | 10056 |
| Most frequent response code | 200 1697914 89.76% | 200 1396473 88.95% |
| Peak hour | 14 122479 | 15 109465 |
| Busiest day | 13/Jul/1995 134203 | 31/Aug/1995 90125 |
| Quietest day | 22/Jul/1995 35267 | 26/Aug/1995 31608 |
| Largest response size | Largest: 6823936 | Largest: 3421948 |
| Average response size | Average: 20657.68 | Average: 17241.67 |

## Simple ASCII charts

### Total requests

- July:   1891714 #####################################
- August: 1569898 ###############################

### 404 errors

- July:   10845 ####################################
- August: 10056 #################################

## Key findings

- July had more total requests.
- The most frequent response code in both months was 200.
- July had the larger average response size.
- August had a major outage.
- Largest gap: 01/Aug/1995:14:52:01 -> 03/Aug/1995:04:36:13
- Duration: 1 days 13 hours 44 minutes 12 seconds

## July details

```
July log analysis

404 errors:
   10845

Request types:
1887646 GET
3952 HEAD
 111 POST

Top 10 hosts excluding 404:
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

IP vs Hostname:
IP: 419140 22.16%
Hostname: 1472575 77.84%

Top 10 requests excluding 404:
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

Most frequent response code:
200 1697914 89.76%

Peak hour:
14 122479

Busiest day:
13/Jul/1995 134203

Quietest day excluding outage dates:
22/Jul/1995 35267

Response size:
Largest: 6823936
Average: 20657.68

Error patterns:
Errors by hour:
15 1011
14 982
16 904
11 876
17 776

Hosts with most errors:
 611 blazemonger.pc.cc.cmu.edu
 251 hoohoo.ncsa.uiuc.edu
 202 128.159.146.92
 131 jbiagioni.npt.nuwc.navy.mil
 110 piweba3y.prodigy.com
```

## August details

```
August log analysis

404 errors:
   10056

Request types:
1565812 GET
3965 HEAD
 111 POST

Top 10 hosts excluding 404:
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

IP vs Hostname:
IP: 446494 28.44%
Hostname: 1123404 71.56%

Top 10 requests excluding 404:
97410 /images/NASA-logosmall.gif
75337 /images/KSC-logosmall.gif
67448 /images/MOSAIC-logosmall.gif
67068 /images/USA-logosmall.gif
66444 /images/WORLD-logosmall.gif
62778 /images/ksclogo-medium.gif
43688 /ksc.html
37826 /history/apollo/images/apollo-logo1.gif
35138 /images/launch-logo.gif
30347 /

Most frequent response code:
200 1396473 88.95%

Peak hour:
15 109465

Busiest day:
31/Aug/1995 90125

Quietest day excluding outage dates:
26/Aug/1995 31608

Hurricane outage:
Largest gap: 01/Aug/1995:14:52:01 -> 03/Aug/1995:04:36:13
Duration: 1 days 13 hours 44 minutes 12 seconds

Response size:
Largest: 3421948
Average: 17241.67

Error patterns:
Errors by hour:
12 797
13 732
16 675
17 674
15 673

Hosts with most errors:
 624 zooropa.res.cmu.edu
 104 columbia.acc.brad.ac.uk
  62 dialip-217.den.mmc.com
  60 escpsabp400.desc.dla.mil
  47 piweba3y.prodigy.com
```
