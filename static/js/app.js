// State management
const state = {
    currentPage: 1,
    generationId: null,
    selectedImageIndex: null,
    selectedImageUrl: null,
    platforms: {},
    currentPlatform: 'Hashnode'
};

// DOM elements
const pages = {
    1: document.getElementById('page-1'),
    2: document.getElementById('page-2')
};

const elements = {
    generateForm: document.getElementById('generate-form'),
    generateBtn: document.getElementById('generate-btn'),
    btnText: document.querySelector('.btn-text'),
    loader: document.querySelector('.loader'),
    customPrompt: document.getElementById('custom-prompt'),
    articleTitle: document.getElementById('article-title'),
    draftLink: document.getElementById('draft-link'),
    styleSelect: document.getElementById('style'),
    imageGrid: document.getElementById('image-grid'),
    selectionView: document.getElementById('selection-view'),
    splitView: document.getElementById('split-view'),
    backToInput: document.getElementById('back-to-input'),
    backToSelection: document.getElementById('back-to-selection'),
    previewImage: document.getElementById('preview-image'),
    dimensionLabel: document.getElementById('dimension-label'),
    platformSelector: document.getElementById('platform-selector'),
    customDims: document.getElementById('custom-dims'),
    widthInput: document.getElementById('width'),
    heightInput: document.getElementById('height'),
    downloadBtn: document.getElementById('download-btn'),
    textOverlay: document.getElementById('text-overlay'),
    overlayText: document.getElementById('overlay-text'),
    textFont: document.getElementById('text-font'),
    textSize: document.getElementById('text-size'),
    colorPresets: document.querySelectorAll('.color-preset'),
    textColorCustom: document.getElementById('text-color-custom'),
    textPosition: document.getElementById('text-position'),
    textShadow: document.getElementById('text-shadow')
};

// Initialize app
document.addEventListener('DOMContentLoaded', () => {
    initializeApp();
    attachEventListeners();
});

async function initializeApp() {
    await fetchStyles();
    await fetchPlatforms();
}

function attachEventListeners() {
    elements.generateForm.addEventListener('submit', handleGenerate);
    elements.backToInput.addEventListener('click', () => navigateToPage(1));
    elements.backToSelection.addEventListener('click', showSelectionView);
    elements.downloadBtn.addEventListener('click', handleDownload);

    // Custom dimension inputs
    elements.widthInput.addEventListener('input', handleCustomDimensionChange);
    elements.heightInput.addEventListener('input', handleCustomDimensionChange);

    // Text overlay inputs
    elements.overlayText.addEventListener('input', updateTextOverlay);
    elements.textFont.addEventListener('change', updateTextOverlay);
    elements.textSize.addEventListener('change', updateTextOverlay);

    // Color presets
    elements.colorPresets.forEach(preset => {
        preset.addEventListener('click', handleColorPresetClick);
    });
    elements.textColorCustom.addEventListener('input', handleCustomColorChange);

    elements.textPosition.addEventListener('change', updateTextOverlay);
    elements.textShadow.addEventListener('change', updateTextOverlay);
}

// Fetch available styles
async function fetchStyles() {
    try {
        const response = await fetch('/api/styles');
        const styles = await response.json();

        styles.forEach(style => {
            const option = document.createElement('option');
            option.value = style;
            option.textContent = style;
            elements.styleSelect.appendChild(option);
        });
    } catch (error) {
        console.error('Error fetching styles:', error);
    }
}

// Fetch platform configurations
async function fetchPlatforms() {
    try {
        const response = await fetch('/api/platforms');
        state.platforms = await response.json();

        renderPlatformOptions();
    } catch (error) {
        console.error('Error fetching platforms:', error);
    }
}

// Render platform selector options
function renderPlatformOptions() {
    elements.platformSelector.innerHTML = '';

    Object.entries(state.platforms).forEach(([name, dims]) => {
        const option = document.createElement('div');
        option.className = 'platform-option';
        option.dataset.platform = name;

        if (name === state.currentPlatform) {
            option.classList.add('selected');
        }

        const header = document.createElement('div');
        header.className = 'platform-option-header';

        const platformName = document.createElement('div');
        platformName.className = 'platform-name';
        platformName.textContent = name;

        const platformDims = document.createElement('div');
        platformDims.className = 'platform-dims';
        platformDims.textContent = name === 'Custom' ? 'Custom size' : `${dims.width} × ${dims.height}px`;

        header.appendChild(platformName);
        header.appendChild(platformDims);
        option.appendChild(header);

        option.addEventListener('click', () => handlePlatformSelect(name));

        elements.platformSelector.appendChild(option);
    });
}

