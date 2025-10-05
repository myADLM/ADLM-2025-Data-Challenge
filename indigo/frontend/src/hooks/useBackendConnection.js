import { useState, useEffect } from 'react'
import { buildApiUrl, API_ENDPOINTS } from '../config/api'

export const useBackendConnection = () => {
  const [backendConnected, setBackendConnected] = useState(null) // null = checking, true = connected, false = failed
  const [apiStatus, setApiStatus] = useState({
    openai_available: true, // Default to true, will be updated by API check
    features: {
      gpt_models: true, // Default to true, will be updated by API check
      vector_search: true, // Default to true, will be updated by API check
      rank_fusion: true, // Default to true, will be updated by API check
      bm25: true
    },
    loading: true,
    error: null,
    checked: false // Track if we've already checked API status
  })

  useEffect(() => {
    const pingBackend = async () => {
      try {
        const response = await fetch('/api/ping')
        if (response.ok) {
          const data = await response.json()
          if (data.ok) {
            setBackendConnected(true)
            
            // If backend is connected, check API status
            if (!apiStatus.checked) {
              await checkApiStatus()
            }
            return true
          }
        }
        setBackendConnected(false)
        return false
      } catch (error) {
        console.error('Backend ping failed:', error)
        setBackendConnected(false)
        return false
      }
    }

    const checkApiStatus = async () => {
      try {
        console.log('🔍 Checking API status during ping...')
        const url = buildApiUrl(API_ENDPOINTS.STATUS)
        const response = await fetch(url)
        
        if (response.ok) {
          const data = await response.json()
          console.log('✅ API status cached:', data)
          setApiStatus({
            ...data,
            loading: false,
            error: null,
            checked: true
          })
        } else {
          console.warn('⚠️ API status check failed, using defaults')
          setApiStatus(prev => ({
            ...prev,
            loading: false,
            error: null,
            checked: true
          }))
        }
      } catch (error) {
        console.warn('⚠️ API status check failed, using defaults:', error)
        setApiStatus(prev => ({
          ...prev,
          loading: false,
          error: null,
          checked: true
        }))
      }
    }

    pingBackend()
  }, [apiStatus.checked])

  return { backendConnected, apiStatus }
}
