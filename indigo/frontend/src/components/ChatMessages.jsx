import React from 'react'
import ReactMarkdown from 'react-markdown'
import remarkGfm from 'remark-gfm'

const ChatMessages = ({ chatHistory, isLoadingChat, chatMessagesRef }) => {
  return (
    <div className="chat-messages" ref={chatMessagesRef}>
      {chatHistory.length === 0 ? (
        <div className="welcome-message">
          <h3>Welcome to the Document Search Assistant</h3>
          <p>Ask me anything about the available documents. I'll help you find relevant information and answer your questions.</p>
        </div>
      ) : (
        <>
          {chatHistory.map((msg, index) => (
            <div key={index} className={`message ${msg.role}`}>
              <div className="message-content">
                {msg.role === 'assistant' ? (
                  <ReactMarkdown remarkPlugins={[remarkGfm]}>{msg.text}</ReactMarkdown>
                ) : (
                  msg.text
                )}
              </div>
            </div>
          ))}
          {isLoadingChat && (
            <div className="message assistant">
              <div className="message-content">
                <div className="loading-indicator">
                  <div className="loading-dots">
                    <span></span>
                    <span></span>
                    <span></span>
                  </div>
                  <span>Assistant is typing...</span>
                </div>
              </div>
            </div>
          )}
        </>
      )}
    </div>
  )
}

export default ChatMessages
