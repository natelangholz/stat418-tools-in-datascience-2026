# Week 5: Large Language Models & RAG

## Overview

This week explores how to leverage Large Language Models (LLMs) in data science applications beyond simple chat interfaces. We'll dive into Retrieval Augmented Generation (RAG), vector databases, and frameworks like LangChain that make building LLM-powered applications practical and scalable.

## Topics Covered

### Large Language Models (LLMs)
- Understanding modern LLMs (GPT, Claude, Gemini, etc.)
- API access vs local models
- Prompt engineering fundamentals
- Token limits and context windows
- Cost considerations and optimization

### Vector Databases
- What are embeddings and why they matter
- Vector similarity search
- Popular vector databases (ChromaDB, Pinecone, Weaviate)
- Storing and retrieving semantic information
- Embedding models and their trade-offs

### Retrieval Augmented Generation (RAG)
- The RAG architecture
- Why RAG beats fine-tuning for many use cases
- Document chunking strategies
- Retrieval techniques and ranking
- Combining retrieval with generation
- Evaluating RAG systems

### LangChain & Frameworks
- LangChain components and abstractions
- Chains, agents, and tools
- Memory and conversation management
- Integration with vector databases
- Alternative frameworks (LlamaIndex, Haystack)

## Learning Objectives

By the end of this week, you should be able to:

1. **Use LLM APIs** effectively with proper error handling and rate limiting
2. **Build a RAG system** that retrieves relevant context and generates answers
3. **Work with vector databases** to store and search embeddings
4. **Implement LangChain** components for common LLM tasks
5. **Understand trade-offs** between different approaches and tools
6. **Deploy LLM applications** with consideration for cost and performance

## Examples

### 1. LLM Basics (`examples/llm-basics/`)
- Simple API calls to different LLM providers
- Prompt engineering techniques
- Streaming responses
- Error handling and retries
- Cost tracking

### 2. Vector Database (`examples/vector-database/`)
- Creating embeddings with different models
- Storing vectors in ChromaDB
- Similarity search
- Metadata filtering
- Persistence and loading

### 3. RAG System (`examples/rag-system/`)
- Document loading and chunking
- Building a vector store
- Retrieval with ranking
- Generation with context
- Complete Q&A system

### 4. LangChain Application (`examples/langchain-app/`)
- LangChain chains and prompts
- Conversation memory
- Agent with tools
- Integration with vector stores
- Production patterns

## Key Concepts

### Embeddings
Embeddings are dense vector representations of text that capture semantic meaning. Similar concepts have similar vectors, enabling semantic search.

### RAG vs Fine-tuning
- **RAG**: Retrieves relevant information at query time, combines with prompt
  - Pros: Easy to update, no training needed, works with any LLM
  - Cons: Retrieval quality matters, slower than pure generation
- **Fine-tuning**: Trains model on specific data
  - Pros: Faster inference, can change model behavior
  - Cons: Expensive, requires training data, hard to update

### Vector Similarity
Common distance metrics:
- **Cosine similarity**: Measures angle between vectors (most common)
- **Euclidean distance**: Straight-line distance
- **Dot product**: Fast but sensitive to magnitude

## Tools & Libraries

### LLM Providers
- **Google** (Gemini): Multimodal, competitive pricing, free tier available
- **Anthropic** (Claude): Strong reasoning, large context
- **Local models** (Ollama): Free, private, slower

### Vector Databases
- **ChromaDB**: Simple, embedded, great for prototypes
- **Pinecone**: Managed, scalable, easy to use
- **Weaviate**: Open source, feature-rich
- **FAISS**: Fast, local, from Meta

### Frameworks
- **LangChain**: Most popular, comprehensive
- **LlamaIndex**: Focused on RAG and data
- **Haystack**: Production-ready, modular

## Best Practices

### Prompt Engineering
1. Be specific and clear
2. Provide examples (few-shot learning)
3. Use system messages for behavior
4. Iterate and test systematically
5. Consider token limits

### RAG Systems
1. Chunk documents thoughtfully (size and overlap)
2. Use appropriate embedding models
3. Implement hybrid search (vector + keyword)
4. Re-rank retrieved results
5. Include source citations
6. Monitor retrieval quality

### Production Considerations
1. **Cost**: Track token usage, cache when possible
2. **Latency**: Stream responses, optimize retrieval
3. **Reliability**: Implement retries, fallbacks
4. **Security**: Sanitize inputs, protect API keys
5. **Monitoring**: Log queries, track performance

## Common Pitfalls

1. **Ignoring context limits**: LLMs have token limits
2. **Poor chunking**: Too large or too small chunks hurt retrieval
3. **Not testing retrieval**: Generation is only as good as retrieval
4. **Hardcoding prompts**: Make prompts configurable
5. **Forgetting costs**: LLM calls add up quickly
6. **No error handling**: APIs fail, networks timeout
7. **Overly complex chains**: Start simple, add complexity as needed

## Resources

### Documentation
- [LangChain Docs](https://python.langchain.com/)
- [ChromaDB Docs](https://docs.trychroma.com/)
- [Google AI Docs](https://ai.google.dev/docs)
- [Anthropic API Docs](https://docs.anthropic.com/)

### Articles & Papers
- [Retrieval-Augmented Generation for Knowledge-Intensive NLP Tasks](https://arxiv.org/abs/2005.11401)
- [Is RAG Dead?](https://qdrant.tech/articles/rag-is-dead/) - Spoiler: No
- [Prompt Engineering Guide](https://www.promptingguide.ai/)

### Tools
- [Ollama](https://ollama.ai/) - Run LLMs locally
- [LangSmith](https://smith.langchain.com/) - LangChain debugging
- [Weights & Biases](https://wandb.ai/) - Experiment tracking
