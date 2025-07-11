/**
 * BaytAlSudani Dashboard - Main JavaScript
 * Arabic RTL Dashboard Application
 */

// Global configuration
const App = {
    config: {
        language: 'ar',
        direction: 'rtl',
        currency: 'ج.س',
        dateFormat: 'DD/MM/YYYY',
        timeFormat: 'HH:mm'
    },
    
    // Initialize application
    init() {
        this.setupFormValidation();
        this.setupTooltips();
        this.setupConfirmDialogs();
        this.setupAjaxDefaults();
        this.setupAutoRefresh();
        this.setupKeyboardShortcuts();
        this.setupTheme();
        console.log('BaytAlSudani Dashboard initialized successfully');
    }
};

// Form Validation Enhancement
App.setupFormValidation = function() {
    // Bootstrap form validation
    const forms = document.querySelectorAll('.needs-validation');
    
    forms.forEach(form => {
        form.addEventListener('submit', event => {
            if (!form.checkValidity()) {
                event.preventDefault();
                event.stopPropagation();
                
                // Focus on first invalid field
                const firstInvalid = form.querySelector(':invalid');
                if (firstInvalid) {
                    firstInvalid.focus();
                    firstInvalid.scrollIntoView({ behavior: 'smooth', block: 'center' });
                }
            }
            form.classList.add('was-validated');
        });
        
        // Real-time validation
        const inputs = form.querySelectorAll('input, select, textarea');
        inputs.forEach(input => {
            input.addEventListener('blur', () => {
                if (form.classList.contains('was-validated')) {
                    input.checkValidity();
                }
            });
        });
    });
    
    // Custom validators
    this.setupCustomValidators();
};

// Custom form validators
App.setupCustomValidators = function() {
    // Arabic phone number validation
    const phoneInputs = document.querySelectorAll('input[type="tel"]');
    phoneInputs.forEach(input => {
        input.addEventListener('input', function() {
            const value = this.value.replace(/\s/g, '');
            const phoneRegex = /^(\+249|0)?[1-9]\d{8}$/;
            
            if (value && !phoneRegex.test(value)) {
                this.setCustomValidity('يرجى إدخال رقم هاتف صحيح (مثال: +249123456789)');
            } else {
                this.setCustomValidity('');
            }
        });
    });
    
    // Price validation
    const priceInputs = document.querySelectorAll('input[name="price"]');
    priceInputs.forEach(input => {
        input.addEventListener('input', function() {
            const value = parseFloat(this.value);
            if (value < 0) {
                this.setCustomValidity('السعر يجب أن يكون أكبر من أو يساوي الصفر');
            } else {
                this.setCustomValidity('');
            }
        });
    });
};

// Setup tooltips
App.setupTooltips = function() {
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function(tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl, {
            placement: 'top',
            trigger: 'hover'
        });
    });
};

// Confirm dialogs for destructive actions
App.setupConfirmDialogs = function() {
    const deleteButtons = document.querySelectorAll('form[onsubmit*="confirm"]');
    deleteButtons.forEach(form => {
        form.addEventListener('submit', function(e) {
            e.preventDefault();
            
            const confirmation = confirm('هل أنت متأكد من هذا الإجراء؟ لا يمكن التراجع عنه.');
            if (confirmation) {
                this.submit();
            }
        });
    });
};

// AJAX defaults and error handling
App.setupAjaxDefaults = function() {
    // Show loading state on AJAX requests
    document.addEventListener('htmx:beforeRequest', function(evt) {
        const target = evt.target;
        target.classList.add('loading');
        
        // Show loading spinner if button
        if (target.tagName === 'BUTTON') {
            const originalText = target.innerHTML;
            target.dataset.originalText = originalText;
            target.innerHTML = '<i class="fas fa-spinner fa-spin me-1"></i>جاري التحميل...';
            target.disabled = true;
        }
    });
    
    document.addEventListener('htmx:afterRequest', function(evt) {
        const target = evt.target;
        target.classList.remove('loading');
        
        // Restore button text
        if (target.tagName === 'BUTTON' && target.dataset.originalText) {
            target.innerHTML = target.dataset.originalText;
            target.disabled = false;
            delete target.dataset.originalText;
        }
    });
    
    // Handle errors
    document.addEventListener('htmx:responseError', function(evt) {
        console.error('HTMX Error:', evt.detail);
        App.showAlert('حدث خطأ في الاتصال بالخادم', 'error');
    });
};

