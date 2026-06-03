# LLM Basics Example

This example demonstrates fundamental concepts for working with Large Language Models through APIs.

## What You'll Learn

- Making API calls to different LLM providers
- Prompt engineering techniques
- Streaming responses for better UX
- Error handling and retries
- Cost tracking and optimization

## Files

- `simple_llm.py` - Basic LLM API calls
- `prompt_engineering.py` - Effective prompting techniques
- `streaming_example.py` - Streaming responses
- `cost_tracking.py` - Monitor API usage and costs
- `requirements.txt` - Python dependencies

## Setup

```bash
# Create virtual environment
uv venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
uv pip install -r requirements.txt

# Set up API keys (create .env file)
cp .env.example .env
# Edit .env and add your API keys
```

## API Keys

You'll need:
- Google AI API key from https://aistudio.google.com/

## Running the Examples

### Simple LLM Call
```bash
python simple_llm.py
```

Demonstrates basic API calls with different providers.

### Prompt Engineering
```bash
python prompt_engineering.py
```

Shows effective prompting techniques:
- Zero-shot vs few-shot
- System messages
- Chain of thought
- Output formatting

### Streaming Responses
```bash
python streaming_example.py
```

Implements streaming for real-time output display.

### Cost Tracking
```bash
python cost_tracking.py
```

Tracks token usage and estimates costs.

## Key Concepts

### Temperature
Controls randomness in responses:
- 0.0: Deterministic, focused
- 0.7: Balanced (default)
- 1.0+: Creative, varied

### Max Tokens
Limits response length. Remember:
- Input + output tokens count toward limits
- Different models have different context windows
- Longer contexts cost more

### System Messages
Set the behavior and personality:
```python
system = "You are a helpful data science tutor."
```

### Few-Shot Learning
Provide examples in the prompt:
```python
prompt = """
Classify sentiment:
"I love this!" -> positive
"It's okay" -> neutral
"Terrible" -> negative
"Amazing work!" -> ?
"""
```

## Best Practices

1. **Start simple**: Get basic calls working first
2. **Test prompts**: Iterate on prompt wording
3. **Handle errors**: APIs fail, implement retries
4. **Track costs**: Monitor token usage
5. **Use streaming**: Better UX for long responses
6. **Cache results**: Don't repeat identical calls
7. **Set timeouts**: Don't wait forever

## Common Issues

### Rate Limits
```python
# Implement exponential backoff
import time
for attempt in range(3):
    try:
        response = model.generate_content(...)
        break
    except Exception as e:
        time.sleep(2 ** attempt)
```

### Token Limits
```python
# Truncate input if needed
max_input_tokens = 3000
if len(text) > max_input_tokens:
    text = text[:max_input_tokens]
```

### API Keys
```python
# Always use environment variables
import os
api_key = os.getenv('GOOGLE_API_KEY')
if not api_key:
    raise ValueError("API key not found")
```

## Next Steps

After mastering these basics:
1. Explore vector databases (next example)
2. Build a RAG system
3. Use LangChain for complex workflows
4. Deploy an LLM-powered application

## Resources

- [Google AI Documentation](https://ai.google.dev/docs)
- [Prompt Engineering Guide](https://www.promptingguide.ai/)
- [Google AI Studio](https://aistudio.google.com/)