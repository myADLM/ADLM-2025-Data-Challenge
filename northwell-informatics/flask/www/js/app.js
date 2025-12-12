/**
 * Laboratory Query System - Main Application JavaScript
 * ===================================================
 * Uses jQuery for DOM manipulation and AJAX requests
 */

$(document).ready(function() {
    // Application state
    const App = {
        systemsInitialized: false,
        conversationHistory: [],
        
        // Initialize the application
        init: function() {
            this.bindEvents();
            console.log('Laboratory Query System initialized');
            // Auto-initialize systems on page load
            this.autoInitializeSystems();
        },
        
        // Bind all event handlers
        bindEvents: function() {
            // System operations
            $('#initializeBtn').on('click', this.initializeSystems);
            
            // Chat operations
            $('#queryBtn').on('click', this.submitQuery);
            $('#clearChatBtn').on('click', this.clearChat);
            
            // Enter key to send message (Shift+Enter for new line)
            $('#questionInput').on('keydown', function(e) {
                if (e.key === 'Enter' && !e.shiftKey) {
                    e.preventDefault();
                    App.submitQuery();
                }
            });
            
            // Clear status messages when user starts typing
            $('#questionInput').on('input', function() {
                if ($(this).val().length > 0) {
                    App.hideStatus();
                }
            });
        },
        
        // Status message functions
        showStatus: function(message, isError = false) {
            const $statusMsg = $('#statusMsg');
            $statusMsg
                .removeClass('status error')
                .addClass(isError ? 'error' : 'status')
                .text(message)
                .show()
                .addClass('fade-in');
        },
        
        hideStatus: function() {
            $('#statusMsg').hide();
        },
        
        // Auto-initialize systems on page load
        autoInitializeSystems: function() {
            console.log('Auto-initializing query systems...');
            App.showLoading();
            App.showStatus('🔄 Initializing query systems automatically...');
            
            $.ajax({
                url: '/initialize_systems',
                method: 'POST',
                contentType: 'application/json'
            })
            .done(function(result) {
                App.hideLoading();
                
                if (result.success) {
                    App.systemsInitialized = true;
                    App.showSystemsReadyAuto();
                    App.hideStatus(); // Hide the initialization status message
                } else {
                    App.showStatus(`❌ Auto-initialization failed: ${result.error}. Please refresh the page.`, true);
                    console.error('Auto-initialization failed:', result.error);
                }
            })
            .fail(function(xhr, status, error) {
                App.hideLoading();
                App.showStatus(`❌ Network error during initialization: ${error}. Please refresh the page.`, true);
                console.error('Auto-initialization network error:', error);
            });
        },
        
        // Loading functions
        showLoading: function() {
            $('#loading').show();
        },
        
        hideLoading: function() {
            $('#loading').hide();
        },
        
        // Initialize query systems
        initializeSystems: function() {
            App.showLoading();
            App.showStatus('🔧 Initializing query systems...');
            
            $.ajax({
                url: '/initialize_systems',
                method: 'POST',
                contentType: 'application/json'
            })
            .done(function(result) {
                App.hideLoading();
                
                if (result.success) {
                    App.systemsInitialized = true;
                    App.showSystemsReady();
                    App.showStatus('✅ Query systems initialized successfully!');
                } else {
                    App.showStatus(`❌ Error initializing systems: ${result.error}`, true);
                }
            })
            .fail(function(xhr, status, error) {
                App.hideLoading();
                App.showStatus(`❌ Network error: ${error}`, true);
            });
        },
        
        // Show systems ready state
        showSystemsReady: function() {
            $('#systemInfo').show().addClass('fade-in');
            $('#queryBtn').prop('disabled', false);
            $('#questionInput').prop('disabled', false);
            $('#initializeBtn').text('✅ Systems Ready').prop('disabled', true).css('animation', 'none');
            
            // Update welcome message
            App.updateChatHistory([{
                type: 'system',
                message: '🚀 Query systems initialized! Choose SOP or FDA query type and ask your questions.'
            }]);
            
            // Focus on question input
            setTimeout(() => $('#questionInput').focus(), 100);
        },
        
        // Show systems ready state for auto-initialization
        showSystemsReadyAuto: function() {
            // Enable chat interface
            $('#queryBtn').prop('disabled', false);
            $('#questionInput').prop('disabled', false);
            
            // Update placeholder text
            $('#questionInput').attr('placeholder', 'Choose SOP or FDA query type above, then ask your questions:\n\nSOP Query Examples:\n• How do I prepare samples for blood glucose testing?\n• What are the safety procedures for handling hazardous chemicals?\n• What\'s the calibration procedure for the pH meter?\n\nFDA Query Examples:\n• What FDA clearances exist for glucose meters?\n• Show me 510(k) submissions for cardiac devices\n• What are the regulatory requirements for point-of-care testing?');
            
            // Focus on question input - no system message needed
            setTimeout(() => $('#questionInput').focus(), 100);
        },
        
        // Submit query to the backend
        submitQuery: function() {
            const $chatInput = $('#questionInput');
            const question = $chatInput.val().trim();
            
            if (!question) {
                App.showStatus('Please enter a question.', true);
                return;
            }
            
            // We'll let the server check initialization status instead of tracking it client-side
            
            // Get selected query type
            const queryType = $('input[name="queryType"]:checked').val();
            
            // Add user message to chat
            App.addMessageToChat(question, true, queryType);
            $chatInput.val('');
            
            // Show loading message in chat
            const loadingId = App.addLoadingMessage();
            
            const queryData = {
                question: question,
                query_type: queryType,
                show_debug: $('#showDebug').is(':checked')
            };
            
            $.ajax({
                url: '/query',
                method: 'POST',
                contentType: 'application/json',
                data: JSON.stringify(queryData)
            })
            .done(function(result) {
                App.removeLoadingMessage(loadingId);
                
                if (result.success) {
                    App.addMessageToChat(result.response, false, queryType, result.system_used);
                    
                    // Update conversation history
                    App.conversationHistory.push({
                        question: question,
                        response: result.response,
                        query_type: queryType,
                        timestamp: new Date().toISOString()
                    });
                    
                    // App.showStatus('✅ Response generated');
                    
                    // Show debug info if requested
                    if (result.debug_info && $('#showDebug').is(':checked')) {
                        App.showDebugInfo(result.debug_info);
                    }
                } else {
                    App.addMessageToChat(`Error: ${result.error}`, false, queryType, null, true);
                    App.showStatus(`❌ Query error: ${result.error}`, true);
                }
            })
            .fail(function(xhr, status, error) {
                App.removeLoadingMessage(loadingId);
                App.addMessageToChat(`Network error: ${error}`, false, queryType, null, true);
                App.showStatus(`❌ Network error: ${error}`, true);
            });
        },
        
        // Add message to chat history
        addMessageToChat: function(message, isUser = false, queryType = 'sop', systemUsed = null, isError = false) {
            const $chatHistory = $('#chatHistory');
            const $messageDiv = $('<div>').addClass('fade-in');
            const timestamp = new Date().toLocaleTimeString();
            
            if (isUser) {
                const typeIcon = queryType === 'fda' ? '📋' : '🔬';
                const typeName = queryType === 'fda' ? 'FDA' : 'SOP';
                $messageDiv
                    .addClass('user-message')
                    .html(`
                        <div class="message-header">
                            <strong>${typeIcon} You (${typeName} Query):</strong>
                            <span class="timestamp">${timestamp}</span>
                        </div>
                        <div class="message-content">${this.escapeHtml(message)}</div>
                    `);
            } else {
                const formattedMessage = isError ? this.escapeHtml(message) : this.formatResponse(message);
                $messageDiv
                    .addClass(isError ? 'system-message' : 'bot-message')
                    .html(`
                        <div class="message-header">
                            <strong>${isError ? '❌ Error' : '🤖 Assistant'}:</strong>
                            <span class="timestamp">${timestamp}</span>
                        </div>
                        <div class="message-content">${formattedMessage}</div>
                        ${systemUsed ? `<div class="system-info">${systemUsed}</div>` : ''}
                    `);
            }
            
            $chatHistory.append($messageDiv);
            this.scrollChatToBottom();
        },
        
        // Add loading message to chat
        addLoadingMessage: function() {
            const $chatHistory = $('#chatHistory');
            const loadingId = 'loading-' + Date.now();
            
            const $loadingMsg = $('<div>')
                .attr('id', loadingId)
                .addClass('bot-message loading-message fade-in')
                .html(`
                    <div class="message-header">
                        <strong>🤖 Assistant:</strong>
                    </div>
                    <div class="message-content"><em>Processing your query...</em></div>
                `);
            
            $chatHistory.append($loadingMsg);
            this.scrollChatToBottom();
            
            return loadingId;
        },
        
        // Remove loading message from chat
        removeLoadingMessage: function(loadingId) {
            $('#' + loadingId).remove();
        },
        
        // Scroll chat to bottom
        scrollChatToBottom: function() {
            const $chatHistory = $('#chatHistory');
            $chatHistory.scrollTop($chatHistory[0].scrollHeight);
        },
        
        // Clear chat history
        clearChat: function() {
            App.conversationHistory = [];
            App.updateChatHistory([{
                type: 'system',
                message: '💬 Chat cleared. Choose your query type and ask new questions!'
            }]);
            App.hideStatus();
            
            // Clear conversation history on server
            $.ajax({
                url: '/clear_conversation',
                method: 'POST',
                contentType: 'application/json'
            });
        },
        
        // Update chat history display
        updateChatHistory: function(messages) {
            const $chatHistory = $('#chatHistory');
            $chatHistory.empty();
            
            messages.forEach(function(msg) {
                if (msg.type === 'system') {
                    $chatHistory.append(
                        $('<div>')
                            .addClass('system-message fade-in')
                            .html(`<div class="message-content">${msg.message}</div>`)
                    );
                }
            });
            
            this.scrollChatToBottom();
        },
        
        // Show debug information
        showDebugInfo: function(debugInfo) {
            const $debugSection = $('#debugSection');
            const $debugContainer = $('#debugContainer');
            
            let debugHtml = '<h4>🔧 Debug Information</h4>';
            
            if (debugInfo.query_steps) {
                debugHtml += `<div class="debug-item"><strong>Query Steps:</strong> ${debugInfo.query_steps}</div>`;
            }
            
            if (debugInfo.processing_steps && debugInfo.processing_steps.length > 0) {
                debugHtml += `<div class="debug-item"><strong>Processing Steps:</strong><ul>`;
                debugInfo.processing_steps.forEach(step => {
                    debugHtml += `<li>${step}</li>`;
                });
                debugHtml += `</ul></div>`;
            }
            
            if (debugInfo.system_type) {
                debugHtml += `<div class="debug-item"><strong>System Type:</strong> ${debugInfo.system_type}</div>`;
            }
            
            $debugContainer.html(debugHtml);
            $debugSection.show().addClass('fade-in');
        },
        
        // Format response text for better display
        formatResponse: function(text) {
            if (!text || typeof text !== 'string') {
                return this.escapeHtml(text || '');
            }
            
            // First escape HTML to prevent injection
            let escaped = this.escapeHtml(text);
            
            // Split into paragraphs and format
            let paragraphs = escaped.split('\n\n').filter(p => p.trim());
            
            let formatted = paragraphs.map(paragraph => {
                paragraph = paragraph.trim();
                
                // Handle numbered steps
                if (/^\d+[\.\)]\s+/.test(paragraph) || /^Step\s+\d+:/i.test(paragraph)) {
                    return this.formatNumberedSteps(paragraph);
                }
                
                // Handle bullet points
                if (/^[•\-\*]\s+/.test(paragraph) || paragraph.includes('\n• ') || paragraph.includes('\n- ')) {
                    return this.formatBulletPoints(paragraph);
                }
                
                // Regular paragraph
                return `<p>${paragraph.replace(/\n/g, '<br>')}</p>`;
            }).join('');
            
            return formatted;
        },
        
        // Format numbered steps
        formatNumberedSteps: function(text) {
            let steps = text.split(/(?=\d+[\.\)]\s+|Step\s+\d+:)/i).filter(s => s.trim());
            
            if (steps.length <= 1) {
                return `<p>${text.replace(/\n/g, '<br>')}</p>`;
            }
            
            let html = '<ol class="formatted-steps">';
            steps.forEach(step => {
                step = step.trim();
                if (step) {
                    let cleanStep = step.replace(/^\d+[\.\)]\s+|^Step\s+\d+:\s*/i, '');
                    if (cleanStep) {
                        html += `<li>${cleanStep.replace(/\n/g, '<br>')}</li>`;
                    }
                }
            });
            html += '</ol>';
            return html;
        },
        
        // Format bullet points
        formatBulletPoints: function(text) {
            let items = text.split(/(?=^[•\-\*]\s+)/m).filter(s => s.trim());
            
            if (items.length <= 1) {
                items = text.split(/\n[•\-\*]\s+/).filter(s => s.trim());
                if (items.length <= 1) {
                    return `<p>${text.replace(/\n/g, '<br>')}</p>`;
                }
            }
            
            let html = '<ul class="formatted-bullets">';
            items.forEach((item, index) => {
                item = item.trim();
                if (item) {
                    let cleanItem = item.replace(/^[•\-\*]\s+/, '');
                    if (cleanItem || index === 0) {
                        html += `<li>${(cleanItem || item).replace(/\n/g, '<br>')}</li>`;
                    }
                }
            });
            html += '</ul>';
            return html;
        },
        
        // Utility function to escape HTML
        escapeHtml: function(text) {
            const div = document.createElement('div');
            div.textContent = text;
            return div.innerHTML;
        }
    };
    
    // Initialize the application
    App.init();
    
    // Make App globally available for debugging
    window.LabApp = App;
});
