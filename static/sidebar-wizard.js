// Sidebar Filter Wizard JavaScript

let currentWizardStep = 1;
const totalWizardSteps = 3;
let selectedFilters = {
    step1: null,
    step2: null,
    step3: null
};

// Select filter option
function selectFilterOption(step, value, element) {
    console.log('🟢 selectFilterOption called:', { step, value });

    // Remove selection from siblings
    const parent = element.parentElement;
    parent.querySelectorAll('.filter-option-card').forEach(card => {
        card.classList.remove('selected');
    });

    // Add selection to clicked element
    element.classList.add('selected');

    // Store selection
    selectedFilters[`step${step}`] = value;
    console.log('🟢 Updated selectedFilters:', JSON.stringify(selectedFilters));

    // Enable next button
    document.getElementById('wizardNextBtn').disabled = false;
    console.log('🟢 Next button enabled');
}

// Prepare next step options based on previous selection
async function prepareNextStepOptions(currentStep, selectedValue) {
    console.log('prepareNextStepOptions called:', { currentStep, selectedValue });

    const nextStep = currentStep + 1;
    const optionsContainer = document.getElementById(`step${nextStep}Options`);

    console.log('Options container:', optionsContainer);

    // If moving to Step 2, load strategies from API
    if (currentStep === 1 && nextStep === 2) {
        console.log('Loading strategies from API for domain:', selectedValue);

        // Show loading message
        optionsContainer.innerHTML = `
            <div style="text-align: center; padding: 40px; color: rgba(255, 255, 255, 0.6);">
                <div style="margin-bottom: 10px;">Loading strategies...</div>
            </div>
        `;


        try {
            const url = `/api/filter/strategies?domain_id=${selectedValue}`;
            console.log('📡 Fetching from URL:', url);

            const response = await fetch(url);
            console.log('📡 Response received:', response.status, response.statusText);

            const data = await response.json();
            console.log('📡 Data parsed:', data);

            if (data.success && data.strategies && data.strategies.length > 0) {
                console.log('✅ Found', data.strategies.length, 'strategies');

                // Clear loading message
                optionsContainer.innerHTML = '';

                // Generate strategy cards
                data.strategies.forEach(strategy => {
                    console.log('Creating card for strategy:', strategy.title);
                    const card = document.createElement('div');
                    card.className = 'filter-option-card';
                    card.setAttribute('data-value', strategy.value);
                    card.onclick = function () {
                        selectFilterOption(2, strategy.value, this);
                    };

                    card.innerHTML = `
                        <div class="option-icon">
                            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                                <path d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2"/>
                            </svg>
                        </div>
                        <div class="option-content">
                            <div class="option-title">${strategy.title}</div>
                            <div class="option-desc">${strategy.description}</div>
                        </div>
                        <div class="option-check">✓</div>
                    `;

                    optionsContainer.appendChild(card);
                });
                console.log('✅ All strategy cards added to container');
            } else {
                console.log('⚠️ No strategies found or data.success is false');
                optionsContainer.innerHTML = `
                    <div style="text-align: center; padding: 40px; color: rgba(255, 255, 255, 0.6);">
                        <div>No strategies found for this domain</div>
                    </div>
                `;
            }
        } catch (error) {
            console.error('❌ Error loading strategies:', error);
            optionsContainer.innerHTML = `
                <div style="text-align: center; padding: 40px; color: rgba(255, 100, 100, 0.8);">
                    <div>Error loading strategies</div>
                    <div style="font-size: 12px; margin-top: 10px;">${error.message}</div>
                </div>
            `;
        }
        return;
    }

    // If moving to Step 3, load alerts from API
    if (currentStep === 2 && nextStep === 3) {
        console.log('Loading alerts from API for domain:', selectedFilters.step1, 'and strategy:', selectedValue);

        // Show loading message
        optionsContainer.innerHTML = `
            <div style="text-align: center; padding: 40px; color: rgba(255, 255, 255, 0.6);">
                <div style="margin-bottom: 10px;">Loading alerts...</div>
            </div>
        `;

        try {
            const url = `/api/filter/alerts?domain_id=${selectedFilters.step1}&strategy_id=${selectedValue}`;
            console.log('📡 Fetching from URL:', url);

            const response = await fetch(url);
            console.log('📡 Response received:', response.status, response.statusText);

            const data = await response.json();
            console.log('📡 Data parsed:', data);
            console.log('📡 data.success:', data.success);
            console.log('📡 data.alerts:', data.alerts);
            console.log('📡 data.alerts length:', data.alerts ? data.alerts.length : 'undefined');

            if (data.success && data.alerts && data.alerts.length > 0) {
                console.log('✅ Found', data.alerts.length, 'alerts (Total:', data.total, ')');

                // Clear loading message
                optionsContainer.innerHTML = '';

                // Generate alert cards
                data.alerts.forEach(alert => {
                    console.log('Creating card for alert:', alert.title);
                    const card = document.createElement('div');
                    card.className = 'filter-option-card';
                    card.setAttribute('data-value', alert.value);
                    card.onclick = function () {
                        selectFilterOption(3, alert.value, this);
                    };

                    card.innerHTML = `
                        <div class="option-icon">
                            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                                <path d="M10.29 3.86L1.82 18a2 2 0 001.71 3h16.94a2 2 0 001.71-3L13.71 3.86a2 2 0 00-3.42 0z"/>
                                <line x1="12" y1="9" x2="12" y2="13"/>
                                <line x1="12" y1="17" x2="12.01" y2="17"/>
                            </svg>
                        </div>
                        <div class="option-content">
                            <div class="option-title">${alert.title}</div>
                            <div class="option-desc">${alert.description}</div>
                        </div>
                        <div class="option-check">✓</div>
                    `;

                    optionsContainer.appendChild(card);
                });

                // Add summary message if there are more alerts
                if (data.total > data.alerts.length) {
                    const summary = document.createElement('div');
                    summary.style.cssText = 'text-align: center; padding: 20px; color: rgba(255, 255, 255, 0.6); font-size: 0.9rem;';
                    summary.textContent = `Showing ${data.alerts.length} of ${data.total} alerts`;
                    optionsContainer.appendChild(summary);
                }

                console.log('✅ All alert cards added to container');
            } else {
                console.log('⚠️ No alerts found or data.success is false');
                optionsContainer.innerHTML = `
                    <div style="text-align: center; padding: 40px; color: rgba(255, 255, 255, 0.6);">
                        <div>No alerts found for this selection</div>
                    </div>
                `;
            }
        } catch (error) {
            console.error('❌ Error loading alerts:', error);
            optionsContainer.innerHTML = `
                <div style="text-align: center; padding: 40px; color: rgba(255, 100, 100, 0.8);">
                    <div>Error loading alerts</div>
                    <div style="font-size: 12px; margin-top: 10px;">${error.message}</div>
                </div>
            `;
        }
        return;
    }

    // For other steps, keep the old static logic
    const optionsMap = {
        2: {
            default: [
                { value: 'all', title: 'All', desc: 'All items', icon: 'M8 6h13M8 12h13M8 18h13M3 6h.01M3 12h.01M3 18h.01' },
                { value: 'recent', title: 'Recent', desc: 'Recent items', icon: 'M12 12m-10 0a10 10 0 1 0 20 0a10 10 0 1 0 -20 0M12 6v6l4 2' }
            ]
        }
    };

    const options = optionsMap[currentStep]?.default || optionsMap[2].default;

    // Generate HTML for options
    optionsContainer.innerHTML = options.map(option => `
        <div class="filter-option-card" data-value="${option.value}" onclick="selectFilterOption(${nextStep}, '${option.value}', this)">
            <div class="option-icon">
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                    <path d="${option.icon}"/>
                </svg>
            </div>
            <div class="option-content">
                <div class="option-title">${option.title}</div>
                <div class="option-desc">${option.desc}</div>
            </div>
            <div class="option-check">✓</div>
        </div>
    `).join('');
}

