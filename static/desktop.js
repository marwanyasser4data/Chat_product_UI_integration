// Desktop OS JavaScript

// State Management
const windowState = {
    activeWindow: null,
    openWindows: [],
    zIndex: 10
};

// Initialize on DOM Load
document.addEventListener('DOMContentLoaded', function() {
    initClock();
    initWindowDragging();
    initKeyboardShortcuts();
    initClickOutside();
    applyTranslations();
    loadChatSessions();
    renderChatHistory();
    updateWidgetStats();
    loadCustomWidgets();
});

// ============ Window Management ============

function toggleWindow(windowId) {
    const window = document.getElementById(windowId);
    if (!window) return;
    
    if (window.style.display === 'none') {
        openWindow(windowId);
    } else {
        closeWindow(windowId);
    }
}

function openWindow(windowId) {
    const window = document.getElementById(windowId);
    if (!window) return;
    
    window.style.display = 'flex';
    window.classList.remove('closing');
    bringToFront(windowId);
    updateTaskbarButton(windowId, true);
    
    if (!windowState.openWindows.includes(windowId)) {
        windowState.openWindows.push(windowId);
    }
}

function closeWindow(windowId) {
    const window = document.getElementById(windowId);
    if (!window) return;
    
    window.classList.add('closing');
    
    setTimeout(() => {
        window.style.display = 'none';
        window.classList.remove('closing');
        updateTaskbarButton(windowId, false);
        
        const index = windowState.openWindows.indexOf(windowId);
        if (index > -1) {
            windowState.openWindows.splice(index, 1);
        }
    }, 200);
}

function minimizeWindow(windowId) {
    const window = document.getElementById(windowId);
    if (!window) return;
    
    window.style.display = 'none';
    updateTaskbarButton(windowId, false);
}

function toggleMaximize(windowId) {
    const window = document.getElementById(windowId);
    if (!window) return;
    
    window.classList.toggle('maximized');
}

function bringToFront(windowId) {
    windowState.zIndex++;
    const window = document.getElementById(windowId);
    if (window) {
        window.style.zIndex = windowState.zIndex;
        windowState.activeWindow = windowId;
    }
}

function updateTaskbarButton(windowId, isActive) {
    const btn = document.querySelector(`[data-window="${windowId}"]`);
    if (btn) {
        btn.classList.toggle('active', isActive);
    }
}

// ============ Start Menu ============

function toggleStartMenu() {
    const menu = document.getElementById('startMenu');
    menu.classList.toggle('show');
}

function closeStartMenu() {
    const menu = document.getElementById('startMenu');
    menu.classList.remove('show');
}

// ============ User Menu ============

function toggleUserMenu() {
    const dropdown = document.getElementById('userDropdown');
    dropdown.classList.toggle('show');
}

// ============ Clock ============

function initClock() {
    updateClock();
    setInterval(updateClock, 1000);
}

function updateClock() {
    const now = new Date();
    
    // Taskbar time
    const timeStr = now.toLocaleTimeString('ar-SA', { 
        hour: '2-digit', 
        minute: '2-digit',
        hour12: false 
    });
    const dateStr = now.toLocaleDateString('ar-SA', { 
        day: 'numeric', 
        month: 'numeric' 
    });
    
    const taskbarTime = document.getElementById('taskbarTime');
    const taskbarDate = document.getElementById('taskbarDate');
    if (taskbarTime) taskbarTime.textContent = timeStr;
    if (taskbarDate) taskbarDate.textContent = dateStr;
    
    // Header bar clock
    const headerTime = document.getElementById('headerTime');
    const headerDate = document.getElementById('headerDate');
    if (headerTime) headerTime.textContent = timeStr;
    if (headerDate) {
        headerDate.textContent = now.toLocaleDateString('ar-SA', { 
            day: 'numeric', 
            month: 'short',
            year: 'numeric'
        });
    }
    
    // Widget clock
    const clockTime = document.getElementById('clockTime');
    const clockDate = document.getElementById('clockDate');
    if (clockTime) clockTime.textContent = timeStr;
    if (clockDate) {
        clockDate.textContent = now.toLocaleDateString('ar-SA', { 
            weekday: 'long',
            day: 'numeric', 
            month: 'long' 
        });
    }
}

// ============ Language ============

function setLanguage(lang) {
    fetch('/set_language', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ language: lang })
    }).then(response => response.json())
    .then(data => {
        if (data.success) {
            // Update localStorage
            localStorage.setItem('preferredLanguage', lang);
            // Reload page to apply changes
            window.location.reload();
        }
    }).catch(err => {
        console.error('Language change error:', err);
        window.location.reload();
    });
}

function applyTranslations() {
    const lang = document.documentElement.lang || 'ar';
    if (typeof translations === 'undefined') return;
    
    const trans = translations[lang] || translations['ar'];
    
    // Update all elements with data-i18n attribute
    document.querySelectorAll('[data-i18n]').forEach(el => {
        const key = el.getAttribute('data-i18n');
        if (trans[key]) {
            el.textContent = trans[key];
        }
    });
    
    // Update placeholders
    document.querySelectorAll('[data-i18n-placeholder]').forEach(el => {
        const key = el.getAttribute('data-i18n-placeholder');
        if (trans[key]) {
            el.placeholder = trans[key];
        }
    });
    
    // Update titles
    document.querySelectorAll('[data-i18n-title]').forEach(el => {
        const key = el.getAttribute('data-i18n-title');
        if (trans[key]) {
            el.title = trans[key];
        }
    });
}

function toggleLanguage() {
    const currentLang = document.getElementById('currentLang').textContent;
    const newLang = currentLang === 'ع' ? 'en' : 'ar';
    setLanguage(newLang);
}

// ============ Window Dragging ============

