# NASA Web Server Log Analysis Report

**Generated:** Tue Apr 21 14:42:26 PDT 2026
**Analyst:** ZhixianWang

## Dataset Overview

| Metric | July 1995 | August 1995 |
|--------|-----------|-------------|
| Total log lines | 1891714 | 1569898 |
| 404 errors | 10714 | 9978 |
| 4xx/5xx errors | 13303 | 11721 |
| Average response (bytes) | 20658 | 17242 |

---

## July 1995

### 1. Top 10 Hosts

| Host | Requests |
|------|----------|
| piweba3y.prodigy.com                          |    17462 |
| piweba4y.prodigy.com                          |    11535 |
| piweba1y.prodigy.com                          |     9776 |
| alyssa.prodigy.com                            |     7798 |
| siltb10.orl.mmc.com                           |     7573 |
| piweba2y.prodigy.com                          |     5884 |
| edams.ksc.nasa.gov                            |     5414 |
| 163.206.89.4                                  |     4891 |
| news.ti.com                                   |     4843 |
| disarray.demon.co.uk                          |     4344 |

### 2. IP vs Hostname

| Type | Count | % |
|------|-------|---|
| IP Addresses | 419140 | 22.2% |
| Hostnames    | 1472575 | 77.8% |

### 3. Top 10 Requested URLs

| URL | Requests |
|-----|----------|
| /images/NASA-logosmall.gif                              |   111144 |
| /images/KSC-logosmall.gif                               |    89530 |
| /images/MOSAIC-logosmall.gif                            |    60300 |
| /images/USA-logosmall.gif                               |    59845 |
| /images/WORLD-logosmall.gif                             |    59325 |
| /images/ksclogo-medium.gif                              |    58616 |
| /images/launch-logo.gif                                 |    40841 |
| /shuttle/countdown/                                     |    40251 |
| /ksc.html                                               |    40072 |
| /images/ksclogosmall.gif                                |    33555 |

### 4. HTTP Methods

| Method | Count |
|--------|-------|
| GET      |  1887646 |
| HEAD     |     3952 |
| POST     |      111 |

### 5. 404 Errors

  404 errors:    10714 (0.57% of all requests)

### 6. Response Code Distribution

| Status | Count | % |
|--------|-------|---|
| 200    |  1697914 |  89.8% |
| 304    |   132626 |   7.0% |
| 302    |    46549 |   2.5% |
| 404    |    10714 |   0.6% |
| 786    |      244 |   0.0% |
| 5866   |      186 |   0.0% |
| 234    |      169 |   0.0% |
| 7071   |      168 |   0.0% |
| 363    |      168 |   0.0% |
| 669    |      164 |   0.0% |

### 7. Hourly Activity (each █ ≈ 5 000 requests)

| Hour | Requests | Chart |
|------|----------|-------|
| 00:00 |   62450 | ████████████ |
| 01:00 |   53066 | ██████████ |
| 02:00 |   45297 | █████████ |
| 03:00 |   37398 | ███████ |
| 04:00 |   32234 | ██████ |
| 05:00 |   31919 | ██████ |
| 06:00 |   35253 | ███████ |
| 07:00 |   54017 | ██████████ |
| 08:00 |   83750 | ████████████████ |
| 09:00 |   99969 | ███████████████████ |
| 10:00 |  105507 | █████████████████████ |
| 11:00 |  115720 | ███████████████████████ |
| 12:00 |  122085 | ████████████████████████ |
| 13:00 |  120814 | ████████████████████████ |
| 14:00 |  122479 | ████████████████████████ |
| 15:00 |  121200 | ████████████████████████ |
| 16:00 |  118037 | ███████████████████████ |
| 17:00 |   97609 | ███████████████████ |
| 18:00 |   79282 | ███████████████ |
| 19:00 |   71776 | ██████████████ |
| 20:00 |   69809 | █████████████ |
| 21:00 |   71922 | ██████████████ |
| 22:00 |   70759 | ██████████████ |
| 23:00 |   69362 | █████████████ |

**Peak hour:** 14:00  **Quiet hour:** 05:00

### 8. Busiest Day

| Date | Requests |
|------|----------|
| 13/Jul/1995   |  134203 |

