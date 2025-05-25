import { useState, useRef, useEffect } from 'react'
import styled from 'styled-components'
import UIActionExecutor from './UIActionExecutor'
import ModeToggle from './ModeToggle'

// Direct API URL
const API_URL = 'http://localhost:8000'

const ChatContainer = styled.div`
  display: flex;
  flex-direction: column;
  height: 100%;
`

const MessagesContainer = styled.div`
  flex: 1;
  overflow-y: auto;
  padding: 1rem;
  display: flex;
  flex-direction: column;
`

const MessageBubble = styled.div`
  max-width: 80%;
  padding: 0.75rem 1rem;
  border-radius: 1rem;
  margin-bottom: 0.5rem;
  line-height: 1.4;

  ${props => props.isUser ? `
    align-self: flex-end;
    background-color: var(--primary-color);
    color: white;
    border-bottom-right-radius: 0.25rem;
  ` : `
    align-self: flex-start;
    background-color: var(--light-gray);
    border-bottom-left-radius: 0.25rem;
  `}
`

const InputContainer = styled.div`
  display: flex;
  padding: 1rem;
  border-top: 1px solid var(--light-gray);
`

const MessageInput = styled.input`
  flex: 1;
  padding: 0.75rem;
  border: 1px solid var(--medium-gray);
  border-radius: 1.5rem;
  margin-right: 0.5rem;

  &:focus {
    outline: none;
    border-color: var(--primary-color);
  }
`

const SendButton = styled.button`
  background-color: var(--primary-color);
  color: white;
  border-radius: 50%;
  width: 2.5rem;
  height: 2.5rem;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 0;

  &:hover {
    background-color: var(--secondary-color);
  }

  &:disabled {
    background-color: var(--medium-gray);
    cursor: not-allowed;
  }
`

const WelcomeMessage = styled.div`
  text-align: center;
  margin: 2rem 0;
  color: var(--dark-gray);
`

function ChatInterface({ onTaskUpdate }) {
  const [messages, setMessages] = useState([
    { id: 1, text: "Hi! I'm your AI assistant. How can I help you with your tasks today?", isUser: false }
  ])
  const [input, setInput] = useState('')
  const [loading, setLoading] = useState(false)
  const [uiActions, setUiActions] = useState(null)
  const [assistantMode, setAssistantMode] = useState(() => {
    // Initialize from localStorage or default to 'act'
    return localStorage.getItem('assistantMode') || 'act'
  })
  const messagesEndRef = useRef(null)

  useEffect(() => {
    scrollToBottom()
  }, [messages])

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }

  const handleSendMessage = async () => {
    if (!input.trim() || loading) return

    const userMessage = { id: Date.now(), text: input, isUser: true }
    setMessages(prev => [...prev, userMessage])
    setInput('')
    setLoading(true)

    try {
      // Get token from localStorage or use hardcoded token
      const token = localStorage.getItem('token') || 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJ0ZXN0dXNlciIsImV4cCI6MTc0NDQwODQ3Mn0.hW9PYGhLPzX5XAC7ieVeMcdqjmyeOBZBcjRHN2u_dvc';

      const response = await fetch(`${API_URL}/api/assistant/chat`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify({ message: input, assistant_mode: assistantMode })
      })

      if (!response.ok) {
        throw new Error('Failed to get response')
      }

      const data = await response.json()

      // Add assistant response
      setMessages(prev => [...prev, {
        id: Date.now() + 1,
        text: data.response,
        isUser: false
      }])

      // If there were task-related actions, refresh the task list
      console.log('Response data:', data);

      // Handle UI actions if present
      console.log('Checking for UI actions in response:', data);
      if (data.uiActions && Array.isArray(data.uiActions) && data.uiActions.length > 0) {
        console.log('Received UI actions directly:', data.uiActions);
        setUiActions(data.uiActions);
      } else {
        console.log('No direct UI actions found in response');

        // Check if UI actions are in the actions array
        if (data.actions && Array.isArray(data.actions)) {
          console.log('Checking actions array for UI actions:', data.actions);
          const uiActionObj = data.actions.find(action =>
            action && typeof action === 'object' && action.type === 'ui_actions'
          );

          if (uiActionObj && uiActionObj.uiActions && Array.isArray(uiActionObj.uiActions)) {
            console.log('Found UI actions in actions array:', uiActionObj.uiActions);
            setUiActions(uiActionObj.uiActions);
          } else {
            console.log('No UI actions found in actions array');
          }
        }
      }

      if (data.actions && data.actions.length > 0) {
        console.log('Received actions:', data.actions);
        // Check for any task-related action types
        if (data.actions.some(action =>
          ['task_added', 'task_updated', 'task_deleted', 'tasks_listed'].includes(action.type)
        )) {
          console.log('Task-related action detected, updating tasks...');
          // Force a delay to ensure the database has updated
          setTimeout(() => {
            console.log('Calling onTaskUpdate...');
            onTaskUpdate();
          }, 500);
        } else {
          console.log('No task-related action types found in:', data.actions);
        }
      } else {
        console.log('No actions found in response');
      }

    } catch (error) {
      console.error('Error sending message:', error)
      setMessages(prev => [...prev, {
        id: Date.now() + 1,
        text: "Sorry, I'm having trouble connecting right now. Please try again later.",
        isUser: false
      }])
    } finally {
      setLoading(false)
    }
  }

  const handleKeyPress = (e) => {
    if (e.key === 'Enter') {
      handleSendMessage()
    }
  }

  return (
    <ChatContainer>
      <MessagesContainer>
        {messages.length === 1 && (
          <WelcomeMessage>
            <h3>Welcome to Todo AI!</h3>
            <p>You can ask me to:</p>
            <ul style={{ textAlign: 'left', display: 'inline-block', marginTop: '0.5rem' }}>
              <li>Add new tasks</li>
              <li>List your tasks</li>
              <li>Mark tasks as complete</li>
              <li>Change task priorities</li>
              <li>And much more!</li>
            </ul>
          </WelcomeMessage>
        )}

        {messages.map(message => (
          <MessageBubble key={message.id} isUser={message.isUser}>
            {message.text}
          </MessageBubble>
        ))}
        <div ref={messagesEndRef} />
      </MessagesContainer>

      <ModeToggle
        onChange={(mode) => {
          setAssistantMode(mode);
          console.log(`Assistant mode changed to: ${mode}`);
        }}
        initialMode={assistantMode}
      />

      <InputContainer>
        <MessageInput
          type="text"
          placeholder="Type your message..."
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyPress={handleKeyPress}
          disabled={loading}
        />
        <SendButton onClick={handleSendMessage} disabled={!input.trim() || loading}>
          →
        </SendButton>
      </InputContainer>

      {/* UI Action Executor */}
      {uiActions && (
        <>
          {console.log('Rendering UIActionExecutor with actions:', uiActions)}
          <UIActionExecutor
            actions={uiActions}
            onComplete={() => {
              console.log('UI actions completed');
              setUiActions(null);
            }}
          />
        </>
      )}
    </ChatContainer>
  )
}

export default ChatInterface
