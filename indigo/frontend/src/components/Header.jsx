import React from 'react'

const Header = ({ backendConnected }) => {
  return (
    <header className="header">
      <h1>Indigo BioAutomation: 2025 ADLM Data Science Challenge</h1>
      <p>Document Search & Chat Assistant</p>
      {backendConnected === false && (
        <div className="backend-warning">
          ⚠️ Could not connect to the backend server.
        </div>
      )}
    </header>
  )
}

export default Header
