# Week 9: CI/CD, Testing & Full-Stack Architecture

## Overview

This week brings together everything you've learned into production-ready systems. You'll implement Continuous Integration and Continuous Deployment (CI/CD) with GitHub Actions, write tests, automate deployments, and design full-stack architectures using Mermaid diagrams. We'll also review all the tools covered throughout the course.

## Topics Covered

### CI/CD Fundamentals
- What is CI/CD and why it matters
- GitHub Actions architecture
- Workflow triggers and events
- Jobs, steps, and actions
- Secrets and environment variables
- Matrix builds and parallel execution
- Caching and optimization

### Automated Testing
- Unit tests for functions and classes
- Integration tests for APIs
- End-to-end tests for applications
- Testing AI agents and LLM interactions
- Mocking external services
- Test coverage and reporting
- Performance testing

### Deployment Automation
- Automated deployment to Cloud Run
- Deployment strategies (blue-green, canary)
- Rollback mechanisms
- Environment-specific configurations
- Database migrations
- Zero-downtime deployments

### Code Quality
- Linting with ruff/pylint
- Type checking with mypy
- Code formatting with black
- Security scanning
- Dependency vulnerability checks
- Documentation generation
- Pre-commit hooks

### Monitoring & Observability
- Application logging
- Error tracking (Sentry)
- Performance monitoring
- Uptime monitoring
- Cost tracking
- Alerting and notifications
- Dashboards and metrics

### Full-Stack Architecture
- Microservices vs monoliths
- API gateway patterns
- Database design for scale
- Caching strategies
- Load balancing
- Security architecture
- Disaster recovery

## Why This Matters

Professional data science requires more than good models:
- **Reliability**: Systems must work consistently
- **Maintainability**: Code must be easy to update
- **Scalability**: Systems must handle growth
- **Security**: Data and systems must be protected
- **Observability**: You must know what's happening

CI/CD enables:
- **Fast iteration**: Deploy changes quickly and safely
- **Quality assurance**: Catch bugs before production
- **Confidence**: Know your code works
- **Collaboration**: Multiple developers can work together
- **Documentation**: Automated processes are self-documenting

For your career:
- CI/CD skills are expected in industry
- Testing demonstrates professionalism
- Architecture knowledge shows maturity
- DevOps skills make you more valuable
- Production experience sets you apart

## Examples

### 1. Basic CI/CD Pipeline (`examples/basic-cicd/`)
- GitHub Actions workflow
- Automated testing on push
- Linting and formatting checks
- Building container images with Podman
- Deploying to Cloud Run

### 2. Full-Stack Application (`examples/fullstack-app/`)
- Streamlit frontend
- FastAPI backend
- PostgreSQL database
- Redis caching
- Complete CI/CD pipeline
- Mermaid architecture diagrams

## GitHub Actions Basics

### Workflow Structure
```yaml
name: CI/CD Pipeline

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      - name: Install dependencies
        run: |
          pip install -r requirements.txt
      - name: Run tests
        run: pytest
```

### Common Triggers
- `push`: On code push
- `pull_request`: On PR creation/update
- `schedule`: Cron-based scheduling
- `workflow_dispatch`: Manual trigger
- `release`: On release creation

### Useful Actions
- `actions/checkout`: Clone repository
- `actions/setup-python`: Set up Python
- `docker/build-push-action`: Build/push Docker images
- `google-github-actions/auth`: Authenticate with GCP
- `google-github-actions/deploy-cloudrun`: Deploy to Cloud Run

## Testing Strategies

### Unit Tests
Test individual functions and classes:
```python
def test_preprocess_data():
    input_data = {"value": "  test  "}
    result = preprocess(input_data)
    assert result["value"] == "test"
```

### Integration Tests
Test API endpoints:
```python
def test_prediction_endpoint():
    response = client.post("/predict", json={"features": [1, 2, 3]})
    assert response.status_code == 200
    assert "prediction" in response.json()
```

### End-to-End Tests
Test complete workflows:
```python
def test_complete_workflow():
    # Upload data
    # Train model
    # Make prediction
    # Verify result
```

### Testing AI Agents
```python
def test_agent_tool_calling():
    agent = create_agent()
    result = agent.run("What is 2+2?")
    assert "4" in result
    assert agent.tool_calls > 0
```

### Mocking External Services
```python
@patch('requests.get')
def test_api_call(mock_get):
    mock_get.return_value.json.return_value = {"data": "test"}
    result = fetch_data()
    assert result == {"data": "test"}
```

## Deployment Strategies

### Blue-Green Deployment
- Deploy new version alongside old
- Switch traffic when ready
- Easy rollback if issues
- Zero downtime

### Canary Deployment
- Deploy to small percentage of users
- Monitor for issues
- Gradually increase traffic
- Rollback if problems detected

### Rolling Deployment
- Update instances one at a time
- Always have some instances running
- Slower but safer
- Good for stateful applications

## Architecture Patterns

### Microservices Architecture
```
User -> Load Balancer -> API Gateway
                            |
                            +-> Auth Service
                            +-> Model Service
                            +-> Data Service
                            +-> Agent Service
```

