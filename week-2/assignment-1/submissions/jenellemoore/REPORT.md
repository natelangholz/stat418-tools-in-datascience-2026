# Assignment 1: Web Server Log Analysis with Bash Report

This report summarizes the analysis of NASA web server logs from July and August 1995.
It compares overall request behavior, errors, and response codes across both months.

Debug check
Checking whether input files exist:
-rw-r--r--@ 1 jenellemoore  staff  167813770 Apr 21 08:40 NASA_Aug95.log
-rw-r--r--@ 1 jenellemoore  staff  205242368 Apr 21 08:40 NASA_Jul95.log

## 1) Top 10 Hosts/IPs

### Top 10 hosts in July (excluding 404 errors)

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

### Top 10 hosts in August (excluding 404 errors)

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

## 2) IP vs Hostname - What percentage of requests came from IP addresses vs hostnames?

### What percentage of requests came from IP addresses vs hostname for July?

```
Total requests:  1891715
IP requests: 419140
Hostname requests: 1472575
IP addresses: 22.16%
Hostnames: 77.84%
```

July Hostnames        | ####################  77.84%
July IP addresses     | #####                 22.16%


### What percentage of requests came from IP addresses vs hostname for August?

```
Total requests:  1569898
IP requests: 446494
Hostname requests: 1123404
IP addresses: 28.44%
Hostnames: 71.56%
```

August Hostnames      | ##################    71.56%
August IP addresses   | ######                28.44%


## 3) Top 10 requested URLs (exclude 404 errors)

### Top 10 most requested URLs (excluding 404) for July

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

### Top 10 most requested URLs (excluding 404) for August

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


## 4) Request types - List the most frequent HTTP methods (GET, POST, etc.) with counts

### Most frequent HTTP methods (GET, POST, etc.) for July

```
1887646 GET
3952 HEAD
 111 POST
```

### Most frequent HTTP methods (GET, POST, etc.) for August

```
1565812 GET
3965 HEAD
 111 POST
```


## 5) 404 errors - How many 404 errors were reported?

### 404 errors reported in July

```
   10714
```

### 404 errors reported in August

```
    9978
```

404 Error Rate
July   | ###----------------- 14.2%
August | #####--------------- 22.8%


## 6) Response codes - What is the most frequent response code and what percentage of responses did it account for?

### Most frequent response code and what percentage of responses did it account for in July?

```
Response code: 200  Count: 1697914  Percentage: 89.89%
Response code: 304  Count: 132626  Percentage: 7.02%
Response code: 302  Count: 46549  Percentage: 2.46%
Response code: 404  Count: 10714  Percentage: 0.57%
Response code: 786  Count: 244  Percentage: 0.01%
Response code: 234  Count: 169  Percentage: 0.01%
Response code: 363  Count: 168  Percentage: 0.01%
Response code: 669  Count: 164  Percentage: 0.01%
Response code: 500  Count: 62  Percentage: 0.00%
Response code: 403  Count: 54  Percentage: 0.00%
```

### Most frequent response code and what percentage of responses did it account for in August?

```
Response code: 200  Count: 1396473  Percentage: 89.08%
Response code: 304  Count: 134138  Percentage: 8.56%
Response code: 302  Count: 26422  Percentage: 1.69%
Response code: 404  Count: 9978  Percentage: 0.64%
Response code: 403  Count: 171  Percentage: 0.01%
Response code: 786  Count: 117  Percentage: 0.01%
Response code: 669  Count: 93  Percentage: 0.01%
Response code: 234  Count: 93  Percentage: 0.01%
Response code: 363  Count: 92  Percentage: 0.01%
Response code: 598  Count: 30  Percentage: 0.00%
```




## 7) Peak hours - What hours of the day see the most activity? When is it quiet?

### Hourly Activity in July:

```
14:00 - 122479 events
12:00 - 122085 events
15:00 - 121200 events
13:00 - 120814 events
16:00 - 118037 events
11:00 - 115720 events
10:00 - 105507 events
09:00 - 99969 events
17:00 - 97609 events
08:00 - 83750 events
18:00 - 79282 events
21:00 - 71922 events
19:00 - 71776 events
22:00 - 70759 events
20:00 - 69809 events
23:00 - 69362 events
00:00 - 62450 events
07:00 - 54017 events
01:00 - 53066 events
02:00 - 45297 events
03:00 - 37398 events
06:00 - 35253 events
04:00 - 32234 events
05:00 - 31919 events
:00 - 1 events
```
The most activity occurs during the 14:00 hour and the least activity is seen during the 00:00 hour.