// Next wizard step
function nextWizardStep() {
    console.log('🔵 nextWizardStep called, current step:', currentWizardStep);
    console.log('🔵 selectedFilters:', JSON.stringify(selectedFilters));

    if (currentWizardStep < totalWizardSteps) {
        const previousStep = currentWizardStep;
        currentWizardStep++;
        console.log('🔵 Moving from step', previousStep, 'to step', currentWizardStep);
        updateWizardUI();

        // If moving to Step 2, load strategies based on Step 1 selection
        if (currentWizardStep === 2 && selectedFilters.step1) {
            console.log('✅ Calling prepareNextStepOptions for Step 2 with domain:', selectedFilters.step1);
            prepareNextStepOptions(previousStep, selectedFilters.step1);
        }
        // If moving to Step 3, load options based on Step 2 selection
        else if (currentWizardStep === 3 && selectedFilters.step2) {
            console.log('✅ Calling prepareNextStepOptions for Step 3 with strategy:', selectedFilters.step2);
            prepareNextStepOptions(previousStep, selectedFilters.step2);
        } else {
            console.log('⚠️ No condition matched for loading next step options');
        }
    } else {
        // Apply filters
        console.log('🔵 Applying filters');
        applyWizardFilters();
    }
}

// Previous wizard step
function previousWizardStep() {
    if (currentWizardStep > 1) {
        currentWizardStep--;
        updateWizardUI();
    }
}

