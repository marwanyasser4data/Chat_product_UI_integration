// Filter Wizard JavaScript
class FilterWizard {
    constructor() {
        this.currentStep = 1;
        this.totalSteps = 3;
        this.selectedFilters = {
            step1: null,
            step2: null,
            step3: null
        };
        this.init();
    }

    init() {
        this.createWizardHTML();
        this.attachEventListeners();
    }

    createWizardHTML() {
        const wizardHTML = `
            <div class="filter-wizard-overlay" id="filterWizardOverlay">
                <div class="filter-wizard-container">
                    <!-- Header -->
                    <div class="filter-wizard-header">
                        <h2 class="filter-wizard-title">
                            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                                <path d="M22 3H2l8 9.46V19l4 2v-8.54L22 3z"/>
                            </svg>
                            <span data-i18n="filterWizardTitle">معالج الفلاتر المتقدم</span>
                        </h2>
                        <button class="filter-wizard-close" onclick="filterWizard.close()">
                            <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                                <path d="M18 6L6 18M6 6l12 12"/>
                            </svg>
                        </button>
                    </div>

                    <!-- Progress Bar -->
                    <div class="filter-wizard-progress">
                        <div class="progress-steps">
                            <div class="progress-line">
                                <div class="progress-line-fill" id="progressLineFill"></div>
                            </div>
                            <div class="progress-step active" data-step="1">
                                <div class="progress-step-circle">1</div>
                                <div class="progress-step-label" data-i18n="step1Label">نوع البيانات</div>
                            </div>
                            <div class="progress-step" data-step="2">
                                <div class="progress-step-circle">2</div>
                                <div class="progress-step-label" data-i18n="step2Label">الفئة</div>
                            </div>
                            <div class="progress-step" data-step="3">
                                <div class="progress-step-circle">3</div>
                                <div class="progress-step-label" data-i18n="step3Label">التفاصيل</div>
                            </div>
                        </div>
                    </div>

                    <!-- Body -->
                    <div class="filter-wizard-body">
                        <!-- Step 1: Data Type Selection -->
                        <div class="wizard-step active" data-step="1">
                            <h3 class="step-title" data-i18n="step1Title">اختر نوع البيانات</h3>
                            <p class="step-description" data-i18n="step1Description">حدد نوع البيانات التي تريد البحث عنها أو تصفيتها</p>
                            
                            <div class="filter-options-grid">
                                <div class="filter-option-card" data-value="taxpayers" onclick="filterWizard.selectOption(1, 'taxpayers', this)">
                                    <div class="filter-option-icon">
                                        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                                            <path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"/>
                                            <circle cx="9" cy="7" r="4"/>
                                            <path d="M23 21v-2a4 4 0 0 0-3-3.87"/>
                                            <path d="M16 3.13a4 4 0 0 1 0 7.75"/>
                                        </svg>
                                    </div>
                                    <div class="filter-option-title">دافعي الضرائب</div>
                                    <div class="filter-option-description">البحث في بيانات دافعي الضرائب والمكلفين</div>
                                    <div class="filter-option-check">
                                        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="3">
                                            <polyline points="20 6 9 17 4 12"/>
                                        </svg>
                                    </div>
                                </div>

                                <div class="filter-option-card" data-value="entities" onclick="filterWizard.selectOption(1, 'entities', this)">
                                    <div class="filter-option-icon">
                                        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                                            <path d="M3 9l9-7 9 7v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z"/>
                                            <polyline points="9 22 9 12 15 12 15 22"/>
                                        </svg>
                                    </div>
                                    <div class="filter-option-title">الكيانات</div>
                                    <div class="filter-option-description">البحث في بيانات الكيانات والمنشآت</div>
                                    <div class="filter-option-check">
                                        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="3">
                                            <polyline points="20 6 9 17 4 12"/>
                                        </svg>
                                    </div>
                                </div>

                                <div class="filter-option-card" data-value="transactions" onclick="filterWizard.selectOption(1, 'transactions', this)">
                                    <div class="filter-option-icon">
                                        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                                            <path d="M12 2v20M17 5H9.5a3.5 3.5 0 0 0 0 7h5a3.5 3.5 0 0 1 0 7H6"/>
                                        </svg>
                                    </div>
                                    <div class="filter-option-title">المعاملات</div>
                                    <div class="filter-option-description">البحث في المعاملات المالية والضريبية</div>
                                    <div class="filter-option-check">
                                        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="3">
                                            <polyline points="20 6 9 17 4 12"/>
                                        </svg>
                                    </div>
                                </div>

                                <div class="filter-option-card" data-value="reports" onclick="filterWizard.selectOption(1, 'reports', this)">
                                    <div class="filter-option-icon">
                                        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                                            <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/>
                                            <polyline points="14 2 14 8 20 8"/>
                                            <line x1="16" y1="13" x2="8" y2="13"/>
                                            <line x1="16" y1="17" x2="8" y2="17"/>
                                            <polyline points="10 9 9 9 8 9"/>
                                        </svg>
                                    </div>
                                    <div class="filter-option-title">التقارير</div>
                                    <div class="filter-option-description">البحث في التقارير والإقرارات الضريبية</div>
                                    <div class="filter-option-check">
                                        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="3">
                                            <polyline points="20 6 9 17 4 12"/>
                                        </svg>
                                    </div>
                                </div>
                            </div>
                        </div>

                        <!-- Step 2: Category Selection -->
                        <div class="wizard-step" data-step="2">
                            <h3 class="step-title" data-i18n="step2Title">اختر الفئة</h3>
                            <p class="step-description" data-i18n="step2Description">حدد الفئة المحددة التي تريد التصفية بناءً عليها</p>
                            
                            <div class="filter-options-grid" id="step2Options">
                                <!-- Options will be populated dynamically based on Step 1 selection -->
                            </div>
                        </div>

                        <!-- Step 3: Details Selection -->
                        <div class="wizard-step" data-step="3">
                            <h3 class="step-title" data-i18n="step3Title">حدد التفاصيل</h3>
                            <p class="step-description" data-i18n="step3Description">اختر التفاصيل النهائية لتطبيق الفلتر</p>
                            
                            <div class="filter-options-grid" id="step3Options">
                                <!-- Options will be populated dynamically based on Step 2 selection -->
                            </div>
                        </div>
                    </div>

                    <!-- Footer -->
                    <div class="filter-wizard-footer">
                        <button class="wizard-btn wizard-btn-secondary" id="wizardPrevBtn" onclick="filterWizard.previousStep()" style="display: none;">
                            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                                <path d="M19 12H5M12 19l-7-7 7-7"/>
                            </svg>
                            <span data-i18n="prevBtn">السابق</span>
                        </button>
                        <button class="wizard-btn wizard-btn-primary" id="wizardNextBtn" onclick="filterWizard.nextStep()" disabled>
                            <span data-i18n="nextBtn">التالي</span>
                            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                                <path d="M5 12h14M12 5l7 7-7 7"/>
                            </svg>
                        </button>
                    </div>
                </div>
            </div>
        `;

        document.body.insertAdjacentHTML('beforeend', wizardHTML);
    }

