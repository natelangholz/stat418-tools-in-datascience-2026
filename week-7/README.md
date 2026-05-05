# Week 7: Building APIs & MCP Servers

## Overview

This week focuses on building production-ready APIs for data science applications. You'll learn to create RESTful APIs with FastAPI, implement Model Context Protocol (MCP) servers for AI tool integration, and apply advanced containerization patterns for deployment. This bridges the gap between your models and the applications that use them.

## Topics Covered

### FastAPI Fundamentals
- Why FastAPI for data science APIs
- Request/response models with Pydantic
- Path parameters and query parameters
- Request body validation
- Automatic API documentation (Swagger/OpenAPI)
- Async endpoints for performance

### Model Serving APIs
- Loading and serving ML models
- Prediction endpoints
- Batch prediction support
- Model versioning strategies
- Caching predictions
- Handling model updates

### MCP (Model Context Protocol) Servers
- What is MCP and why it matters
- MCP server architecture
- Creating custom tools for AI agents
- Tool schemas and validation
- Integrating with Claude and other AI assistants
- Testing MCP servers locally

### Advanced Containerization
- Multi-stage Docker builds for smaller images
- Optimizing layer caching
- Security best practices (non-root users, minimal base images)
- Health checks and readiness probes
- Environment-specific configurations
- Container resource limits
- Production vs development containers

### API Best Practices
- Authentication and authorization (API keys, JWT)
- Rate limiting and throttling
- CORS configuration
- Error handling and status codes
- Input validation and sanitization
- Logging and monitoring
- API versioning strategies

### Deployment Patterns
- Deploying to Google Cloud Run
- Environment variables and secrets management
- Custom domains and SSL
- Scaling and auto-scaling
- Monitoring and alerting
- Cost optimization

## Why This Matters

APIs are how your data science work becomes accessible to applications:
- **Streamlit apps** call your API for predictions
- **Mobile apps** integrate your models
- **Other services** consume your data
- **AI agents** use your tools via MCP

Building good APIs is essential for:
- Separating concerns (model logic vs application logic)
- Enabling multiple clients (web, mobile, other services)
- Versioning and updating models independently
- Scaling model serving separately from applications
- Professional data science deployment

MCP servers are the future of AI tool integration:
- Standardized protocol for AI tools
- Works with Claude, ChatGPT, and other AI assistants
- Enables AI agents to use your custom tools
- Creates reusable, composable AI capabilities

## Examples

### 1. FastAPI Basics (`examples/fastapi-basics/`)
- Simple API with multiple endpoints
- Request/response models
- Query parameters and path parameters
- Automatic documentation
- Error handling

### 2. Model Serving API (`examples/model-serving-api/`)
- Loading a trained model
- Prediction endpoint
- Batch predictions
- Model metadata endpoint
- Health check endpoint
- Complete with tests

### 3. MCP Server (`examples/mcp-server/`)
- Creating a custom MCP server
- Defining tools with schemas
- Implementing tool logic
- Testing with Claude Desktop
- Deployment considerations

### 4. Production API (`examples/production-api/`)
- Authentication with API keys
- Rate limiting
- CORS configuration
- Logging and monitoring
- Multi-stage Dockerfile
- Cloud Run deployment

## Key Concepts

### FastAPI vs Flask
- **FastAPI**: Modern, async, automatic validation, built-in docs
- **Flask**: Mature, simple, more manual, larger ecosystem
- **For data science**: FastAPI is generally better (performance, validation, docs)

### Synchronous vs Asynchronous
- **Sync**: Simple, blocks during I/O, fine for CPU-bound tasks
- **Async**: Complex, non-blocking, better for I/O-bound tasks
- **For ML inference**: Usually sync is fine unless calling external services

### API Design Principles
1. **RESTful**: Use HTTP methods correctly (GET, POST, PUT, DELETE)
2. **Versioned**: Plan for API changes (/v1/, /v2/)
3. **Documented**: Auto-generated docs are your friend
4. **Validated**: Reject bad input early
5. **Secure**: Authenticate, authorize, sanitize
6. **Monitored**: Log everything, track metrics

### MCP Architecture
```
AI Assistant (Claude) <-> MCP Client <-> MCP Server <-> Your Tools
```
- **MCP Server**: Exposes tools via standardized protocol
- **Tools**: Functions that AI can call (search, calculate, query DB, etc.)
- **Schemas**: Define tool parameters and return types
- **Integration**: Works with any MCP-compatible AI assistant

## Advanced Containerization Topics

### Multi-Stage Builds
```dockerfile
# Build stage
FROM python:3.11-slim as builder
WORKDIR /app

# Install uv
RUN pip install --no-cache-dir uv

COPY requirements.txt .
RUN uv pip install --system -r requirements.txt

# Runtime stage
FROM python:3.11-slim
COPY --from=builder /usr/local /usr/local
COPY . /app
WORKDIR /app
CMD ["uvicorn", "main:app", "--host", "0.0.0.0"]
```
Benefits: Smaller images, faster deployments, better security

