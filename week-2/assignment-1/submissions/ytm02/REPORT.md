# NASA Web Server Log Analysis — July & August 1995

_Generated on 2026-04-21T05:42:39Z by `generate_report.sh`._

This report analyzes real NASA Kennedy Space Center web server access
logs from July and August 1995. Data was parsed from the standard
Common Log Format, normalized into a tab-separated intermediate file,
and analyzed with bash, awk, sort, uniq and friends. See `analyze_logs.sh`
for the exact pipeline.

## 1. Executive Summary

| Metric | July 1995 | August 1995 |
|---|---:|---:|
| Raw log lines | 1891714 | 1569898 |
| Parsed lines | 1891706 | 1569888 |
| Unique hosts | 81981 | 75060 |
| Unique URLs | 21210 | 15348 |
| Total 404 responses | 10826 | 10037 |
| Total error responses (4xx/5xx) | 10958 | 10240 |
| Total bytes transferred | 38695977935 | 26828340650 |
| First date observed | 01/Jul/1995 | 01/Aug/1995 |
| Last date observed | 28/Jul/1995 | 31/Aug/1995 |

## 2. July 1995

### 2.1  Top 10 hosts (excluding 404 errors)

```
   17463  piweba3y.prodigy.com
   11535  piweba4y.prodigy.com
    9776  piweba1y.prodigy.com
    7798  alyssa.prodigy.com
    7573  siltb10.orl.mmc.com
    5884  piweba2y.prodigy.com
    5414  edams.ksc.nasa.gov
    4891  163.206.89.4
    4843  news.ti.com
    4344  disarray.demon.co.uk
```

### 2.2  IP addresses vs hostnames

```
Requests from IP addresses: 419135  (22.16%)
Requests from hostnames:    1472571  (77.84%)
Total requests:             1891706
```

### 2.3  Top 10 most requested URLs (excluding 404)

```
  111388  /images/NASA-logosmall.gif
   89639  /images/KSC-logosmall.gif
   60468  /images/MOSAIC-logosmall.gif
   60014  /images/USA-logosmall.gif
   59489  /images/WORLD-logosmall.gif
   58802  /images/ksclogo-medium.gif
   40871  /images/launch-logo.gif
   40279  /shuttle/countdown/
   40231  /ksc.html
   33585  /images/ksclogosmall.gif
```

### 2.4  HTTP request methods

```
 1887640  GET
    3952  HEAD
     111  POST
```

### 2.5  404 errors

```
Total 404 errors: 10826
```

### 2.6  Most frequent response code

```
Most frequent status: 200  (1701534 occurrences, 89.95% of responses)
Total responses:      1891692
```

### 2.7  Peak and quiet hours

```
Requests by hour of day:

00  #########################                           62450
01  #####################                               53066
02  ##################                                  45297
03  ###############                                     37398
04  #############                                       32233
05  #############                                       31919
06  ##############                                      35253
07  ######################                              54017
08  ##################################                  83749
09  ########################################            99969
10  ###########################################         105506
11  ###############################################     115720
12  #################################################   122085
13  #################################################   120813
14  ##################################################  122479
15  #################################################   121199
16  ################################################    118037
17  #######################################             97608
18  ################################                    79282
19  #############################                       71776
20  ############################                        69809
21  #############################                       71922
22  ############################                        70757
23  ############################                        69362

Peak hour:     14:00  (122479 requests)
Quietest hour: 05:00  (31919 requests)
```

### 2.8  Busiest day

```
Busiest day overall:
  13/Jul/1995  (134203 requests)

Top 5 busiest days:
        134203  13/Jul/1995
        100960  06/Jul/1995
         94575  05/Jul/1995
         92536  12/Jul/1995
         89584  03/Jul/1995
```

### 2.9  Quietest day (excluding outage dates)

```
Quietest day (excluding outage days with < 6467 requests):
  28/Jul/1995  (27121 requests)

Bottom 5 days (including possible outage days):
         39199  23/Jul/1995
         38867  08/Jul/1995
         35272  09/Jul/1995
         35267  22/Jul/1995
         27121  28/Jul/1995
```

### 2.10 Hurricane / outage detection

```
Data collection stopped: 1995-07-13 19:48:59
Data collection resumed: 1995-07-13 20:11:05
Total outage duration:   1326 seconds (0 hr 22 min 6 sec)
```

### 2.11 Response sizes

```
Largest response:  6823936 bytes
  URL:             /shuttle/countdown/video/livevideo.jpeg
  Host:            derec
Average response:  20670.94 bytes  (over 1871999 sized responses)
Total bytes sent:  38695977935 bytes  (36.04 GB)
```