function initWindowDragging() {
    document.querySelectorAll('.window-header').forEach(header => {
        let isDragging = false;
        let startX, startY, startLeft, startTop;
        
        header.addEventListener('mousedown', function(e) {
            if (e.target.closest('.window-controls')) return;
            
            const window = header.closest('.app-window');
            if (window.classList.contains('maximized')) return;
            
            isDragging = true;
            bringToFront(window.id);
            
            const rect = window.getBoundingClientRect();
            startX = e.clientX;
            startY = e.clientY;
            startLeft = rect.left;
            startTop = rect.top;
            
            window.style.transition = 'none';
        });
        
        document.addEventListener('mousemove', function(e) {
            if (!isDragging) return;
            
            const window = header.closest('.app-window');
            const deltaX = e.clientX - startX;
            const deltaY = e.clientY - startY;
            
            window.style.left = startLeft + deltaX + 'px';
            window.style.top = startTop + deltaY + 'px';
            window.style.transform = 'none';
        });
        
        document.addEventListener('mouseup', function() {
            if (isDragging) {
                isDragging = false;
                const window = header.closest('.app-window');
                window.style.transition = '';
            }
        });
    });
}

// ============ Keyboard Shortcuts ============

function initKeyboardShortcuts() {
    document.addEventListener('keydown', function(e) {
        // Escape to close active window
        if (e.key === 'Escape') {
            if (windowState.activeWindow) {
                closeWindow(windowState.activeWindow);
            }
            closeStartMenu();
        }
        
        // Enter to send message
        if (e.key === 'Enter' && !e.shiftKey) {
            const input = document.getElementById('messageInput');
            if (document.activeElement === input) {
                e.preventDefault();
                sendMessage();
            }
        }
    });
}

// ============ Click Outside ============

function initClickOutside() {
    document.addEventListener('click', function(e) {
        // Close start menu when clicking outside
        const startMenu = document.getElementById('startMenu');
        const startBtn = document.querySelector('.start-btn');
        if (!startMenu.contains(e.target) && !startBtn.contains(e.target)) {
            closeStartMenu();
        }
        
        // Close user dropdown when clicking outside
        const userDropdown = document.getElementById('userDropdown');
        const userBtn = document.querySelector('.user-btn');
        if (userDropdown && !userDropdown.contains(e.target) && !userBtn.contains(e.target)) {
            userDropdown.classList.remove('show');
        }
    });
}

// ============ Chat Functions ============

let conversationHistory = [];
let currentSessionId = null;
let chatSessions = [];

// Global variables for streaming control
let activeEventSource = null;
let isStreaming = false;

// Load chat sessions from localStorage
function loadChatSessions() {
    const saved = localStorage.getItem('chatSessions');
    if (saved) {
        chatSessions = JSON.parse(saved);
        renderChatHistory();
    }
}

// Save chat sessions to localStorage
function saveChatSessions() {
    localStorage.setItem('chatSessions', JSON.stringify(chatSessions));
}

// Render chat history in sidebar
function renderChatHistory() {
    const historyList = document.getElementById('chatHistoryList');
    if (!historyList) return;
    
    if (chatSessions.length === 0) {
        historyList.innerHTML = '<div class="no-history">لا توجد محادثات سابقة</div>';
        return;
    }
    
    historyList.innerHTML = chatSessions.map((session, index) => `
        <div class="history-item ${session.id === currentSessionId ? 'active' : ''}" 
             onclick="loadSession('${session.id}')" data-session="${session.id}">
            <div class="history-item-content">
                <span class="history-title">${session.title || 'محادثة جديدة'}</span>
                <span class="history-date">${formatDate(session.timestamp)}</span>
            </div>
            <button class="history-delete" onclick="event.stopPropagation(); deleteSession('${session.id}')">
                <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                    <path d="M18 6L6 18M6 6l12 12"/>
                </svg>
            </button>
        </div>
    `).join('');
}

// Format date for display
function formatDate(timestamp) {
    const date = new Date(timestamp);
    const now = new Date();
    const diff = now - date;
    
    if (diff < 60000) return 'الآن';
    if (diff < 3600000) return `منذ ${Math.floor(diff / 60000)} دقيقة`;
    if (diff < 86400000) return `منذ ${Math.floor(diff / 3600000)} ساعة`;
    return date.toLocaleDateString('ar-SA');
}

// Create new chat session
function newChat() {
    // Save current session if it has messages
    if (currentSessionId && conversationHistory.length > 0) {
        saveCurrentSession();
    }
    
    conversationHistory = [];
    currentSessionId = generateSessionId();
    
    // Create new session
    const newSession = {
        id: currentSessionId,
        title: 'محادثة جديدة',
        timestamp: Date.now(),
        messages: []
    };
    chatSessions.unshift(newSession);
    saveChatSessions();
    renderChatHistory();
    
    const messagesContainer = document.getElementById('chatMessages');
    const welcomeScreen = document.getElementById('welcomeScreen');
    
    // Clear messages and show welcome screen
    if (messagesContainer && welcomeScreen) {
        messagesContainer.innerHTML = '';
        messagesContainer.appendChild(welcomeScreen);
        welcomeScreen.style.display = 'flex';
    }
    
    const input = document.getElementById('messageInput');
    if (input) input.value = '';
}

// Save current session
function saveCurrentSession() {
    const session = chatSessions.find(s => s.id === currentSessionId);
    if (session) {
        session.messages = conversationHistory;
        if (conversationHistory.length > 0) {
            // Use first user message as title
            const firstUserMsg = conversationHistory.find(m => m.type === 'user');
            if (firstUserMsg) {
                session.title = firstUserMsg.text.substring(0, 30) + (firstUserMsg.text.length > 30 ? '...' : '');
            }
        }
        saveChatSessions();
        renderChatHistory();
    }
}

// Load a session
function loadSession(sessionId) {
    // Save current session first
    if (currentSessionId && conversationHistory.length > 0) {
        saveCurrentSession();
    }
    
    const session = chatSessions.find(s => s.id === sessionId);
    if (!session) return;
    
    currentSessionId = sessionId;
    conversationHistory = session.messages || [];
    
    // Render messages
    const messagesContainer = document.getElementById('chatMessages');
    const welcomeScreen = document.getElementById('welcomeScreen');
    
    if (!messagesContainer) return;
    
    messagesContainer.innerHTML = '';
    
    if (conversationHistory.length === 0) {
        if (welcomeScreen) {
            messagesContainer.appendChild(welcomeScreen);
            welcomeScreen.style.display = 'flex';
        }
    } else {
        if (welcomeScreen) welcomeScreen.style.display = 'none';
        conversationHistory.forEach(msg => {
            addMessageToDOM(msg.text, msg.type);
        });
    }
    
    renderChatHistory();
}

