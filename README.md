# Setup Instructions
## Prerequisites
- [Install uv](https://docs.astral.sh/uv/#installation)
- Generate an OpenAI token [here](https://platform.openai.com/account/api-keys)
## Setup
- Add your token to `.env`
```OPENAI_API_KEY=your-key-here```
- Install the environment by running
```uv sync --all-groups```

# Quickstart
Run the following script to start the server and start the streamlit frontend\
```./run.sh```

# Assumptions and Limitations
## Assumptions
### Key Features List
- Since we're only including short bullet points that describe the property, there is no need to use AI-generated content. A simple hardcoded logic should suffice. It would in fact be easier for end users to work with if they are for example preparing a spreadsheet of listings that they found.
### Call to Action
Similarly, the call to action can be hardcoded
### Adjectives and Characteristics
- Obviously we can't call a 40sqm apartment "spacious", and we can't describe a building built in the 1970s as "modern".
- The features provided in the JSON input should serve as input to an adjective or phrase generator.
- The generated adjectives/phrases can then be fed to the next step to generate a full description.
### Meta Description
- Simply a summary of the full description, with searchable keywords ensured.
## Limitations
### Neighborhood Summary
- Difficult to verify/validate. We have to rely on ChatGPT here and hope it's accurate for the moment.
### Language Support
- I don't speak Portuguese, so I will pass each section to an LLM for translation. I have no reliable way of verifying the output.