Benefits:
- Independent scaling
- Technology flexibility
- Fault isolation
- Team autonomy

Challenges:
- Complexity
- Network overhead
- Data consistency
- Debugging

### Monolithic Architecture
```
User -> Application (all services in one)
```

Benefits:
- Simpler to develop
- Easier to test
- Lower latency
- Simpler deployment

Challenges:
- Harder to scale
- Technology lock-in
- Deployment risk
- Team coordination

### Hybrid Approach (Recommended for Final Projects)
```
User -> Streamlit App (monolith)
            |
            +-> Model API (microservice)
            +-> Agent System (microservice)
```

Balance simplicity and flexibility.

## Best Practices

### CI/CD
1. Run tests on every commit
2. Keep pipelines fast (<10 minutes)
3. Fail fast on errors
4. Use caching effectively
5. Separate build and deploy
6. Use environment-specific configs
7. Implement proper secrets management

### Testing
1. Write tests before fixing bugs
2. Aim for >80% code coverage
3. Test edge cases and errors
4. Use fixtures for common setups
5. Keep tests fast and isolated
6. Mock external dependencies
7. Test in production-like environments

### Deployment
1. Always deploy to staging first
2. Implement health checks
3. Use feature flags for risky changes
4. Monitor deployments closely
5. Have rollback procedures ready
6. Document deployment process
7. Automate everything possible

### Code Quality
1. Use consistent formatting (black)
2. Enforce linting (ruff)
3. Type hint everything (mypy)
4. Document public APIs
5. Review all code changes
6. Keep functions small and focused
7. Follow SOLID principles

### Monitoring
1. Log all important events
2. Set up error alerting
3. Monitor key metrics
4. Track costs
5. Implement health checks
6. Use structured logging
7. Create dashboards

## Common Pitfalls

1. **No tests**: Can't refactor or deploy confidently
2. **Slow CI/CD**: Developers avoid running it
3. **Hardcoded secrets**: Security vulnerability
4. **No monitoring**: Can't detect or debug issues
5. **Complex architecture**: Over-engineering for scale you don't need
6. **No rollback plan**: Stuck when deployments fail
7. **Ignoring warnings**: Small issues become big problems
8. **No documentation**: Can't maintain or onboard
9. **Manual deployments**: Error-prone and slow
10. **Testing in production**: Risky and unprofessional

## Tools & Services

### CI/CD
- **GitHub Actions**: Built into GitHub, easy to use
- **GitLab CI**: Alternative with similar features
- **CircleCI**: Powerful but more complex
- **Jenkins**: Self-hosted, very flexible

### Testing
- **pytest**: Python testing framework
- **pytest-cov**: Coverage reporting
- **pytest-asyncio**: Async test support
- **httpx**: Testing HTTP clients
- **faker**: Generate test data

### Code Quality
- **ruff**: Fast Python linter
- **black**: Code formatter
- **mypy**: Type checker
- **pre-commit**: Git hooks
- **bandit**: Security linter

### Monitoring
- **Sentry**: Error tracking
- **Datadog**: Full observability platform
- **Prometheus**: Metrics collection
- **Grafana**: Dashboards
- **Google Cloud Monitoring**: GCP native

### Deployment
- **Google Cloud Run**: Serverless containers
- **Cloud Build**: Build automation
- **Terraform**: Infrastructure as code
- **Docker**: Containerization

## Resources

### Articles

[The Art of Giving and Receiving Code Reviews (Gracefully)](https://www.alexandra-hill.com/2018/06/25/the-art-of-giving-and-receiving-code-reviews/) - Alex Hill

[Technical Debt for Data Scientists](https://www.gordonshot well.com/blog/technical-debt-data-science/) - Gordon Shotwell

[Hiring a Data Scientist: The Good, The Bad and The Ugly](https://www.forbes.com/sites/forbestechcouncil/2019/03/14/hiring-a-data-scientist-the-good-the-bad-and-the-ugly/) - Nisha Talagala, Forbes

### GitHub Actions
- [GitHub Actions Documentation](https://docs.github.com/en/actions)
- [GitHub Actions Marketplace](https://github.com/marketplace?type=actions)
- [Workflow Syntax](https://docs.github.com/en/actions/reference/workflow-syntax-for-github-actions)
- [GitHub Actions Examples](https://github.com/actions/starter-workflows)

### Testing
- [pytest Documentation](https://docs.pytest.org/)
- [Testing Best Practices](https://testdriven.io/blog/testing-best-practices/)
- [Python Testing Guide](https://realpython.com/python-testing/)

### DevOps
- [The Twelve-Factor App](https://12factor.net/)
- [Google SRE Book](https://sre.google/books/)
- [DevOps Handbook](https://itrevolution.com/product/the-devops-handbook/)

### Architecture
- [System Design Primer](https://github.com/donnemartin/system-design-primer)
- [Microservices Patterns](https://microservices.io/patterns/)
- [Cloud Architecture Center](https://cloud.google.com/architecture)
