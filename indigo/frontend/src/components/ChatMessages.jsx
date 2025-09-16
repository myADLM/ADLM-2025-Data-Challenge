import React from 'react'

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
            <div key={index} className={`message ${msg.agent}`}>
              <div className="message-content">
                {msg.text}
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