// Delete a session
function deleteSession(sessionId) {
    chatSessions = chatSessions.filter(s => s.id !== sessionId);
    saveChatSessions();
    
    if (sessionId === currentSessionId) {
        if (chatSessions.length > 0) {
            loadSession(chatSessions[0].id);
        } else {
            newChat();
        }
    } else {
        renderChatHistory();
    }
}

function sendMessage() {
    const input = document.getElementById('messageInput');
    const message = input.value.trim();
    
    if (!message) return;
    
    // Hide welcome screen
    const welcomeScreen = document.getElementById('welcomeScreen');
    if (welcomeScreen) {
        welcomeScreen.style.display = 'none';
    }
    
    // Add user message to history first
    conversationHistory.push({ text: message, type: 'user', timestamp: Date.now() });
    
    // Add user message to DOM
    addMessageToDOM(message, 'user');
    input.value = '';
    
    // Show typing indicator
    showTypingIndicator();
    
    // Change button to stop icon
    toggleSendButton(true);
    isStreaming = true;
    
    // Always use streaming for real-time response
    const url = '/stream-chat?' + new URLSearchParams({
        message: message,
        current_session_id: currentSessionId || ''
    });
    
    const eventSource = new EventSource(url);
    activeEventSource = eventSource;
    
    let botMessageDiv = null;
    let botContent = null;
    let fullResponse = '';
    let hasError = false;
    
    eventSource.onmessage = function(event) {
        // Hide typing indicator on first chunk
        if (!botMessageDiv) {
            hideTypingIndicator();
        }
        
        const chunk = event.data;
        fullResponse += chunk;
        
        // Create bot message div if it doesn't exist
        if (!botMessageDiv) {
            const container = document.getElementById('chatMessages');
            botMessageDiv = document.createElement('div');
            botMessageDiv.className = 'message bot';
            
            const avatar = document.createElement('div');
            avatar.className = 'message-avatar';
            avatar.textContent = 'AI';
            
            botContent = document.createElement('div');
            botContent.className = 'message-content';
            
            botMessageDiv.appendChild(avatar);
            botMessageDiv.appendChild(botContent);
            container.appendChild(botMessageDiv);
        }
        
        // Update content with streaming text
        botContent.textContent = fullResponse;
        
        // Scroll to bottom
        const container = document.getElementById('chatMessages');
        container.scrollTop = container.scrollHeight;
    };
    
    eventSource.onerror = function(error) {
        hideTypingIndicator();
        toggleSendButton(false);
        isStreaming = false;
        activeEventSource = null;
        hasError = true;
        eventSource.close();
        
        console.error('Streaming error:', error);
        
        if (!fullResponse) {
            // No response received, show error message
            addMessageToDOM('حدث خطأ في الاتصال. يرجى المحاولة مرة أخرى.', 'bot');
            conversationHistory.push({ text: 'حدث خطأ في الاتصال', type: 'bot', timestamp: Date.now() });
        } else {
            // Partial response received, save it
            conversationHistory.push({ text: fullResponse, type: 'bot', timestamp: Date.now() });
        }
        
        saveCurrentSession();
    };
    
    eventSource.addEventListener('end', function(event) {
        eventSource.close();
        toggleSendButton(false);
        isStreaming = false;
        activeEventSource = null;
        
        if (!hasError && fullResponse) {
            // Save complete response to history
            conversationHistory.push({ text: fullResponse, type: 'bot', timestamp: Date.now() });
            saveCurrentSession();
        }
    });
    
    // Timeout safety - close after 5 minutes
    setTimeout(() => {
        if (eventSource.readyState !== EventSource.CLOSED) {
            eventSource.close();
            toggleSendButton(false);
            isStreaming = false;
            activeEventSource = null;
            if (fullResponse) {
                conversationHistory.push({ text: fullResponse, type: 'bot', timestamp: Date.now() });
                saveCurrentSession();
            }
        }
    }, 300000);
}

// Toggle send button between send and stop icons
function toggleSendButton(showStop) {
    const sendIcon = document.getElementById('sendIcon');
    const stopIcon = document.getElementById('stopIcon');
    
    if (sendIcon && stopIcon) {
        if (showStop) {
            sendIcon.style.display = 'none';
            stopIcon.style.display = 'block';
        } else {
            sendIcon.style.display = 'block';
            stopIcon.style.display = 'none';
        }
    }
}

// Handle send button click - either send or stop
function handleSendButton() {
    if (isStreaming && activeEventSource) {
        // Stop streaming
        activeEventSource.close();
        activeEventSource = null;
        isStreaming = false;
        toggleSendButton(false);
        hideTypingIndicator();
    } else {
        // Send message
        sendMessage();
    }
}

function sendQuickMessage(message) {
    document.getElementById('messageInput').value = message;
    sendMessage();
}

// Clear all chat history
function clearHistory() {
    if (confirm('هل أنت متأكد من مسح جميع المحادثات؟')) {
        chatSessions = [];
        conversationHistory = [];
        currentSessionId = null;
        saveChatSessions();
        renderChatHistory();
        
        // Reset to welcome screen
        const messagesContainer = document.getElementById('chatMessages');
        const welcomeScreen = document.getElementById('welcomeScreen');
        if (messagesContainer && welcomeScreen) {
            messagesContainer.innerHTML = '';
            messagesContainer.appendChild(welcomeScreen);
            welcomeScreen.style.display = 'flex';
        }
        
        // Update stats
        updateWidgetStats();
    }
}

// Update widget statistics
function updateWidgetStats() {
    const totalChats = document.getElementById('totalChats');
    const todayChats = document.getElementById('todayChats');
    const totalMessages = document.getElementById('totalMessages');
    
    if (totalChats) totalChats.textContent = chatSessions.length;
    if (todayChats) {
        const today = new Date().toDateString();
        const todayCount = chatSessions.filter(s => new Date(s.timestamp).toDateString() === today).length;
        todayChats.textContent = todayCount;
    }
    if (totalMessages) {
        let msgCount = 0;
        chatSessions.forEach(s => { msgCount += (s.messages?.length || 0); });
        totalMessages.textContent = msgCount > 999 ? (msgCount/1000).toFixed(1) + 'K' : msgCount;
    }
}

