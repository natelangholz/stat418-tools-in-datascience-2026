# NASA Web Server Log Analysis Report

## Overview
This report summarizes the analysis of NASA web server logs for **July 1995** and **August 1995**.  
The goal was to compare traffic patterns, errors, request behavior, and unusual events across the two months.

## Summary Statistics

| Metric | July 1995 | August 1995 |
|---|---:|---:|
| Total requests |  1891714 |  1569898 |
| 404 errors | 10714 | 9978 |
| Peak hour | 14:00 with 122479 requests | 15:00 with 109465 requests |
| Busiest day | 13/Jul/1995 with 134203 requests | 31/Aug/1995 with 90125 requests |
| Quietest day | 28/Jul/1995 with 27121 requests | 26/Aug/1995 with 31608 requests |
| Most frequent response code | 200 | 200 |
| Response code count | 1697914 | 1396473 |
| Response code percentage | 89.76% | 88.95% |
| Largest response size | 6823936 bytes | 3421948 bytes |
| Average response size | 20657.68 bytes | 17241.67 bytes |

## July vs August Comparison

- July had more total requests than August.
- July had more 404 errors than August.
- July peak activity occurred at **14:00 with 122479 requests**.
- August peak activity occurred at **15:00 with 109465 requests**.
- July busiest day was **13/Jul/1995 with 134203 requests**.
- August busiest day was **31/Aug/1995 with 90125 requests**.
- August includes a major outage event that does not appear in July.

## Hurricane Outage in August

The August log shows a major gap in data collection:

- Last entry before outage: 01/Aug/1995:14:52:01
- First entry after outage: 03/Aug/1995:04:36:13
- Outage duration: 135852 seconds (37 hours, 44 minutes, 12 seconds)

This outage is likely related to the hurricane event mentioned in the assignment.

## ASCII Visualizations

### Total Requests
- July   | ########################################  1891714
- August | #################################  1569898

### 404 Errors
- July   | ######################################## 10714
- August | ##################################### 9978

### Average Response Size
- July   | ######################################## 20657 bytes
- August | ################################# 17241 bytes

## Top 10 Hosts

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

## Top 10 Requested URLs

### July 1995
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

### August 1995
```
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
```

## Request Methods

### July 1995
```
1884726 GET
3952 HEAD
 111 POST
```

### August 1995
```
1563968 GET
3965 HEAD
 111 POST
```

## Interesting Findings

1. The vast majority of requests in both months received response code **200**, showing that most requests were successful.
2. Image files such as NASA logos and KSC logos were among the most frequently requested resources.
3. GET was by far the dominant HTTP method, while HEAD and POST were much less common.
4. August contained a clear outage, shown by the long time gap in the logs.
5. Traffic was concentrated in daytime and afternoon hours, while early morning hours were much quieter.

## Conclusion

Overall, both months show heavy web activity with similar request patterns, but **August stands out because of the outage event**.  
The logs also show that NASA image assets and homepage-related files were highly requested, and most traffic came through successful GET requests.

## Appendix: Full July Analysis

```
==========================================
NASA Log Analysis - July 1995
File: data/NASA_Jul95.log
==========================================

BASIC ANALYSIS
--------------
1. Top 10 hosts/IPs making requests (excluding 404 errors):
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

2. Percentage of requests from IP addresses vs hostnames:
IP addresses: 22.16% (419140)
Hostnames: 77.84% (1472575)

3. Top 10 most requested URLs (excluding 404 errors):
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

4. HTTP request methods with counts:
1884726 GET
3952 HEAD
 111 POST

5. Number of 404 errors:
10714

6. Most frequent response code and percentage:
Most frequent response code: 200
Count: 1697914
Percentage: 89.76%

TIME-BASED ANALYSIS
-------------------
7. Peak hour(s):
14:00 with 122479 requests

Quietest hour(s):
05:00 with 31919 requests

8. Busiest day:
13/Jul/1995 with 134203 requests

9. Quietest day (excluding outage dates if applicable):
28/Jul/1995 with 27121 requests

ADVANCED ANALYSIS
-----------------
10. Hurricane outage: Not applicable for July log

11. Response size analysis:
Largest response size: 6823936 bytes
Average response size: 20657.68 bytes

12. Error patterns:
Errors by hour (4xx and 5xx):
837 15:00
751 14:00
731 11:00
646 12:00
643 10:00
640 16:00
613 17:00
531 13:00
494 18:00
484 22:00
481 09:00
461 23:00
443 21:00
427 00:00
411 19:00
380 20:00
358 08:00
319 01:00
269 02:00
240 07:00
238 03:00
167 04:00
147 05:00
133 06:00

Top hosts causing errors:
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
```

## Appendix: Full August Analysis

```
==========================================
NASA Log Analysis - August 1995
File: data/NASA_Aug95.log
==========================================

BASIC ANALYSIS
--------------
1. Top 10 hosts/IPs making requests (excluding 404 errors):
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

2. Percentage of requests from IP addresses vs hostnames:
IP addresses: 28.44% (446494)
Hostnames: 71.56% (1123404)

3. Top 10 most requested URLs (excluding 404 errors):
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

4. HTTP request methods with counts:
1563968 GET
3965 HEAD
 111 POST

5. Number of 404 errors:
9978

6. Most frequent response code and percentage:
Most frequent response code: 200
Count: 1396473
Percentage: 88.95%

TIME-BASED ANALYSIS
-------------------
7. Peak hour(s):
15:00 with 109465 requests

Quietest hour(s):
04:00 with 26756 requests

8. Busiest day:
31/Aug/1995 with 90125 requests

9. Quietest day (excluding outage dates if applicable):
26/Aug/1995 with 31608 requests

ADVANCED ANALYSIS
-----------------
10. Hurricane outage (largest gap in log timestamps):
Last entry before outage: 01/Aug/1995:14:52:01
First entry after outage: 03/Aug/1995:04:36:13
Outage duration: 135852 seconds (37 hours, 44 minutes, 12 seconds)

11. Response size analysis:
Largest response size: 3421948 bytes
Average response size: 17241.67 bytes

12. Error patterns:
Errors by hour (4xx and 5xx):
651 12:00
618 02:00
616 13:00
586 17:00
579 16:00
548 15:00
525 14:00
485 10:00
483 23:00
459 22:00
445 20:00
444 19:00
434 21:00
429 18:00
423 11:00
367 00:00
361 03:00
352 09:00
340 08:00
330 01:00
222 07:00
182 04:00
167 05:00
135 06:00

Top hosts causing errors:
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
```
