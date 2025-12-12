/**
 * Chat Interface for SOP Query System
 * Handles conversational interactions with conversation history
 */

let currentDirectory = null;
let conversationHistory = [];

function showStatus(message, isError = false) {
    const statusMsg = document.getElementById('statusMsg');
    if (statusMsg) {
        statusMsg.className = isError ? 'error' : 'status';
        statusMsg.textContent = message;
        statusMsg.style.display = 'block';
    }
}

function hideStatus() {
    const statusMsg = document.getElementById('statusMsg');
    if (statusMsg) {
        statusMsg.style.display = 'none';
    }
}

function showTypingIndicator() {
    const chatHistory = document.getElementById('chatHistory');
    const typingDiv = document.createElement('div');
    typingDiv.className = 'typing-indicator';
    typingDiv.id = 'typingIndicator';
    typingDiv.innerHTML = `
        <div class="typing-dots">
            <div class="typing-dot"></div>
            <div class="typing-dot"></div>
            <div class="typing-dot"></div>
        </div>
    `;
    chatHistory.appendChild(typingDiv);
    typingDiv.style.display = 'block';
    scrollToBottom();
}

function hideTypingIndicator() {
    const typingIndicator = document.getElementById('typingIndicator');
    if (typingIndicator) {
        typingIndicator.remove();
    }
}

function addMessageToChat(message, isUser = false, systemInfo = null) {
    const chatHistory = document.getElementById('chatHistory');
    
    // Remove welcome message if it exists
    const welcomeMessage = chatHistory.querySelector('.welcome-message');
    if (welcomeMessage) {
        welcomeMessage.remove();
    }
    
    const messageDiv = document.createElement('div');
    messageDiv.className = `chat-message ${isUser ? 'message-user' : 'message-assistant'}`;
    
    const timestamp = new Date().toLocaleTimeString();
    
    messageDiv.innerHTML = `
        <div class="message-bubble">${message}</div>
        <div class="message-timestamp">${timestamp}</div>
        ${systemInfo ? `<div class="message-system">${systemInfo}</div>` : ''}
    `;
    
    chatHistory.appendChild(messageDiv);
    scrollToBottom();
}

function scrollToBottom() {
    const chatHistory = document.getElementById('chatHistory');
    chatHistory.scrollTop = chatHistory.scrollHeight;
}

async function submitQuery() {
    const question = document.getElementById('questionInput').value.trim();
    if (!question) {
        showStatus('Please enter a question.', true);
        return;
    }
    
    if (!currentDirectory) {
        showStatus('Please load a directory first.', true);
        return;
    }
    
    // Add user message to chat
    addMessageToChat(question, true);
    
    // Clear input and show typing
    document.getElementById('questionInput').value = '';
    showTypingIndicator();
    hideStatus();
    
    const useEnhanced = document.getElementById('useEnhanced').checked;
    const showDebug = document.getElementById('showDebug').checked;
    
    try {
        const response = await fetch('/query', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                question: question,
                use_enhanced: useEnhanced,
                show_debug: showDebug
            })
        });
        
        const result = await response.json();
        hideTypingIndicator();
        
        if (result.success) {
            // Add assistant response to chat
            addMessageToChat(
                result.response,
                false,
                result.system_used + (result.conversation_length ? ` • Turn ${result.conversation_length}` : '')
            );
            
            // Show debug info if requested
            if (result.debug_info && showDebug) {
                document.getElementById('debugSection').style.display = 'block';
                const debugContainer = document.getElementById('debugContainer');
                debugContainer.innerHTML = `
                    <h4>🔧 Debug Information</h4>
                    <div class="debug-item"><strong>Original Question:</strong> ${result.debug_info.original_question}</div>
                    ${result.debug_info.contextualized_question ? `<div class="debug-item"><strong>With Context:</strong> ${result.debug_info.contextualized_question}</div>` : ''}
                    <div class="debug-item"><strong>Improved Question:</strong> ${result.debug_info.improved_question}</div>
                    <div class="debug-item"><strong>Search Strategy:</strong> ${result.debug_info.search_strategy}</div>
                    <div class="debug-item"><strong>Keywords:</strong> ${result.debug_info.keywords.join(', ')}</div>
                    <div class="debug-item"><strong>Context Used:</strong> ${result.debug_info.context_count} extractions</div>
                    <div class="debug-item"><strong>Conversation Turns:</strong> ${result.debug_info.conversation_turns || 0}</div>
                    <div class="debug-item"><strong>Context Summary:</strong> 
                        ${Object.entries(result.debug_info.context_summary).map(([k,v]) => `${k}: ${v}`).join(', ')}
                    </div>
                `;
                debugContainer.style.display = 'block';
            } else {
                document.getElementById('debugSection').style.display = 'none';
            }
            
            // showStatus('✅ Response generated successfully!');
        } else {
            addMessageToChat(`❌ Error: ${result.error}`, false, 'System: Error');
            showStatus(`❌ Query error: ${result.error}`, true);
        }
    } catch (error) {
        hideTypingIndicator();
        addMessageToChat(`❌ Network error: ${error.message}`, false, 'System: Error');
        showStatus(`❌ Network error: ${error.message}`, true);
    }
}

async function clearConversation() {
    try {
        const response = await fetch('/clear_conversation', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            }
        });
        
        const result = await response.json();
        
        if (result.success) {
            // Clear chat history UI
            const chatHistory = document.getElementById('chatHistory');
            chatHistory.innerHTML = `
                <div class="welcome-message">
                    <p>💬 Conversation cleared! Start a new conversation.</p>
                    <p>🔄 Your next questions will start fresh without previous context.</p>
                </div>
            `;
            
            showStatus('🗑️ Conversation history cleared');
            document.getElementById('questionInput').focus();
        }
    } catch (error) {
        showStatus(`❌ Error clearing conversation: ${error.message}`, true);
    }
}

// Auto-submit on Enter (but allow Shift+Enter for new lines)
document.addEventListener('DOMContentLoaded', function() {
    const questionInput = document.getElementById('questionInput');
    if (questionInput) {
        questionInput.addEventListener('keydown', function(e) {
            if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                submitQuery();
            }
        });
    }
    
    // Auto-focus question input when directory is loaded
    const directorySelect = document.getElementById('directorySelect');
    if (directorySelect) {
        directorySelect.addEventListener('change', function() {
            if (this.value) {
                setTimeout(() => {
                    document.getElementById('questionInput').focus();
                }, 100);
            }
        });
    }
});
