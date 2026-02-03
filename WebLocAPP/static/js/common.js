// Common functions used across all pages

// Property management
const PROPERTY_KEY = 'locapp_current_property';
const PROPERTY_THEME_KEY = 'locapp_current_theme';

// Theme mapping by property slug
const PROPERTY_THEMES = {
    '1': 'mazet-bsa',      // Mazet BSA - Orange Provence
    '2': 'vaujany',        // Vaujany - Blue Mountain
    'mazet-bsa': 'mazet-bsa',
    'vaujany': 'vaujany'
};

// Property info cache
let propertiesCache = null;

function getCurrentPropertyId() {
    return localStorage.getItem(PROPERTY_KEY) || null;
}

function setCurrentPropertyId(propertyId) {
    localStorage.setItem(PROPERTY_KEY, propertyId);
    applyThemeForProperty(propertyId);
}

function getCurrentTheme() {
    return localStorage.getItem(PROPERTY_THEME_KEY) || 'mazet-bsa';
}

function setCurrentTheme(theme) {
    localStorage.setItem(PROPERTY_THEME_KEY, theme);
}

function getApiUrl(endpoint) {
    const propertyId = getCurrentPropertyId();
    if (!propertyId) {
        return endpoint; // No property ID, API will return empty data
    }
    const separator = endpoint.includes('?') ? '&' : '?';
    return `${endpoint}${separator}property_id=${propertyId}`;
}

// Apply theme based on property
function applyThemeForProperty(propertyId) {
    const theme = PROPERTY_THEMES[propertyId] || 'mazet-bsa';
    document.documentElement.setAttribute('data-theme', theme);
    document.body.setAttribute('data-theme', theme);
    setCurrentTheme(theme);

    // Get property display info
    const propInfo = getPropertyDisplayInfo(propertyId);

    // Update brand icon based on theme
    const brandIcon = document.querySelector('.brand-icon');
    if (brandIcon) {
        brandIcon.textContent = propInfo.icon;
    }

    // Update property location
    const locationText = document.querySelector('.location-text');
    if (locationText) {
        locationText.textContent = propInfo.location;
    }

    console.log(`Theme applied: ${theme} for property ${propertyId}`);
}

// Initialize theme on page load
function initTheme() {
    const propertyId = getCurrentPropertyId();
    if (propertyId) {
        applyThemeForProperty(propertyId);
    }
}

// Show alert message
function showAlert(message, type = 'info') {
    const alertContainer = document.getElementById('alert-container');
    if (!alertContainer) return;

    const alert = document.createElement('div');
    alert.className = `alert alert-${type} show`;
    alert.textContent = message;

    alertContainer.appendChild(alert);

    setTimeout(() => {
        alert.classList.remove('show');
        setTimeout(() => alert.remove(), 300);
    }, 3000);
}

// Get authentication headers (uses session-based auth, no credentials needed)
function getAuthHeaders() {
    return {
        'Content-Type': 'application/json'
    };
}

// Generic fetch with error handling (uses property_id automatically)
async function fetchAPI(url, options = {}) {
    try {
        // Add property_id to URL if it's an API call (except for /api/properties)
        const finalUrl = url.startsWith('/api/') && !url.includes('/api/properties')
            ? getApiUrl(url)
            : url;
        const response = await fetch(finalUrl, options);

        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }

        return await response.json();
    } catch (error) {
        console.error('Fetch error:', error);
        showAlert('Erreur de connexion: ' + error.message, 'error');
        throw error;
    }
}

// Fetch properties list
async function fetchProperties() {
    if (propertiesCache) return propertiesCache;

    try {
        const response = await fetch('/api/properties');
        if (response.ok) {
            propertiesCache = await response.json();
            return propertiesCache;
        }
    } catch (error) {
        console.error('Error fetching properties:', error);
    }
    return [];
}

// Load data into form
function loadDataIntoForm(data, formId) {
    const form = document.getElementById(formId);
    if (!form) return;

    // If no data or empty object, clear the form
    if (!data || Object.keys(data).length === 0) {
        form.reset();
        return;
    }

    Object.keys(data).forEach(key => {
        const input = form.querySelector(`[name="${key}"]`);
        if (input) {
            if (input.type === 'checkbox') {
                input.checked = data[key];
            } else {
                input.value = data[key] || '';
            }
        }
    });
}

