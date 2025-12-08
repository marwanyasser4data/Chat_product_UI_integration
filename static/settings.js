// Settings Management

let currentSettings = null;
let selectedTheme = 'nhc';

// Load current theme
async function loadCurrentTheme() {
    try {
        const response = await fetch('/get-theme');
        const data = await response.json();
        selectedTheme = data.theme || 'nhc';
        updateThemeSelection();
    } catch (error) {
        console.error('Error loading theme:', error);
    }
}

// Update theme selection UI
function updateThemeSelection() {
    document.querySelectorAll('.theme-option').forEach(option => {
        if (option.dataset.theme === selectedTheme) {
            option.classList.add('selected');
        } else {
            option.classList.remove('selected');
        }
    });
}

// Select theme
function selectTheme(theme) {
    selectedTheme = theme;
    updateThemeSelection();
}

// Apply theme
async function applyTheme(theme) {
    try {
        const response = await fetch('/change-theme', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ theme: theme })
        });

        const data = await response.json();

        if (data.success) {
            // Change stylesheet
            const stylesheet = document.getElementById('themeStylesheet');
            stylesheet.href = `/static/style-${theme}.css`;

            // Update selected theme
            selectedTheme = theme;

            return true;
        }
        return false;
    } catch (error) {
        console.error('Error applying theme:', error);
        return false;
    }
}

// Load settings
async function loadSettings() {
    try {
        const response = await fetch('/get-settings');
        const data = await response.json();

        currentSettings = data.settings;
        const availableModels = data.available_models;

        // Update settings modal
        updateSettingsModal(currentSettings, availableModels);

    } catch (error) {
        console.error('Error loading settings:', error);
    }
}

// Update settings modal
function updateSettingsModal(settings, availableModels) {
    const providerSelect = document.getElementById('providerSelect');
    const modelSelect = document.getElementById('modelSelect');
    const temperatureSlider = document.getElementById('temperatureSlider');
    const temperatureValue = document.getElementById('temperatureValue');
    const maxTokensInput = document.getElementById('maxTokensInput');
    const apiKeyInput = document.getElementById('apiKeyInput');

    if (!providerSelect) return;

    // Set current values
    providerSelect.value = settings.provider;
    temperatureSlider.value = settings.temperature;
    temperatureValue.textContent = settings.temperature.toFixed(1);
    maxTokensInput.value = settings.max_tokens;
    apiKeyInput.value = settings.api_key || '';

    // Update model options based on provider
    updateModelOptions(settings.provider, availableModels, settings.model);

    // Update API key field visibility
    updateApiKeyVisibility(settings.provider);
}

// Update model options
function updateModelOptions(provider, availableModels, selectedModel) {
    const modelSelect = document.getElementById('modelSelect');
    if (!modelSelect) return;

    modelSelect.innerHTML = '';

    if (provider === 'fake') {
        const option = document.createElement('option');
        option.value = 'fake';
        option.textContent = currentLang === 'ar' ? 'نموذج تجريبي' : 'Demo Model';
        modelSelect.appendChild(option);
        modelSelect.disabled = true;
        return;
    }

    modelSelect.disabled = false;
    const models = availableModels[provider] || [];

    models.forEach(model => {
        const option = document.createElement('option');
        option.value = model.id;
        option.textContent = `${model.name} - ${model.description}`;
        if (model.id === selectedModel) {
            option.selected = true;
        }
        modelSelect.appendChild(option);
    });
}

// Update API key visibility
function updateApiKeyVisibility(provider) {
    const apiKeyContainer = document.getElementById('apiKeyContainer');
    if (!apiKeyContainer) return;

    if (provider === 'fake') {
        apiKeyContainer.style.display = 'none';
    } else {
        apiKeyContainer.style.display = 'block';
    }
}

// Show settings modal
// Show settings modal
window.showSettingsModal = function () {
    const modal = document.getElementById('settingsModal');
    if (modal) {
        modal.classList.add('show');
        loadSettings();
    }
}

// Hide settings modal
function hideSettingsModal() {
    const modal = document.getElementById('settingsModal');
    if (modal) {
        modal.classList.remove('show');
    }
}

