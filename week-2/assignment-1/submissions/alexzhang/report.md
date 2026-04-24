# NASA Web Log Analysis Report
Generated on Sat Apr 18 15:12:15 PDT 2026

## Summary
This report analyzes NASA web logs from July and August 1995, focusing on traffic patterns, error behavior, and a major outage event in August.

## Key Findings
- A significant outage occurred in August lasting ~37 hours.
- Errors are concentrated among a small subset of hosts.
- Error frequency varies by hour, with peaks during high traffic periods.
- Both months showed zero traffic from 12 AM to 9 AM.
- August shows reduced traffic due to outage compared to July.

## July Summary Statistics

### Overall Activity
- Total requests: 1891714
- 4xx errors: 10977 (0.58%)
- 5xx errors: 385 (0.02%)
- 404 errors: 10714
- Most common response code: 200 (1697914 requests, 89.76%)

### Top 5 Hosts/IPs
- piweba3y.prodigy.com: 17462 requests
- piweba4y.prodigy.com: 11535 requests
- piweba1y.prodigy.com: 9776 requests
- alyssa.prodigy.com: 7798 requests
- siltb10.orl.mmc.com: 7573 requests

### Peak Activity Hours
- Most active hours: 14:00 12:00 15:00 13:00 16:00

### HTTP Methods
- "GET: 1887646 requests
- "HEAD: 3952 requests
- "POST: 111 requests

## August Summary Statistics

### Overall Activity
- Total requests: 1569898
- 4xx errors: 10245 (0.65%)
- 5xx errors: 244 (0.02%)
- 404 errors: 9978
- Most common response code: 200 (1396473 requests, 88.95%)

### Top 5 Hosts/IPs
- edams.ksc.nasa.gov: 6519 requests
- piweba4y.prodigy.com: 4816 requests
- 163.206.89.4: 4779 requests
- piweba5y.prodigy.com: 4576 requests
- piweba3y.prodigy.com: 4369 requests

### Peak Activity Hours
- Most active hours: 15:00 12:00 13:00 14:00 16:00

### HTTP Methods
- "GET: 1565812 requests
- "HEAD: 3965 requests
- "POST: 111 requests

## July vs August Comparison

### Total Requests
- July: 1891714 requests
- August: 1569898 requests
- Difference: 321816 fewer requests in August (17.0% decrease)

### Error Analysis
- July 4xx errors: 10977 (0.58%)
- August 4xx errors: 10245 (0.65%)
- July 5xx errors: 385 (0.02%)
- August 5xx errors: 244 (0.02%)

### Most Common Response Code
- July: Response code 200 (1697914 requests)
- August: Response code 200 (1396473 requests)

### Peak Traffic Hours
- July (Top 3 hours): 14:00 12:00 15:00
- August (Top 3 hours): 15:00 12:00 13:00
## Errors by Hour in July (ASCII Chart)
00:  (0)

01:  (0)

02:  (0)

03:  (0)

04:  (0)

05:  (0)

06:  (0)

07:  (0)

08:  (0)

09:  (0)

10: ############## (654)

11: ################ (766)

12: ############## (670)

13: ########### (542)

14: ################ (794)

15: ################## (867)

16: ############## (677)

17: ############# (636)

18: ########### (503)

19: ######### (426)

20: ######## (397)

21: ########## (471)

22: ########### (506)

23: ########## (492)

## Errors by Hour in August (ASCII Chart)
00:  (0)

01:  (0)

02:  (0)

03:  (0)

04:  (0)

05:  (0)

06:  (0)

07:  (0)

08:  (0)

09:  (0)

10: ########## (500)

11: ######### (447)

12: ############## (688)

13: ############# (631)

14: ########### (539)

15: ############ (562)

16: ############ (590)

17: ############ (599)

18: ######### (436)

19: ########## (457)

20: ########## (469)

21: ######### (443)

22: ########## (467)

23: ########## (492)

