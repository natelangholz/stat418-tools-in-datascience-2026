# Final Project: Create a Data/ML/AI Application

Please note there are 2 branches for final project submissions; 1 for slide submission and 1 for link to github repo submission. The final slides are due **June 1st 11:59 pm** and the deadline for everything else is **June 2nd end of day**. Grading of the github repositories start on the 3rd and functionality assessment of the APP and API will begin then as well.

## Project Description

The STAT 418 final project will be to create a useable application with connectivity to a deployed 'model' and doing a short demo. This requires taking a project from conception to completion including:
* Data collection through web scraping or APIs
* Building and training a model
* Interactive APP interface hosted on the cloud (Shiny for Python/R or Streamlit)
* Cloud hosted model API that your Shiny/Streamlit app will connect to
* Containerization with Docker
* **Solution Architecture Diagram**: A clear visual diagram showing how all components connect
* **AI Assistant Integration**: Document how you used AI assistants (like Cursor, GitHub Copilot, Claude, etc.) throughout your development process

Create a stand alone GitHub repo for your project that will show the progress of your work and stand as a stand-alone project (and repo) that you can show outside of class if necessary.

Data should be collected through a web scraping process whether it be through an API or scraping the HTML files themselves. You can pull it however you like but make a nice tabular dataset (if text or images have a reference to the image with other metadata info as other columns) from which you can build a model.

The modeling piece can be more sophisticated given the AI assistant tools available. Consider implementing:
* Multiple model comparisons with performance metrics
* Feature engineering and selection processes
* Hyperparameter tuning
* Model interpretability (SHAP values, feature importance, etc.)
* Cross-validation and robust evaluation strategies

Additionally, the 'model' itself should be something that you would like to show after this course concludes. Really this should be something that I or your classmates can interact with in some way whether it be dropdown menu to change values in App or adding new values to make predictions through an API. (see Deployment below) Do this through your GitHub repo so that someone else who comes across it can understand the process you have to complete your project. Create a README.md file explaining what the project is and then additional directories (also with explanation READMEs) that contain your code, presentations, and any additional files of interest.

### Enhanced Requirements (Leveraging AI Assistants)

Since you'll be using AI assistants throughout development, consider adding these components:

1. **Automated Testing**: Implement unit tests for your API endpoints and data processing functions
2. **CI/CD Pipeline**: Set up GitHub Actions for automated testing and deployment
3. **Data Validation**: Implement data quality checks and validation in your pipeline
4. **Logging & Monitoring**: Add proper logging to track API usage and errors
5. **Documentation**: Generate comprehensive API documentation (e.g., using Swagger/OpenAPI)
6. **Error Handling**: Robust error handling with informative error messages
7. **Performance Optimization**: Consider caching strategies or optimization techniques
8. **Security**: Implement API authentication or rate limiting if appropriate

### Solution Architecture Diagram

Your GitHub repository must include a solution architecture diagram that clearly shows:
* Data sources and collection methods
* Data storage/database (if applicable)
* Model training pipeline
* Model API service
* Web application interface
* Deployment infrastructure (Cloud Run, shinyapps.io, etc.)
* How components communicate with each other (API calls, data flow)

This diagram should be included in your main README and can be created using tools like draw.io, Lucidchart, Mermaid, or similar diagramming tools.

### AI Assistant Documentation

Create a dedicated section in your README documenting:
* Which AI assistants you used and for what tasks
* Examples of particularly helpful prompts or interactions
* Challenges where AI assistance was most valuable
* Areas where you had to significantly modify AI-generated code
* Lessons learned about working with AI coding assistants

### Proposal Presentation

Slide submissions for the proposal presentation will be available until **11:59 am May 5, 2026**. Create a pull request to the corresponding GitHub directory.

There is a proposal presentation component that will happen during week 6 for **5-7 minutes** each. There will be a maximum of **6 slides**: 1 title slide and then 5 with content. This should show:
* Your data collection approach and progress
* Exploratory data analysis with visualizations
* Proposed modeling approach(es)
* ~~Planned application features and user interface mockups~~
* ~~**Solution architecture diagram** (how components will connect)~~
* Timeline and milestones for completion

Order of presentations will be randomized.

To that end you will need to start collecting your data prior to week six. Create your project GitHub repo. Both week 3 and 4 will show different methods to collect data from websites. Adapt these methods to do so for your project. It may not be the case that you have completed your data collection at this point but be well on your way to doing so.

### Final Presentation

Slide submissions for the final presentation will be available until **11:59 pm June 1, 2026**. Create a pull request to the corresponding GitHub directory.

There is also a presentation component that will happen final class period for **10-12 minutes** each. Here there will be a maximum of **7 slides**: 1 title slide and then 6 with content. Your presentation should cover:
* Project overview and motivation
* Data collection and preprocessing approach
* Model development and evaluation (with metrics)
* **Final solution architecture diagram** showing deployed system
* Application features and user interface
* Live demonstration of your deployed app and API
* Challenges faced, how you overcame them, and lessons learned

Order of presentations will be randomized.

A final writeup with exploratory data analysis, methodology, and results should be present on your GitHub repo. This will be assessed; make your GitHub repo so that someone else who comes across it can understand the process you have to complete your project. Create a README.md file explaining what the project is and then additional directories (also with explanation READMEs) that contain your code, presentations, and any additional files of interest.

### Deployment

The final application should be deployed as a service online so that I and anyone of your classmates can visit or interact with it from their machines with a correct example or instructions. The App should be hosted on shinyapps.io or Google Cloud Run and the model API can be created through Plumber or Flask and hosted **separately** on Google Cloud Run. This should be available for interaction at least through week 10 until **June 9, 2026** for anyone to test (including me). With the amount of free resources on Google and on shinyapps.io it should be sufficient to run deployed for a week. Once that week has passed feel free to take it down. A working service will be part of the grade of this project.

### Examples

Here are a few nice examples of past GitHub repos from this course in past iterations.

[UCLA Clubs App](https://github.com/DavidLiu0619/ucla-clubs-app) - David Liu - Interactive app for discovering UCLA student organizations

[Hike Finder App](https://github.com/yesitsmary/hike-finder-app) - Mary - Deployed Shiny app for finding hiking trails ([Live App](https://yesitsmary.shinyapps.io/hike-finder-app/))

[Crows From Around the World](https://github.com/samanthawavell/Stats-418-Final-Project) - Samantha Wavell - Complete project with data collection, modeling, and deployment

## Submission Instructions

1. **Proposal Slides**: Submit via pull request to the `project-proposal` branch in `final-project/proposal-slides/` by May 5, 2026 11:59 AM
2. **Final Slides**: Submit via pull request to `final-project/final-slides/` by June 1, 2026 11:59 PM
3. **GitHub Repository Link**: Submit via pull request with your project repository URL by June 2, 2026 end of day
4. **Deployed Services**: Ensure both app and API are live and accessible by June 2, 2026

## Required Deliverables

Your GitHub repository must include:
- [ ] README.md with project overview and setup instructions
- [ ] Solution architecture diagram
- [ ] Data collection scripts/notebooks
- [ ] Data preprocessing and EDA notebooks
- [ ] Model training and evaluation code
- [ ] API implementation (Flask/Plumber)
- [ ] Web application code (Shiny/Streamlit)
- [ ] Dockerfile(s) for containerization
- [ ] Documentation of AI assistant usage
- [ ] Links to deployed services
