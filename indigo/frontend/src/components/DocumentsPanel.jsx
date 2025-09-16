import React from 'react'

const DocumentsPanel = ({ 
  chatDocuments, 
  documents, 
  loadingDocuments,
  onViewDocument
}) => {
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
                  className="view-document-btn"
                  onClick={() => {
                    console.log('Viewing document:', doc.title, 'URL:', doc.url)
                    onViewDocument(doc.url, doc.title)
                  }}
                  title="View document"
                >
                  🔍
                </button>
                <a 
                  href={doc.url} 
                  className="minimal-doc-link" 
                  download
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
        ) : documents.length === 0 ? (
          <div className="empty-state">
            <p>No documents loaded.</p>
          </div>
        ) : (
          // Show static documents as fallback
          documents.map((doc) => (
            <div key={doc.id} className="document-item">
              <h4>{doc.title}</h4>
              <p>{doc.description}</p>
              <a href={doc.url} className="doc-link" target="_blank" rel="noopener noreferrer">
                View Document
              </a>
            </div>
          ))
        )}
      </div>
    </div>
  )
}

export default DocumentsPanel
