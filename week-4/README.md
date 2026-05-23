# Week 4: Data Acquisition - APIs & Web Scraping

## Week Overview

This week covers acquiring data from the web using APIs and web scraping. You'll learn to work with REST APIs, handle authentication, scrape websites ethically, and build robust data collection pipelines. These are essential skills for modern data science where most data isn't available in convenient CSV files.

## Resources

### Slides

[slides-week-4](slides-week-4.pdf)

### Key Topics

#### APIs
- REST API fundamentals
- HTTP methods and status codes
- Authentication (API keys, OAuth)
- Rate limiting and retry logic
- Error handling
- Working with JSON responses

#### Web Scraping
- HTML structure and parsing
- Beautiful Soup and CSS selectors
- Handling pagination
- Dynamic content with Selenium
- Rate limiting and politeness
- robots.txt and ethical scraping

#### AI-Assisted Development
- Using AI to write scraping scripts
- Debugging with AI assistance
- Effective prompting for data acquisition
- Validating AI-generated code

## Examples

- [API Basics](examples/api-basics/) - Working with REST APIs, authentication, and error handling
- [Web Scraping Basics](examples/web-scraping-basics/) - HTML parsing, CSS selectors, and ethical scraping

## Homework Assignment 2

**Due**: One week from today (before Week 5 class)

See [assignment-2/](assignment-2/) for details.

Build a data collection pipeline that combines API integration (TMDB) and web scraping (IMDb) to gather and analyze movie data. This assignment challenges you to handle real-world data acquisition, combining multiple sources, and performing meaningful analysis.

## Ethical Considerations

### Always Remember
- Check `robots.txt` before scraping
- Implement rate limiting (minimum 1-2 seconds between requests)
- Use descriptive User-Agent headers
- Respect Terms of Service
- Don't overload servers
- Handle errors gracefully
- Document your data sources

### Legal and Ethical Guidelines
- Prefer APIs when available
- Scrape only public data
- Don't scrape personal information
- Respect copyright
- Don't use scraped data commercially without permission
- Be transparent about your data collection

## Free APIs for Practice

- **GitHub API**: https://api.github.com (no key needed for basic use)
- **The Movie Database (TMDB)**: https://www.themoviedb.org/settings/api
- **OpenWeatherMap**: https://openweathermap.org/api (free tier)
- **NASA APIs**: https://api.nasa.gov (free with API key)
- **REST Countries**: https://restcountries.com/v3.1/all
- **JSONPlaceholder**: https://jsonplaceholder.typicode.com (test API)
- **Public APIs List**: https://github.com/public-apis/public-apis

## Recommended Libraries

### API Work
- `requests` - HTTP library for Python
- `httpx` - Modern async HTTP client
- `python-dotenv` - Environment variable management
- `requests-cache` - Response caching

### Web Scraping
- `beautifulsoup4` - HTML/XML parsing
- `lxml` - Fast parser for Beautiful Soup
- `selenium` - Browser automation for dynamic content
- `scrapy` - Full-featured scraping framework
- `playwright` - Modern browser automation

### Data Processing
- `pandas` - Data manipulation and analysis
- `json` - JSON handling (built-in)
- `csv` - CSV handling (built-in)

## Additional Resources

### Articles
- [The Follower Factory - NY Times Interactive](https://www.nytimes.com/interactive/2018/01/27/technology/social-media-bots.html) - Investigation into social media bots and fake followers
- [AI Copyright Case Tracker - Wired](https://www.wired.com/story/ai-copyright-case-tracker/) - Tracking legal cases involving AI and copyright

### Documentation
- [Requests Documentation](https://docs.python-requests.org/)
- [Beautiful Soup Documentation](https://www.crummy.com/software/BeautifulSoup/)
- [Selenium Documentation](https://selenium-python.readthedocs.io/)
- [HTTP Status Codes](https://httpstatuses.com/)

### Tutorials
- [Real Python Web Scraping](https://realpython.com/beautiful-soup-web-scraper-python/)
- [API Integration Tutorial](https://realpython.com/api-integration-in-python/)
- [Web Scraping Best Practices](https://www.scrapehero.com/web-scraping-best-practices/)

### Tools
- [Postman](https://www.postman.com/) - API testing
- [HTTPie](https://httpie.io/) - Command-line HTTP client
- [Browser DevTools](https://developer.chrome.com/docs/devtools/) - Inspect network requests
- [Explain Shell](https://explainshell.com/) - Understand shell commands

## Common Challenges

### API Issues
- **Rate limiting**: Implement delays and respect limits
- **Authentication errors**: Check API key and permissions
- **Timeout errors**: Increase timeout or check connection
- **JSON parsing errors**: Validate response structure

### Scraping Issues
- **Missing elements**: Check if element exists before accessing
- **Dynamic content**: Use Selenium or find the underlying API
- **Blocked requests**: Add User-Agent, respect robots.txt
- **Inconsistent HTML**: Add validation and error handling


