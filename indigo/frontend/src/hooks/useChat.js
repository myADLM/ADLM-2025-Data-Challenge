import { useState, useEffect, useRef } from 'react'

const STORAGE_KEYS = {
  message: 'indigo.message',
  chatHistory: 'indigo.chatHistory',
  chatDocuments: 'indigo.chatDocuments',
  settings: 'indigo.settings'
}

export const useChat = (backendConnected) => {
  const [message, setMessage] = useState(() => {
    try {
      return localStorage.getItem(STORAGE_KEYS.message) || ''
    } catch {
      return ''
    }
  })
  const [chatHistory, setChatHistory] = useState(() => {
    try {
      const raw = localStorage.getItem(STORAGE_KEYS.chatHistory)
      return raw ? JSON.parse(raw) : []
    } catch {
      return []
    }
  })
  const [chatDocuments, setChatDocuments] = useState(() => {
    try {
      const raw = localStorage.getItem(STORAGE_KEYS.chatDocuments)
      return raw ? JSON.parse(raw) : []
    } catch {
      return []
    }
  })
  const [isLoadingChat, setIsLoadingChat] = useState(false)
  const [settings, setSettings] = useState(() => {
    try {
      const raw = localStorage.getItem(STORAGE_KEYS.settings)
      return raw ? JSON.parse(raw) : { query_model: 'gpt-5', search_type: 'rank_fusion' }
    } catch {
      return { query_model: 'gpt-5', search_type: 'rank_fusion' }
    }
  })
  const chatMessagesRef = useRef(null)

  // Auto-scroll to bottom when chat history changes
  useEffect(() => {
    if (chatMessagesRef.current) {
      chatMessagesRef.current.scrollTop = chatMessagesRef.current.scrollHeight
    }
  }, [chatHistory, isLoadingChat])

  // Persist state to localStorage when it changes
  useEffect(() => {
    try {
      localStorage.setItem(STORAGE_KEYS.message, message)
    } catch {}
  }, [message])

  useEffect(() => {
    try {
      localStorage.setItem(STORAGE_KEYS.chatHistory, JSON.stringify(chatHistory))
    } catch {}
  }, [chatHistory])

  useEffect(() => {
    try {
      localStorage.setItem(STORAGE_KEYS.chatDocuments, JSON.stringify(chatDocuments))
    } catch {}
  }, [chatDocuments])

  useEffect(() => {
    try {
      localStorage.setItem(STORAGE_KEYS.settings, JSON.stringify(settings))
    } catch {}
  }, [settings])

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
              chat_items: newChatHistory,
              query_model: settings.query_model,
              search_type: settings.search_type
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
    try {
      localStorage.removeItem(STORAGE_KEYS.chatHistory)
      localStorage.removeItem(STORAGE_KEYS.chatDocuments)
      localStorage.removeItem(STORAGE_KEYS.message)
    } catch {}
  }

  return {
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
  }
}