### Hourly Activity in August:

```
15:00 - 109465 events
12:00 - 105143 events
13:00 - 104536 events
14:00 - 101394 events
16:00 - 99527 events
11:00 - 95344 events
10:00 - 88309 events
17:00 - 80834 events
09:00 - 78695 events
18:00 - 66809 events
08:00 - 65443 events
22:00 - 60673 events
20:00 - 59944 events
19:00 - 59315 events
21:00 - 57985 events
23:00 - 54570 events
00:00 - 47862 events
07:00 - 47386 events
01:00 - 38531 events
02:00 - 32508 events
06:00 - 31287 events
03:00 - 29995 events
05:00 - 27587 events
04:00 - 26756 events
```
The most activity occurs during the 15:00 hour and the least activity is seen during the 04:00 hour.


## 8) Busiest day - Which date saw the most activity overall?

### Busiest day in July:

```
[13/Jul/1995:00 - 134203 events
[06/Jul/1995:00 - 100960 events
[05/Jul/1995:00 - 94575 events
[12/Jul/1995:00 - 92536 events
[03/Jul/1995:00 - 89584 events
[07/Jul/1995:00 - 87233 events
[14/Jul/1995:00 - 84103 events
[11/Jul/1995:00 - 80407 events
[17/Jul/1995:00 - 74981 events
[10/Jul/1995:00 - 72860 events
[19/Jul/1995:00 - 72738 events
[04/Jul/1995:00 - 70452 events
[20/Jul/1995:00 - 66593 events
[01/Jul/1995:00 - 64714 events
[21/Jul/1995:00 - 64629 events
[18/Jul/1995:00 - 64282 events
[24/Jul/1995:00 - 64259 events
[25/Jul/1995:00 - 62699 events
[27/Jul/1995:00 - 61680 events
[02/Jul/1995:00 - 60265 events
[26/Jul/1995:00 - 58849 events
[16/Jul/1995:00 - 47854 events
[15/Jul/1995:00 - 45532 events
[23/Jul/1995:00 - 39199 events
[08/Jul/1995:00 - 38867 events
[09/Jul/1995:00 - 35272 events
[22/Jul/1995:00 - 35267 events
[28/Jul/1995:00 - 27121 events
:00 - 1 events
```
The busiet day in July was July 13, 1995.


### Busiest day in August:

```
[31/Aug/1995:00 - 90125 events
[30/Aug/1995:00 - 80641 events
[29/Aug/1995:00 - 67988 events
[10/Aug/1995:00 - 61248 events
[11/Aug/1995:00 - 61246 events
[09/Aug/1995:00 - 60458 events
[08/Aug/1995:00 - 60157 events
[14/Aug/1995:00 - 59878 events
[04/Aug/1995:00 - 59557 events
[17/Aug/1995:00 - 58988 events
[15/Aug/1995:00 - 58847 events
[23/Aug/1995:00 - 58097 events
[22/Aug/1995:00 - 57762 events
[07/Aug/1995:00 - 57362 events
[25/Aug/1995:00 - 57321 events
[16/Aug/1995:00 - 56653 events
[18/Aug/1995:00 - 56246 events
[21/Aug/1995:00 - 55540 events
[28/Aug/1995:00 - 55496 events
[24/Aug/1995:00 - 52552 events
[03/Aug/1995:00 - 41388 events
[12/Aug/1995:00 - 38071 events
[13/Aug/1995:00 - 36480 events
[01/Aug/1995:00 - 33996 events
[20/Aug/1995:00 - 32963 events
[27/Aug/1995:00 - 32823 events
[06/Aug/1995:00 - 32420 events
[19/Aug/1995:00 - 32094 events
[05/Aug/1995:00 - 31893 events
[26/Aug/1995:00 - 31608 events
```
The busiet day in August was August 31, 1995.


## 9) Quietest day - Excluding outage dates, which date saw the least activity?

