# Components

This directory contains all the React components for the Indigo BioAutomation chat application.

## Component Structure

### Header
- **File**: `Header.jsx`
- **Purpose**: Displays the application title and backend connection status
- **Props**: `backendConnected` (boolean)

### ChatMessages
- **File**: `ChatMessages.jsx`
- **Purpose**: Renders the chat message list with welcome message and loading states
- **Props**: `chatHistory`, `isLoadingChat`, `chatMessagesRef`

### ChatInput
- **File**: `ChatInput.jsx`
- **Purpose**: Handles the chat input form with send and clear buttons
- **Props**: `message`, `setMessage`, `handleSubmit`, `isLoadingChat`, `chatHistory`, `clearChat`

### ChatWindow
- **File**: `ChatWindow.jsx`
- **Purpose**: Combines ChatMessages and ChatInput into a single chat interface
- **Props**: All props from ChatMessages and ChatInput

### DocumentsPanel
- **File**: `DocumentsPanel.jsx`
- **Purpose**: Displays relevant documents from chat responses or static documents
- **Props**: `chatDocuments`, `documents`, `loadingDocuments`

## Usage

```jsx
import { Header, ChatWindow, DocumentsPanel } from './components'
```

## Index File

The `index.js` file exports all components for clean imports.
