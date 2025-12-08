// DataScienve LLM Chat Model App - JavaScript

let isTyping = false;
let currentSessionId = null;
let chatHistory = [];

// Logout function
function logout() {
    if (confirm(currentLang === 'ar' ? 'هل تريد تسجيل الخروج؟' : 'Do you want to logout?')) {
        window.location.href = '/logout';
    }
}

// Initialize
document.addEventListener('DOMContentLoaded', function () {
    // Set initial language
    currentLang = initialLang || localStorage.getItem('preferredLanguage') || 'ar';

    // Load chat history
    loadChatHistory();

    // Auto-resize textarea
    const textarea = document.getElementById('messageInput');
    if (textarea) {
        textarea.addEventListener('input', function () {
            this.style.height = 'auto';
            this.style.height = Math.min(this.scrollHeight, 150) + 'px';
        });

        // Focus on input
        textarea.focus();
    }

    // Update translations
    updateAllTranslations();
});

// Update all translations
function updateAllTranslations() {
    document.querySelectorAll('[data-i18n]').forEach(el => {
        const key = el.getAttribute('data-i18n');
        if (el.tagName === 'INPUT' || el.tagName === 'TEXTAREA') {
            el.placeholder = t(key);
        } else {
            el.textContent = t(key);
        }
    });
}

// Handle Enter key
function handleKeyPress(event) {
    if (event.key === 'Enter' && !event.shiftKey) {
        event.preventDefault();
        sendMessage(event);
    }
}

// Send suggestion
function sendSuggestion(text) {
    document.getElementById('messageInput').value = text;
    sendMessage(new Event('submit'));
}

// Send message
async function sendMessage(event) {
    event.preventDefault();

    if (isTyping) return;

    const input = document.getElementById('messageInput');
    const message = input.value.trim();

    if (!message) return;

    // Hide welcome message
    const welcomeMsg = document.getElementById('welcomeMessage');
    if (welcomeMsg) {
        welcomeMsg.style.display = 'none';
    }

    // Add user message
    addMessage(message, 'user');

    // Clear input
    input.value = '';
    input.style.height = 'auto';

    // Disable send button
    isTyping = true;
    updateSendButton(false);

    // Add typing indicator
    const typingDiv = addTypingIndicator();

    try {
        const response = await fetch('/chat', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                message: message,
                current_session_id: currentSessionId
            })
        });

        const data = await response.json();

        // Remove typing indicator
        typingDiv.remove();

        if (data.error) {
            addMessage(t('errorOccurred') + ' ' + data.error, 'bot');
        } else {
            addMessage(data.response, 'bot');

            // Update current session ID
            if (data.current_session_id) {
                currentSessionId = data.current_session_id;
            }

            // Reload history
            loadChatHistory();
        }
    } catch (error) {
        // Remove typing indicator
        typingDiv.remove();
        addMessage(t('errorConnection'), 'bot');
        console.error('Error:', error);
    } finally {
        isTyping = false;
        updateSendButton(true);
    }
}

// Add message to chat
function addMessage(text, sender) {
    const chatContainer = document.getElementById('chatContainer');

    const messageDiv = document.createElement('div');
    messageDiv.className = `message ${sender}-message`;

    const avatar = document.createElement('div');
    avatar.className = 'message-avatar';

    if (sender === 'user') {
        avatar.textContent = '👤';
    } else {
        avatar.textContent = 'AI';
    }

    const content = document.createElement('div');
    content.className = 'message-content';
    content.textContent = text;

    messageDiv.appendChild(avatar);
    messageDiv.appendChild(content);

    chatContainer.appendChild(messageDiv);

    // Scroll to bottom
    chatContainer.scrollTop = chatContainer.scrollHeight;
}

// Add typing indicator
function addTypingIndicator() {
    const chatContainer = document.getElementById('chatContainer');

    const messageDiv = document.createElement('div');
    messageDiv.className = 'message bot-message';
    messageDiv.id = 'typingIndicator';

    const avatar = document.createElement('div');
    avatar.className = 'message-avatar';
    avatar.textContent = 'AI';

    const content = document.createElement('div');
    content.className = 'message-content';

    const typingDiv = document.createElement('div');
    typingDiv.className = 'typing-indicator';
    typingDiv.innerHTML = `
        <div class="typing-dot"></div>
        <div class="typing-dot"></div>
        <div class="typing-dot"></div>
    `;

    content.appendChild(typingDiv);
    messageDiv.appendChild(avatar);
    messageDiv.appendChild(content);

    chatContainer.appendChild(messageDiv);
    chatContainer.scrollTop = chatContainer.scrollHeight;

    return messageDiv;
}

// Update send button state
function updateSendButton(enabled) {
    const sendBtn = document.getElementById('sendBtn');
    sendBtn.disabled = !enabled;
}

// Load chat history
async function loadChatHistory() {
    try {
        const response = await fetch('/get-history');
        const data = await response.json();

        chatHistory = data.sessions || [];
        updateHistoryUI();
    } catch (error) {
        console.error('Error loading history:', error);
    }
}

