# Todo AI - AI-Powered Todo List Assistant

An intelligent todo list application with an AI assistant that allows users to control all functionalities through natural language conversations.

## Features

- Natural language interface for managing tasks
- Task creation, updating, and deletion
- Task status and priority management
- User authentication
- Responsive UI for desktop and mobile

## Tech Stack

### Backend
- FastAPI
- SQLAlchemy
- PostgreSQL
- OpenAI GPT-4

### Frontend
- React
- Styled Components
- Vite

## Getting Started

### Prerequisites

- Python 3.8+
- Node.js 14+
- PostgreSQL
- Redis (optional)

### Environment Setup

1. Clone the repository:
```bash
git clone https://github.com/yourusername/todo_ai.git
cd todo_ai
```

2. Create and activate a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install backend dependencies:
```bash
pip install -r requirements.txt
```

4. Set up environment variables:
Create a `.env` file in the root directory with the following variables:
```
DATABASE_URL=postgresql://postgres:password@localhost/todo_ai
OPENAI_API_KEY=your_openai_api_key
SECRET_KEY=your_secret_key
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

5. Install frontend dependencies:
```bash
cd frontend
npm install
```

### Running the Application

1. Start the backend server:
```bash
cd backend
uvicorn main:app --reload
```

2. Start the frontend development server:
```bash
cd frontend
npm run dev
```

3. Open your browser and navigate to `http://localhost:5173`

## Usage

1. Register a new account or log in
2. Use the chat interface to interact with the AI assistant
3. Example commands:
   - "Add a task to buy groceries tomorrow"
   - "Show me all my high priority tasks"
   - "Mark the grocery task as complete"
   - "Change the priority of my report task to urgent"

## Project Structure

```
todo_ai/
├── backend/
│   ├── api/         # API endpoints
│   ├── models/      # Database models
│   └── agent/       # AI assistant components
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   ├── context/
│   │   └── App.jsx
└── requirements.txt
```

## License

This project is licensed under the MIT License - see the LICENSE file for details.
