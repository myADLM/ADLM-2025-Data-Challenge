import React from 'react'

const ChatInput = ({ 
  message, 
  setMessage, 
  handleSubmit, 
  isLoadingChat, 
  chatHistory, 
  clearChat 
}) => {
  return (
    <form className="chat-input-form" onSubmit={handleSubmit}>
      <div className="input-container">
        <input
          type="text"
          value={message}
          onChange={(e) => setMessage(e.target.value)}
          placeholder="Ask a question about the documents..."
          className="chat-input"
        />
        <button type="submit" className="send-button" disabled={isLoadingChat || (message?.trim()?.length === 0)}>
          {isLoadingChat ? 'Sending...' : 'Send'}
        </button>
        <button 
          type="button" 
          className={`clear-button ${chatHistory.length === 0 ? 'hidden' : ''}`} 
          onClick={clearChat}
        >
          Clear
        </button>
      </div>
    </form>
  )
}

export default ChatInput
