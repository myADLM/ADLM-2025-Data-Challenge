import { useState, useEffect, useRef } from 'react'

export const useChat = (backendConnected) => {
  const [message, setMessage] = useState('')
  const [chatHistory, setChatHistory] = useState([])
  const [chatDocuments, setChatDocuments] = useState([])
  const [isLoadingChat, setIsLoadingChat] = useState(false)
  const chatMessagesRef = useRef(null)

  // Auto-scroll to bottom when chat history changes
  useEffect(() => {
    if (chatMessagesRef.current) {
      chatMessagesRef.current.scrollTop = chatMessagesRef.current.scrollHeight
    }
  }, [chatHistory, isLoadingChat])

  const handleSubmit = async (e) => {
    e.preventDefault()
    if (message.trim() && !isLoadingChat) {
      const userMessage = { agent: 'user', text: message.trim() }
      const newChatHistory = [...chatHistory, userMessage]
      setChatHistory(newChatHistory)
      setMessage('')
      
      // Clear previous chat documents when starting new conversation
      if (chatHistory.length === 0) {
        setChatDocuments([])
      }
      
      // Only process if backend is connected
      if (backendConnected) {
        setIsLoadingChat(true)
        try {
          const response = await fetch('/api/chat', {
            method: 'POST',
            headers: {
              'Content-Type': 'application/json',
            },
            body: JSON.stringify({
              chat_items: newChatHistory
            })
          })
          
          if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`)
          }
          
          const data = await response.json()
          
          // Update chat history with the response
          if (data.chat_items) {
            setChatHistory(data.chat_items)
          } else {
            // Fallback if response doesn't include chat_items
            setChatHistory(prev => [...prev, { 
              agent: 'assistant', 
              text: data.response || 'I received your message but couldn\'t process it properly.' 
            }])
          }
          
          // Update documents from chat response
          if (data.documents && Array.isArray(data.documents)) {
            setChatDocuments(data.documents)
          } else {
            // Clear chat documents if none provided
            setChatDocuments([])
          }
        } catch (error) {
          console.error('Error calling chat API:', error)
          setChatHistory(prev => [...prev, { 
            agent: 'assistant', 
            text: 'Sorry, I encountered an error processing your request. Please try again.' 
          }])
        } finally {
          setIsLoadingChat(false)
        }
      } else {
        // Add error message to chat if backend is not connected
        setChatHistory(prev => [...prev, { 
          agent: 'assistant', 
          text: "Sorry, I cannot process your request because the backend server is not available." 
        }])
      }
    }
  }

  const clearChat = () => {
    setChatHistory([])
    setChatDocuments([])
    setMessage('')
  }

  return {
    message,
    setMessage,
    chatHistory,
    chatDocuments,
    isLoadingChat,
    chatMessagesRef,
    handleSubmit,
    clearChat
  }
}