// Handle platform selection
function handlePlatformSelect(platformName) {
    state.currentPlatform = platformName;

    // Update UI
    document.querySelectorAll('.platform-option').forEach(opt => {
        opt.classList.remove('selected');
    });
    document.querySelector(`[data-platform="${platformName}"]`).classList.add('selected');

    // Show/hide custom dimensions
    if (platformName === 'Custom') {
        elements.customDims.classList.remove('hidden');
        updatePreviewDimensions(
            parseInt(elements.widthInput.value) || 1200,
            parseInt(elements.heightInput.value) || 630
        );
    } else {
        elements.customDims.classList.add('hidden');
        const dims = state.platforms[platformName];
        updatePreviewDimensions(dims.width, dims.height);
    }
}

// Handle custom dimension changes
function handleCustomDimensionChange() {
    if (state.currentPlatform === 'Custom') {
        const width = parseInt(elements.widthInput.value) || 1200;
        const height = parseInt(elements.heightInput.value) || 630;
        updatePreviewDimensions(width, height);
    }
}

// Handle color preset button click
function handleColorPresetClick(e) {
    const preset = e.currentTarget;
    const color = preset.dataset.color;

    // Remove active class from all presets
    elements.colorPresets.forEach(p => p.classList.remove('active'));

    // Add active class to clicked preset
    preset.classList.add('active');

    // Update color picker value
    elements.textColorCustom.value = color;

    // Update overlay
    updateTextOverlay();
}

// Handle custom color picker change
function handleCustomColorChange() {
    // Remove active class from all preset buttons
    elements.colorPresets.forEach(p => p.classList.remove('active'));

    // Update overlay
    updateTextOverlay();
}

// Get current text color (always from color picker)
function getCurrentTextColor() {
    return elements.textColorCustom.value;
}

// Update text overlay preview
function updateTextOverlay() {
    const text = elements.overlayText.value;  // Keep whitespace/line breaks
    const font = elements.textFont.value;
    const size = elements.textSize.value;
    const color = getCurrentTextColor();
    const position = elements.textPosition.value;
    const shadow = elements.textShadow.checked;  // Changed from value to checked

    if (!text.trim()) {
        elements.textOverlay.classList.add('hidden');
        return;
    }

    // Show overlay and update properties
    elements.textOverlay.classList.remove('hidden');
    elements.textOverlay.textContent = text;
    elements.textOverlay.style.fontFamily = font;
    elements.textOverlay.style.fontSize = size + 'px';
    elements.textOverlay.style.color = color;

    // Update shadow
    if (shadow) {
        elements.textOverlay.style.textShadow = '2px 2px 4px rgba(0, 0, 0, 0.8)';
    } else {
        elements.textOverlay.style.textShadow = 'none';
    }

    // Remove all position classes
    elements.textOverlay.classList.remove('top-left', 'top-center', 'top-right', 'center', 'bottom-left', 'bottom-center', 'bottom-right');

    // Add current position class
    elements.textOverlay.classList.add(position);
}

// Update preview image dimensions with animation
function updatePreviewDimensions(width, height) {
    // Update dimension label with animation
    elements.dimensionLabel.style.opacity = '0';

    setTimeout(() => {
        elements.dimensionLabel.textContent = `${width} × ${height}px`;
        elements.dimensionLabel.style.opacity = '1';
    }, 150);

    // Update image preview (visual representation)
    // Note: This is a visual update only. Actual resizing happens on download.
    const aspectRatio = width / height;
    const currentWidth = elements.previewImage.naturalWidth;
    const currentHeight = elements.previewImage.naturalHeight;
    const currentRatio = currentWidth / currentHeight;

    // Add subtle scale animation to indicate dimension change
    elements.previewImage.style.transform = 'scale(0.98)';
    setTimeout(() => {
        elements.previewImage.style.transform = 'scale(1)';
    }, 150);
}

