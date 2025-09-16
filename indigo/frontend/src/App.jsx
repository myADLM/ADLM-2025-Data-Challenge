import React, { useState, useEffect } from 'react'
import './App.css'
import { Header, ChatWindow, DocumentsPanel, PDFViewer } from './components'
import { useBackendConnection, useChat } from './hooks'

function App() {
  const [documents, setDocuments] = useState([])
  const [loadingDocuments, setLoadingDocuments] = useState(true)
  const [pdfViewer, setPdfViewer] = useState({
    isOpen: false,
    url: '',
    title: ''
  })
  
  const { backendConnected } = useBackendConnection()
  const {
    message,
    setMessage,
    chatHistory,
    chatDocuments,
    isLoadingChat,
    chatMessagesRef,
    handleSubmit,
    clearChat
  } = useChat(backendConnected)

  // Initialize documents (now just a placeholder since documents come from chat)
  useEffect(() => {
    setLoadingDocuments(false)
    setDocuments([])
  }, [])

  const handleViewDocument = (url, title) => {
    setPdfViewer({
      isOpen: true,
      url,
      title
    })
  }

  const handleClosePdfViewer = () => {
    setPdfViewer({
      isOpen: false,
      url: '',
      title: ''
    })
  }

  return (
    <div className="app">
      <Header backendConnected={backendConnected} />
      
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
            onViewDocument={handleViewDocument}
          />
        </div>
      </main>
      
      <PDFViewer
        isOpen={pdfViewer.isOpen}
        onClose={handleClosePdfViewer}
        documentUrl={pdfViewer.url}
        documentTitle={pdfViewer.title}
      />
    </div>
  )
}

export default App
