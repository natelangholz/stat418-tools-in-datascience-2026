# Final Project Proposal Presentations

## Overview

During the first half of Week 6 class, each student will present their final project proposal. This is your opportunity to share your progress, get feedback, and refine your approach before diving into the final implementation.

## Submission Deadline

**Slides due: May 5, 2026 at 11:59 AM**

Submit your slides via pull request to the `project-proposal` branch in this directory before class begins.

## Presentation Format

- **Duration**: 5-7 minutes per student
- **Maximum Slides**: 6 slides total
  - 1 title slide
  - 5 content slides
- **Format**: PDF or PowerPoint (.pdf or .pptx)
- **File naming**: `lastname-firstname-proposal.pdf` (e.g., `smith-john-proposal.pdf`)

## Required Content

Your 5 content slides should cover:

### Slide 1: Project Overview & Motivation
- **Project title and brief description**
- **Problem statement**: What problem are you solving?
- **Motivation**: Why is this interesting or important?
- **Target users**: Who will use your application?

**What to include**:
- Clear, concise problem statement
- Real-world relevance or impact
- Personal motivation for choosing this project

**Example**: "Predicting hiking trail difficulty to help hikers choose appropriate trails and avoid injuries. 30% of hiking injuries occur when hikers underestimate trail difficulty."

### Slide 2: Data Collection Approach & Progress
- **Data source(s)**: Where is your data coming from?
- **Collection method**: API, web scraping, or both?
- **Current progress**: How much data have you collected?
- **Data structure**: What does your dataset look like?

**What to include**:
- Specific APIs or websites you're scraping
- Code snippets or examples of your scraping approach
- Sample of collected data (table or screenshot)
- Any challenges encountered and how you solved them

**Example**: "Scraping AllTrails.com using BeautifulSoup. Collected 5,000 trails across California with features: elevation gain, distance, user ratings, reviews, photos."

### Slide 3: Exploratory Data Analysis
- **Key visualizations**: Show your data
- **Patterns discovered**: What insights have you found?
- **Data quality**: Any issues or preprocessing needed?
- **Feature engineering ideas**: What features will you create?

**What to include**:
- 2-3 compelling visualizations
- Statistical summaries
- Distribution of key variables
- Correlations or relationships discovered

**Example**: Include histograms of trail difficulty, scatter plots of elevation vs. distance, geographic distribution maps, etc.

### Slide 4: Proposed Modeling Approach
- **Model type(s)**: What algorithms will you use?
- **Features**: What inputs will your model use?
- **Target variable**: What are you predicting/classifying?
- **Evaluation metrics**: How will you measure success?
- **Baseline approach**: What's your starting point?

**What to include**:
- Specific model names (Random Forest, XGBoost, Neural Network, etc.)
- Justification for model choice
- Feature list or categories
- Success criteria (accuracy, RMSE, F1-score, etc.)

**Example**: "Multi-class classification (Easy/Moderate/Hard) using Random Forest and XGBoost. Features: elevation gain, distance, terrain type, season. Target: 80%+ accuracy."

### Slide 5: Timeline & Next Steps
- **Milestones**: Key dates and deliverables
- **Current status**: What's done, what's in progress
- **Remaining work**: What needs to be completed
- **Potential challenges**: What might go wrong?
- **Mitigation strategies**: How will you handle challenges?

**What to include**:
- Week-by-week timeline through Week 10
- Specific tasks for each milestone
- Risk assessment
- Backup plans

**Example Timeline**:
- Week 6: Complete data collection (5,000+ trails)
- Week 7: Finish EDA and feature engineering
- Week 8: Train and evaluate models
- Week 9: Build and deploy API
- Week 10: Build and deploy Streamlit app, final testing

## Presentation Tips

### Content
- **Be specific**: Avoid vague statements. Show actual data, code, or results.
- **Show progress**: Demonstrate what you've already accomplished.
- **Be realistic**: Don't overpromise. It's okay to have challenges.
- **Get feedback**: This is your chance to get input before final implementation.