// Update wizard UI
function updateWizardUI() {
    console.log('🔄 Updating UI for step:', currentWizardStep);

    // Update steps visibility
    document.querySelectorAll('.wizard-step').forEach((step, index) => {
        const stepNum = index + 1;
        step.classList.remove('active');

        if (stepNum === currentWizardStep) {
            step.classList.add('active');
            step.style.display = 'block';
            console.log(`✅ Showing step ${stepNum}`);
        } else {
            step.style.display = 'none';
            console.log(`❌ Hiding step ${stepNum}`);
        }
    });

    // Update progress
    document.querySelectorAll('.progress-step').forEach((step, index) => {
        const stepNum = index + 1;
        step.classList.remove('active', 'completed');

        if (stepNum < currentWizardStep) {
            step.classList.add('completed');
        } else if (stepNum === currentWizardStep) {
            step.classList.add('active');
        }
    });

    // Update buttons
    const backBtn = document.getElementById('wizardBackBtn');
    const nextBtn = document.getElementById('wizardNextBtn');

    backBtn.style.display = currentWizardStep > 1 ? 'flex' : 'none';

    if (currentWizardStep === totalWizardSteps) {
        nextBtn.innerHTML = `
            Apply Filter
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <polyline points="20 6 9 17 4 12"/>
            </svg>
        `;
    } else {
        nextBtn.innerHTML = `
            Next
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <path d="M5 12h14M12 5l7 7-7 7"/>
            </svg>
        `;
    }

    // Disable next button if no selection made for current step
    nextBtn.disabled = !selectedFilters[`step${currentWizardStep}`];
}

// Apply wizard filters
function applyWizardFilters() {
    console.log('🎯 Applying filters:', selectedFilters);

    // Validate all steps are selected
    if (!selectedFilters.step1 || !selectedFilters.step2 || !selectedFilters.step3) {
        alert('Please complete all steps before applying filters');
        return;
    }

    // Build the final SQL query
    const finalQuery = `SELECT *
FROM svi_alerts.tdc_alert ta
JOIN fdhdata.tm_cases tc 
    ON ta.alert_id = tc.alert_id
WHERE ta.domain_id = '${selectedFilters.step1}'
  AND alert_status_id = 'ACTIVE'
  AND ta.alert_id = '${selectedFilters.step3}'
  AND ta.queue_id IN (
      SELECT queue_id
      FROM svi_alerts.tdc_queue
      WHERE domain_id = '${selectedFilters.step1}'
        AND strategy_id = '${selectedFilters.step2}'
  );`;

    console.log('📊 Final Query:', finalQuery);

    // Show confirmation popup
    showAnalysisConfirmation(finalQuery);
}