### Quietest day (excluding outage dates) in July:

```
:00 - 1 events
[28/Jul/1995:00 - 27117 events
[22/Jul/1995:00 - 35266 events
[09/Jul/1995:00 - 35267 events
[08/Jul/1995:00 - 38867 events
[23/Jul/1995:00 - 39199 events
[15/Jul/1995:00 - 45530 events
[16/Jul/1995:00 - 47854 events
[26/Jul/1995:00 - 58844 events
[02/Jul/1995:00 - 60265 events
[27/Jul/1995:00 - 61678 events
[25/Jul/1995:00 - 62690 events
[24/Jul/1995:00 - 64253 events
[18/Jul/1995:00 - 64272 events
[21/Jul/1995:00 - 64627 events
[01/Jul/1995:00 - 64714 events
[20/Jul/1995:00 - 66589 events
[04/Jul/1995:00 - 70452 events
[19/Jul/1995:00 - 72734 events
[10/Jul/1995:00 - 72856 events
[17/Jul/1995:00 - 74980 events
[11/Jul/1995:00 - 80407 events
[14/Jul/1995:00 - 84099 events
[07/Jul/1995:00 - 87230 events
[03/Jul/1995:00 - 89530 events
[12/Jul/1995:00 - 92536 events
[05/Jul/1995:00 - 94573 events
[06/Jul/1995:00 - 100960 events
[13/Jul/1995:00 - 134201 events
```
The quietest day excluding outades was on July 28, 1995.


### Quietest day (excluding outage dates) in August:

```
[26/Aug/1995:00 - 31602 events
[05/Aug/1995:00 - 31890 events
[19/Aug/1995:00 - 32094 events
[06/Aug/1995:00 - 32420 events
[27/Aug/1995:00 - 32823 events
[20/Aug/1995:00 - 32953 events
[01/Aug/1995:00 - 33996 events
[13/Aug/1995:00 - 36480 events
[12/Aug/1995:00 - 38070 events
[03/Aug/1995:00 - 41386 events
[24/Aug/1995:00 - 52538 events
[28/Aug/1995:00 - 55493 events
[21/Aug/1995:00 - 55540 events
[18/Aug/1995:00 - 56244 events
[16/Aug/1995:00 - 56650 events
[25/Aug/1995:00 - 57321 events
[07/Aug/1995:00 - 57362 events
[22/Aug/1995:00 - 57759 events
[23/Aug/1995:00 - 58093 events
[15/Aug/1995:00 - 58843 events
[17/Aug/1995:00 - 58988 events
[04/Aug/1995:00 - 59556 events
[14/Aug/1995:00 - 59878 events
[08/Aug/1995:00 - 60155 events
[09/Aug/1995:00 - 60458 events
[10/Aug/1995:00 - 61218 events
[11/Aug/1995:00 - 61244 events
[29/Aug/1995:00 - 67980 events
[30/Aug/1995:00 - 80640 events
[31/Aug/1995:00 - 90125 events
```
The quietest day excluding outades was on August 26, 1995.




## 10) Hurricane outage - There was a hurricane in August causing a data outage. Identify the exact dates and times when data was not collected. How long was the outage?

### Dates and times data was not collected in August

```
01/Aug/1995 15
01/Aug/1995 16
01/Aug/1995 17
01/Aug/1995 18
01/Aug/1995 19
01/Aug/1995 20
01/Aug/1995 21
01/Aug/1995 22
01/Aug/1995 23
02/Aug/1995 00
02/Aug/1995 01
02/Aug/1995 02
02/Aug/1995 03
02/Aug/1995 04
02/Aug/1995 05
02/Aug/1995 06
02/Aug/1995 07
02/Aug/1995 08
02/Aug/1995 09
02/Aug/1995 10
02/Aug/1995 11
02/Aug/1995 12
02/Aug/1995 13
02/Aug/1995 14
02/Aug/1995 15
02/Aug/1995 16
02/Aug/1995 17
02/Aug/1995 18
02/Aug/1995 19
02/Aug/1995 20
02/Aug/1995 21
02/Aug/1995 22
02/Aug/1995 23
03/Aug/1995 00
03/Aug/1995 01
03/Aug/1995 02
03/Aug/1995 03
```
The hurricane resulted in a data outage lasting 1 day and 12 hours. The hurricane occured August 1, 1995 during the 15:00 hour and lasted untill August 3,1995 03:00 hour.


