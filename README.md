# TodoAI - AI-Powered Task Management Application

An intelligent todo list application with an AI assistant that allows users to control all functionalities through natural language conversations.

## 🚀 Features

### Core Functionality
- **Natural Language Interface**: Manage tasks through conversational AI
- **Multi-Agent AI System**: Sophisticated AI architecture with specialized agents
- **Two AI Modes**:
  - **Plan Mode**: Direct API actions for efficiency
  - **Act Mode**: UI simulation that mimics user interactions
- **Web Search Integration**: Real-time web search capabilities via LangChain
- **Traditional UI Controls**: Full task management interface as backup

### Task Management
- Task creation, updating, and deletion
- Priority levels and due date management
- Task status tracking (todo, in_progress, done)
- Natural language due dates ("tomorrow", "next week", etc.)
- Task filtering and search

### User Experience
- User authentication and authorization
- Real-time chat interface
- Responsive design for desktop and mobile
- Dark/Light theme support
- Professional modern UI with animations

## 🏗️ Architecture

### Backend (FastAPI + Python)
- **Multi-Agent System**: Conversational Agent + Action Agent + Web Search Agent
- **AI Models**: Gemini 2.5 Pro Experimental (free tier)
- **Database**: SQLite with SQLAlchemy ORM
- **Authentication**: JWT-based security
- **API**: RESTful endpoints with FastAPI

### Frontend (React + Vite)
- **Modern React**: Hooks, Context API, Styled Components
- **Real-time Updates**: Dynamic task management
- **Chat Interface**: Natural language interaction
- **UI Components**: Custom design system
- **Routing**: React Router for navigation

### AI Integration
- **LangChain**: For web search and external services
- **Request Router**: Intelligent routing between agents
- **Context Management**: Conversation history and state
- **Error Handling**: Graceful fallbacks and user-friendly messages

## 🛠️ Tech Stack

### Backend
- FastAPI
- SQLAlchemy
- SQLite
- Gemini API
- LangChain
- JWT Authentication

### Frontend
- React 18
- Vite
- Styled Components
- Axios
- React Router

## 📋 Prerequisites

- Python 3.8+
- Node.js 14+
- Gemini API Key (free tier available)

## 🚀 Getting Started

### 1. Clone the Repository
```bash
git clone https://github.com/sahit1011/TodoAI.git
cd TodoAI
```

### 2. Backend Setup
```bash
# Create and activate virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set up environment variables
cp .env.example .env
# Edit .env and add your API keys
```

### 3. Frontend Setup
```bash
cd frontend
npm install
```

### 4. Environment Configuration
Create a `.env` file in the root directory:
```env
# Database
DATABASE_URL=sqlite:///./todo_ai.db

# API Keys
GEMINI_API_KEY=your_gemini_api_key_here
OPENAI_API_KEY=your_openai_api_key_here  # Optional for LangChain
SERPAPI_API_KEY=your_serpapi_key_here    # Optional for web search

# JWT Configuration
SECRET_KEY=your_secret_key_here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

### 5. Run the Application

#### Start Backend Server
```bash
# From project root
python run_backend.py
# Or
cd backend && uvicorn main:app --reload
```

#### Start Frontend Development Server
```bash
cd frontend
npm run dev
```

### 6. Access the Application
Open your browser and navigate to `http://localhost:5173`

## 💬 Usage Examples

### Natural Language Commands
- "Add a task to buy groceries tomorrow with high priority"
- "Show me all my completed tasks"
- "Mark the grocery task as complete"
- "Change the priority of my report task to urgent"
- "What tasks do I have due this week?"
- "Search the web for React best practices"

### AI Modes
- **Plan Mode**: "Create a task called 'Review code' with medium priority"
- **Act Mode**: "Click the add task button and fill in the form"

## 📁 Project Structure

```
TodoAI/
├── backend/
│   ├── agent/                 # AI system components
│   │   ├── multi_agent/       # Multi-agent architecture
│   │   ├── langchain_integration/  # Web search & external services
│   │   └── *.py              # Individual agent implementations
│   ├── api/                  # REST API endpoints
│   ├── models/               # Database models
│   ├── migrations/           # Database migrations
│   └── main.py              # FastAPI application
├── frontend/
│   ├── src/
│   │   ├── components/       # React components
│   │   ├── context/         # React context providers
│   │   ├── styles/          # Design system
│   │   └── App.jsx          # Main application
│   └── package.json
├── requirements.txt          # Python dependencies
├── .env.example             # Environment template
└── README.md
```

## 🤖 AI System Details

### Multi-Agent Architecture
1. **Conversational Agent**: Understands user intent and extracts parameters
2. **Action Agent**: Executes database operations and task management
3. **Web Search Agent**: Handles external information requests
4. **Request Router**: Routes requests to appropriate agents

### Supported Intents
- `task_create` - Create new tasks
- `task_update` - Modify existing tasks
- `task_delete` - Remove tasks
- `task_list` - Display tasks with filters
- `task_complete` - Mark tasks as done
- `task_reopen` - Reopen completed tasks
- `conversation` - General chat and questions

## 🔧 Development

### Running Tests
```bash
# Backend tests
python -m pytest tests/

# Frontend tests
cd frontend && npm test
```

### Code Style
- Python: PEP 8 with type hints
- JavaScript: ESLint configuration
- Commits: Conventional commit format

## 🚀 Deployment

### Backend Deployment
```bash
# Production server
uvicorn backend.main:app --host 0.0.0.0 --port 8000

# With Gunicorn
gunicorn backend.main:app -w 4 -k uvicorn.workers.UvicornWorker
```

### Frontend Deployment
```bash
cd frontend
npm run build
# Deploy dist/ folder to your hosting service
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Gemini API for AI capabilities
- LangChain for external integrations
- FastAPI and React communities
- Open source contributors

## 📞 Support

For support, please open an issue on GitHub or contact the maintainers.

---

**TodoAI** - Where natural language meets task management! 🎯
