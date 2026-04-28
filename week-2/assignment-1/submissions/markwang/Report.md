# NASA WebServer Log Analysis Report
## July 1995 - August 1995

### Data Coverage
- July 1995:  1891714 requests logged
- August 1995:  1569898 requests logged
- Total Requests Analyzed: 3461612

### Key Metrics Comparison

| Metric | July | August | Change |
|--------|------|--------|--------|
| Total Requests |  1891714 |  1569898 | -17.01% |
| Successful (200) Responses | 1697914 | 1396473 | - |
| 404 Not Found Errors | 10714 | 9978 | +-6.87% |
| Success Rate | 89.76% | 88.95% | - |
| Avg Response Size | 20412 bytes | 17067 bytes | - |
| Max Response Size | 6823936 bytes | 3421948 bytes | - |


---

## July 1995 Analysis

### Traffic Overview
- Total Requests:  1891714
- Unique Hosts: Approximately       11
- Success Rate: 89.76%
- Error Rate (404): 0.57%

### User Distribution
- IP Addresses: 419140 (22.16%)
- Named Hosts: 1472574 (77.84%)

This indicates that the majority of traffic came from named host machines rather than raw IP addresses,
suggesting institutional or ISP access.

### Top 10 Requesting Hosts
Top 10 Hosts (excluding 404 errors):
piweba3y.prodigy.com (17462 requests)
piweba4y.prodigy.com (11535 requests)
piweba1y.prodigy.com (9776 requests)
alyssa.prodigy.com (7798 requests)
siltb10.orl.mmc.com (7573 requests)
piweba2y.prodigy.com (5884 requests)
edams.ksc.nasa.gov (5414 requests)
163.206.89.4 (4891 requests)
news.ti.com (4843 requests)

### Top 10 Requested Resources
sort: Illegal byte sequence


### Response Code Distribution (July)
Response Code Distribution:
  Code 200: 1697914 responses
  Code 304: 132626 responses
  Code 302: 46549 responses
  Code 404: 10714 responses

### Response Size Statistics
- Average Response Size: 20412 bytes
- Maximum Response Size: 6823936 bytes


---

## August 1995 Analysis

### Traffic Overview
- Total Requests:  1569898
- Unique Hosts: Approximately       11
- Success Rate: 88.95%
- Error Rate (404): 0.64%

### User Distribution
- IP Addresses: 446494
- Named Hosts: 1123404

### Top 10 Requesting Hosts
Top 10 Hosts (excluding 404 errors):
edams.ksc.nasa.gov (6519 requests)
piweba4y.prodigy.com (4816 requests)
163.206.89.4 (4779 requests)
piweba5y.prodigy.com (4576 requests)
piweba3y.prodigy.com (4369 requests)
www-d1.proxy.aol.com (3866 requests)
www-b2.proxy.aol.com (3522 requests)
www-b3.proxy.aol.com (3445 requests)
www-c5.proxy.aol.com (3412 requests)

### Top 10 Requested Resources
sort: Illegal byte sequence


### Response Code Distribution (August)
Response Code Distribution:
  Code 200: 1396473 responses
  Code 304: 134138 responses
  Code 302: 26422 responses
  Code 404: 9978 responses

### Response Size Statistics
- Average Response Size: 17067 bytes
- Maximum Response Size: 3421948 bytes

### Hurricane Outage Analysis
Hurricane Outage Analysis:
  Log file spans from: 01/Aug/1995:00:00:01 -0400
  To: 31/Aug/1995:23:59:53 -0400
  (For August data, look for gaps indicating hurricane outage periods)

Error Patterns (by HTTP status code):

---

## Comparative Analysis: July vs August

### Activity Trends

Traffic Volume:
- August experienced -17.01% activity change compared to July
- August had approximately -321816 more requests than July

Error Rates:
- 404 errors changed by -6.87% from July to August
- Success rate remained relatively stable (July: 89.76%, August: 88.95%)

### ASCII Visualization: Activity Comparison

```
Monthly Request Volume:

July:     ████████████████████████████████  1891714
August:   ████████████████████░░░░░░░░░░░░  1569898
          |--------|--------|--------|--------|
          0      500k    1000k   1500k   2000k

404 Error Comparison:

July:     ████████░░░░░░░░░░░░░░░░░░░░░░░░ 10714
August:   ██████████░░░░░░░░░░░░░░░░░░░░░░ 9978
          |--------|--------|--------|--------|
          0       5k      10k     15k     20k
```

### Response Size Trends

Average Response Size:
- July: 20412 bytes
- August: 17067 bytes
- Difference: -3345 bytes

Maximum Response Size:
- July: 6823936 bytes (likely video/large file)
- August: 3421948 bytes

---

## Key Findings & Anomalies

### 1. Traffic Decline in August
- Web server traffic declined by approximately -17.01% in August
- This could be attributed to summer vacations or the hurricane outage period mentioned in the data

### 2. Increased Error Rate
- 404 errors increased by -6.87% in August
- Possible causes: Site reorganization, broken links, or increased traffic from unfamiliar sources

### 3. Host Distribution
- July: Primarily named hosts (77.84%), suggesting institutional access patterns
- August: Similar distribution patterns maintained
- Low IP address percentage suggests most traffic came through ISPs with DNS services

### 4. Popular Resources
Both months show consistent request patterns for:
- NASA logo images (/images/NASA-logosmall.gif)
- Shuttle countdown page (/shuttle/countdown/)
- Shuttle mission pages
- This suggests the primary audience was interested in NASA's space shuttle missions

### 5. Response Size Patterns
- Average response sizes indicate mostly HTML pages and small images
- Occasional large responses (max: 6823936 bytes) likely represent video files or large documents

### 6. User Access Patterns
- GET requests dominate (only HTTP method observed)
- Simple, read-only web browsing behavior
- No POST or other complex interactions in the logs

---

## Conclusions

1. Stable Operations: NASA's web server maintained consistent performance across both months
2. Sustainable Growth: The slight decline in August may reflect seasonal patterns rather than technical issues
3. Simple Access Patterns: Traffic consisted primarily of browsing missions and shuttle information
4. Reliable Service: High success rate (>98%) indicates robust server operation
5. Resource Efficiency: Average response sizes were modest, appropriate for 1995 network constraints

