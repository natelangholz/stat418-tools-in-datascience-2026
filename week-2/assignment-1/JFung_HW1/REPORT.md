# Final Report: Analysis of NASA Web Server Logs

Generated on: Tue Apr 21 01:22:49 PDT 2026

## Step 1 Output
```
Downloading NASA web server logs...
Downloaded NASA_Jul95.log
Downloaded NASA_Aug95.log
Download complete!
NASA_Jul95.log file size:
-rw-r--r-- 1 jfung 197609 196M Apr 21 00:37 NASA_Jul95.log
NASA_Aug95.log file size:
-rw-r--r-- 1 jfung 197609 161M Apr 21 00:37 NASA_Aug95.log
NASA_Jul95.log line count:
1891714 NASA_Jul95.log
NASA_Aug95.log line count:
1569898 NASA_Aug95.log
```

## Step 2 Output
```
Starting basic analysis of NASA log files...
Top 10 Hosts in NASA_Jul95.log:
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
Top 10 Hosts in NASA_Aug95.log:
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
Calculating percentage of requests from IP addresses vs hostnames in NASA_Jul95.log:
Percentage of requests from IP addresses in NASA_Jul95.log: 22%
Percentage of requests from hostnames in NASA_Jul95.log: 78%
Calculating percentage of requests from IP addresses vs hostnames in NASA_Aug95.log:
Percentage of requests from IP addresses in NASA_Aug95.log: 28%
Percentage of requests from hostnames in NASA_Aug95.log: 72%
Top 10 URLs in NASA_Jul95.log:
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
Top 10 URLs in NASA_Aug95.log:
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
Most frequent HTTP methods in NASA_Jul95.log:
1887646 "GET
   3952 "HEAD
    111 "POST
      2 "kƒûtxƒûtGƒûtÍƒû"
      2 "1/history/apollo/images/"
      1 ""
      1 
Most frequent HTTP methods in NASA_Aug95.log:
1565812 "GET
   3965 "HEAD
    111 "POST
      4 "±‰6žÿT7‰FÃÇF"
      2 "ýÑí.Š2í.‹>î
      2 "€|t°9Ã°'Ã€|u&÷G"
      1 "huttle/countdown/"
      1 "?"
Number of 404 errors in NASA_Jul95.log:
10714
Number of 404 errors in NASA_Aug95.log:
9978
Most frequent response code in NASA_Jul95.log:
1697914 200
Calculating percentage of Jul95 responses:
Percentage of most frequent response code in NASA_Jul95.log: 89%
Most frequent response code in NASA_Aug95.log:
1396473 200
Calculating percentage of Aug95 responses:
Percentage of most frequent response code in NASA_Aug95.log: 88%
Top five active hours in NASA_Jul95.log:
 122479 14
 122085 12
 121200 15
 120814 13
 118037 16
Top five quiet hours in NASA_Jul95.log:
  31919 05
  32234 04
  35253 06
  37398 03
  45297 02
Top five active hours in NASA_Aug95.log:
 109465 15
 105143 12
 104536 13
 101394 14
  99527 16
Top five quiet hours in NASA_Aug95.log:
  26756 04
  27587 05
  29995 03
  31287 06
  32508 02
Busiest day in NASA_Jul95.log:
 134203 13/Jul/1995
Busiest day in NASA_Aug95.log:
  90125 31/Aug/1995
Quietest day in NASA_Jul95.log:
  27121 28/Jul/1995
Quietest day in NASA_Aug95.log:
  31608 26/Aug/1995
  33996 01/Aug/1995
  41388 03/Aug/1995
  59557 04/Aug/1995
  31893 05/Aug/1995
  32420 06/Aug/1995
  57362 07/Aug/1995
  60157 08/Aug/1995
  60458 09/Aug/1995
  61248 10/Aug/1995
  61246 11/Aug/1995
  38071 12/Aug/1995
  36480 13/Aug/1995
  59878 14/Aug/1995
  58847 15/Aug/1995
  56653 16/Aug/1995
  58988 17/Aug/1995
  56246 18/Aug/1995
  32094 19/Aug/1995
  32963 20/Aug/1995
  55540 21/Aug/1995
  57762 22/Aug/1995
  58097 23/Aug/1995
  52552 24/Aug/1995
  57321 25/Aug/1995
  31608 26/Aug/1995
  32823 27/Aug/1995
  55496 28/Aug/1995
  67988 29/Aug/1995
  80641 30/Aug/1995
  90125 31/Aug/1995
While the quietest August day in part 9 is 26/Aug/1995, there was no data on 02/Aug/1995, which represents the Hurricane Erin outage.
Hurricane data outage start:
01/Aug/1995:14:52:01 -0400
end:
03/Aug/1995:04:36:13 -0400
135852
The largest response size(bytes) in NASA_Jul95.log is:
6823936
The largest response size(bytes) in NASA_Aug95.log is:
3421948
The average response size(bytes) in NASA_Jul95.log is:
20572
The average response size(bytes) in NASA_Aug95.log is:
17198.5
There are 10714 404 errors in NASA_Jul95.log
Top 5 hosts causing 404 errors in NASA_Jul95.log:
    251 hoohoo.ncsa.uiuc.edu
    131 jbiagioni.npt.nuwc.navy.mil
    110 piweba3y.prodigy.com
     92 piweba1y.prodigy.com
     64 phaelon.ksc.nasa.gov
The top host, hoohoo.ncsa.uiuc.edu, was responsible for 2.34273% of the 404 errors.
Top 5 URLs causing 404 errors in NASA_Jul95.log:
    667 /pub/winvn/readme.txt
    547 /pub/winvn/release.txt
    286 /history/apollo/apollo-13.html
    230 /shuttle/resources/orbiters/atlantis.gif
    230 /history/apollo/a-001/a-001-patch-small.gif
The top URL, /pub/winvn/readme.txt, was responsible for 6.2255% of the 404 errors.
Top 5 request types causing 404 errors in NASA_Jul95.log:
  10707 "GET
      5 "POST
      2 "HEAD
The top request type, "GET, was responsible for 99.9347% of the 404 errors.
However, GET requests accounted for 99.785% of all requests in NASA_Jul95.log
And, GET requests accounted for 99.7848% of no error requests in NASA_Jul95.log
So while GET requests are the most common request type causing 404 errors, they are also the most common request type overall, and a significant portion of GET requests do not result in 404 errors at 99.9998%.
Top 5 hours causing 404 errors in NASA_Jul95.log:
    833 15
    752 14
    731 11
    657 12
    632 16
The top hours for 404 errors in NASA_Jul95.log occur between 11 and 16 hours(excluding 13/1pm).
From part 7b, the busiest hours in NASA_Jul95.log are similarly between 11 and 16 hours, which suggests that the 404 errors are more likely to occur during busy hours, indicating potential server overload.
The percentage of 404 errors that occur between 11 and 16 hours in NASA_Jul95.log is: 38.6317%
The percentage of requests that occur between 11 and 16 hours in NASA_Jul95.log that result in 404 errors is: 0.574594%
The most errors occur during the busy hours, however, the busy hours only account for 38.6317% of errors, and only 0.574594% of requests during busy hours result in 404 errors.
Top 5 dates causing 404 errors in NASA_Jul95.log:
    641 06/Jul/1995
    638 19/Jul/1995
    569 07/Jul/1995
    531 13/Jul/1995
    497 05/Jul/1995
The top date for 404 errors in NASA_Jul95.log is: 06/Jul/1995 with 5.98283% of all 404 errors.
In July 1995, there were 10714 404 errors.  On the surface, the most highly correlated variables are the request type and hour.
GET requests are the most common request type causing 404 errors, however, most requests are GET request and of GET requests, the majority do not result in 404 errors.
The most common hours for 404 errors are between hours 11 and 16, but the hours are also the most high traffic hours and the majority of requests during the busy hours did not return errors.
There are 9978 404 errors in NASA_Aug95.log
Top 5 hosts causing 404 errors in NASA_Aug95.log:
     62 dialip-217.den.mmc.com
     47 piweba3y.prodigy.com
     44 155.148.25.4
     39 maz3.maz.net
     38 gate.barr.com
The top host, dialip-217.den.mmc.com, was responsible for 0.621367% of the 404 errors.
Top 5 URLs causing 404 errors in NASA_Aug95.log:
   1337 /pub/winvn/readme.txt
   1185 /pub/winvn/release.txt
    682 /shuttle/missions/STS-69/mission-STS-69.html
    319 /images/nasa-logo.gif
    251 /shuttle/missions/sts-68/ksc-upclose.gif
The top URL, /pub/winvn/readme.txt, was responsible for 13.3995% of the 404 errors.
Top 5 request types causing 404 errors in NASA_Aug95.log:
   9969 "GET
      7 "POST
      2 "HEAD
The top request type, "GET, was responsible for 99.9098% of the 404 errors.
However, GET requests accounted for 99.7397% of all requests in NASA_Aug95.log.
And, GET requests accounted for 99.7396% of no error requests in NASA_Aug95.log
So while GET requests are the most common request type causing 404 errors, they are also the most common request type overall, and a significant portion of GET requests do not result in 404 errors at 99.9999%.
Top 5 hours causing 404 errors in NASA_Aug95.log:
    651 12
    614 13
    598 02
    586 17
    550 16
The top hours for 404 errors in NASA_Aug95.log occur during 12,13,02,17,16 hours.
The percentage of 404 errors that occur in the top hours in NASA_Aug95.log is: 30.0561%
Top 5 dates causing 404 errors in NASA_Aug95.log:
    571 30/Aug/1995
    537 07/Aug/1995
    526 31/Aug/1995
    420 29/Aug/1995
    420 24/Aug/1995
The top date for 404 errors in NASA_Aug95.log is: 30/Aug/1995 with 5.72259% of all 404 errors.
The last three days of the month occured in the top days for 404 errors in NASA_Aug95.log, which suggests that there may be an end of month pattern for 404 errors.
The percentage of 404 errors that occur in the last three days of the month in NASA_Aug95.log is: 15.2034%
While the last three days of the month accound for many 404 errors, the closest time unit is a week, so I also looked at the last week.
The percentage of 404 errors that occur in the last week in NASA_Aug95.log is: 30.8278%
In August 1995, there were 9978 404 errors.  On the surface, the most highly related variables are the request type and the date.
GET requests are the most common request type causing 404 errors, however, most requests are GET request and of GET requests, the majority do not result in 404 errors.
The most common dates for 404 errors tended to be at the end of the month with 30.8278% of errors in the last week and 15.2034% of errors in just the last three days, which suggests a potential end of month pattern for 404 errors.
However, the end of month pattern may be confounded with the high traffic at the end of the month.
overall, the most prominent relationship with 404 error quantity was the traffic during the time.
As the traffic increased, the number of 404 errors tended to increase.
End of basic analysis of NASA log files.
```

