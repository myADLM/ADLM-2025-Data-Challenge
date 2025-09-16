# Custom Hooks

This directory contains custom React hooks that encapsulate business logic and state management.

## Hook Structure

### useBackendConnection
- **File**: `useBackendConnection.js`
- **Purpose**: Manages backend connection status
- **Returns**: `{ backendConnected }`
- **Features**: Automatically pings backend on mount

### useChat
- **File**: `useChat.js`
- **Purpose**: Manages all chat-related state and logic
- **Parameters**: `backendConnected` (boolean)
- **Returns**: 
  - `message`, `setMessage` - Input message state
  - `chatHistory` - Array of chat messages
  - `chatDocuments` - Documents from chat responses
  - `isLoadingChat` - Loading state for chat requests
  - `chatMessagesRef` - Ref for auto-scrolling
  - `handleSubmit` - Form submission handler
  - `clearChat` - Function to clear chat history

## Usage

```jsx
import { useBackendConnection, useChat } from './hooks'

function App() {
  const { backendConnected } = useBackendConnection()
  const { message, setMessage, chatHistory, handleSubmit } = useChat(backendConnected)
  
  // Component logic...
}
```

## Index File

The `index.js` file exports all hooks for clean imports.