## Full Analysis Output
```
[2026-04-18 15:13:07] Top 10 hosts/IPs making requests (excluding 404 errors) for July log:
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
[2026-04-18 15:13:12] Top 10 hosts/IPs making requests (excluding 404 errors) for August log:
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
[2026-04-18 15:13:16] Percentage of requests from IP addresses vs hostnames for July log:
[2026-04-18 15:13:17] IP addresses: 22.16% (419140 requests)
[2026-04-18 15:13:17] Hostnames: 77.84% (1472574 requests)
[2026-04-18 15:13:17] Percentage of requests from IP addresses vs hostnames for August log:
[2026-04-18 15:13:19] IP addresses: 28.44% (446494 requests)
[2026-04-18 15:13:19] Hostnames: 71.56% (1123404 requests)
[2026-04-18 15:13:19] Top 10 most requested URLs (excluding 404 errors) for July log:
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
[2026-04-18 15:13:25] Top 10 most requested URLs (excluding 404 errors) for August log:
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
[2026-04-18 15:13:31] Most frequent HTTP methods with counts for July log:
1887646 "GET
   3952 "HEAD
    111 "POST
[2026-04-18 15:13:33] Most frequent HTTP methods with counts for August log:
1565812 "GET
   3965 "HEAD
    111 "POST
[2026-04-18 15:13:35] Number of 404 errors for July log:
10714
[2026-04-18 15:13:36] Number of 404 errors for August log:
9978
[2026-04-18 15:13:38] Most frequent response code and percentage for July log:
[2026-04-18 15:13:40] Response code: 200, Count: 1697914, Percentage: 89.76%
[2026-04-18 15:13:40] Most frequent response code and percentage for August log:
[2026-04-18 15:13:43] Response code: 200, Count: 1396473, Percentage: 88.95%
[2026-04-18 15:13:43] Hours of the day with most activity for July log:
 122479 14
 122079 12
 121200 15
 120814 13
 118025 16
 115720 11
 105507 10
  99969 09
  97609 17
  83750 08
[2026-04-18 15:13:45] Hours of the day with most activity for August log:
 109465 15
 105143 12
 104536 13
 101394 14
  99525 16
  95344 11
  88309 10
  80816 17
  78695 09
  66802 18
[2026-04-18 15:13:47] Hours of the day with least activity for July log:
  31919 05
  32234 04
  35253 06
  37398 03
  45297 02
  53066 01
  54017 07
  62450 00
  69362 23
  69809 20
[2026-04-18 15:13:49] Hours of the day with least activity for August log:
  26756 04
  27587 05
  29995 03
  31287 06
  32508 02
  38531 01
  47386 07
  47862 00
  54570 23
  57960 21
[2026-04-18 15:13:51] Date with the most activity for July log:
 134203 13/Jul/1995
[2026-04-18 15:13:55] Date with the most activity for August log:
  90125 31/Aug/1995
[2026-04-18 15:13:57] Date with the least activity for July log (excluding outage dates):
  27115 28/Jul/1995
[2026-04-18 15:14:01] Date with the least activity for August log (excluding outage dates):
  31608 26/Aug/1995
[2026-04-18 15:14:03] Data outage periods for August log:
=== Data Outage Detected ===
Last log before outage : 1995-08-01 14:52:01
First log after outage : 1995-08-03 04:36:13
Outage duration        : 37 hours, 44 minutes, 12 seconds
[2026-04-18 15:14:29] Largest response size and average response size for July log:
Largest response size: 6823936 bytes
Average response size: 20671.1 bytes
[2026-04-18 15:14:31] Largest response size and average response size for August log:
Largest response size: 3421948 bytes
Average response size: 17245 bytes
[2026-04-18 15:14:33] Host patterns in when errors occur for July log:
hoohoo.ncsa.uiuc.edu 251
jbiagioni.npt.nuwc.navy.mil 131
piweba3y.prodigy.com 110
piweba1y.prodigy.com 92
163.205.1.45 70
phaelon.ksc.nasa.gov 64
www-d4.proxy.aol.com 61
titan02f 57
piweba4y.prodigy.com 56
monarch.eng.buffalo.edu 56
[2026-04-18 15:14:34] Hour patterns in when errors occur for July log:
15 841
14 753
11 732
12 649
16 643
10 643
17 616
13 531
18 494
22 487
[2026-04-18 15:14:35] Host patterns in when errors occur for August log:
dialip-217.den.mmc.com 62
piweba3y.prodigy.com 47
155.148.25.4 44
scooter.pa-x.dec.com 39
maz3.maz.net 39
gate.barr.com 38
ts8-1.westwood.ts.ucla.edu 37
nexus.mlckew.edu.au 37
m38-370-9.mit.edu 37
204.62.245.32 37
[2026-04-18 15:14:36] Hour patterns in when errors occur for August log:
12 670
02 618
13 616
17 590
16 583
15 549
14 525
10 488
23 487
22 459
```