// Add message to DOM only (no save)
function addMessageToDOM(text, type) {
    const container = document.getElementById('chatMessages');
    if (!container) return;
    
    const messageDiv = document.createElement('div');
    messageDiv.className = `message ${type}`;
    
    const avatar = document.createElement('div');
    avatar.className = 'message-avatar';
    avatar.textContent = type === 'user' ? 'أ' : 'AI';
    
    const content = document.createElement('div');
    content.className = 'message-content';
    content.textContent = text;
    
    messageDiv.appendChild(avatar);
    messageDiv.appendChild(content);
    container.appendChild(messageDiv);
    
    // Scroll to bottom
    container.scrollTop = container.scrollHeight;
}

// Add message and save to history
function addMessage(text, type) {
    // Add to DOM
    addMessageToDOM(text, type);
    
    // Save to conversation history
    conversationHistory.push({ text, type, timestamp: Date.now() });
    
    // Update session
    saveCurrentSession();
}

function showTypingIndicator() {
    const container = document.getElementById('chatMessages');
    
    const indicator = document.createElement('div');
    indicator.className = 'message bot typing-indicator';
    indicator.id = 'typingIndicator';
    indicator.innerHTML = `
        <div class="message-avatar">AI</div>
        <div class="message-content">
            <div class="typing-dots">
                <span></span><span></span><span></span>
            </div>
        </div>
    `;
    
    container.appendChild(indicator);
    container.scrollTop = container.scrollHeight;
}

function hideTypingIndicator() {
    const indicator = document.getElementById('typingIndicator');
    if (indicator) {
        indicator.remove();
    }
}

function generateSessionId() {
    currentSessionId = 'session_' + Date.now() + '_' + Math.random().toString(36).substr(2, 9);
    return currentSessionId;
}

// ============ Utility Functions ============

function attachFile() {
    // Create file input
    const input = document.createElement('input');
    input.type = 'file';
    input.accept = 'image/*,.pdf,.doc,.docx,.txt';
    input.onchange = function(e) {
        const file = e.target.files[0];
        if (file) {
            // Handle file upload
            console.log('File selected:', file.name);
        }
    };
    input.click();
}

function voiceInput() {
    // Voice input functionality
    if ('webkitSpeechRecognition' in window) {
        const recognition = new webkitSpeechRecognition();
        recognition.lang = document.documentElement.lang === 'ar' ? 'ar-SA' : 'en-US';
        recognition.onresult = function(event) {
            const text = event.results[0][0].transcript;
            document.getElementById('messageInput').value = text;
        };
        recognition.start();
    } else {
        alert('المتصفح لا يدعم الإدخال الصوتي');
    }
}

// ============ Custom Widgets ============

async function loadCustomWidgets() {
    try {
        // Get ALL widgets (not just active) to know which ones to hide
        const response = await fetch('/api/widgets');
        const data = await response.json();
        const allWidgets = data.widgets || [];
        
        // Update default widget visibility based on active state
        updateDefaultWidgets(allWidgets);
        
        // Load only active custom widgets
        const activeCustomWidgets = allWidgets.filter(w => w.type === 'custom' && w.html_content && w.active);
        renderCustomWidgets(activeCustomWidgets);
        
    } catch (error) {
        console.error('Error loading widgets:', error);
    }
}

function updateDefaultWidgets(allWidgets) {
    const defaultWidgetIds = ['ai-models', 'chat-stats', 'system-status', 'quick-actions'];
    
    defaultWidgetIds.forEach(widgetId => {
        const widgetElement = document.querySelector(`[data-widget-id="${widgetId}"]`);
        if (widgetElement) {
            const widgetData = allWidgets.find(w => w.id === widgetId);
            // Hide if widget exists in data and is not active
            if (widgetData && widgetData.active === false) {
                widgetElement.style.display = 'none';
            } else {
                widgetElement.style.display = '';
            }
        }
    });
}

function renderCustomWidgets(widgets) {
    const container = document.getElementById('customWidgetsContainer');
    if (!container) return;
    
    container.innerHTML = widgets.map(widget => `
        <div class="desktop-widget custom-widget" data-widget-id="${widget.id}">
            <div class="widget-header">
                <div class="widget-icon custom-icon">
                    <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                        <rect x="3" y="3" width="7" height="7" rx="1"/>
                        <rect x="14" y="3" width="7" height="7" rx="1"/>
                        <rect x="3" y="14" width="7" height="7" rx="1"/>
                        <circle cx="17.5" cy="17.5" r="3.5"/>
                    </svg>
                </div>
                <span class="widget-title">${widget.name}</span>
            </div>
            <div class="widget-body">
                ${widget.html_content}
            </div>
        </div>
    `).join('');
}

// ============ Advanced Settings ============

const settingsState = {
    aiModel: 'gpt-4o',
    aiProvider: 'openai',
    temperature: 0.7,
    topP: 0.9,
    maxTokens: 2048,
    systemPrompt: 'أنت مساعد ذكاء اصطناعي متقدم. تتحدث العربية بطلاقة وتقدم إجابات دقيقة ومفيدة.',
    expertMode: false,
    showTimestamps: true,
    streamResponses: true,
    markdownEnabled: true,
    codeHighlight: true,
    autoDarkMode: false,
    animationsEnabled: true,
    notificationsEnabled: true,
    soundEnabled: true,
    desktopNotifications: false,
    saveHistory: true,
    clearOnClose: false,
    timezone: 'Asia/Riyadh'
};

// Initialize settings on load
function initSettings() {
    // Load saved settings from localStorage
    const saved = localStorage.getItem('appSettings');
    if (saved) {
        Object.assign(settingsState, JSON.parse(saved));
    }
    
    // Apply settings to UI
    applySettingsToUI();
    
    // Setup event listeners
    setupSettingsEventListeners();
}