### Security Hardening
- Use minimal base images (alpine, slim)
- Run as non-root user
- Scan for vulnerabilities
- Don't include secrets in images
- Use .dockerignore

### Production Optimizations
- Layer caching strategies
- Health check endpoints
- Graceful shutdown handling
- Resource limits (CPU, memory)
- Logging to stdout/stderr

## Tools & Libraries

### API Development
- **FastAPI**: Modern Python web framework
- **Pydantic**: Data validation using Python type hints
- **Uvicorn**: ASGI server for FastAPI
- **python-multipart**: For file uploads
- **python-jose**: For JWT tokens

### MCP Development
- **mcp**: Official MCP Python SDK
- **anthropic**: For testing with Claude
- **pydantic**: For tool schemas

### Testing
- **pytest**: Testing framework
- **httpx**: Async HTTP client for testing
- **pytest-asyncio**: Async test support

### Deployment
- **Docker/Podman**: Containerization
- **Google Cloud Run**: Serverless container platform
- **gcloud CLI**: Google Cloud command-line tools

## Best Practices

### API Design
1. Use clear, consistent naming
2. Version your API from the start
3. Provide comprehensive error messages
4. Document all endpoints
5. Use appropriate HTTP status codes
6. Implement pagination for large results
7. Support filtering and sorting

### Security
1. Never commit secrets to git
2. Use environment variables for configuration
3. Implement authentication
4. Validate all inputs
5. Use HTTPS in production
6. Implement rate limiting
7. Log security events

### Performance
1. Use async for I/O-bound operations
2. Cache expensive computations
3. Implement connection pooling
4. Use background tasks for long operations
5. Monitor response times
6. Profile and optimize bottlenecks

### Containerization
1. Use multi-stage builds
2. Minimize layer count
3. Order layers by change frequency
4. Use .dockerignore
5. Don't run as root
6. Include health checks
7. Set resource limits

## Common Pitfalls

1. **Not validating inputs**: Use Pydantic models for all inputs
2. **Blocking async endpoints**: Don't use blocking I/O in async functions
3. **Ignoring errors**: Handle and log all errors properly
4. **Hardcoding configuration**: Use environment variables
5. **No authentication**: Even internal APIs need auth
6. **Large Docker images**: Use multi-stage builds
7. **Not testing**: Write tests for all endpoints
8. **Forgetting CORS**: Configure CORS for web clients
9. **No monitoring**: Implement logging and metrics
10. **Poor error messages**: Return helpful error information

## Resources

### Articles

[Using Docker to Deploy an R Plumber API](https://medium.com/tmobile-tech/using-docker-to-deploy-an-r-plumber-api-863ccf91516d) - T-Mobile Tech, real-world example of deploying ML models with Docker
  - [GitHub Repository](https://github.com/tmobile/r-tensorflow-api) - Complete working example

[Technical Debt for Data Scientists](https://www.gordonshot well.com/blog/technical-debt-data-science/) - Gordon Shotwell

[Hiring a Data Scientist: The Good, The Bad and The Ugly](https://www.forbes.com/sites/forbestechcouncil/2019/03/14/hiring-a-data-scientist-the-good-the-bad-and-the-ugly/) - Nisha Talagala, Forbes

### FastAPI
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [FastAPI Tutorial](https://fastapi.tiangolo.com/tutorial/)
- [Pydantic Documentation](https://docs.pydantic.dev/)
- [Uvicorn Documentation](https://www.uvicorn.org/)

### MCP
- [MCP Specification](https://modelcontextprotocol.io/)
- [MCP Python SDK](https://github.com/anthropics/mcp-python)
- [Claude MCP Integration](https://docs.anthropic.com/claude/docs/mcp)

### Containerization
- [Docker Best Practices](https://docs.docker.com/develop/dev-best-practices/)
- [Multi-stage Builds](https://docs.docker.com/build/building/multi-stage/)
- [Dockerfile Reference](https://docs.docker.com/engine/reference/builder/)

### Deployment
- [Google Cloud Run Docs](https://cloud.google.com/run/docs)
- [Cloud Run Quickstart](https://cloud.google.com/run/docs/quickstarts)
- [Container Best Practices](https://cloud.google.com/architecture/best-practices-for-building-containers)

### API Design
- [REST API Tutorial](https://restfulapi.net/)
- [HTTP Status Codes](https://httpstatuses.com/)
- [API Security Best Practices](https://owasp.org/www-project-api-security/)

## Assignment 3

**Due**: Before Week 9 class

See [assignment-3/](assignment-3/) for details.

Build a complete, production-ready API that serves a machine learning model. You'll create a FastAPI application, containerize it with Podman, deploy it to Google Cloud Run, and implement production best practices.

---

*"The best API is the one that's so simple and obvious that it doesn't need documentation. But document it anyway."*
