import React, { useState, useEffect, useRef } from 'react'
import { createPortal } from 'react-dom'

const SettingsMenu = ({ apiStatus, settings, onSettingsChange }) => {
  const [isOpen, setIsOpen] = useState(false)
  const [dropdownPosition, setDropdownPosition] = useState({ top: 0, left: 0 })
  const menuRef = useRef(null)
  const buttonRef = useRef(null)
  
  // Debug API status
  console.log('SettingsMenu - API Status:', apiStatus)
  
  // Use API status values directly - they default to true and are updated by API check
  const isOpenAIAvailable = apiStatus?.openai_available ?? true
  const isRankFusionAvailable = apiStatus?.features?.rank_fusion ?? true
  const isBM25Available = apiStatus?.features?.bm25 ?? true
  const isVectorSearchAvailable = apiStatus?.features?.vector_search ?? true
  
  console.log('SettingsMenu - Availability:', {
    isOpenAIAvailable,
    isRankFusionAvailable,
    isBM25Available,
    isVectorSearchAvailable
  })

  const handleQueryModelChange = (e) => {
    onSettingsChange({
      ...settings,
      query_model: e.target.value
    })
  }

  const handleSearchTypeChange = (e) => {
    onSettingsChange({
      ...settings,
      search_type: e.target.value
    })
  }

  const toggleMenu = () => {
    if (!isOpen && buttonRef.current) {
      const rect = buttonRef.current.getBoundingClientRect()
      setDropdownPosition({
        top: rect.bottom + 8, // 8px margin
        left: rect.left
      })
    }
    setIsOpen(!isOpen)
  }

  // Close menu when clicking outside
  useEffect(() => {
    const handleClickOutside = (event) => {
      // Check if click is outside both the button and the dropdown
      const isOutsideButton = buttonRef.current && !buttonRef.current.contains(event.target)
      const isOutsideDropdown = !event.target.closest('.settings-dropdown')
      
      if (isOutsideButton && isOutsideDropdown) {
        setIsOpen(false)
      }
    }

    if (isOpen) {
      document.addEventListener('mousedown', handleClickOutside)
    }

    return () => {
      document.removeEventListener('mousedown', handleClickOutside)
    }
  }, [isOpen])

  return (
    <div className="settings-menu" ref={menuRef}>
      <button 
        ref={buttonRef}
        className="settings-menu-button"
        onClick={toggleMenu}
        aria-label="Settings"
      >
        <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">
          <line x1="3" y1="6" x2="21" y2="6"></line>
          <line x1="3" y1="12" x2="21" y2="12"></line>
          <line x1="3" y1="18" x2="21" y2="18"></line>
        </svg>
      </button>
      
      {isOpen && createPortal(
        <div 
          className="settings-dropdown"
          style={{
            top: `${dropdownPosition.top}px`,
            left: `${dropdownPosition.left}px`
          }}
        >
          {apiStatus?.loading && (
            <div className="settings-loading">
              <div className="loading-spinner"></div>
              <span>Checking API status...</span>
            </div>
          )}
          <div className="settings-section">
            <h4>Query Model</h4>
            <div className="radio-group">
              <label className={!isOpenAIAvailable ? 'disabled' : ''} title={!isOpenAIAvailable ? 'OpenAI key is unavailable' : ''}>
                <input
                  type="radio"
                  name="query_model"
                  value="gpt-5"
                  checked={settings.query_model === 'gpt-5'}
                  onChange={handleQueryModelChange}
                  disabled={!isOpenAIAvailable}
                />
                GPT-5
              </label>
              <label className={!isOpenAIAvailable ? 'disabled' : ''} title={!isOpenAIAvailable ? 'OpenAI key is unavailable' : ''}>
                <input
                  type="radio"
                  name="query_model"
                  value="gpt-5-mini"
                  checked={settings.query_model === 'gpt-5-mini'}
                  onChange={handleQueryModelChange}
                  disabled={!isOpenAIAvailable}
                />
                GPT-5 Mini
              </label>
              <label className={!isOpenAIAvailable ? 'disabled' : ''} title={!isOpenAIAvailable ? 'OpenAI key is unavailable' : ''}>
                <input
                  type="radio"
                  name="query_model"
                  value="gpt-5-nano"
                  checked={settings.query_model === 'gpt-5-nano'}
                  onChange={handleQueryModelChange}
                  disabled={!isOpenAIAvailable}
                />
                GPT-5 Nano
              </label>
              <label className={!isOpenAIAvailable ? 'disabled' : ''} title={!isOpenAIAvailable ? 'OpenAI key is unavailable' : ''}>
                <input
                  type="radio"
                  name="query_model"
                  value="amazon.nova-pro-v1:0"
                  checked={settings.query_model === 'amazon.nova-pro-v1:0'}
                  onChange={handleQueryModelChange}
                  disabled={!isOpenAIAvailable}
                />
                Amazon Nova
              </label>
              <label>
                <input
                  type="radio"
                  name="query_model"
                  value="none"
                  checked={settings.query_model === 'none'}
                  onChange={handleQueryModelChange}
                />
                None
              </label>
            </div>
          </div>
          
          <div className="settings-section">
            <h4>Search Type</h4>
            <div className="radio-group">
              <label className={!isRankFusionAvailable ? 'disabled' : ''} title={!isRankFusionAvailable ? 'Rank fusion feature is unavailable' : ''}>
                <input
                  type="radio"
                  name="search_type"
                  value="rank_fusion"
                  checked={settings.search_type === 'rank_fusion'}
                  onChange={handleSearchTypeChange}
                  disabled={!isRankFusionAvailable}
                />
                Rank Fusion
              </label>
              <label className={!isBM25Available ? 'disabled' : ''} title={!isBM25Available ? 'BM25 feature is unavailable' : ''}>
                <input
                  type="radio"
                  name="search_type"
                  value="bm25"
                  checked={settings.search_type === 'bm25'}
                  onChange={handleSearchTypeChange}
                  disabled={!isBM25Available}
                />
                BM25
              </label>
              <label className={!isVectorSearchAvailable ? 'disabled' : ''} title={!isVectorSearchAvailable ? 'Vector search feature is unavailable' : ''}>
                <input
                  type="radio"
                  name="search_type"
                  value="vector_search"
                  checked={settings.search_type === 'vector_search'}
                  onChange={handleSearchTypeChange}
                  disabled={!isVectorSearchAvailable}
                />
                Vector Search
              </label>
            </div>
          </div>
        </div>,
        document.body
      )}
    </div>
  )
}

export default SettingsMenu