// Provider changed
function onProviderChange() {
    const providerSelect = document.getElementById('providerSelect');
    const provider = providerSelect.value;

    fetch('/get-settings')
        .then(response => response.json())
        .then(data => {
            const models = data.available_models;
            updateModelOptions(provider, models, models[provider]?.[0]?.id || 'gpt-4o');
            updateApiKeyVisibility(provider);
        });
}

// Temperature slider changed
function onTemperatureChange(value) {
    const temperatureValue = document.getElementById('temperatureValue');
    if (temperatureValue) {
        temperatureValue.textContent = parseFloat(value).toFixed(1);
    }
}

// Test API key
async function testApiKey() {
    const provider = document.getElementById('providerSelect').value;
    const apiKey = document.getElementById('apiKeyInput').value;
    const testButton = document.getElementById('testApiKeyBtn');
    const testResult = document.getElementById('testApiKeyResult');

    if (!apiKey || apiKey === '****') {
        testResult.textContent = currentLang === 'ar' ? 'الرجاء إدخال مفتاح API' : 'Please enter API key';
        testResult.className = 'api-test-result error';
        testResult.style.display = 'block';
        return;
    }

    testButton.disabled = true;
    testButton.textContent = currentLang === 'ar' ? 'جاري الاختبار...' : 'Testing...';
    testResult.textContent = '';
    testResult.style.display = 'none';

    try {
        const response = await fetch('/test-api-key', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                provider: provider,
                api_key: apiKey
            })
        });

        const data = await response.json();

        testResult.textContent = data.message;
        testResult.className = `api-test-result ${data.valid ? 'success' : 'error'}`;
        testResult.style.display = 'block';

    } catch (error) {
        testResult.textContent = currentLang === 'ar' ? 'فشل الاختبار' : 'Test failed';
        testResult.className = 'api-test-result error';
        testResult.style.display = 'block';
    } finally {
        testButton.disabled = false;
        testButton.textContent = currentLang === 'ar' ? 'اختبار المفتاح' : 'Test Key';
    }
}

// Save settings
async function saveSettings() {
    const provider = document.getElementById('providerSelect').value;
    const model = document.getElementById('modelSelect').value;
    const temperature = parseFloat(document.getElementById('temperatureSlider').value);
    const maxTokens = parseInt(document.getElementById('maxTokensInput').value);
    const apiKey = document.getElementById('apiKeyInput').value;

    const saveButton = document.getElementById('saveSettingsBtn');
    const originalText = saveButton.textContent;

    saveButton.disabled = true;
    saveButton.textContent = currentLang === 'ar' ? 'جاري الحفظ...' : 'Saving...';

    try {
        // Apply theme if changed
        await applyTheme(selectedTheme);

        // Prepare settings object
        const settingsData = {
            provider: provider,
            model: model,
            temperature: temperature,
            max_tokens: maxTokens
        };

        // Only include API key if it's not masked (doesn't end with ...)
        if (apiKey && !apiKey.endsWith('...')) {
            settingsData.api_key = apiKey;
        }

        const response = await fetch('/update-settings', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(settingsData)
        });

        const data = await response.json();

        if (data.success) {
            // Show success message
            const successMsg = document.createElement('div');
            successMsg.className = 'success-toast';
            successMsg.textContent = currentLang === 'ar' ? 'تم حفظ الإعدادات بنجاح!' : 'Settings saved successfully!';
            document.body.appendChild(successMsg);

            setTimeout(() => {
                successMsg.remove();
            }, 3000);

            // Close modal
            setTimeout(() => {
                hideSettingsModal();
            }, 1000);
        } else {
            alert(data.error || 'Failed to save settings');
        }

    } catch (error) {
        alert(currentLang === 'ar' ? 'فشل حفظ الإعدادات' : 'Failed to save settings');
        console.error('Error saving settings:', error);
    } finally {
        saveButton.disabled = false;
        saveButton.textContent = originalText;
    }
}

// Initialize settings on page load
document.addEventListener('DOMContentLoaded', function () {
    loadSettings();
    loadCurrentTheme();
});