// Auto-refresh functionality
App.setupAutoRefresh = function() {
    const autoRefreshElements = document.querySelectorAll('[data-auto-refresh]');
    
    autoRefreshElements.forEach(element => {
        const interval = parseInt(element.dataset.autoRefresh) || 30000; // Default 30 seconds
        
        setInterval(() => {
            if (document.visibilityState === 'visible') {
                location.reload();
            }
        }, interval);
    });
};

// Keyboard shortcuts
App.setupKeyboardShortcuts = function() {
    document.addEventListener('keydown', function(e) {
        // Ctrl/Cmd + Enter to submit forms
        if ((e.ctrlKey || e.metaKey) && e.key === 'Enter') {
            const activeForm = document.activeElement.closest('form');
            if (activeForm) {
                const submitButton = activeForm.querySelector('button[type="submit"]');
                if (submitButton) {
                    submitButton.click();
                }
            }
        }
        
        // Escape to close modals
        if (e.key === 'Escape') {
            const openModal = document.querySelector('.modal.show');
            if (openModal) {
                const modal = bootstrap.Modal.getInstance(openModal);
                if (modal) {
                    modal.hide();
                }
            }
        }
    });
};

// Theme management
App.setupTheme = function() {
    const themeToggle = document.querySelector('#theme-toggle');
    const currentTheme = localStorage.getItem('theme') || 'light';
    
    document.documentElement.setAttribute('data-theme', currentTheme);
    
    if (themeToggle) {
        themeToggle.addEventListener('click', function() {
            const currentTheme = document.documentElement.getAttribute('data-theme');
            const newTheme = currentTheme === 'dark' ? 'light' : 'dark';
            
            document.documentElement.setAttribute('data-theme', newTheme);
            localStorage.setItem('theme', newTheme);
        });
    }
};

// Utility functions
App.utils = {
    // Format currency
    formatCurrency(amount) {
        return new Intl.NumberFormat('ar-SD', {
            style: 'currency',
            currency: 'SDG',
            minimumFractionDigits: 0
        }).format(amount) + ' ' + App.config.currency;
    },
    
    // Format date
    formatDate(date) {
        return new Intl.DateTimeFormat('ar-SD').format(new Date(date));
    },
    
    // Format time
    formatTime(date) {
        return new Intl.DateTimeFormat('ar-SD', {
            hour: '2-digit',
            minute: '2-digit'
        }).format(new Date(date));
    },
    
    // Debounce function
    debounce(func, wait) {
        let timeout;
        return function executedFunction(...args) {
            const later = () => {
                clearTimeout(timeout);
                func(...args);
            };
            clearTimeout(timeout);
            timeout = setTimeout(later, wait);
        };
    },
    
    // Show alert message
    showAlert(message, type = 'info') {
        const alertContainer = document.querySelector('#alert-container') || document.body;
        const alertId = 'alert-' + Date.now();
        
        const alertHTML = `
            <div id="${alertId}" class="alert alert-${type === 'error' ? 'danger' : type} alert-dismissible fade show" role="alert">
                <i class="fas fa-${this.getAlertIcon(type)} me-2"></i>
                ${message}
                <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
            </div>
        `;
        
        alertContainer.insertAdjacentHTML('afterbegin', alertHTML);
        
        // Auto-dismiss after 5 seconds
        setTimeout(() => {
            const alert = document.getElementById(alertId);
            if (alert) {
                const bsAlert = new bootstrap.Alert(alert);
                bsAlert.close();
            }
        }, 5000);
    },
    
    // Get icon for alert type
    getAlertIcon(type) {
        const icons = {
            success: 'check-circle',
            error: 'exclamation-triangle',
            warning: 'exclamation-triangle',
            info: 'info-circle'
        };
        return icons[type] || 'info-circle';
    },
    
    // Copy to clipboard
    copyToClipboard(text) {
        navigator.clipboard.writeText(text).then(() => {
            this.showAlert('تم النسخ إلى الحافظة', 'success');
        }).catch(() => {
            this.showAlert('فشل في النسخ', 'error');
        });
    },
    
    // Scroll to element
    scrollToElement(selector, offset = 0) {
        const element = document.querySelector(selector);
        if (element) {
            const elementPosition = element.getBoundingClientRect().top;
            const offsetPosition = elementPosition + window.pageYOffset - offset;
            
            window.scrollTo({
                top: offsetPosition,
                behavior: 'smooth'
            });
        }
    }
};