// Show analysis confirmation popup
function showAnalysisConfirmation(query) {
    // Create popup overlay
    const overlay = document.createElement('div');
    overlay.id = 'analysisConfirmationOverlay';
    overlay.style.cssText = `
        position: fixed;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        background: rgba(0, 0, 0, 0.7);
        display: flex;
        align-items: center;
        justify-content: center;
        z-index: 10000;
        backdrop-filter: blur(5px);
    `;

    // Create popup content
    const popup = document.createElement('div');
    popup.style.cssText = `
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        border-radius: 20px;
        padding: 40px;
        max-width: 600px;
        width: 90%;
        box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
        color: white;
        text-align: center;
    `;

    popup.innerHTML = `
        <div style="font-size: 48px; margin-bottom: 20px;">🤖</div>
        <h2 style="margin: 0 0 15px 0; font-size: 28px; font-weight: 600;">Start AI Analysis?</h2>
        <p style="margin: 0 0 30px 0; font-size: 16px; opacity: 0.9; line-height: 1.6;">
            The AI will analyze the selected alert data and provide insights.<br/>
            Do you want to proceed with the analysis?
        </p>
        <div style="display: flex; gap: 15px; justify-content: center;">
            <button id="confirmAnalysisBtn" style="
                background: white;
                color: #667eea;
                border: none;
                padding: 15px 40px;
                border-radius: 10px;
                font-size: 16px;
                font-weight: 600;
                cursor: pointer;
                transition: all 0.3s;
                box-shadow: 0 4px 15px rgba(0, 0, 0, 0.2);
            ">
                ✓ Yes, Start Analysis
            </button>
            <button id="cancelAnalysisBtn" style="
                background: rgba(255, 255, 255, 0.2);
                color: white;
                border: 2px solid white;
                padding: 15px 40px;
                border-radius: 10px;
                font-size: 16px;
                font-weight: 600;
                cursor: pointer;
                transition: all 0.3s;
            ">
                ✗ Cancel
            </button>
        </div>
    `;

    overlay.appendChild(popup);
    document.body.appendChild(overlay);

    // Add hover effects
    const confirmBtn = popup.querySelector('#confirmAnalysisBtn');
    const cancelBtn = popup.querySelector('#cancelAnalysisBtn');

    confirmBtn.onmouseover = () => confirmBtn.style.transform = 'scale(1.05)';
    confirmBtn.onmouseout = () => confirmBtn.style.transform = 'scale(1)';
    cancelBtn.onmouseover = () => cancelBtn.style.transform = 'scale(1.05)';
    cancelBtn.onmouseout = () => cancelBtn.style.transform = 'scale(1)';

    // Handle confirmation
    confirmBtn.onclick = () => {
        console.log('✅ User confirmed analysis');
        document.body.removeChild(overlay);
        sendQueryToAI(query);
    };

    // Handle cancellation
    cancelBtn.onclick = () => {
        console.log('❌ User cancelled analysis');
        document.body.removeChild(overlay);
    };

    // Close on overlay click
    overlay.onclick = (e) => {
        if (e.target === overlay) {
            document.body.removeChild(overlay);
        }
    };
}