// Show settings tab
function showSettingsTab(tabName) {
    // Hide all tabs
    document.querySelectorAll('.settings-tab').forEach(tab => {
        tab.classList.remove('active');
    });
    
    // Remove active from all nav items
    document.querySelectorAll('.settings-nav-item').forEach(item => {
        item.classList.remove('active');
    });
    
    // Show selected tab
    const selectedTab = document.getElementById('tab-' + tabName);
    if (selectedTab) {
        selectedTab.classList.add('active');
    }
    
    // Activate nav item
    const navItems = document.querySelectorAll('.settings-nav-item');
    navItems.forEach(item => {
        if (item.textContent.trim().toLowerCase().includes(tabName) || 
            item.onclick?.toString().includes(tabName)) {
            item.classList.add('active');
        }
    });
    
    // Find the correct nav item by its onclick handler
    document.querySelectorAll('.settings-nav-item').forEach(item => {
        const onclickStr = item.getAttribute('onclick');
        if (onclickStr && onclickStr.includes(`'${tabName}'`)) {
            item.classList.add('active');
        }
    });
}

// Apply settings state to UI elements
function applySettingsToUI() {
    // AI Model
    const modelSelect = document.getElementById('aiModelSelect');
    if (modelSelect) modelSelect.value = settingsState.aiModel;
    
    // AI Provider
    const providerSelect = document.getElementById('aiProvider');
    if (providerSelect) providerSelect.value = settingsState.aiProvider;
    
    // Temperature
    const tempSlider = document.getElementById('temperatureSlider');
    const tempValue = document.getElementById('temperatureValue');
    if (tempSlider) {
        tempSlider.value = settingsState.temperature * 100;
        if (tempValue) tempValue.textContent = settingsState.temperature;
    }
    
    // Top P
    const topPSlider = document.getElementById('topPSlider');
    const topPValue = document.getElementById('topPValue');
    if (topPSlider) {
        topPSlider.value = settingsState.topP * 100;
        if (topPValue) topPValue.textContent = settingsState.topP;
    }
    
    // Max Tokens
    const maxTokensSelect = document.getElementById('maxTokens');
    if (maxTokensSelect) maxTokensSelect.value = settingsState.maxTokens;
    
    // System Prompt
    const systemPrompt = document.getElementById('systemPrompt');
    if (systemPrompt) systemPrompt.value = settingsState.systemPrompt;
    
    // Toggle switches
    const toggles = {
        'autoDarkMode': settingsState.autoDarkMode,
        'animationsEnabled': settingsState.animationsEnabled,
        'expertMode': settingsState.expertMode,
        'showTimestamps': settingsState.showTimestamps,
        'streamResponses': settingsState.streamResponses
    };
    
    Object.entries(toggles).forEach(([id, value]) => {
        const toggle = document.getElementById(id);
        if (toggle) toggle.checked = value;
    });
    
    // Timezone
    const timezoneSelect = document.getElementById('timezoneSelect');
    if (timezoneSelect) timezoneSelect.value = settingsState.timezone;
    
    // Apply animations setting
    if (!settingsState.animationsEnabled) {
        document.body.classList.add('no-animations');
    }
}

// Setup all event listeners for settings
function setupSettingsEventListeners() {
    // Temperature Slider
    const tempSlider = document.getElementById('temperatureSlider');
    if (tempSlider) {
        tempSlider.addEventListener('input', function() {
            const value = (parseInt(this.value) / 100).toFixed(1);
            document.getElementById('temperatureValue').textContent = value;
            settingsState.temperature = parseFloat(value);
            saveSettings();
        });
    }
    
    // Top P Slider
    const topPSlider = document.getElementById('topPSlider');
    if (topPSlider) {
        topPSlider.addEventListener('input', function() {
            const value = (parseInt(this.value) / 100).toFixed(1);
            document.getElementById('topPValue').textContent = value;
            settingsState.topP = parseFloat(value);
            saveSettings();
        });
    }
    
    // AI Model Select
    const modelSelect = document.getElementById('aiModelSelect');
    if (modelSelect) {
        modelSelect.addEventListener('change', function() {
            settingsState.aiModel = this.value;
            saveSettings();
            showSettingsNotification('تم تغيير نموذج الذكاء الاصطناعي');
        });
    }
    
    // AI Provider Select
    const providerSelect = document.getElementById('aiProvider');
    if (providerSelect) {
        providerSelect.addEventListener('change', function() {
            settingsState.aiProvider = this.value;
            saveSettings();
            showSettingsNotification('تم تغيير مزود الخدمة');
        });
    }
    
    // Max Tokens
    const maxTokensSelect = document.getElementById('maxTokens');
    if (maxTokensSelect) {
        maxTokensSelect.addEventListener('change', function() {
            settingsState.maxTokens = parseInt(this.value);
            saveSettings();
        });
    }
    
    // System Prompt
    const systemPrompt = document.getElementById('systemPrompt');
    if (systemPrompt) {
        systemPrompt.addEventListener('change', function() {
            settingsState.systemPrompt = this.value;
            saveSettings();
            showSettingsNotification('تم تحديث تعليمات النظام');
        });
    }
    
    // Timezone
    const timezoneSelect = document.getElementById('timezoneSelect');
    if (timezoneSelect) {
        timezoneSelect.addEventListener('change', function() {
            settingsState.timezone = this.value;
            saveSettings();
        });
    }
    
    // Toggle Switches
    setupToggleListeners();
}

// Setup toggle switch listeners
function setupToggleListeners() {
    const toggleMappings = {
        'autoDarkMode': { key: 'autoDarkMode', action: null },
        'animationsEnabled': { key: 'animationsEnabled', action: toggleAnimations },
        'expertMode': { key: 'expertMode', action: null },
        'showTimestamps': { key: 'showTimestamps', action: null },
        'streamResponses': { key: 'streamResponses', action: null }
    };
    
    Object.entries(toggleMappings).forEach(([id, config]) => {
        const toggle = document.getElementById(id);
        if (toggle) {
            toggle.addEventListener('change', function() {
                settingsState[config.key] = this.checked;
                saveSettings();
                if (config.action) config.action(this.checked);
            });
        }
    });
}

// Save settings to localStorage
function saveSettings() {
    localStorage.setItem('appSettings', JSON.stringify(settingsState));
}

// Toggle animations
function toggleAnimations(enabled) {
    document.body.classList.toggle('no-animations', !enabled);
    showSettingsNotification(enabled ? 'تم تفعيل الحركات' : 'تم إيقاف الحركات');
}