### 9. Quietest Day (≥100 requests)

| Date | Requests |
|------|----------|
| 28/Jul/1995   |   27121 |

### 10. Data Outage Detection

| Last before gap | First after gap | Notes |
|-----------------|-----------------|-------|
| — | — | No gaps detected |

### 11. Response Size

| Metric | Value |
|--------|-------|
| Largest | 6823936 bytes /shuttle/countdown/video/livevideo.jpeg |
| Average | 20658 bytes |

### 12. Error Patterns (4xx/5xx)

**Errors by hour:**

| Hour | Errors |
|------|--------|
| 00:00 | 665 |
| 01:00 | 487 |
| 02:00 | 297 |
| 03:00 | 302 |
| 04:00 | 179 |
| 05:00 | 195 |
| 06:00 | 195 |
| 07:00 | 289 |
| 08:00 | 421 |
| 09:00 | 577 |
| 10:00 | 704 |
| 11:00 | 857 |
| 12:00 | 744 |
| 13:00 | 610 |
| 14:00 | 954 |
| 15:00 | 978 |
| 16:00 | 872 |
| 17:00 | 733 |
| 18:00 | 574 |
| 19:00 | 479 |
| 20:00 | 461 |
| 21:00 | 583 |
| 22:00 | 574 |
| 23:00 | 573 |

**Top 5 hosts generating errors:**

| Host | Errors |
|------|--------|
| hoohoo.ncsa.uiuc.edu                          |    251 |
| 128.159.146.92                                |    202 |
| jbiagioni.npt.nuwc.navy.mil                   |    131 |
| piweba3y.prodigy.com                          |    110 |
| columbia.acc.brad.ac.uk                       |    108 |

**Top 5 error URLs:**

| URL | Errors |
|-----|--------|
| /pub/winvn/readme.txt                              |    667 |
| /pub/winvn/release.txt                             |    547 |
| /history/apollo/apollo-13.html                     |    286 |
| /images/NASA-logosmall.gif"                        |    244 |
| /shuttle/resources/orbiters/atlantis.gif           |    230 |

---

## August 1995

### 1. Top 10 Hosts

| Host | Requests |
|------|----------|
| edams.ksc.nasa.gov                            |     6519 |
| piweba4y.prodigy.com                          |     4816 |
| 163.206.89.4                                  |     4779 |
| piweba5y.prodigy.com                          |     4576 |
| piweba3y.prodigy.com                          |     4369 |
| www-d1.proxy.aol.com                          |     3866 |
| www-b2.proxy.aol.com                          |     3522 |
| www-b3.proxy.aol.com                          |     3445 |
| www-c5.proxy.aol.com                          |     3412 |
| www-b5.proxy.aol.com                          |     3393 |

### 2. IP vs Hostname

| Type | Count | % |
|------|-------|---|
| IP Addresses | 446494 | 28.4% |
| Hostnames    | 1123404 | 71.6% |

### 3. Top 10 Requested URLs

| URL | Requests |
|-----|----------|
| /images/NASA-logosmall.gif                              |    97293 |
| /images/KSC-logosmall.gif                               |    75283 |
| /images/MOSAIC-logosmall.gif                            |    67356 |
| /images/USA-logosmall.gif                               |    66975 |
| /images/WORLD-logosmall.gif                             |    66351 |
| /images/ksclogo-medium.gif                              |    62670 |
| /ksc.html                                               |    43619 |
| /history/apollo/images/apollo-logo1.gif                 |    37806 |
| /images/launch-logo.gif                                 |    35119 |
| /                                                       |    30123 |

### 4. HTTP Methods

| Method | Count |
|--------|-------|
| GET      |  1565812 |
| HEAD     |     3965 |
| POST     |      111 |

### 5. 404 Errors

  404 errors:     9978 (0.64% of all requests)

### 6. Response Code Distribution

| Status | Count | % |
|--------|-------|---|
| 200    |  1396473 |  89.0% |
| 304    |   134138 |   8.5% |
| 302    |    26422 |   1.7% |
| 404    |     9978 |   0.6% |
| 403    |      171 |   0.0% |
| 7089   |      128 |   0.0% |
| 786    |      117 |   0.0% |
| 5866   |      108 |   0.0% |
| 7131   |       98 |   0.0% |
| 669    |       93 |   0.0% |