// Update history UI
function updateHistoryUI() {
    const historyList = document.getElementById('historyList');
    if (!historyList) return;

    historyList.innerHTML = '';

    if (chatHistory.length === 0) {
        const noHistory = document.createElement('div');
        noHistory.className = 'no-history';
        noHistory.setAttribute('data-i18n', 'noHistory');
        noHistory.textContent = t('noHistory');
        historyList.appendChild(noHistory);
        return;
    }

    chatHistory.forEach((session) => {
        const historyItem = document.createElement('div');
        historyItem.className = 'history-item';
        if (session.id === currentSessionId) {
            historyItem.classList.add('active');
        }

        historyItem.onclick = () => loadSession(session.id);

        const itemContent = document.createElement('div');
        itemContent.className = 'history-item-content';

        const title = document.createElement('div');
        title.className = 'history-item-title';
        title.textContent = session.title;

        const time = document.createElement('div');
        time.className = 'history-item-time';
        time.textContent = formatTime(session.updated_at);

        itemContent.appendChild(title);
        itemContent.appendChild(time);

        const deleteBtn = document.createElement('button');
        deleteBtn.className = 'delete-session-btn';
        deleteBtn.innerHTML = `
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <path d="M3 6h18M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"/>
            </svg>
        `;
        deleteBtn.onclick = (e) => {
            e.stopPropagation();
            deleteSession(session.id);
        };
        deleteBtn.title = t('delete');

        historyItem.appendChild(itemContent);
        historyItem.appendChild(deleteBtn);

        historyList.appendChild(historyItem);
    });
}

// Format time
function formatTime(isoString) {
    const date = new Date(isoString);
    const now = new Date();
    const diffMs = now - date;
    const diffMins = Math.floor(diffMs / 60000);
    const diffHours = Math.floor(diffMs / 3600000);
    const diffDays = Math.floor(diffMs / 86400000);

    if (diffMins < 1) return t('justNow');
    if (diffMins === 1) return t('minuteAgo');
    if (diffMins < 60) return t('minutesAgo', { n: diffMins });
    if (diffHours === 1) return t('hourAgo');
    if (diffHours < 24) return t('hoursAgo', { n: diffHours });
    if (diffDays === 1) return t('dayAgo');
    return t('daysAgo', { n: diffDays });
}

// Load session
async function loadSession(sessionId) {
    try {
        const response = await fetch(`/get-session/${sessionId}`);
        const data = await response.json();

        if (data.session) {
            currentSessionId = sessionId;

            // Clear chat container
            const chatContainer = document.getElementById('chatContainer');
            chatContainer.innerHTML = '';

            // Hide welcome message
            const welcomeMsg = document.getElementById('welcomeMessage');
            if (welcomeMsg) {
                welcomeMsg.style.display = 'none';
            }

            // Load all messages
            data.session.messages.forEach(msg => {
                addMessage(msg.user, 'user');
                addMessage(msg.bot, 'bot');
            });

            // Update UI
            updateHistoryUI();
        }
    } catch (error) {
        console.error('Error loading session:', error);
    }
}

// Delete session
async function deleteSession(sessionId) {
    if (!confirm(t('confirmDelete'))) {
        return;
    }

    try {
        const response = await fetch(`/delete-session/${sessionId}`, {
            method: 'DELETE'
        });

        if (response.ok) {
            // If deleted current session, reset
            if (sessionId === currentSessionId) {
                newChat();
            }

            // Reload history
            loadChatHistory();
        }
    } catch (error) {
        console.error('Error deleting session:', error);
    }
}

// Clear all history
async function clearAllHistory() {
    if (!confirm(t('confirmDeleteAll'))) {
        return;
    }

    try {
        const response = await fetch('/clear-all-history', {
            method: 'POST'
        });

        if (response.ok) {
            // Reset current session
            newChat();

            // Reload history
            loadChatHistory();
        }
    } catch (error) {
        console.error('Error clearing history:', error);
    }
}

// New chat session
async function newChat() {
    if (currentSessionId && chatHistory.length > 0) {
        if (!confirm(t('confirmNewChat'))) {
            return;
        }
    }

    try {
        const response = await fetch('/new-session', { method: 'POST' });
        const data = await response.json();

        // Reset current session
        currentSessionId = null;

        // Clear chat container
        const chatContainer = document.getElementById('chatContainer');
        chatContainer.innerHTML = '';

        // Show welcome message
        const welcomeMsg = document.createElement('div');
        welcomeMsg.className = 'welcome-message';
        welcomeMsg.id = 'welcomeMessage';
        welcomeMsg.innerHTML = `
            <div class="orb-container">
                <div class="orb"></div>
                <div class="orb-glow"></div>
            </div>
            <div class="welcome-features">
                <div class="feature-item" data-i18n="feature1">${t('feature1')}</div>
                <div class="feature-item" data-i18n="feature2">${t('feature2')}</div>
            </div>
            <div class="suggestions-label" data-i18n="suggestionsLabel">${t('suggestionsLabel')}</div>
            <div class="suggestions">
                <button class="suggestion-btn" onclick="sendSuggestion('${t('suggestion1')}')">
                    <span data-i18n="suggestion1">${t('suggestion1')}</span>
                </button>
                <button class="suggestion-btn" onclick="sendSuggestion('${t('suggestion2')}')">
                    <span data-i18n="suggestion2">${t('suggestion2')}</span>
                </button>
            </div>
        `;
        chatContainer.appendChild(welcomeMsg);

        // Update history UI
        updateHistoryUI();

    } catch (error) {
        console.error('Error:', error);
        alert('حدث خطأ أثناء بدء محادثة جديدة');
    }
}

// Toggle sidebar on mobile
function toggleSidebar() {
    const sidebar = document.querySelector('.sidebar');
    sidebar.classList.toggle('open');
}
