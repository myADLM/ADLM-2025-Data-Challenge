import React from 'react'
import { SettingsMenu } from './index'

const Header = ({ backendConnected, settings, onSettingsChange }) => {
  return (
    <header className="header">
      <div className="header-content">
        <div className="header-left">
          <SettingsMenu 
            settings={settings} 
            onSettingsChange={onSettingsChange} 
          />
        </div>
        <div className="header-center">
          <h1>Indigo BioAutomation: 2025 ADLM Data Science Challenge</h1>
          <p>Document Search & Chat Assistant</p>
        </div>
        <div className="header-right">
          {backendConnected === false && (
            <div className="backend-warning">
              ⚠️ Could not connect to the backend server.
            </div>
          )}
        </div>
      </div>
    </header>
  )
}

export default Header