// Handle form submission
async function handleGenerate(e) {
    e.preventDefault();

    const customPrompt = elements.customPrompt.value.trim();
    const articleTitle = elements.articleTitle.value.trim();
    const draftLink = elements.draftLink.value.trim();
    const style = elements.styleSelect.value;

    // Validation
    if (!customPrompt && !articleTitle) {
        alert('Please enter either a custom prompt or an article title.');
        return;
    }

    // Prepare request data
    const requestData = {
        style: style
    };

    if (customPrompt) {
        requestData.title = customPrompt;
    } else {
        requestData.title = articleTitle;
    }

    // Add draft link if provided
    if (draftLink) {
        requestData.draft_link = draftLink;
    }

    setLoading(true);

    try {
        const response = await fetch('/api/generate', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(requestData)
        });

        const data = await response.json();

        if (response.ok) {
            state.generationId = data.generation_id;
            displayImages(data.images);
            navigateToPage(2);
        } else {
            alert('Error generating images: ' + data.error);
        }
    } catch (error) {
        console.error('Error:', error);
        alert('An unexpected error occurred. Please try again.');
    } finally {
        setLoading(false);
    }
}

// Display generated images on page 2
function displayImages(images) {
    elements.imageGrid.innerHTML = '';

    images.forEach((imageUrl, index) => {
        const card = document.createElement('div');
        card.className = 'image-card';
        card.setAttribute('tabindex', '0');
        card.setAttribute('role', 'button');
        card.setAttribute('aria-label', `Select image ${index + 1}`);

        const img = document.createElement('img');
        img.src = imageUrl;
        img.alt = `Generated Image ${index + 1}`;

        card.appendChild(img);

        // Click handler
        card.addEventListener('click', () => selectImage(index, imageUrl, card));

        // Keyboard support
        card.addEventListener('keydown', (e) => {
            if (e.key === 'Enter' || e.key === ' ') {
                e.preventDefault();
                selectImage(index, imageUrl, card);
            }
        });

        elements.imageGrid.appendChild(card);
    });
}

// Handle image selection
function selectImage(index, imageUrl, cardElement) {
    state.selectedImageIndex = index;
    state.selectedImageUrl = imageUrl;

    // Update UI
    document.querySelectorAll('.image-card').forEach(c => c.classList.remove('selected'));
    cardElement.classList.add('selected');

    // Animate the clicked image to the left position
    animateImageToPreview(cardElement, imageUrl);
}

// Animate clicked image to preview position on the left
function animateImageToPreview(cardElement, imageUrl) {
    // Get the position of the clicked card
    const cardRect = cardElement.getBoundingClientRect();

    // Calculate target position to match where the preview image will be
    // Preview panel is 50% of screen, with 90% max-width for the image wrapper
    const previewPanelWidth = window.innerWidth * 0.5; // 50% (left half)
    const targetWidth = previewPanelWidth * 0.9; // 90% of preview panel (matches .preview-wrapper max-width)
    const targetHeight = (cardRect.height / cardRect.width) * targetWidth;

    // Center in the preview panel area
    const previewPanelLeft = 0;
    const targetLeft = previewPanelLeft + (previewPanelWidth - targetWidth) / 2;
    const targetTop = (window.innerHeight - targetHeight) / 2; // Vertically centered

    // Clone the card for animation
    const clone = cardElement.cloneNode(true);
    clone.classList.add('transitioning');
    clone.style.position = 'fixed';
    clone.style.top = cardRect.top + 'px';
    clone.style.left = cardRect.left + 'px';
    clone.style.width = cardRect.width + 'px';
    clone.style.height = cardRect.height + 'px';
    clone.style.margin = '0';
    clone.style.zIndex = '1001';

    document.body.appendChild(clone);

    // Fade out the selection view immediately
    elements.selectionView.classList.add('fade-out');

    // Setup the split view in the background (but keep preview image hidden)
    setupPreviewPanel(imageUrl);
    elements.splitView.classList.remove('hidden');
    // Keep preview image hidden during animation
    elements.previewImage.classList.remove('visible');

    // Use requestAnimationFrame to ensure the starting position is rendered
    // before triggering the transition
    requestAnimationFrame(() => {
        requestAnimationFrame(() => {
            // Show split view (this will trigger settings fade-up)
            elements.splitView.classList.add('active');

            // Animate the clone to the preview position
            clone.style.top = targetTop + 'px';
            clone.style.left = targetLeft + 'px';
            clone.style.width = targetWidth + 'px';
            clone.style.height = targetHeight + 'px';
        });
    });

    // After image animation completes, remove clone and show real preview image
    setTimeout(() => {
        // Remove the clone
        clone.remove();

        // Show the real preview image
        elements.previewImage.classList.add('visible');

        // Hide selection view completely
        elements.selectionView.classList.add('hidden');
    }, 750);
}

// Setup preview panel
function setupPreviewPanel(imageUrl) {
    elements.previewImage.src = imageUrl;

    // Set initial platform
    state.currentPlatform = 'Hashnode';
    renderPlatformOptions();

    const dims = state.platforms['Hashnode'];
    updatePreviewDimensions(dims.width, dims.height);
}