### 2.12 Error patterns

```
Error definition: any status code >= 400.
Total error responses: 10958

Errors by hour:
  00:00  432
  01:00  320
  02:00  265
  03:00  240
  04:00  167
  05:00  148
  06:00  134
  07:00  243
  08:00  365
  09:00  482
  10:00  647
  11:00  742
  12:00  658
  13:00  538
  14:00  756
  15:00  843
  16:00  651
  17:00  618
  18:00  507
  19:00  415
  20:00  383
  21:00  448
  22:00  486
  23:00  470

Top 10 hosts producing errors:
       251  hoohoo.ncsa.uiuc.edu
       131  jbiagioni.npt.nuwc.navy.mil
       109  piweba3y.prodigy.com
        92  piweba1y.prodigy.com
        70  163.205.1.45
        64  phaelon.ksc.nasa.gov
        61  www-d4.proxy.aol.com
        57  titan02f
        56  piweba4y.prodigy.com
        56  monarch.eng.buffalo.edu

Top 10 URLs that produced errors:
       667  /pub/winvn/readme.txt
       547  /pub/winvn/release.txt
       286  /history/apollo/apollo-13.html
       232  /shuttle/resources/orbiters/atlantis.gif
       230  /history/apollo/a-001/a-001-patch-small.gif
       215  /history/apollo/pad-abort-test-1/pad-abort-test-1-patch-small.gif
       215  /://spacelink.msfc.nasa.gov
       214  /images/crawlerway-logo.gif
       183  /history/apollo/sa-1/sa-1-patch-small.gif
       180  /shuttle/resources/orbiters/discovery.gif

Error status code breakdown:
     10826  404
        62  500
        53  403
        14  501
         3  400
```

## 3. August 1995

### 3.1  Top 10 hosts (excluding 404 errors)

```
    6517  edams.ksc.nasa.gov
    4818  piweba4y.prodigy.com
    4779  163.206.89.4
    4576  piweba5y.prodigy.com
    4369  piweba3y.prodigy.com
    3866  www-d1.proxy.aol.com
    3522  www-b2.proxy.aol.com
    3445  www-b3.proxy.aol.com
    3412  www-c5.proxy.aol.com
    3393  www-b5.proxy.aol.com
```

### 3.2  IP addresses vs hostnames

```
Requests from IP addresses: 446486  (28.44%)
Requests from hostnames:    1123402  (71.56%)
Total requests:             1569888
```

### 3.3  Top 10 most requested URLs (excluding 404)

```
   97410  /images/NASA-logosmall.gif
   75337  /images/KSC-logosmall.gif
   67448  /images/MOSAIC-logosmall.gif
   67068  /images/USA-logosmall.gif
   66444  /images/WORLD-logosmall.gif
   62778  /images/ksclogo-medium.gif
   43688  /ksc.html
   37826  /history/apollo/images/apollo-logo1.gif
   35138  /images/launch-logo.gif
   30347  /
```

### 3.4  HTTP request methods

```
 1565810  GET
    3965  HEAD
     111  POST
```

### 3.5  404 errors

```
Total 404 errors: 10037
```

### 3.6  Most frequent response code

```
Most frequent status: 200  (1398987 occurrences, 89.11% of responses)
Total responses:      1569870
```

### 3.7  Peak and quiet hours

```
Requests by hour of day:

00  #####################                               47862
01  #################                                   38531
02  ##############                                      32508
03  #############                                       29995
04  ############                                        26756
05  ############                                        27587
06  ##############                                      31287
07  #####################                               47386
08  #############################                       65443
09  ###################################                 78695
10  ########################################            88309
11  ###########################################         95341
12  ################################################    105143
13  ###############################################     104534
14  ##############################################      101393
15  ##################################################  109461
16  #############################################       99527
17  ####################################                80834
18  ##############################                      66809
19  ###########################                         59315
20  ###########################                         59944
21  ##########################                          57985
22  ###########################                         60673
23  ########################                            54570

Peak hour:     15:00  (109461 requests)
Quietest hour: 04:00  (26756 requests)
```

### 3.8  Busiest day

```
Busiest day overall:
  31/Aug/1995  (90121 requests)

Top 5 busiest days:
         90121  31/Aug/1995
         80640  30/Aug/1995
         67988  29/Aug/1995
         61248  10/Aug/1995
         61246  11/Aug/1995
```

### 3.9  Quietest day (excluding outage dates)

```
Quietest day (excluding outage days with < 5698 requests):
  26/Aug/1995  (31608 requests)

Bottom 5 days (including possible outage days):
         32823  27/Aug/1995
         32420  06/Aug/1995
         32094  19/Aug/1995
         31893  05/Aug/1995
         31608  26/Aug/1995
```

