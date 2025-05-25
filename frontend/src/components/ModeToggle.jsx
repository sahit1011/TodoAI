import { useState, useEffect } from 'react'
import styled from 'styled-components'

const ToggleContainer = styled.div`
  display: flex;
  align-items: center;
  margin-bottom: 10px;
  padding: 8px;
  background-color: #f5f5f5;
  border-radius: 8px;
`

const ToggleLabel = styled.span`
  font-size: 14px;
  margin-right: 10px;
  color: #333;
  font-weight: ${props => props.active ? 'bold' : 'normal'};
`

const ToggleSwitch = styled.div`
  position: relative;
  width: 60px;
  height: 30px;
  background-color: ${props => props.active ? '#4CAF50' : '#2196F3'};
  border-radius: 15px;
  transition: background-color 0.3s;
  cursor: pointer;
  display: flex;
  align-items: center;
  padding: 0 5px;
  justify-content: ${props => props.active ? 'flex-end' : 'flex-start'};
`

const ToggleButton = styled.div`
  width: 24px;
  height: 24px;
  background-color: white;
  border-radius: 50%;
  transition: transform 0.3s;
`

const ModeDescription = styled.div`
  font-size: 12px;
  color: #666;
  margin-top: 5px;
  padding: 0 8px;
`

function ModeToggle({ onChange, initialMode }) {
  const [mode, setMode] = useState(initialMode || 'act')

  useEffect(() => {
    // Load the saved mode from localStorage on component mount
    const savedMode = localStorage.getItem('assistantMode')
    if (savedMode) {
      setMode(savedMode)
    }
  }, [])

  const toggleMode = () => {
    const newMode = mode === 'act' ? 'plan' : 'act'
    setMode(newMode)
    
    // Save the mode to localStorage
    localStorage.setItem('assistantMode', newMode)
    
    // Call the onChange handler if provided
    if (onChange) {
      onChange(newMode)
    }
  }

  return (
    <div>
      <ToggleContainer>
        <ToggleLabel active={mode === 'plan'}>Plan Mode</ToggleLabel>
        <ToggleSwitch active={mode === 'act'} onClick={toggleMode}>
          <ToggleButton />
        </ToggleSwitch>
        <ToggleLabel active={mode === 'act'}>Act Mode</ToggleLabel>
      </ToggleContainer>
      <ModeDescription>
        {mode === 'act' 
          ? 'Act Mode: AI will control the UI and perform actions visually'
          : 'Plan Mode: AI will perform actions directly without UI interaction'}
      </ModeDescription>
    </div>
  )
}

export default ModeToggle