### Delivery
- **Practice timing**: 5-7 minutes is short. Practice to stay within time.
- **Speak clearly**: Project your voice, make eye contact.
- **Show enthusiasm**: Your excitement is contagious.
- **Prepare for questions**: Anticipate what people might ask.

### Visuals
- **Use visuals**: Charts, diagrams, and screenshots are more engaging than text.
- **Keep text minimal**: Bullet points, not paragraphs.
- **Make it readable**: Large fonts, high contrast, clear labels.
- **Show, don't tell**: Actual data and mockups beat descriptions.

## Common Mistakes to Avoid

1. **Too much text**: Slides should support your talk, not be your script.
2. **No actual data**: Show real data you've collected, not hypotheticals.
3. **Vague plans**: "I'll use machine learning" isn't specific enough.
4. **No architecture**: Show how your components will connect.
5. **Unrealistic timeline**: Be honest about what's achievable.
6. **Going over time**: Practice and time yourself.
7. **Reading slides**: Talk to the audience, not the screen.

## Evaluation Criteria

Your proposal will be evaluated on:

- **Clarity**: Is your project well-defined and understandable?
- **Feasibility**: Can this be completed in the remaining time?
- **Progress**: Have you made meaningful progress on data collection?
- **Technical approach**: Is your modeling and architecture plan sound?
- **Presentation quality**: Are your slides clear and well-organized?
- **Delivery**: Did you communicate effectively within the time limit?

## Questions You Should Be Able to Answer

Be prepared to answer:
- How much data have you collected so far?
- What challenges have you encountered?
- Why did you choose this particular model/approach?
- How will users interact with your application?
- What's your backup plan if something doesn't work?
- How will you evaluate if your model is successful?
- What's the most interesting thing you've discovered in your data?

## After Your Presentation

- **Take notes**: Write down feedback and suggestions you receive.
- **Revise your plan**: Incorporate feedback into your project timeline.
- **Ask for help**: If you're stuck on something, ask classmates or instructor.
- **Keep working**: Don't wait until after presentations to continue progress.

## Example Projects from Past Years

Here are examples of successful final projects to inspire you:

**UCLA Clubs App** - Interactive app for discovering student organizations
- Data: Scraped UCLA student org websites
- Model: Recommendation system based on interests
- App: Searchable database with filters and recommendations

**Hike Finder** - Trail recommendation system
- Data: Scraped AllTrails.com
- Model: Difficulty classification and recommendation engine
- App: Map-based interface with trail details and predictions

**Crows From Around the World** - Bird species classifier
- Data: Scraped images and data from bird databases
- Model: Image classification CNN
- App: Upload photo, get species prediction and information

## Resources

- [Final Project Requirements](../../final-project/README.md)
- [Example Proposal Slides](./examples/) (if available)
- [Streamlit Gallery](https://streamlit.io/gallery) - For UI inspiration
- [Google Slides Templates](https://www.google.com/slides/about/) - Free presentation templates

## Submission Process

1. **Create your slides** (PDF or PowerPoint)
2. **Name your file**: `lastname-firstname-proposal.pdf`
3. **Fork the course repository** (if you haven't already)
4. **Add your slides** to `week-6/proposal-presentation/`
5. **Create a pull request to the `project-proposal` branch** with title: "Proposal: [Your Name]"
6. **Submit by deadline**: May 5, 2026 at 11:59 AM

## Presentation Day (May 6, 2026)

- **Arrive on time**: Presentations start promptly at 6:00 PM
- **Bring backup**: Have your slides on a USB drive and in the cloud
- **Be ready**: Presentation order will be randomized
- **Support classmates**: Be an engaged audience member
- **Take notes**: Learn from others' projects and approaches

## Questions?

If you have questions about the proposal presentation:
- Post in the Slack channel
- Email the instructor
- Ask during office hours
- Review the final project requirements

Good luck with your presentations! This is an exciting milestone in your final project journey.