// Show settings notification
function showSettingsNotification(message) {
    // Remove existing notification
    const existing = document.querySelector('.settings-toast');
    if (existing) existing.remove();
    
    const notification = document.createElement('div');
    notification.className = 'settings-toast';
    notification.innerHTML = `
        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <polyline points="20,6 9,17 4,12"/>
        </svg>
        <span>${message}</span>
    `;
    
    document.body.appendChild(notification);
    
    setTimeout(() => notification.classList.add('show'), 10);
    setTimeout(() => {
        notification.classList.remove('show');
        setTimeout(() => notification.remove(), 300);
    }, 2500);
}

// Export Data
function exportData() {
    const exportData = {
        settings: settingsState,
        chatSessions: chatSessions,
        exportDate: new Date().toISOString()
    };
    
    const blob = new Blob([JSON.stringify(exportData, null, 2)], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `ai-chat-backup-${new Date().toISOString().split('T')[0]}.json`;
    a.click();
    URL.revokeObjectURL(url);
    
    showSettingsNotification('تم تصدير البيانات بنجاح');
}

// Import Data
function importData() {
    const input = document.createElement('input');
    input.type = 'file';
    input.accept = '.json';
    input.onchange = function(e) {
        const file = e.target.files[0];
        if (!file) return;
        
        const reader = new FileReader();
        reader.onload = function(e) {
            try {
                const data = JSON.parse(e.target.result);
                
                if (data.settings) {
                    Object.assign(settingsState, data.settings);
                    saveSettings();
                    applySettingsToUI();
                }
                
                if (data.chatSessions) {
                    chatSessions = data.chatSessions;
                    saveChatSessions();
                    renderChatHistory();
                }
                
                showSettingsNotification('تم استيراد البيانات بنجاح');
            } catch (error) {
                showSettingsNotification('فشل في قراءة الملف');
                console.error('Import error:', error);
            }
        };
        reader.readAsText(file);
    };
    input.click();
}


// Clear All Data
function clearAllData() {
    if (confirm('هل أنت متأكد من مسح جميع البيانات؟ هذا الإجراء لا يمكن التراجع عنه.')) {
        // Clear localStorage
        localStorage.removeItem('appSettings');
        localStorage.removeItem('chatSessions');
        
        // Reset state
        chatSessions = [];
        conversationHistory = [];
        currentSessionId = null;
        
        // Reload page
        window.location.reload();
    }
}

// Reset Settings to Default
function resetSettings() {
    if (confirm('هل تريد إعادة تعيين جميع الإعدادات إلى الافتراضية؟')) {
        const defaults = {
            aiModel: 'gpt-4o',
            aiProvider: 'openai',
            temperature: 0.7,
            topP: 0.9,
            maxTokens: 2048,
            systemPrompt: 'أنت مساعد ذكاء اصطناعي متقدم. تتحدث العربية بطلاقة وتقدم إجابات دقيقة ومفيدة.',
            expertMode: false,
            showTimestamps: true,
            streamResponses: true,
            markdownEnabled: true,
            codeHighlight: true,
            autoDarkMode: false,
            animationsEnabled: true,
            notificationsEnabled: true,
            soundEnabled: true,
            desktopNotifications: false,
            saveHistory: true,
            clearOnClose: false,
            timezone: 'Asia/Riyadh'
        };
        
        Object.assign(settingsState, defaults);
        saveSettings();
        applySettingsToUI();
        document.body.classList.remove('no-animations');
        showSettingsNotification('تم إعادة تعيين الإعدادات');
    }
}

// ============ Enhanced Chat Functions ============

// Toggle Chat Search
function toggleChatSearch() {
    const searchBar = document.getElementById('chatSearchBar');
    if (searchBar.style.display === 'none') {
        searchBar.style.display = 'block';
        document.getElementById('chatSearchInput').focus();
    } else {
        searchBar.style.display = 'none';
        document.getElementById('chatSearchInput').value = '';
        clearSearchHighlights();
    }
}

// Search Messages
function searchMessages(query) {
    const resultsCount = document.getElementById('searchResultsCount');
    const messages = document.querySelectorAll('.message .message-content');
    
    clearSearchHighlights();
    
    if (!query.trim()) {
        resultsCount.textContent = '';
        return;
    }
    
    let count = 0;
    messages.forEach(msg => {
        const text = msg.textContent.toLowerCase();
        if (text.includes(query.toLowerCase())) {
            count++;
            // Highlight matching text
            const regex = new RegExp(`(${query})`, 'gi');
            msg.innerHTML = msg.textContent.replace(regex, '<mark class="search-highlight">$1</mark>');
        }
    });
    
    resultsCount.textContent = count > 0 ? `${count} نتيجة` : 'لا توجد نتائج';
}

// Clear Search Highlights
function clearSearchHighlights() {
    document.querySelectorAll('.search-highlight').forEach(el => {
        el.outerHTML = el.textContent;
    });
}

// Export Chat
function exportChat() {
    if (conversationHistory.length === 0) {
        alert('لا توجد رسائل لتصديرها');
        return;
    }
    
    const session = chatSessions.find(s => s.id === currentSessionId);
    const title = session ? session.title : 'محادثة';
    
    let content = `# ${title}\n`;
    content += `التاريخ: ${new Date().toLocaleDateString('ar-SA')}\n\n`;
    content += '---\n\n';
    
    conversationHistory.forEach(msg => {
        const role = msg.type === 'user' ? '👤 أنت' : '🤖 المساعد';
        const time = new Date(msg.timestamp).toLocaleTimeString('ar-SA');
        content += `**${role}** (${time}):\n${msg.text}\n\n`;
    });
    
    // Create download
    const blob = new Blob([content], { type: 'text/markdown;charset=utf-8' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `chat-${Date.now()}.md`;
    a.click();
    URL.revokeObjectURL(url);
}

// Toggle Chat Settings
function toggleChatSettings() {
    // Open settings window with chat tab selected
    openWindow('settingsWindow');
    setTimeout(() => showSettingsTab('chat'), 100);
}

// Handle Input Keydown
function handleInputKeydown(event) {
    const textarea = event.target;
    
    // Send on Enter (without Shift)
    if (event.key === 'Enter' && !event.shiftKey) {
        event.preventDefault();
        sendMessage();
        return;
    }
    
    // Command detection (/)
    if (event.key === '/' && textarea.value === '') {
        showCommandMenu();
    }
}

// Auto Resize Textarea
function autoResizeTextarea(textarea) {
    textarea.style.height = 'auto';
    textarea.style.height = Math.min(textarea.scrollHeight, 150) + 'px';
    
    // Update character count
    const charCount = document.getElementById('charCount');
    if (charCount) {
        charCount.textContent = textarea.value.length;
    }
}

// Toggle Voice Input
let isRecording = false;
let recognition = null;

function toggleVoiceInput() {
    const voiceBtn = document.getElementById('voiceBtn');
    
    if (!('webkitSpeechRecognition' in window) && !('SpeechRecognition' in window)) {
        alert('المتصفح لا يدعم الإدخال الصوتي');
        return;
    }
    
    if (isRecording) {
        stopVoiceInput();
    } else {
        startVoiceInput();
    }
}

function startVoiceInput() {
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    recognition = new SpeechRecognition();
    
    recognition.lang = document.documentElement.lang === 'ar' ? 'ar-SA' : 'en-US';
    recognition.continuous = true;
    recognition.interimResults = true;
    
    const voiceBtn = document.getElementById('voiceBtn');
    const textarea = document.getElementById('messageInput');
    const statusText = document.getElementById('chatStatusText');
    
    recognition.onstart = function() {
        isRecording = true;
        voiceBtn.classList.add('recording');
        if (statusText) statusText.textContent = 'جارٍ الاستماع...';
        updateStatusIndicator('typing');
    };
    
    recognition.onresult = function(event) {
        let transcript = '';
        for (let i = event.resultIndex; i < event.results.length; i++) {
            transcript += event.results[i][0].transcript;
        }
        textarea.value = transcript;
        autoResizeTextarea(textarea);
    };
    
    recognition.onerror = function(event) {
        console.error('Speech recognition error:', event.error);
        stopVoiceInput();
    };
    
    recognition.onend = function() {
        stopVoiceInput();
    };
    
    recognition.start();
}

function stopVoiceInput() {
    if (recognition) {
        recognition.stop();
    }
    isRecording = false;
    
    const voiceBtn = document.getElementById('voiceBtn');
    const statusText = document.getElementById('chatStatusText');
    
    voiceBtn.classList.remove('recording');
    if (statusText) statusText.textContent = 'جاهز للمساعدة';
    updateStatusIndicator('online');
}

// Update Status Indicator
function updateStatusIndicator(status) {
    const indicator = document.querySelector('.chat-status-bar .status-indicator');
    if (indicator) {
        indicator.className = 'status-indicator ' + status;
    }
}

// Insert Emoji
function insertEmoji() {
    const emojis = ['😊', '👍', '🎉', '💡', '🚀', '✨', '🔥', '💪', '👏', '🙏', '❤️', '⭐'];
    const textarea = document.getElementById('messageInput');
    
    // Simple emoji picker
    const picker = document.createElement('div');
    picker.className = 'emoji-picker';
    picker.innerHTML = emojis.map(e => `<button onclick="insertEmojiChar('${e}')">${e}</button>`).join('');
    
    // Position and show
    const inputArea = document.querySelector('.input-container-modern');
    inputArea.appendChild(picker);
    
    // Close on outside click
    setTimeout(() => {
        document.addEventListener('click', function closeEmoji(e) {
            if (!picker.contains(e.target)) {
                picker.remove();
                document.removeEventListener('click', closeEmoji);
            }
        });
    }, 100);
}

function insertEmojiChar(emoji) {
    const textarea = document.getElementById('messageInput');
    const start = textarea.selectionStart;
    const end = textarea.selectionEnd;
    textarea.value = textarea.value.substring(0, start) + emoji + textarea.value.substring(end);
    textarea.focus();
    textarea.selectionStart = textarea.selectionEnd = start + emoji.length;
    
    // Remove picker
    const picker = document.querySelector('.emoji-picker');
    if (picker) picker.remove();
}

// Command Menu
function showCommandMenu() {
    const commands = [
        { cmd: '/clear', desc: 'مسح المحادثة الحالية' },
        { cmd: '/new', desc: 'بدء محادثة جديدة' },
        { cmd: '/export', desc: 'تصدير المحادثة' },
        { cmd: '/help', desc: 'عرض المساعدة' },
        { cmd: '/model', desc: 'تغيير النموذج' }
    ];
    
    const menu = document.createElement('div');
    menu.className = 'command-menu';
    menu.innerHTML = commands.map(c => `
        <button class="command-item" onclick="executeCommand('${c.cmd}')">
            <span class="command-name">${c.cmd}</span>
            <span class="command-desc">${c.desc}</span>
        </button>
    `).join('');
    
    const inputArea = document.querySelector('.input-container-modern');
    inputArea.appendChild(menu);
    
    // Close on escape or outside click
    function closeMenu(e) {
        if (e.key === 'Escape' || (e.type === 'click' && !menu.contains(e.target))) {
            menu.remove();
            document.removeEventListener('keydown', closeMenu);
            document.removeEventListener('click', closeMenu);
        }
    }
    
    setTimeout(() => {
        document.addEventListener('keydown', closeMenu);
        document.addEventListener('click', closeMenu);
    }, 100);
}

function executeCommand(cmd) {
    const textarea = document.getElementById('messageInput');
    textarea.value = '';
    
    switch(cmd) {
        case '/clear':
            if (confirm('مسح المحادثة الحالية؟')) {
                conversationHistory = [];
                const messagesContainer = document.getElementById('chatMessages');
                const welcomeScreen = document.getElementById('welcomeScreen');
                messagesContainer.innerHTML = '';
                messagesContainer.appendChild(welcomeScreen);
                welcomeScreen.style.display = 'flex';
                saveCurrentSession();
            }
            break;
        case '/new':
            newChat();
            break;
        case '/export':
            exportChat();
            break;
        case '/help':
            sendQuickMessage('ما هي الأوامر المتاحة وكيف يمكنني استخدام هذا المساعد؟');
            break;
        case '/model':
            openWindow('settingsWindow');
            setTimeout(() => showSettingsTab('ai'), 100);
            break;
    }
    
    // Remove menu
    const menu = document.querySelector('.command-menu');
    if (menu) menu.remove();
}

// Enhanced Add Message with Actions
function addMessageToDOM(text, type, timestamp = null) {
    const container = document.getElementById('chatMessages');
    if (!container) return;
    
    const messageDiv = document.createElement('div');
    messageDiv.className = `message ${type}`;
    
    const avatar = document.createElement('div');
    avatar.className = 'message-avatar';
    avatar.textContent = type === 'user' ? 'أ' : 'AI';
    
    const contentWrapper = document.createElement('div');
    contentWrapper.className = 'message-content-wrapper';
    
    const content = document.createElement('div');
    content.className = 'message-content';
    
    // Parse markdown if enabled
    if (settingsState?.markdownEnabled) {
        content.innerHTML = parseMarkdown(text);
    } else {
        content.textContent = text;
    }
    
    contentWrapper.appendChild(content);
    
    // Add timestamp if enabled
    if (settingsState?.showTimestamps) {
        const time = document.createElement('div');
        time.className = 'message-time';
        time.textContent = timestamp ? 
            new Date(timestamp).toLocaleTimeString('ar-SA', { hour: '2-digit', minute: '2-digit' }) :
            new Date().toLocaleTimeString('ar-SA', { hour: '2-digit', minute: '2-digit' });
        contentWrapper.appendChild(time);
    }
    
    // Add actions for bot messages
    if (type === 'bot') {
        const actions = document.createElement('div');
        actions.className = 'message-actions';
        actions.innerHTML = `
            <button class="msg-action-btn" onclick="copyMessage(this)">
                <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                    <rect x="9" y="9" width="13" height="13" rx="2" ry="2"/>
                    <path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1"/>
                </svg>
                نسخ
            </button>
            <button class="msg-action-btn" onclick="regenerateMessage()">
                <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                    <polyline points="23 4 23 10 17 10"/>
                    <path d="M20.49 15a9 9 0 1 1-2.12-9.36L23 10"/>
                </svg>
                إعادة
            </button>
        `;
        contentWrapper.appendChild(actions);
    }
    
    messageDiv.appendChild(avatar);
    messageDiv.appendChild(contentWrapper);
    container.appendChild(messageDiv);
    
    // Scroll to bottom
    container.scrollTop = container.scrollHeight;
}

// Simple Markdown Parser
function parseMarkdown(text) {
    // Code blocks
    text = text.replace(/```(\w+)?\n([\s\S]*?)```/g, '<pre><code class="language-$1">$2</code></pre>');
    text = text.replace(/`([^`]+)`/g, '<code>$1</code>');
    
    // Bold and Italic
    text = text.replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>');
    text = text.replace(/\*(.+?)\*/g, '<em>$1</em>');
    
    // Links
    text = text.replace(/\[(.+?)\]\((.+?)\)/g, '<a href="$2" target="_blank">$1</a>');
    
    // Line breaks
    text = text.replace(/\n/g, '<br>');
    
    return text;
}

// Copy Message
function copyMessage(btn) {
    const content = btn.closest('.message-content-wrapper').querySelector('.message-content');
    const text = content.textContent || content.innerText;
    
    navigator.clipboard.writeText(text).then(() => {
        const originalText = btn.innerHTML;
        btn.innerHTML = `
            <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <polyline points="20 6 9 17 4 12"/>
            </svg>
            تم النسخ
        `;
        setTimeout(() => {
            btn.innerHTML = originalText;
        }, 2000);
    });
}

// Regenerate Message
function regenerateMessage() {
    if (conversationHistory.length < 2) return;
    
    // Remove last bot message
    conversationHistory.pop();
    const lastUserMsg = conversationHistory[conversationHistory.length - 1];
    
    // Remove last message from DOM
    const messages = document.querySelectorAll('.message');
    if (messages.length > 0) {
        messages[messages.length - 1].remove();
    }
    
    // Resend
    showTypingIndicator();
    
    fetch('/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
            message: lastUserMsg.text,
            session_id: currentSessionId
        })
    })
    .then(response => response.json())
    .then(data => {
        hideTypingIndicator();
        if (data.response) {
            addMessage(data.response, 'bot');
        }
    })
    .catch(error => {
        hideTypingIndicator();
        console.error('Error:', error);
    });
}

// File Attachment Handler
let attachedFiles = [];

function attachFile() {
    const input = document.createElement('input');
    input.type = 'file';
    input.accept = 'image/*,.pdf,.doc,.docx,.txt,.csv,.json';
    input.multiple = true;
    
    input.onchange = function(e) {
        const files = Array.from(e.target.files);
        files.forEach(file => {
            if (file.size > 10 * 1024 * 1024) {
                alert(`الملف ${file.name} أكبر من 10MB`);
                return;
            }
            
            attachedFiles.push(file);
            displayAttachment(file);
        });
    };
    
    input.click();
}

function displayAttachment(file) {
    const preview = document.getElementById('attachmentsPreview');
    const list = document.getElementById('attachmentsList');
    
    preview.style.display = 'block';
    
    const item = document.createElement('div');
    item.className = 'attachment-item';
    
    let icon = '📄';
    if (file.type.startsWith('image/')) icon = '🖼️';
    else if (file.type === 'application/pdf') icon = '📕';
    else if (file.type.includes('word')) icon = '📘';
    
    item.innerHTML = `
        <span>${icon}</span>
        <span>${file.name}</span>
        <button class="remove-attachment" onclick="removeAttachment('${file.name}', this)">
            <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <path d="M18 6L6 18M6 6l12 12"/>
            </svg>
        </button>
    `;
    
    list.appendChild(item);
}

function removeAttachment(fileName, btn) {
    attachedFiles = attachedFiles.filter(f => f.name !== fileName);
    btn.parentElement.remove();
    
    if (attachedFiles.length === 0) {
        document.getElementById('attachmentsPreview').style.display = 'none';
    }
}

// Initialize session
generateSessionId();
loadChatSessions();

// Initialize first session if none exists
if (chatSessions.length === 0) {
    newChat();
}

// Initialize settings
initSettings();