// Add utility methods to App object
Object.assign(App, {
    formatCurrency: App.utils.formatCurrency,
    formatDate: App.utils.formatDate,
    formatTime: App.utils.formatTime,
    showAlert: App.utils.showAlert,
    copyToClipboard: App.utils.copyToClipboard,
    scrollToElement: App.utils.scrollToElement
});

// Modal management
App.modal = {
    show(modalId, data = {}) {
        const modalElement = document.getElementById(modalId);
        if (modalElement) {
            const modal = new bootstrap.Modal(modalElement);
            
            // Fill modal with data if provided
            if (Object.keys(data).length > 0) {
                this.fillModalData(modalElement, data);
            }
            
            modal.show();
            return modal;
        }
    },
    
    hide(modalId) {
        const modalElement = document.getElementById(modalId);
        if (modalElement) {
            const modal = bootstrap.Modal.getInstance(modalElement);
            if (modal) {
                modal.hide();
            }
        }
    },
    
    fillModalData(modalElement, data) {
        Object.keys(data).forEach(key => {
            const input = modalElement.querySelector(`[name="${key}"], #${key}`);
            if (input) {
                if (input.type === 'checkbox') {
                    input.checked = data[key];
                } else {
                    input.value = data[key];
                }
            }
        });
    }
};

// Data tables enhancement
App.dataTable = {
    init(tableSelector, options = {}) {
        const table = document.querySelector(tableSelector);
        if (!table) return;
        
        const defaultOptions = {
            searchable: true,
            sortable: true,
            pagination: true,
            pageSize: 10
        };
        
        const config = { ...defaultOptions, ...options };
        
        if (config.searchable) {
            this.addSearch(table);
        }
        
        if (config.sortable) {
            this.addSorting(table);
        }
        
        return table;
    },
    
    addSearch(table) {
        const searchInput = document.createElement('input');
        searchInput.type = 'text';
        searchInput.className = 'form-control mb-3';
        searchInput.placeholder = 'البحث...';
        
        table.parentNode.insertBefore(searchInput, table);
        
        searchInput.addEventListener('input', App.utils.debounce((e) => {
            const searchTerm = e.target.value.toLowerCase();
            const rows = table.querySelectorAll('tbody tr');
            
            rows.forEach(row => {
                const text = row.textContent.toLowerCase();
                row.style.display = text.includes(searchTerm) ? '' : 'none';
            });
        }, 300));
    },
    
    addSorting(table) {
        const headers = table.querySelectorAll('th[data-sortable]');
        
        headers.forEach(header => {
            header.style.cursor = 'pointer';
            header.innerHTML += ' <i class="fas fa-sort text-muted"></i>';
            
            header.addEventListener('click', () => {
                this.sortTable(table, header.cellIndex, header.dataset.sortType || 'string');
            });
        });
    },
    
    sortTable(table, columnIndex, type) {
        const tbody = table.querySelector('tbody');
        const rows = Array.from(tbody.querySelectorAll('tr'));
        
        rows.sort((a, b) => {
            const aValue = a.cells[columnIndex].textContent.trim();
            const bValue = b.cells[columnIndex].textContent.trim();
            
            if (type === 'number') {
                return parseFloat(aValue) - parseFloat(bValue);
            } else if (type === 'date') {
                return new Date(aValue) - new Date(bValue);
            } else {
                return aValue.localeCompare(bValue, 'ar');
            }
        });
        
        rows.forEach(row => tbody.appendChild(row));
    }
};

// Network status monitoring
App.networkMonitor = {
    init() {
        window.addEventListener('online', () => {
            App.showAlert('تم استعادة الاتصال بالإنترنت', 'success');
        });
        
        window.addEventListener('offline', () => {
            App.showAlert('تم فقدان الاتصال بالإنترنت', 'warning');
        });
    }
};

// Performance monitoring
App.performance = {
    init() {
        // Monitor page load time
        window.addEventListener('load', () => {
            const loadTime = performance.timing.loadEventEnd - performance.timing.navigationStart;
            console.log(`Page loaded in ${loadTime}ms`);
            
            if (loadTime > 3000) {
                console.warn('Slow page load detected');
            }
        });
    }
};

// Initialize when DOM is ready
document.addEventListener('DOMContentLoaded', function() {
    App.init();
    App.networkMonitor.init();
    App.performance.init();
});

// Export for global access
window.BaytAlSudani = App;