// Show selection view (fade in selection view, hide split view)
function showSelectionView() {
    // Hide split view
    elements.splitView.classList.remove('active');

    // Show selection view and remove fade-out class
    elements.selectionView.classList.remove('hidden');
    elements.selectionView.classList.remove('fade-out');

    // After transition, hide split view completely
    setTimeout(() => {
        elements.splitView.classList.add('hidden');
    }, 600);
}

// Page navigation with transitions
function navigateToPage(pageNumber) {
    const currentPage = pages[state.currentPage];
    const nextPage = pages[pageNumber];

    if (!currentPage || !nextPage || state.currentPage === pageNumber) return;

    // If going back to page 1, reset page 2 to selection view
    if (pageNumber === 1) {
        resetPage2();
    }

    // Determine animation direction
    const isForward = pageNumber > state.currentPage;

    // Remove active class from current page
    currentPage.classList.remove('active');

    // Add exit animation
    if (isForward) {
        currentPage.classList.add('slide-out-left');
    } else {
        currentPage.classList.add('slide-out-right');
    }

    // After animation, show next page
    setTimeout(() => {
        // Clean up current page
        currentPage.classList.remove('slide-out-left', 'slide-out-right');
        currentPage.style.display = 'none';

        // Show next page
        nextPage.style.display = 'block';
        nextPage.classList.add('active');

        // Add entrance animation
        if (isForward) {
            nextPage.classList.add('slide-in-right');
        } else {
            nextPage.classList.add('slide-in-left');
        }

        // Clean up animation classes
        setTimeout(() => {
            nextPage.classList.remove('slide-in-right', 'slide-in-left');
        }, 400);

        // Update state
        state.currentPage = pageNumber;

        // Scroll to top
        window.scrollTo(0, 0);
    }, 400);
}

// Reset page 2 to selection view
function resetPage2() {
    elements.splitView.classList.remove('active');
    elements.splitView.classList.add('hidden');
    elements.selectionView.classList.remove('hidden');
    elements.selectionView.classList.remove('fade-out');
}

// Handle download
async function handleDownload() {
    if (!state.generationId || state.selectedImageIndex === null) {
        alert('No image selected for download.');
        return;
    }

    const platform = state.currentPlatform;
    const payload = {
        generation_id: state.generationId,
        selected_image_index: state.selectedImageIndex,
        platform: platform
    };

    // Add custom dimensions if platform is Custom
    if (platform === 'Custom') {
        const width = parseInt(elements.widthInput.value);
        const height = parseInt(elements.heightInput.value);

        if (!width || !height || width < 100 || height < 100) {
            alert('Please specify valid width and height (minimum 100px).');
            return;
        }

        payload.custom_dims = { width, height };
    }

    // Add text overlay if text is provided
    const overlayText = elements.overlayText.value;
    if (overlayText.trim()) {
        payload.text_overlay = {
            text: overlayText,  // Keep line breaks
            font: elements.textFont.value,
            size: parseInt(elements.textSize.value),
            color: getCurrentTextColor(),
            position: elements.textPosition.value,
            shadow: elements.textShadow.checked  // Changed from value === 'true' to checked
        };
    }

    try {
        setDownloadLoading(true);

        const response = await fetch('/api/download', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(payload)
        });

        if (response.ok) {
            const blob = await response.blob();
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = `blog-cover-${platform.toLowerCase()}.png`;
            document.body.appendChild(a);
            a.click();
            window.URL.revokeObjectURL(url);
            a.remove();
        } else {
            const data = await response.json();
            alert('Error downloading image: ' + data.error);
        }
    } catch (error) {
        console.error('Error:', error);
        alert('An unexpected error occurred during download.');
    } finally {
        setDownloadLoading(false);
    }
}

// Set loading state for generate button
function setLoading(isLoading) {
    if (isLoading) {
        elements.generateBtn.disabled = true;
        elements.btnText.textContent = 'Generating...';
        elements.loader.classList.remove('hidden');
    } else {
        elements.generateBtn.disabled = false;
        elements.btnText.textContent = '✨ Generate Images';
        elements.loader.classList.add('hidden');
    }
}

// Set loading state for download button
function setDownloadLoading(isLoading) {
    if (isLoading) {
        elements.downloadBtn.disabled = true;
        elements.downloadBtn.textContent = 'Downloading...';
    } else {
        elements.downloadBtn.disabled = false;
        elements.downloadBtn.textContent = '⬇ Download Image';
    }
}
