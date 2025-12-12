import React from 'react'

const DocumentsPanel = ({ 
  chatDocuments, 
  documents, 
  loadingDocuments,
  onViewMatches
}) => {
  // Only render if there are documents to show
  if (chatDocuments.length === 0 && !loadingDocuments && documents.length === 0) {
    return null
  }

  return (
    <div className="documents-section">
      <h3>
        {chatDocuments.length > 0 ? 'Relevant Documents' : 'Available Documents'}
      </h3>
      <div className="document-links">
        {chatDocuments.length > 0 ? (
          // Show documents from chat response
          chatDocuments.map((doc, index) => (
            <div key={`chat-${index}`} className="minimal-document-item">
              <div className="document-item-content">
                <button 
                  className="view-matches-btn"
                  onClick={() => onViewMatches(doc.title, doc.matches)}
                  title="View matching text"
                >
                  🔍
                </button>
                <a 
                  href={doc.url} 
                  className="minimal-doc-link" 
                  download={doc.title}
                  target="_blank"
                  rel="noopener noreferrer"
                  title={doc.ghost || doc.title}
                >
                  {doc.title}
                </a>
              </div>
            </div>
          ))
        ) : loadingDocuments ? (
          <div className="loading-state">
            <div className="loading-spinner"></div>
            <p>Loading documents...</p>
          </div>
        ) : (
          // Show static documents as fallback
          documents.map((doc) => (
            <div key={doc.id} className="document-item">
              <h4>{doc.title}</h4>
              <p>{doc.description}</p>
            </div>
          ))
        )}
      </div>
    </div>
  )
}

export default DocumentsPanel