### 3.10 Hurricane / outage detection

```
Data collection stopped: 1995-08-01 14:52:01
Data collection resumed: 1995-08-03 04:36:13
Total outage duration:   135852 seconds (37 hr 44 min 12 sec)
```

### 3.11 Response sizes

```
Largest response:  3421948 bytes
  URL:             /statistics/1995/Jul/Jul95_reverse_domains.html
  Host:            163.205.156.16
Average response:  17244.80 bytes  (over 1555735 sized responses)
Total bytes sent:  26828340650 bytes  (24.99 GB)
```

### 3.12 Error patterns

```
Error definition: any status code >= 400.
Total error responses: 10240

Errors by hour:
  00:00  368
  01:00  332
  02:00  616
  03:00  364
  04:00  185
  05:00  168
  06:00  135
  07:00  223
  08:00  341
  09:00  363
  10:00  494
  11:00  428
  12:00  653
  13:00  617
  14:00  527
  15:00  556
  16:00  582
  17:00  587
  18:00  428
  19:00  443
  20:00  442
  21:00  437
  22:00  465
  23:00  486

Top 10 hosts producing errors:
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

Top 10 URLs that produced errors:
      1337  /pub/winvn/readme.txt
      1185  /pub/winvn/release.txt
       683  /shuttle/missions/STS-69/mission-STS-69.html
       319  /images/nasa-logo.gif
       253  /shuttle/missions/sts-68/ksc-upclose.gif
       209  /elv/DELTA/uncons.htm
       200  /history/apollo/sa-1/sa-1-patch-small.gif
       166  /://spacelink.msfc.nasa.gov
       160  /images/crawlerway-logo.gif
       154  /history/apollo/a-001/a-001-patch-small.gif

Error status code breakdown:
     10037  404
       171  403
        27  501
         3  500
         2  400
```

## 4. July vs August Comparison

The dataset lets us compare two back-to-back months of traffic from
the same server. Points worth highlighting:

- **Traffic volume change**: -17.01% from July to August (parsed lines).
- **404 error change**: -7.29%.
- **All 4xx/5xx error change**: -6.55%.
- August includes a multi-day outage (see §3.10 of the August section);
  this depresses the monthly total relative to a hypothetical full month.

### 4.1 Key metrics comparison (ASCII)

```
Metric               0%                         100%               Count
--------------  ---  --------------------------------------------
Requests        Jul  ############################################  1891706
                Aug  ####################################          1569888

404 errors      Jul  ############################################  10826
                Aug  ########################################      10037

All errors      Jul  ############################################  10958
                Aug  #########################################     10240

Bytes sent      Jul  ############################################  38695977935
                Aug  ##############################                26828340650
```

## 5. Interesting findings & anomalies

- **Hurricane Erin (August 1995)** caused a multi-day collection gap;
  the largest entries in §3.9 (August) identify the outage window: from
  1995-08-01 14:52 to 1995-08-03 04:36 (approx. 37.7 hours), with
  02/Aug/1995 recording zero requests.
- **Peak hours** cluster during US east-coast daytime (see §2.6 / §3.6).
  Traffic is highly bursty — the peak-to-trough ratio across 24 hours is
  typically 3–4×.
- **Top requested URLs** are overwhelmingly small GIF images (NASA/KSC
  logos, countdown clock). In the pre-CDN era every HTML page triggered
  several separate image requests.
- **GET dominates**: over 99.7% of requests in both months use GET,
  consistent with a read-only public documentation/mission site.
- **Hostname share dropped** from 77.8% in July to 71.6% in August,
  suggesting slightly more anonymous (IP-only) traffic in August.

## 6. Methodology notes

- Parsing uses awk + regex to extract the bracketed timestamp and
  the quoted request line rather than positional field splitting;
  this is robust to embedded spaces in URLs.
- Response sizes recorded as `-` (unknown) are excluded from average
  and max computations but still counted as responses.
- HTTP status codes are validated to match `[1-5][0-9][0-9]` before counting;
  malformed log lines that produce garbage in the status field are excluded.
- HTTP methods are validated to contain only uppercase letters (`[A-Z]+`);
  mis-parsed method fields from unusual log entries are excluded.
- "Error" means any valid status code in the 4xx or 5xx range.
- Outage detection uses two techniques: (a) the largest gaps between
  consecutive timestamps, and (b) calendar days with zero entries
  in the observed date range.

---

_Scripts: `download_data.sh`, `analyze_logs.sh`, `generate_report.sh`,
`run_pipeline.sh`. Run `./run_pipeline.sh` to regenerate this report
from scratch._