### 7. Hourly Activity (each █ ≈ 5 000 requests)

| Hour | Requests | Chart |
|------|----------|-------|
| 00:00 |   47862 | █████████ |
| 01:00 |   38531 | ███████ |
| 02:00 |   32508 | ██████ |
| 03:00 |   29995 | █████ |
| 04:00 |   26756 | █████ |
| 05:00 |   27587 | █████ |
| 06:00 |   31287 | ██████ |
| 07:00 |   47386 | █████████ |
| 08:00 |   65443 | █████████████ |
| 09:00 |   78695 | ███████████████ |
| 10:00 |   88309 | █████████████████ |
| 11:00 |   95344 | ███████████████████ |
| 12:00 |  105143 | █████████████████████ |
| 13:00 |  104536 | ████████████████████ |
| 14:00 |  101394 | ████████████████████ |
| 15:00 |  109465 | █████████████████████ |
| 16:00 |   99527 | ███████████████████ |
| 17:00 |   80834 | ████████████████ |
| 18:00 |   66809 | █████████████ |
| 19:00 |   59315 | ███████████ |
| 20:00 |   59944 | ███████████ |
| 21:00 |   57985 | ███████████ |
| 22:00 |   60673 | ████████████ |
| 23:00 |   54570 | ██████████ |

**Peak hour:** 15:00  **Quiet hour:** 04:00

### 8. Busiest Day

| Date | Requests |
|------|----------|
| 31/Aug/1995   |   90125 |

### 9. Quietest Day (≥100 requests)

| Date | Requests |
|------|----------|
| 26/Aug/1995   |   31608 |

### 10. Data Outage Detection

| Last before gap | First after gap | Notes |
|-----------------|-----------------|-------|
| 01/Aug/1995 | 03/Aug/1995 | gap |

### 11. Response Size

| Metric | Value |
|--------|-------|
| Largest | 3421948 bytes /statistics/1995/Jul/Jul95_reverse_domains.html |
| Average | 17242 bytes |

### 12. Error Patterns (4xx/5xx)

**Errors by hour:**

| Hour | Errors |
|------|--------|
| 00:00 | 508 |
| 01:00 | 412 |
| 02:00 | 638 |
| 03:00 | 388 |
| 04:00 | 188 |
| 05:00 | 202 |
| 06:00 | 159 |
| 07:00 | 252 |
| 08:00 | 354 |
| 09:00 | 424 |
| 10:00 | 543 |
| 11:00 | 522 |
| 12:00 | 786 |
| 13:00 | 699 |
| 14:00 | 624 |
| 15:00 | 639 |
| 16:00 | 643 |
| 17:00 | 640 |
| 18:00 | 507 |
| 19:00 | 528 |
| 20:00 | 531 |
| 21:00 | 504 |
| 22:00 | 508 |
| 23:00 | 522 |

**Top 5 hosts generating errors:**

| Host | Errors |
|------|--------|
| columbia.acc.brad.ac.uk                       |    104 |
| dialip-217.den.mmc.com                        |     62 |
| escpsabp400.desc.dla.mil                      |     60 |
| piweba3y.prodigy.com                          |     47 |
| stadir.mil.nasa.gov                           |     44 |

**Top 5 error URLs:**

| URL | Errors |
|-----|--------|
| /pub/winvn/readme.txt                              |   1337 |
| /pub/winvn/release.txt                             |   1185 |
| /shuttle/missions/STS-69/mission-STS-69.html       |    682 |
| /images/nasa-logo.gif                              |    319 |
| /shuttle/missions/sts-68/ksc-upclose.gif           |    251 |

---

## July vs August Comparison

| Metric | July | August | Change |
|--------|------|--------|--------|
| Total requests | 1891714 | 1569898 | -321816 (-17.0%) |
| 404 errors | 10714 | 9978 | — |
| 4xx/5xx errors | 13303 | 11721 | — |
| Avg response bytes | 20658 | 17242 | — |

---

*Report generated by generate_report.sh — ZhixianWang*
