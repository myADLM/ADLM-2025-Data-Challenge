import { useState, useEffect } from 'react'

export const useBackendConnection = () => {
  const [backendConnected, setBackendConnected] = useState(null) // null = checking, true = connected, false = failed

  useEffect(() => {
    const pingBackend = async () => {
      try {
        const response = await fetch('/api/ping')
        if (response.ok) {
          const data = await response.json()
          if (data.ok) {
            setBackendConnected(true)
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

    pingBackend()
  }, [])

  return { backendConnected }
}
