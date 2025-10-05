import React, { useState, useEffect, useRef } from 'react'
import { createPortal } from 'react-dom'

const SettingsMenu = ({ settings, onSettingsChange }) => {
  const [isOpen, setIsOpen] = useState(false)
  const [dropdownPosition, setDropdownPosition] = useState({ top: 0, left: 0 })
  const menuRef = useRef(null)
  const buttonRef = useRef(null)

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
      if (menuRef.current && !menuRef.current.contains(event.target)) {
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
          onClick={(e) => e.stopPropagation()}
        >
          <div className="settings-section">
            <h4>Query Model</h4>
            <div className="radio-group">
              <label>
                <input
                  type="radio"
                  name="query_model"
                  value="gpt-5"
                  checked={settings.query_model === 'gpt-5'}
                  onChange={handleQueryModelChange}
                />
                GPT-5
              </label>
              <label>
                <input
                  type="radio"
                  name="query_model"
                  value="gpt-5-mini"
                  checked={settings.query_model === 'gpt-5-mini'}
                  onChange={handleQueryModelChange}
                />
                GPT-5 Mini
              </label>
                <label>
                  <input
                    type="radio"
                    name="query_model"
                    value="gpt-5-nano"
                    checked={settings.query_model === 'gpt-5-nano'}
                    onChange={handleQueryModelChange}
                  />
                  GPT-5 Nano
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
            <label>
                <input
                  type="radio"
                  name="search_type"
                  value="rank_fusion"
                  checked={settings.search_type === 'rank_fusion'}
                  onChange={handleSearchTypeChange}
                />
                Rank Fusion
              </label>
              <label>
                <input
                  type="radio"
                  name="search_type"
                  value="bm25"
                  checked={settings.search_type === 'bm25'}
                  onChange={handleSearchTypeChange}
                />
                BM25
              </label>
              <label>
                <input
                  type="radio"
                  name="search_type"
                  value="vector_search"
                  checked={settings.search_type === 'vector_search'}
                  onChange={handleSearchTypeChange}
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
