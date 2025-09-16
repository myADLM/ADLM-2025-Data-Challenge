import React, { useState, useEffect } from 'react'

const PDFViewer = ({ isOpen, onClose, documentUrl, documentTitle }) => {
  const [pdfError, setPdfError] = useState(false)
  const [isLoading, setIsLoading] = useState(true)

  // Convert relative URL to full backend URL for iframe
  const getFullUrl = (url) => {
    if (url.startsWith('/documents/')) {
      return `http://localhost:5174${url}`
    }
    return url
  }

  useEffect(() => {
    if (isOpen) {
      const fullUrl = getFullUrl(documentUrl)
      console.log('Opening PDF viewer for URL:', documentUrl)
      console.log('Full URL for iframe:', fullUrl)
      setPdfError(false)
      setIsLoading(true)
      
      // Test if the PDF URL is accessible
      const testUrl = async () => {
        try {
          const response = await fetch(fullUrl, { method: 'HEAD' })
          console.log('PDF URL test response:', response.status, response.headers.get('content-type'))
          if (!response.ok) {
            console.error('PDF URL not accessible:', response.status)
            setPdfError(true)
            setIsLoading(false)
            return
          }
        } catch (error) {
          console.error('PDF URL test failed:', error)
          setPdfError(true)
          setIsLoading(false)
          return
        }
      }
      
      testUrl()
      
      // Set a timeout to stop loading after 10 seconds
      const timeout = setTimeout(() => {
        console.log('PDF loading timeout - stopping loading state')
        setPdfError(true)
        setIsLoading(false)
      }, 10000)
      
      return () => clearTimeout(timeout)
    }
  }, [isOpen, documentUrl])

  if (!isOpen) return null

  const handleObjectLoad = () => {
    console.log('PDF object loaded successfully')
    setIsLoading(false)
  }

  const handleObjectError = () => {
    console.error('PDF loading error for URL:', documentUrl)
    setPdfError(true)
    setIsLoading(false)
  }

  const openInNewTab = () => {
    window.open(documentUrl, '_blank')
  }

  return (
    <div className="pdf-viewer-overlay" onClick={onClose}>
      <div className="pdf-viewer-panel" onClick={(e) => e.stopPropagation()}>
        <div className="pdf-viewer-header">
          <h3>{documentTitle}</h3>
          <div className="pdf-viewer-actions">
            <button 
              className="pdf-viewer-open-tab" 
              onClick={openInNewTab}
              title="Open in new tab"
            >
              🔗
            </button>
            <button className="pdf-viewer-close" onClick={onClose}>
              ✕
            </button>
          </div>
        </div>
        <div className="pdf-viewer-content">
          {isLoading && (
            <div className="pdf-loading">
              <div className="loading-spinner"></div>
              <p>Loading PDF...</p>
            </div>
          )}
          {pdfError ? (
            <div className="pdf-error">
              <p>Unable to display PDF in viewer.</p>
              <p>URL: {getFullUrl(documentUrl)}</p>
              <button className="pdf-fallback-btn" onClick={openInNewTab}>
                Open in New Tab
              </button>
            </div>
          ) : (
            <object
              data={getFullUrl(documentUrl)}
              type="application/pdf"
              className="pdf-viewer-iframe"
              onLoad={handleObjectLoad}
              onError={handleObjectError}
              style={{ display: isLoading ? 'none' : 'block' }}
            >
              <p>Your browser does not support PDFs. 
                <a href={getFullUrl(documentUrl)} target="_blank" rel="noopener noreferrer">
                  Click here to download the PDF
                </a>
              </p>
            </object>
          )}
        </div>
      </div>
    </div>
  )
}

export default PDFViewer
