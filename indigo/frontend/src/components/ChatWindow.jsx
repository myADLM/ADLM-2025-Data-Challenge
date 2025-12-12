import React from 'react'
import ChatMessages from './ChatMessages'
import ChatInput from './ChatInput'

const ChatWindow = ({
  chatHistory,
  isLoadingChat,
  chatMessagesRef,
  message,
  setMessage,
  handleSubmit,
  clearChat
}) => {
  return (
    <div className="chat-window">
      <ChatMessages
        chatHistory={chatHistory}
        isLoadingChat={isLoadingChat}
        chatMessagesRef={chatMessagesRef}
      />
      <ChatInput
        message={message}
        setMessage={setMessage}
        handleSubmit={handleSubmit}
        isLoadingChat={isLoadingChat}
        chatHistory={chatHistory}
        clearChat={clearChat}
      />
    </div>
  )
}

export default ChatWindow