    attachEventListeners() {
        // Close on overlay click
        document.getElementById('filterWizardOverlay').addEventListener('click', (e) => {
            if (e.target.id === 'filterWizardOverlay') {
                this.close();
            }
        });

        // Close on Escape key
        document.addEventListener('keydown', (e) => {
            if (e.key === 'Escape' && document.getElementById('filterWizardOverlay').classList.contains('active')) {
                this.close();
            }
        });
    }

    open() {
        document.getElementById('filterWizardOverlay').classList.add('active');
        document.body.style.overflow = 'hidden';
    }

    close() {
        document.getElementById('filterWizardOverlay').classList.remove('active');
        document.body.style.overflow = '';
        this.reset();
    }

    reset() {
        this.currentStep = 1;
        this.selectedFilters = {
            step1: null,
            step2: null,
            step3: null
        };
        this.updateUI();
    }

    selectOption(step, value, element) {
        // Remove selection from siblings
        const parent = element.parentElement;
        parent.querySelectorAll('.filter-option-card').forEach(card => {
            card.classList.remove('selected');
        });

        // Add selection to clicked element
        element.classList.add('selected');

        // Store selection
        this.selectedFilters[`step${step}`] = value;

        // Enable next button
        document.getElementById('wizardNextBtn').disabled = false;

        // If not on last step, prepare next step options
        if (step < this.totalSteps) {
            this.prepareNextStepOptions(step, value);
        }
    }

