# Week 6: Final Project Proposals & Interactive Applications

## Overview

Week 6 is a pivotal week in the course where we transition from learning tools to applying them in your final projects. The class is structured in two parts:

1. **First Half**: Final project proposal presentations (students present)
2. **Second Half**: Lecture on building interactive applications with Streamlit and cloud deployment

This week bridges the gap between data science work and user-facing applications. You'll learn how to take your models and analyses and make them accessible to non-technical users through web applications.

## Slides

- [Week 6 Slides (PDF)](slides-week-6.pdf)

## Class Structure

### Part 1: Proposal Presentations (First ~90 minutes)

Students will present their final project proposals. Each presentation is **5-7 minutes** with a maximum of **6 slides**:
- 1 title slide
- 5 content slides covering:
  - Project overview and motivation
  - Data collection approach and progress
  - Exploratory data analysis
  - Proposed modeling approach
  - Application design and architecture
  - Timeline and milestones

See [proposal-presentation/README.md](proposal-presentation/README.md) for detailed guidelines.

### Part 2: Lecture on Interactive Applications (Remaining time)

After presentations, we'll dive into building interactive web applications with Streamlit and deploying them to the cloud. This is essential for your final projects - you'll need to deploy both an app and an API.

## Learning Objectives

By the end of this week, you will be able to:

1. **Build Interactive Applications**
   - Create web apps with Streamlit
   - Design intuitive user interfaces
   - Handle user inputs and display outputs
   - Integrate visualizations and data displays

2. **Deploy to the Cloud**
   - Deploy Streamlit apps to Streamlit Cloud
   - Deploy applications to Google Cloud Run
   - Understand deployment configurations
   - Manage environment variables and secrets

3. **Connect Apps to APIs**
   - Make API calls from Streamlit apps
   - Handle API responses and errors
   - Display API results to users
   - Implement loading states and error handling

4. **Design User Experiences**
   - Create intuitive layouts
   - Implement interactive widgets
   - Provide feedback to users
   - Handle edge cases gracefully

## Topics Covered

### Streamlit Fundamentals
- What is Streamlit and why use it?
- Basic Streamlit components (text, data, charts)
- Layout and containers
- User input widgets
- Session state management
- Caching for performance

### Building Interactive Apps
- Designing user interfaces
- Handling user inputs
- Displaying results dynamically
- Creating multi-page apps
- Implementing forms
- File uploads and downloads

### Cloud Deployment
- Streamlit Cloud deployment
- Google Cloud Run deployment
- Environment configuration
- Managing secrets
- Custom domains
- Monitoring and logs

### Integration Patterns
- Connecting to APIs
- Database integration
- Authentication and authorization
- Error handling and validation
- Performance optimization
- Production best practices

## Why This Matters

Most data science work ends up in one of two places:
1. **Reports/Notebooks**: Static analysis for stakeholders
2. **Applications**: Interactive tools for end users

Applications are more powerful because they:
- Let users explore data themselves
- Make models accessible to non-technical users
- Enable real-time predictions and insights
- Scale to many users
- Provide immediate value

Streamlit makes building these applications remarkably simple. What used to require full-stack development skills can now be done by data scientists with Python knowledge. This democratizes application development and lets you focus on the data science rather than web development.

## Streamlit vs Other Frameworks

**Streamlit**:
- Pros: Pure Python, very simple, fast development, great for data apps
- Cons: Less flexible than full frameworks, limited customization
- Best for: Data dashboards, ML demos, internal tools

**Shiny (R/Python)**:
- Pros: Reactive programming, mature ecosystem, good for R users
- Cons: Steeper learning curve, more verbose
- Best for: Complex reactive apps, R-based workflows

**Flask/FastAPI + React**:
- Pros: Maximum flexibility, production-grade, full control
- Cons: Requires frontend skills, much more code, slower development
- Best for: Production apps, complex UIs, when you need full control

For most data science applications, Streamlit hits the sweet spot of simplicity and capability.

## Cloud Deployment Options

### Streamlit Cloud (Recommended for Streamlit apps)
- **Pros**: Free tier, automatic deployment from GitHub, zero configuration
- **Cons**: Limited resources, Streamlit-specific
- **Best for**: Streamlit apps, quick demos, prototypes

### Google Cloud Run (Recommended for production)
- **Pros**: Scales to zero, pay per use, supports any containerized app
- **Cons**: Requires container knowledge (using Podman in this course), more setup
- **Best for**: Production apps, APIs, any framework

### Other Options
- **Heroku**: Simple but expensive, being phased out
- **AWS Lambda**: Serverless, complex setup
- **DigitalOcean**: Simple VMs, requires more management
- **Vercel/Netlify**: Great for static sites, limited for Python apps

For your final projects, you'll use:
- **Streamlit Cloud** or **Google Cloud Run** for your web app
- **Google Cloud Run** for your model API

## Examples

This week includes practical examples:

1. **[streamlit-basics](examples/streamlit-basics/)**: Core Streamlit concepts and components
2. **[interactive-dashboard](examples/interactive-dashboard/)**: Building a complete dashboard
3. **[ml-app-deployment](examples/ml-app-deployment/)**: Deploying a machine learning app
4. **[api-integration](examples/api-integration/)**: Connecting Streamlit to APIs

## Final Project Connection

This week is crucial for your final project. You need to:

1. **Present your proposal** - Show your progress and plans
2. **Learn Streamlit** - You'll build your app with this
3. **Learn deployment** - You'll deploy both app and API
4. **See integration patterns** - How to connect your app to your API

Your final project requires:
- A Streamlit (or Shiny) web application
- A separate model API (Flask/Plumber)
- Both deployed to the cloud
- Integration between them

Everything we cover today directly applies to your final project.

## Common Pitfalls

**Streamlit-specific**:
- Not understanding session state (leads to unexpected behavior)
- Forgetting to cache expensive operations (slow apps)
- Not handling errors gracefully (poor user experience)
- Overcomplicating the UI (keep it simple)

**Deployment**:
- Hardcoding secrets (security risk)
- Not testing locally first (deployment failures)
- Ignoring resource limits (apps crash)
- Not monitoring logs (can't debug issues)

**Integration**:
- Not handling API failures (app breaks)
- Blocking the UI during API calls (poor UX)
- Not validating user inputs (errors and security issues)
- Forgetting about CORS (API calls fail)

We'll address all of these in the examples and lecture.

## Resources

### Streamlit
- [Streamlit Documentation](https://docs.streamlit.io/)
- [Streamlit Gallery](https://streamlit.io/gallery) - Example apps
- [Streamlit Cheat Sheet](https://docs.streamlit.io/library/cheatsheet)
- [Streamlit Components](https://streamlit.io/components) - Community extensions

### Deployment
- [Streamlit Cloud Docs](https://docs.streamlit.io/streamlit-community-cloud)
- [Google Cloud Run Docs](https://cloud.google.com/run/docs)
- [Podman Documentation](https://podman.io/docs)

### Design
- [Streamlit Design Guidelines](https://docs.streamlit.io/library/advanced-features/app-design)
- [Data Visualization Best Practices](https://www.storytellingwithdata.com/)

