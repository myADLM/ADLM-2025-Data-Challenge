import React, { useState, useEffect } from 'react'
import './App.css'
import { Header, ChatWindow, DocumentsPanel, MatchesModal } from './components'
import { useBackendConnection, useChat } from './hooks'

function App() {
  const [documents, setDocuments] = useState([])
  const [loadingDocuments, setLoadingDocuments] = useState(true)
  const [matchesModal, setMatchesModal] = useState({
    isOpen: false,
    documentTitle: '',
    matches: []
  })
  
  const { backendConnected, apiStatus } = useBackendConnection()
  const {
    message,
    setMessage,
    chatHistory,
    chatDocuments,
    isLoadingChat,
    chatMessagesRef,
    handleSubmit,
    clearChat,
    settings,
    setSettings
  } = useChat(backendConnected)

  // Initialize documents (now just a placeholder since documents come from chat)
  useEffect(() => {
    setLoadingDocuments(false)
    setDocuments([])
  }, [])

  const handleViewMatches = (documentTitle, matches) => {
    setMatchesModal({
      isOpen: true,
      documentTitle,
      matches: matches || []
    })
  }

  const handleCloseMatchesModal = () => {
    setMatchesModal({
      isOpen: false,
      documentTitle: '',
      matches: []
    })
  }

  return (
    <div className="app">
      <Header 
        backendConnected={backendConnected} 
        apiStatus={apiStatus}
        settings={settings}
        onSettingsChange={setSettings}
      />
      
      <main className="main">
        <div className="chat-container">
          <div className="chat-section">
            <ChatWindow
              chatHistory={chatHistory}
              isLoadingChat={isLoadingChat}
              chatMessagesRef={chatMessagesRef}
              message={message}
              setMessage={setMessage}
              handleSubmit={handleSubmit}
              clearChat={clearChat}
            />
          </div>
          
          <DocumentsPanel
            chatDocuments={chatDocuments}
            documents={documents}
            loadingDocuments={loadingDocuments}
            onViewMatches={handleViewMatches}
          />
        </div>
      </main>
      
      <MatchesModal
        isOpen={matchesModal.isOpen}
        onClose={handleCloseMatchesModal}
        documentTitle={matchesModal.documentTitle}
        matches={matchesModal.matches}
      />
    </div>
  )
}

export default App
