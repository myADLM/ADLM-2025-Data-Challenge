import React from 'react'

const MatchesModal = ({ isOpen, onClose, documentTitle, matches }) => {
  if (!isOpen) return null

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal-content" onClick={(e) => e.stopPropagation()}>
        <div className="modal-header">
          <h3>Matching Text for: {documentTitle}</h3>
          <button className="modal-close-btn" onClick={onClose}>
            ×
          </button>
        </div>
        <div className="modal-body">
          {matches && matches.length > 0 ? (
            <div className="matches-list">
              {matches.map((match, index) => (
                <div key={index} className="match-item">
                  <div className="match-number">{index + 1}</div>
                  <div className="match-text">{match}</div>
                </div>
              ))}
            </div>
          ) : (
            <div className="no-matches">
              <p>No matching text found for this document.</p>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}

export default MatchesModal