// Get form data as object
function getFormData(formId) {
    const form = document.getElementById(formId);
    const formData = new FormData(form);
    const data = {};

    for (let [key, value] of formData.entries()) {
        const input = form.querySelector(`[name="${key}"]`);
        if (input && input.type === 'checkbox') {
            data[key] = input.checked;
        } else {
            data[key] = value;
        }
    }

    return data;
}

// Format date
function formatDate(dateString) {
    if (!dateString) return 'N/A';
    const date = new Date(dateString);
    return date.toLocaleString('fr-FR');
}

// Confirm action
function confirmAction(message) {
    return confirm(message);
}

// Show loading spinner
function showLoading(elementId) {
    const element = document.getElementById(elementId);
    if (element) {
        element.innerHTML = '<div class="spinner"></div>';
    }
}

// Hide loading spinner
function hideLoading(elementId, content = '') {
    const element = document.getElementById(elementId);
    if (element) {
        element.innerHTML = content;
    }
}

// Modal functions
function openModal(modalId) {
    const modal = document.getElementById(modalId);
    if (modal) {
        modal.classList.add('show');
    }
}

function closeModal(modalId) {
    const modal = document.getElementById(modalId);
    if (modal) {
        modal.classList.remove('show');
    }
}

// Close modal on outside click
document.addEventListener('click', function(event) {
    if (event.target.classList.contains('modal')) {
        event.target.classList.remove('show');
    }
});

// Check if user has any properties
function hasUserProperties() {
    const selector = document.getElementById('property-selector');
    if (!selector) return false;
    const propertyOptions = Array.from(selector.options).filter(opt => opt.value !== 'new' && opt.value !== '');
    return propertyOptions.length > 0;
}

// Property selector functions
function initPropertySelector() {
    const selector = document.getElementById('property-selector');
    if (!selector) return;

    // Check if we're on the new property page
    const isNewPropertyPage = window.location.pathname === '/property/new';

    if (isNewPropertyPage) {
        // Keep "Nouvelle Propriété..." selected
        selector.value = 'new';
        return;
    }

    // Check if user has any properties (excluding the "new" option)
    const propertyOptions = Array.from(selector.options).filter(opt => opt.value !== 'new' && opt.value !== '');

    if (propertyOptions.length === 0) {
        // User has no properties - clear localStorage
        localStorage.removeItem(PROPERTY_KEY);
        console.log('User has no properties - fields will be empty');
        return;
    }

    // Get stored property ID
    let currentPropertyId = localStorage.getItem(PROPERTY_KEY);

    // Verify that the stored property ID exists in user's properties
    const validPropertyIds = propertyOptions.map(opt => opt.value);
    if (!currentPropertyId || !validPropertyIds.includes(currentPropertyId)) {
        // Use first available property
        currentPropertyId = propertyOptions[0].value;
        localStorage.setItem(PROPERTY_KEY, currentPropertyId);
    }

    // Set current selection
    selector.value = currentPropertyId;

    // Apply theme immediately
    applyThemeForProperty(currentPropertyId);

    // Update active indicator
    updatePropertyIndicator();

    // Listen for changes
    selector.addEventListener('change', function() {
        const newPropertyId = this.value;
        setCurrentPropertyId(newPropertyId);
        updatePropertyIndicator();

        // Reload page data
        if (typeof loadData === 'function') {
            loadData();
        } else {
            // Reload page if no loadData function exists
            window.location.reload();
        }
    });
}

function updatePropertyIndicator() {
    const selector = document.getElementById('property-selector');
    const indicator = document.getElementById('current-property-name');
    if (selector && indicator) {
        const selectedOption = selector.options[selector.selectedIndex];
        indicator.textContent = selectedOption ? selectedOption.text : '';
    }
}

// Get property info for display
function getPropertyDisplayInfo(propertyId) {
    const id = String(propertyId);
    if (id === '1' || id === 'mazet-bsa') {
        return {
            name: 'Mazet BSA',
            icon: '🏡',
            theme: 'mazet-bsa',
            location: 'Ardèche',
            accentColor: '#D4A574'
        };
    } else if (id === '2' || id === 'vaujany') {
        return {
            name: 'Vaujany',
            icon: '🏔️',
            theme: 'vaujany',
            location: 'Isère',
            accentColor: '#5B8FB9'
        };
    }
    return {
        name: 'Propriété',
        icon: '🏠',
        theme: 'mazet-bsa',
        location: '',
        accentColor: '#D4A574'
    };
}

// Initialize tooltips or other common features
document.addEventListener('DOMContentLoaded', function() {
    // Initialize theme first
    initTheme();

    // Initialize property selector
    initPropertySelector();

    console.log('LocApp Admin initialized');
});