    prepareNextStepOptions(currentStep, selectedValue) {
        const nextStep = currentStep + 1;
        const optionsContainer = document.getElementById(`step${nextStep}Options`);

        // Define options based on previous selection
        const optionsMap = {
            1: {
                taxpayers: [
                    { value: 'individual', icon: 'user', title: 'أفراد', description: 'دافعي الضرائب الأفراد' },
                    { value: 'corporate', icon: 'briefcase', title: 'شركات', description: 'دافعي الضرائب من الشركات' },
                    { value: 'government', icon: 'shield', title: 'جهات حكومية', description: 'الجهات والهيئات الحكومية' }
                ],
                entities: [
                    { value: 'active', icon: 'check-circle', title: 'كيانات نشطة', description: 'الكيانات النشطة حالياً' },
                    { value: 'inactive', icon: 'x-circle', title: 'كيانات غير نشطة', description: 'الكيانات المعطلة أو المغلقة' },
                    { value: 'pending', icon: 'clock', title: 'قيد المراجعة', description: 'الكيانات قيد المراجعة' }
                ],
                transactions: [
                    { value: 'payment', icon: 'credit-card', title: 'المدفوعات', description: 'معاملات الدفع والسداد' },
                    { value: 'refund', icon: 'rotate-ccw', title: 'المرتجعات', description: 'معاملات الاسترداد والمرتجعات' },
                    { value: 'adjustment', icon: 'edit', title: 'التعديلات', description: 'التعديلات والتصحيحات' }
                ],
                reports: [
                    { value: 'monthly', icon: 'calendar', title: 'تقارير شهرية', description: 'التقارير الشهرية الدورية' },
                    { value: 'annual', icon: 'file-text', title: 'تقارير سنوية', description: 'التقارير والإقرارات السنوية' },
                    { value: 'custom', icon: 'sliders', title: 'تقارير مخصصة', description: 'تقارير مخصصة حسب الطلب' }
                ]
            },
            2: {
                // Step 3 options based on Step 2 selection
                individual: [
                    { value: 'status_active', icon: 'user-check', title: 'نشط', description: 'دافعي ضرائب نشطين' },
                    { value: 'status_suspended', icon: 'user-x', title: 'موقوف', description: 'حسابات موقوفة' }
                ],
                corporate: [
                    { value: 'small', icon: 'home', title: 'منشآت صغيرة', description: 'المنشآت الصغيرة والمتوسطة' },
                    { value: 'large', icon: 'building', title: 'منشآت كبيرة', description: 'الشركات والمنشآت الكبيرة' }
                ],
                // Add more mappings as needed
                default: [
                    { value: 'all', icon: 'list', title: 'الكل', description: 'جميع العناصر' },
                    { value: 'recent', icon: 'clock', title: 'الأحدث', description: 'العناصر الأحدث' }
                ]
            }
        };

        const options = optionsMap[currentStep][selectedValue] || optionsMap[currentStep].default || optionsMap[2].default;

        // Generate HTML for options
        optionsContainer.innerHTML = options.map(option => `
            <div class="filter-option-card" data-value="${option.value}" onclick="filterWizard.selectOption(${nextStep}, '${option.value}', this)">
                <div class="filter-option-icon">
                    ${this.getIconSVG(option.icon)}
                </div>
                <div class="filter-option-title">${option.title}</div>
                <div class="filter-option-description">${option.description}</div>
                <div class="filter-option-check">
                    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="3">
                        <polyline points="20 6 9 17 4 12"/>
                    </svg>
                </div>
            </div>
        `).join('');
    }

    getIconSVG(iconName) {
        const icons = {
            'user': '<path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"/><circle cx="12" cy="7" r="4"/>',
            'briefcase': '<rect x="2" y="7" width="20" height="14" rx="2" ry="2"/><path d="M16 21V5a2 2 0 0 0-2-2h-4a2 2 0 0 0-2 2v16"/>',
            'shield': '<path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/>',
            'check-circle': '<path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"/><polyline points="22 4 12 14.01 9 11.01"/>',
            'x-circle': '<circle cx="12" cy="12" r="10"/><line x1="15" y1="9" x2="9" y2="15"/><line x1="9" y1="9" x2="15" y2="15"/>',
            'clock': '<circle cx="12" cy="12" r="10"/><polyline points="12 6 12 12 16 14"/>',
            'credit-card': '<rect x="1" y="4" width="22" height="16" rx="2" ry="2"/><line x1="1" y1="10" x2="23" y2="10"/>',
            'rotate-ccw': '<polyline points="1 4 1 10 7 10"/><path d="M3.51 15a9 9 0 1 0 2.13-9.36L1 10"/>',
            'edit': '<path d="M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7"/><path d="M18.5 2.5a2.121 2.121 0 0 1 3 3L12 15l-4 1 1-4 9.5-9.5z"/>',
            'calendar': '<rect x="3" y="4" width="18" height="18" rx="2" ry="2"/><line x1="16" y1="2" x2="16" y2="6"/><line x1="8" y1="2" x2="8" y2="6"/><line x1="3" y1="10" x2="21" y2="10"/>',
            'file-text': '<path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><polyline points="14 2 14 8 20 8"/><line x1="16" y1="13" x2="8" y2="13"/><line x1="16" y1="17" x2="8" y2="17"/><line x1="10" y1="9" x2="8" y2="9"/>',
            'sliders': '<line x1="4" y1="21" x2="4" y2="14"/><line x1="4" y1="10" x2="4" y2="3"/><line x1="12" y1="21" x2="12" y2="12"/><line x1="12" y1="8" x2="12" y2="3"/><line x1="20" y1="21" x2="20" y2="16"/><line x1="20" y1="12" x2="20" y2="3"/><line x1="1" y1="14" x2="7" y2="14"/><line x1="9" y1="8" x2="15" y2="8"/><line x1="17" y1="16" x2="23" y2="16"/>',
            'user-check': '<path d="M16 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"/><circle cx="8.5" cy="7" r="4"/><polyline points="17 11 19 13 23 9"/>',
            'user-x': '<path d="M16 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"/><circle cx="8.5" cy="7" r="4"/><line x1="18" y1="8" x2="23" y2="13"/><line x1="23" y1="8" x2="18" y2="13"/>',
            'home': '<path d="M3 9l9-7 9 7v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z"/><polyline points="9 22 9 12 15 12 15 22"/>',
            'building': '<rect x="4" y="2" width="16" height="20" rx="2" ry="2"/><path d="M9 22v-4h6v4"/><path d="M8 6h.01"/><path d="M16 6h.01"/><path d="M12 6h.01"/><path d="M12 10h.01"/><path d="M12 14h.01"/><path d="M16 10h.01"/><path d="M16 14h.01"/><path d="M8 10h.01"/><path d="M8 14h.01"/>',
            'list': '<line x1="8" y1="6" x2="21" y2="6"/><line x1="8" y1="12" x2="21" y2="12"/><line x1="8" y1="18" x2="21" y2="18"/><line x1="3" y1="6" x2="3.01" y2="6"/><line x1="3" y1="12" x2="3.01" y2="12"/><line x1="3" y1="18" x2="3.01" y2="18"/>'
        };

        return `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">${icons[iconName] || icons['list']}</svg>`;
    }

