import { useState, useEffect } from 'react'
import { buildApiUrl, API_ENDPOINTS } from '../config/api'

export const useApiStatus = () => {
  const [apiStatus, setApiStatus] = useState({
    openai_available: false,
    features: {
      gpt_models: false,
      vector_search: false,
      rank_fusion: false,
      bm25: true
    },
    loading: true,
    error: null
  })

  useEffect(() => {
    const checkApiStatus = async (retryCount = 0) => {
      try {
        // First check if backend is alive
        const pingUrl = buildApiUrl(API_ENDPOINTS.PING)
        console.log(`🏓 Checking backend ping at: ${pingUrl}`)
        const pingResponse = await fetch(pingUrl)
        
        if (!pingResponse.ok) {
          throw new Error(`Backend ping failed: ${pingResponse.status}`)
        }
        
        console.log('✅ Backend is alive, checking API status...')
        
        // Now check API status
        const url = buildApiUrl(API_ENDPOINTS.STATUS)
        console.log(`🔍 Checking API status at: ${url} (attempt ${retryCount + 1})`)
        const response = await fetch(url)
        console.log('📡 API status response:', response.status, response.statusText)
        
        if (response.ok) {
          const data = await response.json()
          console.log('✅ API status data:', data)
          setApiStatus({
            ...data,
            loading: false,
            error: null
          })
        } else {
          throw new Error(`HTTP error! status: ${response.status}`)
        }
      } catch (error) {
        console.error(`❌ Error checking API status (attempt ${retryCount + 1}):`, error)
        
        // Retry up to 3 times with exponential backoff
        if (retryCount < 3) {
          const delay = Math.pow(2, retryCount) * 1000 // 1s, 2s, 4s
          console.log(`⏳ Retrying in ${delay}ms...`)
          setTimeout(() => checkApiStatus(retryCount + 1), delay)
        } else {
          setApiStatus(prev => ({
            ...prev,
            loading: false,
            error: error.message
          }))
        }
      }
    }

    checkApiStatus()
  }, [])

  return apiStatus
}
