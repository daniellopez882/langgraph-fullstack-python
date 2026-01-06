# Full-Stack Python Chatbot with LangGraph

This is a full-stack chatbot application built with [LangGraph](https://github.com/langchain-ai/langgraph) and [FastHTML](https://fasthtml.readme.io/). It features a React-style agent with a modern web UI, all hosted within a single LangGraph deployment.

## Features

- **Single Deployment**: Host both your agent and UI in one LangGraph deployment.
- **Modern UI**: Beautiful chat interface built with FastHTML and DaisyUI.
- **Reasoning Agent**: Intelligent chatbot using LangGraph's React agent pattern.
- **Easy Configuration**: Simple HTTP routing setup through `langgraph.json`.

## Getting Started

### Prerequisites

- Python 3.11+
- [uv](https://github.com/astral-sh/uv)

### Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/daniellopez882/langgraph-fullstack-python.git
   cd langgraph-fullstack-python
   ```

2. Install dependencies:
   ```bash
   uv sync --dev
   ```

### Running Locally

Run the local development server:
```bash
uv run langgraph dev --no-browser
```

The application will be available at `http://localhost:2024`.

## Author

- **Daniel Lopez** (GitHub: [daniellopez882](https://github.com/daniellopez882))

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.