    nextStep() {
        if (this.currentStep < this.totalSteps) {
            this.currentStep++;
            this.updateUI();
        } else {
            // Apply filters
            this.applyFilters();
        }
    }

    previousStep() {
        if (this.currentStep > 1) {
            this.currentStep--;
            this.updateUI();
        }
    }

    updateUI() {
        // Update steps
        document.querySelectorAll('.wizard-step').forEach(step => {
            step.classList.remove('active');
        });
        document.querySelector(`.wizard-step[data-step="${this.currentStep}"]`).classList.add('active');

        // Update progress
        document.querySelectorAll('.progress-step').forEach((step, index) => {
            const stepNum = index + 1;
            step.classList.remove('active', 'completed');

            if (stepNum < this.currentStep) {
                step.classList.add('completed');
                step.querySelector('.progress-step-circle').innerHTML = `
                    <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="3">
                        <polyline points="20 6 9 17 4 12"/>
                    </svg>
                `;
            } else if (stepNum === this.currentStep) {
                step.classList.add('active');
                step.querySelector('.progress-step-circle').textContent = stepNum;
            } else {
                step.querySelector('.progress-step-circle').textContent = stepNum;
            }
        });

        // Update progress line
        const progress = ((this.currentStep - 1) / (this.totalSteps - 1)) * 100;
        document.getElementById('progressLineFill').style.width = `${progress}%`;

        // Update buttons
        const prevBtn = document.getElementById('wizardPrevBtn');
        const nextBtn = document.getElementById('wizardNextBtn');

        prevBtn.style.display = this.currentStep > 1 ? 'flex' : 'none';

        if (this.currentStep === this.totalSteps) {
            nextBtn.querySelector('span').textContent = 'تطبيق الفلتر';
            nextBtn.querySelector('span').setAttribute('data-i18n', 'applyBtn');
        } else {
            nextBtn.querySelector('span').textContent = 'التالي';
            nextBtn.querySelector('span').setAttribute('data-i18n', 'nextBtn');
        }

        // Disable next button if no selection made for current step
        nextBtn.disabled = !this.selectedFilters[`step${this.currentStep}`];
    }

    applyFilters() {
        console.log('Applying filters:', this.selectedFilters);

        // Here you would implement the actual filter logic
        // For now, we'll just show a success message and close

        // You can emit a custom event that the main app can listen to
        const event = new CustomEvent('filtersApplied', {
            detail: this.selectedFilters
        });
        document.dispatchEvent(event);

        this.close();
    }
}

// Initialize the wizard when DOM is ready
let filterWizard;
document.addEventListener('DOMContentLoaded', () => {
    filterWizard = new FilterWizard();
});

// Function to open the wizard (can be called from anywhere)
function openFilterWizard() {
    if (filterWizard) {
        filterWizard.open();
    }
}