## Step 3 Output
```
Summary Statistics for NASA Log Analysis
NASA_Jul95.log Summary Statistics:
There were 1891714 requests in total.
The most active hosts were:
piweba3y.prodigy.com | ################################################## (17572)
piweba4y.prodigy.com | ################################ (11591)
piweba1y.prodigy.com | ############################ (9868)
The top three hosts appear to be from the same user under different account names, which accounted for 39031 requests, which is 2% of the total requests.
There were 5701 hosts that made only one request, which accounts for 0.30% of all requests.
The minimum number of requests per host was 1 requests for 5701 hosts.  The mean was 23.0745 requests.  The median was 10 requests.  The standard deviation was 127.746 requests.  The maximum was 17572 requests from piweba3y.prodigy.com.
Because the median is far less than the mean and the standard deviation is high, the requests distribution by user is highly right skewed, with a few hosts making many requests and many hosts making few requests.
The most active days were:
13/Jul/1995          | ################################################## (134203)
06/Jul/1995          | ##################################### (100960)
05/Jul/1995          | ################################### (94575)
The top three most active days accounted for 329738 requests, which is 17% of the total requests.
The least active days were:
28/Jul/1995          | ###################################### (27121)
22/Jul/1995          | ################################################# (35267)
09/Jul/1995          | ################################################## (35272)
The three least active days accounted for 97660 requests, which is 5% of the total requests.
The mean request day was 13.423, and the median was 13, indicating more requests at the beginning of the month rather than the end.
The result is consistent with the most and least active day lists.
The minimum number of requests per day was 27121 requests on 28/Jul/1995.  The mean was 67561.2 requests.  The median was 64671.5 requests.  The standard deviation was 22981.4 requests.   The maximum was 134203 requests on 13/Jul/1995.
The most active hours were:
14                   | ################################################## (122479)
12                   | ################################################# (122085)
15                   | ################################################# (121200)
The top three most active hours accounted for 365764 requests, which is 19% of the total requests.
The least active hours were:
05                   | ############################################# (31919)
04                   | ############################################# (32234)
06                   | ################################################## (35253)
The three least active hours accounted for 99406 requests, which is 5% of the total requests.
The mean hour of request was 12.6855, and the median was 13.
The minimum number of requests per hour was 31919 requests during hour 05.  The mean was 78821.4 requests.  The median was 71849 requests. The standard deviation was 30795.7 requests.  The maximum was 122479 requests during hour 14.
Most frequent HTTP methods:
"GET                 | ################################################## (1887646)
"HEAD                |  (3952)
"POST                |  (111)
"k                   |  (2)
"1/history/apollo/images/" |  (2)
The top request type accounted for 1887646 requests, which is 99% of the total requests.
The minimum number of requests per type was 1 request of type .  The mean was 270245 requests.  The median was 2 requests.  The standard deviation was 660303 requests.  The maximum was 1887646 requests for "GET type requests.
Because the median is far less than the mean and the standard deviation is high, the requests distribution by request type is highly right skewed, with a few request types making many requests but more types making few requests.
Most frequent URLs requested:
/images/NASA-logosmall.gif | ################################################## (111144)
/images/KSC-logosmall.gif | ######################################## (89530)
/images/MOSAIC-logosmall.gif | ########################### (60300)
The top 3 requested URLs are all images, and further investigating, part 3a from the basic analysis showed the top 7 URLs are all images.
The top image URL requests accounted for 479601 requests, which is 25% of the total requests.
There were 11418 URLs with only one request, which accounts for 0.60% of all requests.
The minimum number of requests per URL was 1 request for 11418 URLs.  The mean was 87.3005 requests.  The median was 1 request.  The standard deviation was 1536.91 requests.  The maximum was 111144 requests for the URL /images/NASA-logosmall.gif.
Because the median is far less than the mean and the standard deviation is high, the requests distribution by URL is highly right skewed, with a few requests for many URLs and many requests for few URLs.
Most frequent response codes:
200                  | ################################################## (1697914)
304                  | ### (132626)
302                  | # (46549)
The top response code requests accounted for 1888846 requests, which is 99% of the total requests.
There were 273 response codes returned to only one request, which accounts for 0.01% of all requests.
The minimum number of requests for a response code was 1 request for 273 response codes.  The mean was 3516.2 requests.  The median was 1 requests.  The standard deviation was 73369.9 requests.  The maximum was 1697914 requests with a 200 response code.
Because the median is far less than the mean and the standard deviation is high, the requests distribution by response code is highly right skewed, with many response codes returned only for one request and few response codes returned to many requests.
The largest responses in bytes were:
"GET                 | ################################################## (6823936)
"GET                 | ####################### (3155499)
"GET                 | ####################### (3155499)
There were 159343 requests with a response size of 0 bytes, which accounts for 8% of requests.
The minimum response size for a request was 0 bytes for 159343 requests.  The mean size was 20455.5 bytes.  The median was 3635 bytes.  The standard deviation was 76957.4 bytes.  The maximum was 6823936 bytes from the request "GET /shuttle/countdown/video/livevideo.jpeg.
Because the median is far less than the mean and the standard deviation is high, the response size distribution by request is highly right skewed, with many requests with small response sizes and few with large response sizes.
NASA_Aug95.log Summary Statistics:
There were 1569898 requests in total.
The most active hosts were:
edams.ksc.nasa.gov   | ################################################## (6530)
piweba4y.prodigy.com | ##################################### (4846)
163.206.89.4         | #################################### (4791)
The top three hosts accounted for 16167 requests, which is 1% of the total requests.
There were 5382 hosts that made only one request, which accounts for 0.34% of all requests.
The minimum number of requests per host was 1 request for 5382 hosts.  The mean was 20.9152 requests.  The median was 9 requests.  The standard deviation was 86.9087 requests.  The maximum was 6530 requests from edams.ksc.nasa.gov.
Because the median is noticeably less than the mean and the standard deviation is high, the requests distribution by user is highly right skewed, with a few hosts making many requests and many hosts making few requests.
The most active days were:
31/Aug/1995          | ################################################## (90125)
30/Aug/1995          | ############################################ (80641)
29/Aug/1995          | ##################################### (67988)
The top three most active days are also the last three days of the month and accounted for 238754 requests, which is 15% of the total requests.
The least active days were:
26/Aug/1995          | ################################################# (31608)
05/Aug/1995          | ################################################# (31893)
19/Aug/1995          | ################################################## (32094)
The three least active days accounted for 95595 requests, which is 6% of the total requests.
The mean request day was 17.3391, and the median was 17, indicating more requests at the end of the month rather than the beginning.
The result is consistent with the most active day list.
The minimum number of requests per day was 31608 requests on 26/Aug/1995.  The mean was 52329.9 requests.  The median was 56987 requests.  The standard deviation was 14655.9 requests.   The maximum was 90125 requests on 31/Aug/1995.
The most active hours were:
15                   | ################################################## (109465)
12                   | ################################################ (105143)
13                   | ############################################### (104536)
The top three most active hours accounted for 319144 requests, which is 20% of the total requests.
The least active hours were:
04                   | ############################################ (26756)
05                   | ############################################# (27587)
03                   | ################################################## (29995)
The three least active hours unsurprisingly occurred when people usually sleep and accounted for 84338 requests, which is 5% of the total requests.
The mean hour of request was 12.8075, and the median was 13.
The minimum number of requests per hour was 26756 requests during hour 04.  The mean was 65412.4 requests.  The median was 60308.5 requests. The standard deviation was 26917.5 requests.  The maximum was 109465 requests during hour 15.
Most frequent HTTP methods:
"GET                 | ################################################## (1565812)
"HEAD                |  (3965)
"POST                |  (111)
"                   |  (4)
"                    |  (2)
The top request type accounted for 1565812 requests, which is 99% of the total requests.
The minimum number of requests per type was 1 request of type "?".  The mean was 196237 requests.  The median was 3 requests.  The standard deviation was 517652 requests.  The maximum was 1565812 requests for "GET type requests.
Because the median is far less than the mean and the standard deviation is high, the requests distribution by request type is highly right skewed, with a few request types making many requests but more types making few requests.
Most frequent URLs requested:
/images/NASA-logosmall.gif | ################################################## (97293)
/images/KSC-logosmall.gif | ###################################### (75283)
/images/MOSAIC-logosmall.gif | ################################## (67356)
The top 3 requested URLs are all images, and further investigating, part 3b from the basic analysis showed the top 6 URLs are all images.
The top image URL requests accounted for 435928 requests, which is 27% of the total requests.
There were 7900 URLs with only one request, which accounts for 0.50% of all requests.
The minimum number of requests per URL was 1 request for 7900 URLs.  The mean was 99.9935 requests.  The median was 1 request.  The standard deviation was 1689.74 requests.  The maximum was 97293 requests for the URL /images/NASA-logosmall.gif.
Because the median is far less than the mean and the standard deviation is high, the requests distribution by URL is highly right skewed, with a few requests for many URLs and many requests for few URLs.
Most frequent response codes:
200                  | ################################################## (1396473)
304                  | #### (134138)
302                  |  (26422)
The top response code requests accounted for 1567934 requests, which is 99% of the total requests.
There were 200 different response codes returned to only one request, which accounts for 0.01% of all requests.
The minimum number for requests for a response code was 1 request for 200 different response codes.  The mean was 4242.97 requests.  The median was 1 request.  The standard deviation was 72824.6 requests.  The maximum was 1396473 requests with a 200 response code.
Because the median is far less than the mean and the standard deviation is high, the requests distribution by response code is highly right skewed, with many response codes returned only for one request and few response codes returned to many requests.
The largest responses in bytes were:
3421948 "GET /statistics/1995/Jul/Jul95_reverse_domains.html
3155499 "GET /statistics/1995/bkup/Mar95_full.html
3155499 "GET /statistics/1995/bkup/Mar95_full.html
There were 154588 requests with a response size of 0 bytes, which accounts for 9% of requests.
The minimum response size for a request was 0 bytes for 154588 requests.  The mean size was 17089.2 bytes.  The median was 3164 bytes.  The standard deviation was 67954.7 bytes.  The maximum was 3421948 bytes from the request "GET /statistics/1995/Jul/Jul95_reverse_domains.html.
Because the median is far less than the mean and the standard deviation is high, the response size distribution by request is highly right skewed, with many requests with small response sizes and few with large response sizes.
July was more busy than August with 321816 more requests.
The most active hosts were more active in July with 22864 more requests and accounting for 1.0000 percentage point more of the month's total requests.
There were 319 more hosts that made only one request in July than in August; however, the percentage of requests from hosts who only made one request was 0.0400 percentage points higher in August.
The minimum number of requests per host was the same for both months, but the other metrics were higher in July matching the higher overall traffic in July.
The mean was 2.1593 requests higher, and the median was 1 requests higher in July than August.  However, the standard deviation was 40.8373 requests higher in July as well.  The maximum was also 11042.0000 requests higher in July than August.
The most active days were more active in July with 90984 more requests and accounting for 2.0000 percentage point more of the month's total requests.
The most active days differed with the most active days of July at the beginning of the month, and the most active August days at the end of the month.
The least active days were more active in July with 2065 more requests; however, the least active days in August accounted for higher proportion of the total requests by -1.0000 percentage points.
The mean day of request was -3.9161 days higher in August than in July, and the median was -4 days higher in August than in July, indicating more requests at the end of the month rather than the beginning in August compared to July.
The minimum requests per day was 4487 requests higher in August than in July, but the other metrics were higher in July matching the higher overall traffic in July.  The mean was 15231.3000 requests higher, and the median was 7684.5000 requests higher in July than August.  However, the standard deviation was 8325.5000 requests higher in July as well.  The maximum was also 44078 requests higher in July than August.
The most active hours in July were more active than the most active hours in August by 46620 requests; however, the most active hours in August accounted for 1.0000 percentage points more of the total month requests than the most active hours in July.
The least active hours in July were more active than the least active hours in August by 15068 requests, but the respective quiet hours requests accounted for the same percentage of the months' total requests.
The mean hour of request in July and August were similar, where July's metrics were 12.6855 and 13, and August's metrics were 12.8075 and 13.
Matching the overall traffic, the metrics were higher in July than August.  The minimum requests per hour was 5163 requests higher, the median 11540.5000 requests higher, the mean 13409.0000 requests higher, the standard deviation 3878.2000 requests higher, and the maximum 13014 requests higher in July than August.
The most requent request types were the same for both months and accounted for the same percentage of total requests per month, but the most frequent request types in July accounted for 321834 more requests than the most frequent request types in August.
The minimum number of requests per type was the same accross months, but the type was different.  Additionally, the response type distribution was the same with a heavy right skew.
The mean was 74008.0000 requests higher in July, but the median was -1 request higher in August than July.  The standard deviation was 142651.0000 requests higher in July and the maximum was also 321834 requests higher in July than August.
The most requested URLs were the same accross months and were all images.  The most requested images in August accounted for a higher percentage of the total month's reuqests than July by 2.0000 percentage points, but the most requested images in July accounted for 43673 more requests than the most requested images in August.
There were 3518 more URLs with only one request in July than in August accounting for 0.1000 percentage points higher of the total requests in July than in August.
The minimum number of requests per URL was the same for both months as well as the median and the right skew distribution shape.
On the other hand, August had a higher mean by 12.6930 requests and a higher standard deviation by 152.8300 requests, but the maximum was higher in July by 13851 requests than August.
The most frequent response codes were the same for both months and both accounted for 99 percentage of the total requests in their respective months.
There were 73.0000 more response codes returned to only one request in July than August, but the infrequent codes accounted for the same percentage of total requests 0.01%.
The minimum number of requests for a response code was the same for both months  as well as the median 1 requests and the right skew distribution shape.  However, the mean was higher in August by 726.7700 requests, the standard deviation was higher in July by 545.3000 requests, and the maximum was higher in July by 0 requests than August.
The largest response in bytes was larger in July than August by 3401988 bytes, but the second and third largest reponses were the same in both months.
There were 4755 more requests with a response size of 0 bytes in July than August, but the percentage of requests with no response was 1.0000 percentage points higher in August than in July.
The July size metrics were higher than August's where the mean was 3366.3000 bytes higher, the median was -471 bytes higher, the standard deviation was 9002.7000 bytes higher, and the maximum was 3401988 bytes higher in July than August.
```
