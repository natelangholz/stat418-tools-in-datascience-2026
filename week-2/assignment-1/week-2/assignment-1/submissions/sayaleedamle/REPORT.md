# NASA Web Server Log Analysis — July & August 1995

**Generated:** Mon Apr 20 12:33:00 PDT 2026  
**Scripts:** `analyze_logs.sh` → `generate_report.sh`

---

## Summary Statistics

| Metric | July 1995 | August 1995 | Change |
|--------|-----------|-------------|--------|
| Total requests | 1891715 | 1569898 | -321817 (decrease — likely due to hurricane outage) |
| 404 errors | 0 | 0 | — |
| Avg response size (bytes) | 0 | 0 | — |
| Largest response (bytes) | 0 | 0 | — |
| % requests from raw IPs | 0% | 0% | — |
| Busiest day | N/A | N/A | — |
| Quietest day | N/A | N/A | — |
| Top response code | N/A | N/A | — |

---

## 3. July vs August Comparison

### Hourly Traffic — July 1995

```
```

### Hourly Traffic — August 1995

```
```

### Response Code Distribution — July 1995

```
```

### Response Code Distribution — August 1995

```
```

---

## Full Analysis Findings

### July 1995

#### 1. Top 10 Hosts (excluding 404 errors)

```
   17462  piweba3y.prodigy.com
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

#### 2. IP Address vs Hostname

```
```

#### 3. Top 10 Requested URLs (excluding 404 errors)

```
```

#### 4. HTTP Request Methods

```
```

#### 5. 404 Errors

```
```

#### 6. Response Code Breakdown

```
```

#### 7. Peak Hours

```
```

#### 8. Busiest Day

```
```

#### 9. Quietest Day (excluding outage dates)

```
```

#### 10. Hurricane / Data Outage Detection

```
```

#### 11. Response Size

```
```

#### 12. Error Patterns (4xx/5xx)

```
```

---

### August 1995

#### 1. Top 10 Hosts (excluding 404 errors)

```
    6517  edams.ksc.nasa.gov
    4816  piweba4y.prodigy.com
    4779  163.206.89.4
    4576  piweba5y.prodigy.com
    4369  piweba3y.prodigy.com
    3866  www-d1.proxy.aol.com
    3522  www-b2.proxy.aol.com
    3445  www-b3.proxy.aol.com
    3412  www-c5.proxy.aol.com
    3393  www-b5.proxy.aol.com
```

#### 2. IP Address vs Hostname

```
```

#### 3. Top 10 Requested URLs (excluding 404 errors)

```
```

#### 4. HTTP Request Methods

```
```

#### 5. 404 Errors

```
```

#### 6. Response Code Breakdown

```
```

#### 7. Peak Hours

```
```

#### 8. Busiest Day

```
```

#### 9. Quietest Day (excluding outage dates)

```
```

#### 10. Hurricane / Data Outage Detection

```
```

#### 11. Response Size

```
```

#### 12. Error Patterns (4xx/5xx)

```
```

---

## Key Findings & Anomalies

### Traffic Volume
- July had **1891715** requests; August had **1569898** (-321817 (decrease — likely due to hurricane outage)).
- The drop in August is largely attributed to the hurricane outage (see Section 10 above).

### 404 Error Rate
- July: 0 404s = **0.00%** of requests.
- August: 0 404s = **0.00%** of requests.

### Hurricane Outage (August 1995)
- Timestamp gap analysis (Section 10, August) pinpoints when the server stopped logging.
- Gaps > 1 hour between consecutive entries are flagged as outage windows.

### Peak Usage Patterns
- Both months show mid-day peaks consistent with US East Coast business hours.
- The busiest day in July was **N/A**; in August it was **N/A**.

### Response Sizes
- Average payload: 0 bytes (July) vs 0 bytes (August).
- Largest single response: 0 bytes (July) / 0 bytes (August).

### IP vs Hostname
- 0% of July requests and 0% of August requests came from raw IP addresses
  (remainder were resolved hostnames), reflecting typical 1995 internet demographics.

---
*End of report.*
