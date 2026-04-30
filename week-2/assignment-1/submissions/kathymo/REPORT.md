# NASA Web Server Analysis Report
## Global Traffic Analysis: July - August 1995

---
## 1. Monthly Summary Comparison
| Metric | July 1995 | August 1995 |
| :--- | :--- | :--- |
| **Busiest Day (Date)** | 13/Jul/1995 | 31/Aug/1995 |
| **Quietest Day (Date)** | 28/Jul/1995 | 26/Aug/1995 |
| **Total 404 Errors** | 10714 | 9978 |

## 2. Protocol & Request Methods
| Method | July Frequency | August Frequency |
| :--- | :--- | :--- |
| **GET** | 1887646 | 1565812 |
| **HEAD** | 3952 | 3965 |
| **POST** | 111 | 111 |

## 3. Server Response Success Rates
| Status Code | July Success % | August Success % |
| :--- | :--- | :--- |
| **Code 200 (OK)** | 89.80% | 89.01% |

## 4. Host Resolution Metrics
| Category | July Percentage | August Percentage |
| :--- | :--- | :--- |
| **Resolved Hostnames** | 77.77% | 71.50% |
| **Raw IP Addresses** | 22.23% | 28.50% |

## 5. Daily Traffic Volume (Visualized)
Comparison of Peak Daily Volume (1 '#' = 5,000 requests)
```text
July Peak   [##########################    ] 134203
August Peak [##################            ] 90125
```
## 6. Time-Based Analysis: Hourly Peaks
| Month | Peak Traffic Hour | Quietest Traffic Hour |
| :--- | :--- | :--- |
| **July** | 14:00 122479 reqs | 05:00 31919 reqs |
| **August** | 15:00 109465 reqs | 04:00 26756 reqs |

## 7. Data Payload Statistics
| Metric | July 1995 | August 1995 |
| :--- | :--- | :--- |
| **Maximum Single Response** | 6823936 bytes | 3421948 bytes |
| **Average Response Size** | Avg: 20657.68 | Avg: 17241.67 |

## 8. Top 10 Host Activity (Frequency)
| Rank | July Active Host (Hits) | August Active Host (Hits) |
| :--- | :--- | :--- |
| 1 | piweba3y.prodigy.com (17462) | edams.ksc.nasa.gov (6519) |
| 2 | piweba4y.prodigy.com (11535) | piweba4y.prodigy.com (4816) |
| 3 | piweba1y.prodigy.com (9776) | 163.206.89.4 (4779) |
| 4 | alyssa.prodigy.com (7798) | piweba5y.prodigy.com (4576) |
| 5 | siltb10.orl.mmc.com (7573) | piweba3y.prodigy.com (4369) |
| 6 | piweba2y.prodigy.com (5884) | www-d1.proxy.aol.com (3866) |
| 7 | edams.ksc.nasa.gov (5414) | www-b2.proxy.aol.com (3522) |
| 8 | 163.206.89.4 (4891) | www-b3.proxy.aol.com (3445) |
| 9 | news.ti.com (4843) | www-c5.proxy.aol.com (3412) |
| 10 | disarray.demon.co.uk (4344) | www-b5.proxy.aol.com (3393) |

## 9. Top 10 Content Requests
| Rank | July URL (Hits) | August URL (Hits) |
| :--- | :--- | :--- |
| 1 | /images/NASA-logosmall.gif (111144) | /images/NASA-logosmall.gif (97293) |
| 2 | /images/KSC-logosmall.gif (89530) | /images/KSC-logosmall.gif (75283) |
| 3 | /images/MOSAIC-logosmall.gif (60300) | /images/MOSAIC-logosmall.gif (67356) |
| 4 | /images/USA-logosmall.gif (59845) | /images/USA-logosmall.gif (66975) |
| 5 | /images/WORLD-logosmall.gif (59325) | /images/WORLD-logosmall.gif (66351) |
| 6 | /images/ksclogo-medium.gif (58616) | /images/ksclogo-medium.gif (62670) |
| 7 | /images/launch-logo.gif (40841) | /ksc.html (43619) |
| 8 | /shuttle/countdown/ (40251) | /history/apollo/images/apollo-logo1.gif (37806) |
| 9 | /ksc.html (40072) | /images/launch-logo.gif (35119) |
| 10 | /images/ksclogosmall.gif (33555) | / (30123) |

## 10. Advanced Error Patterns
### 10.1 Peak Error Hours
| Rank | July Error Hour (Count) | August Error Hour (Count) |
| :--- | :--- | :--- |
| 1 | 15:00 (1011 errors) | 12:00 (797 errors) |
| 2 | 14:00 (982 errors) | 13:00 (732 errors) |
| 3 | 16:00 (904 errors) | 16:00 (675 errors) |

### 10.2 Highest Error-Producing Hosts
| Rank | July Host (Count) | August Host (Count) |
| :--- | :--- | :--- |
| 1 | blazemonger.pc.cc.cmu.edu (611 errors) | zooropa.res.cmu.edu (624 errors) |
| 2 | hoohoo.ncsa.uiuc.edu (251 errors) | columbia.acc.brad.ac.uk (104 errors) |
| 3 | 128.159.146.92 (202 errors) | dialip-217.den.mmc.com (62 errors) |

## 11. Hurricane Outage Analysis
> [!CAUTION]
> Operational Gap Detected: August 1, 1995 - August 3, 1995

| Metric | Data Point |
| :--- | :--- |
| **Outage Start** | 192.94.94.33 - - [01/Aug/1995:14:52:01 -0400] "GET /shuttle/countdown/video/livevideo.jpeg HTTP/1.0" 200 40960 |
| **Outage End** | n1031657.ksc.nasa.gov - - [03/Aug/1995:04:36:13 -0400] "GET /ksc.html HTTP/1.0" 200 7280 |
| **Total Downtime** | 37 hours and 44 minutes (135852 total seconds). |

## 12. Technical Spreadsheet Export (CSV)
```csv
Month,GET,HEAD,POST,Busiest_Day_Vol,Max_Bytes,404_Errors
July,1887646,3952,111,134203,6823936,10714
August,1565812,3965,111,90125,3421948,9978
```
