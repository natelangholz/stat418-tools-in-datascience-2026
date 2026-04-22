# NASA Web Server Log Analysis Report

**Generated:** Wed Apr 15 21:02:36 PDT 2026

---

## Summary Statistics

| Metric | July 1995 | August 1995 |
|--------|-----------|-------------|
| Total requests | 1891714 | 1569898 |
| Unique hosts | 81983 | 75060 |
| 404 errors | 10714 | 9978 |
| Largest response | 6823936 bytes | 3421948 bytes |
| Avg response size | 20658 bytes | 17242 bytes |
| Busiest day |  134203 13/Jul/1995 |   90125 31/Aug/1995 |
| Peak hour |  122479 14 |  109465 15 |

---

## July 1995 Analysis

**Most requested URL:** `/images/NASA-logosmall.gif`

### Requests by Hour of Day (July)

Each `#` represents ~2,000 requests. Scale is relative to July's peak hour.

```
  00 | #################### (62450)
  01 | ################# (53066)
  02 | ############## (45297)
  03 | ############ (37398)
  04 | ########## (32234)
  05 | ########## (31919)
  06 | ########### (35253)
  07 | ################# (54017)
  08 | ########################### (83750)
  09 | ################################ (99969)
  10 | ################################## (105507)
  11 | ##################################### (115720)
  12 | ####################################### (122085)
  13 | ####################################### (120814)
  14 | ######################################## (122479)
  15 | ####################################### (121200)
  16 | ###################################### (118037)
  17 | ############################### (97609)
  18 | ######################### (79282)
  19 | ####################### (71776)
  20 | ###################### (69809)
  21 | ####################### (71922)
  22 | ####################### (70759)
  23 | ###################### (69362)
```

---

## August 1995 Analysis

**Most requested URL:** `/images/NASA-logosmall.gif`

**Hurricane outage:** August 2nd is entirely missing from the logs.
Data stopped at `01/Aug/1995 14:52:01` and resumed at `03/Aug/1995 04:36:13`,
an outage of approximately **37 hours 44 minutes**.

### Requests by Hour of Day (August)

Each `#` represents ~2,000 requests. Scale is relative to August's peak hour.
Note: lower total counts reflect the two-day outage.

```
  00 | ################# (47862)
  01 | ############## (38531)
  02 | ########### (32508)
  03 | ########## (29995)
  04 | ######### (26756)
  05 | ########## (27587)
  06 | ########### (31287)
  07 | ################# (47386)
  08 | ####################### (65443)
  09 | ############################ (78695)
  10 | ################################ (88309)
  11 | ################################## (95344)
  12 | ###################################### (105143)
  13 | ###################################### (104536)
  14 | ##################################### (101394)
  15 | ######################################## (109465)
  16 | #################################### (99527)
  17 | ############################# (80834)
  18 | ######################## (66809)
  19 | ##################### (59315)
  20 | ##################### (59944)
  21 | ##################### (57985)
  22 | ###################### (60673)
  23 | ################### (54570)
```

---

## July vs August Comparison

July had **321816 more requests** than August.

| Metric | Change |
|--------|--------|
| Requests | July: 1891714 vs August: 1569898 |
| 404 errors | July: 10714 vs August: 9978 |
| Unique hosts | July: 81983 vs August: 75060 |
| Avg response size | July: 20658B vs August: 17242B |

---

## Interesting Findings and Anomalies

- **Hurricane outage (August):** August 2nd is completely absent from the logs due to a hurricane.
  Nearly 38 hours of traffic data was lost, affecting day-over-day totals.
- **Peak traffic time:** Both months peak around 3 PM EDT (hour 15), consistent with
  daytime NASA website browsing patterns.
- **404 error rate:** July had 10714 404 errors vs August's 9978 — the similar
  counts across both months suggest persistent broken links rather than one-off issues.
- **Response sizes:** The largest single response was over 3 MB (likely a large image or
  file download), while the average of ~17 KB is typical for a mix of HTML and images.
- **Host types:** The majority of traffic comes from named hostnames rather than raw IP
  addresses, suggesting most visitors were on institutional networks.