// Send query to AI chat
async function sendQueryToAI(query) {
    console.log('📤 Preparing to send query to AI');
    console.log('📊 Selected filters:', selectedFilters);

    try {
        // Show loading indicator
        const loadingOverlay = document.createElement('div');
        loadingOverlay.id = 'queryLoadingOverlay';
        loadingOverlay.style.cssText = `
            position: fixed;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            background: rgba(0, 0, 0, 0.8);
            display: flex;
            align-items: center;
            justify-content: center;
            z-index: 10001;
            color: white;
            font-size: 18px;
        `;
        loadingOverlay.innerHTML = '<div>⏳ Executing query and preparing analysis...</div>';
        document.body.appendChild(loadingOverlay);

        // Call API to execute query and get investigator prompt
        const response = await fetch('/api/filter/execute-final-query', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                domain_id: selectedFilters.step1,
                strategy_id: selectedFilters.step2,
                alert_id: selectedFilters.step3
            })
        });

        const data = await response.json();
        console.log('📡 API Response:', data);

        // Remove loading overlay
        document.body.removeChild(loadingOverlay);

        if (data.success && data.prompt) {
            console.log('✅ Investigator prompt received');

            // Get the chat input element
            const chatInput = document.getElementById('messageInput');

            if (chatInput) {
                // Set the investigator prompt in the input
                chatInput.value = data.prompt;
                console.log('✅ Prompt set in input');

                // Auto-resize the textarea
                if (typeof autoResizeTextarea === 'function') {
                    autoResizeTextarea(chatInput);
                }

                // Trigger send by simulating Enter key press
                const enterEvent = new KeyboardEvent('keydown', {
                    key: 'Enter',
                    code: 'Enter',
                    keyCode: 13,
                    which: 13,
                    bubbles: true,
                    cancelable: true
                });

                chatInput.dispatchEvent(enterEvent);
                console.log('✅ Enter key event dispatched');

                // Close the filter wizard and switch to chat view
                setTimeout(() => {
                    toggleSidebarView('history');
                    resetWizard();
                    console.log('✅ Investigator prompt sent to AI successfully');
                }, 100);
            } else {
                console.error('❌ Could not find chat input element');
                alert('Error: Could not send to AI. Please try again.');
            }
        } else {
            console.error('❌ API Error:', data.error);
            alert(`Error: ${data.error || 'Could not execute query'}`);
        }
    } catch (error) {
        console.error('❌ Error:', error);

        // Remove loading overlay if it exists
        const overlay = document.getElementById('queryLoadingOverlay');
        if (overlay) {
            document.body.removeChild(overlay);
        }

        alert('Error: Could not execute query. Please try again.');
    }
}

// Reset wizard
function resetWizard() {
    currentWizardStep = 1;
    selectedFilters = {
        step1: null,
        step2: null,
        step3: null
    };

    // Remove all selections
    document.querySelectorAll('.filter-option-card').forEach(card => {
        card.classList.remove('selected');
    });

    updateWizardUI();
}

// Listen for filters applied event
document.addEventListener('filtersApplied', (event) => {
    const filters = event.detail;
    console.log('✅ Filters applied successfully:', filters);

    // Here you can implement the actual filtering logic
    // For example, send to server or filter local data
});

// Initialize wizard on page load
document.addEventListener('DOMContentLoaded', () => {
    console.log('Sidebar Filter Wizard initialized');
    loadDomainsFromAPI();
});

// Load domains from API
async function loadDomainsFromAPI() {
    const container = document.getElementById('step1Options');

    try {
        const response = await fetch('/api/filter/domains');
        const data = await response.json();

        if (data.success && data.domains && data.domains.length > 0) {
            // Clear loading message
            container.innerHTML = '';

            // Generate domain cards
            data.domains.forEach(domain => {
                const card = document.createElement('div');
                card.className = 'filter-option-card';
                card.setAttribute('data-value', domain.value);
                card.onclick = function () {
                    selectFilterOption(1, domain.value, this);
                };

                card.innerHTML = `
                    <div class="option-content">
                        <div class="option-title">${domain.title}</div>
                        <div class="option-desc">${domain.description}<br/>ID: ${domain.id}</div>
                    </div>
                    <div class="option-check">✓</div>
                `;

                container.appendChild(card);
            });
        } else {
            container.innerHTML = `
                <div style="text-align: center; padding: 40px; color: rgba(255, 255, 255, 0.6);">
                    <div>No domains found</div>
                </div>
            `;
        }
    } catch (error) {
        console.error('Error loading domains:', error);
        container.innerHTML = `
            <div style="text-align: center; padding: 40px; color: rgba(255, 100, 100, 0.8);">
                <div>Error loading domains</div>
                <div style="font-size: 12px; margin-top: 10px;">${error.message}</div>
            </div>
        `;
    }
}