## 11) Response size - What is the largest response (in bytes) and what is the average response size?

### Largest response (in bytes) for July

```
6823936
```

Average response size (in bytes) for July
```
Average: 20624.9
```

### Largest response (in bytes) for August

```
3421948
```

### Average response size (in bytes) for August

```
Average: 17221
```

July Largest Response        | ####################  6,823,936 bytes
July Average Response        | ####                  20,624.90 bytes

August Largest Response      | ##########            3,421,948 bytes
August Average Response      | ####.                 17,221 bytes


## 12) Error patterns - Are there any patterns in when errors occur (time of day, specific hosts, etc.)?

### Total error service codes in July

```
10714 404
  62 500
  54 403
  19 509
  14 501
  13 527
   9 543
   4 515
   3 598
   1 421
```

### Total error service codes in August

```
9978 404
 171 403
  30 598
  27 501
  19 509
  12 527
   3 543
   3 515
   3 500
   2 530
```

The service code, 404, was the error that occured the most in July and August.


### Top 10 hosts/IPs making error request in July
```
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

### Top 10 hosts/IPs making error request in August

```
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

The top host that made an error request in July was hoohoo.ncsa.uiuc.edu. For August, 62 dialip-217.den.mmc.com.


### Day with the most errors

```
[19/Jul/1995 - 642 events
[06/Jul/1995 - 635 events
[30/Aug/1995 - 591 events
[07/Jul/1995 - 567 events
[07/Aug/1995 - 529 events
[03/Jul/1995 - 529 events
[31/Aug/1995 - 526 events
[13/Jul/1995 - 526 events
[05/Jul/1995 - 496 events
[18/Jul/1995 - 482 events
```

The days with the most errors in July and August were July 19, 1995 and August 30, 1995.


### Top specific day and hour error spikes

```
[07/Aug/1995 02:00 - 158 events
[18/Jul/1995 15:00 - 106 events
[06/Aug/1995 02:00 - 100 events
[01/Aug/1995 03:00 - 85 events
[12/Jul/1995 10:00 - 82 events
[30/Aug/1995 02:00 - 78 events
[25/Jul/1995 15:00 - 78 events
[19/Jul/1995 12:00 - 77 events
[13/Jul/1995 11:00 - 75 events
[03/Jul/1995 10:00 - 72 events
```

The top hour of the day with the most errors in July and August were July 18, 1995 during the 15:00 hour and August 7, 1995 during the 02:00 hour.


### Top pages/resources with the most errors in July

```
 667 /pub/winvn/readme.txt
 547 /pub/winvn/release.txt
 286 /history/apollo/apollo-13.html
 230 /shuttle/resources/orbiters/atlantis.gif
 230 /history/apollo/a-001/a-001-patch-small.gif
 215 /history/apollo/pad-abort-test-1/pad-abort-test-1-patch-small.gif
 215 /://spacelink.msfc.nasa.gov
 214 /images/crawlerway-logo.gif
 183 /history/apollo/sa-1/sa-1-patch-small.gif
 180 /shuttle/resources/orbiters/discovery.gif
```

Top pages/resources with the most errors in August

```
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

The top pages/resources with the most errors for both July and August were /pub/winvn.readme.txt. 



## Summary Statistics

Total requests were higher in August than July, showing increased server traffic.
The most common response code in both months was 200, meaning most requests were successful.
August had a higher 404 error rate (22.8%) compared to July (14.2%).
Most requests used the GET HTTP method, with very few POST or HEAD requests.
Peak traffic occurred in the afternoon: July's busiest hour was 14:00 and August's busiest hour was 15:00.
The response file was larger in July (6,823,936 bytes) than August (3,421,948 bytes).
Average response size was also larger in July.
August logs contained a major anomaly, a 1 day 12 hour outage, likely caused by Hurricane Erin.
Most common missing/error page in both months involved: /pub/winvn/readme.txt

## Overall Conclusion
The NASA server handled heavy traffic in both months with mostly successful responses. August showed more traffic and more client errors, while July served larger average files. The hurricane outage was the most significant unusual event in the dataset.


