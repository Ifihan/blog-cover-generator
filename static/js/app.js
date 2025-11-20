
const state = {
    currentPage: 1,
    generationId: null,
    selectedImageIndex: null,
    selectedImageUrl: null,
    platforms: {},
    currentPlatform: 'Hashnode'
};

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

    elements.widthInput.addEventListener('input', handleCustomDimensionChange);
    elements.heightInput.addEventListener('input', handleCustomDimensionChange);

    elements.overlayText.addEventListener('input', updateTextOverlay);
    elements.textFont.addEventListener('change', updateTextOverlay);
    elements.textSize.addEventListener('change', updateTextOverlay);

    elements.colorPresets.forEach(preset => {
        preset.addEventListener('click', handleColorPresetClick);
    });
    elements.textColorCustom.addEventListener('input', handleCustomColorChange);

    elements.textPosition.addEventListener('change', updateTextOverlay);
    elements.textShadow.addEventListener('change', updateTextOverlay);
}

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

async function fetchPlatforms() {
    try {
        const response = await fetch('/api/platforms');
        state.platforms = await response.json();

        renderPlatformOptions();
    } catch (error) {
        console.error('Error fetching platforms:', error);
    }
}

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

function handlePlatformSelect(platformName) {
    state.currentPlatform = platformName;

    document.querySelectorAll('.platform-option').forEach(opt => {
        opt.classList.remove('selected');
    });
    document.querySelector(`[data-platform="${platformName}"]`).classList.add('selected');

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

function handleCustomDimensionChange() {
    if (state.currentPlatform === 'Custom') {
        const width = parseInt(elements.widthInput.value) || 1200;
        const height = parseInt(elements.heightInput.value) || 630;
        updatePreviewDimensions(width, height);
    }
}

function handleColorPresetClick(e) {
    const preset = e.currentTarget;
    const color = preset.dataset.color;

    elements.colorPresets.forEach(p => p.classList.remove('active'));

    preset.classList.add('active');

    elements.textColorCustom.value = color;

    updateTextOverlay();
}

function handleCustomColorChange() {

    elements.colorPresets.forEach(p => p.classList.remove('active'));

    updateTextOverlay();
}

function getCurrentTextColor() {
    return elements.textColorCustom.value;
}

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

    elements.textOverlay.classList.remove('hidden');
    elements.textOverlay.textContent = text;
    elements.textOverlay.style.fontFamily = font;
    elements.textOverlay.style.fontSize = size + 'px';
    elements.textOverlay.style.color = color;

    if (shadow) {
        elements.textOverlay.style.textShadow = '2px 2px 4px rgba(0, 0, 0, 0.8)';
    } else {
        elements.textOverlay.style.textShadow = 'none';
    }

    elements.textOverlay.classList.remove('top-left', 'top-center', 'top-right', 'center', 'bottom-left', 'bottom-center', 'bottom-right');

    elements.textOverlay.classList.add(position);
}

function updatePreviewDimensions(width, height) {

    elements.dimensionLabel.style.opacity = '0';

    setTimeout(() => {
        elements.dimensionLabel.textContent = `${width} × ${height}px`;
        elements.dimensionLabel.style.opacity = '1';
    }, 150);

    const aspectRatio = width / height;
    const currentWidth = elements.previewImage.naturalWidth;
    const currentHeight = elements.previewImage.naturalHeight;
    const currentRatio = currentWidth / currentHeight;

    elements.previewImage.style.transform = 'scale(0.98)';
    setTimeout(() => {
        elements.previewImage.style.transform = 'scale(1)';
    }, 150);
}

async function handleGenerate(e) {
    e.preventDefault();

    const customPrompt = elements.customPrompt.value.trim();
    const articleTitle = elements.articleTitle.value.trim();
    const draftLink = elements.draftLink.value.trim();
    const style = elements.styleSelect.value;

    if (!customPrompt && !articleTitle) {
        alert('Please enter either a custom prompt or an article title.');
        return;
    }

    const requestData = {
        style: style
    };

    if (customPrompt) {
        requestData.title = customPrompt;
    } else {
        requestData.title = articleTitle;
    }

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

        card.addEventListener('click', () => selectImage(index, imageUrl, card));

        card.addEventListener('keydown', (e) => {
            if (e.key === 'Enter' || e.key === ' ') {
                e.preventDefault();
                selectImage(index, imageUrl, card);
            }
        });

        elements.imageGrid.appendChild(card);
    });
}

function selectImage(index, imageUrl, cardElement) {
    state.selectedImageIndex = index;
    state.selectedImageUrl = imageUrl;

    document.querySelectorAll('.image-card').forEach(c => c.classList.remove('selected'));
    cardElement.classList.add('selected');

    animateImageToPreview(cardElement, imageUrl);
}

function animateImageToPreview(cardElement, imageUrl) {

    const cardRect = cardElement.getBoundingClientRect();

    const previewPanelWidth = window.innerWidth * 0.5; // 50% (left half)
    const targetWidth = previewPanelWidth * 0.9; // 90% of preview panel (matches .preview-wrapper max-width)
    const targetHeight = (cardRect.height / cardRect.width) * targetWidth;

    const previewPanelLeft = 0;
    const targetLeft = previewPanelLeft + (previewPanelWidth - targetWidth) / 2;
    const targetTop = (window.innerHeight - targetHeight) / 2; // Vertically centered

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

    elements.selectionView.classList.add('fade-out');

    setupPreviewPanel(imageUrl);
    elements.splitView.classList.remove('hidden');

    elements.previewImage.classList.remove('visible');

    requestAnimationFrame(() => {
        requestAnimationFrame(() => {

            elements.splitView.classList.add('active');

            clone.style.top = targetTop + 'px';
            clone.style.left = targetLeft + 'px';
            clone.style.width = targetWidth + 'px';
            clone.style.height = targetHeight + 'px';
        });
    });

    setTimeout(() => {

        clone.remove();

        elements.previewImage.classList.add('visible');

        elements.selectionView.classList.add('hidden');
    }, 750);
}

function setupPreviewPanel(imageUrl) {
    elements.previewImage.src = imageUrl;

    state.currentPlatform = 'Hashnode';
    renderPlatformOptions();

    const dims = state.platforms['Hashnode'];
    updatePreviewDimensions(dims.width, dims.height);
}

function showSelectionView() {

    elements.splitView.classList.remove('active');

    elements.selectionView.classList.remove('hidden');
    elements.selectionView.classList.remove('fade-out');

    setTimeout(() => {
        elements.splitView.classList.add('hidden');
    }, 600);
}

function navigateToPage(pageNumber) {
    const currentPage = pages[state.currentPage];
    const nextPage = pages[pageNumber];

    if (!currentPage || !nextPage || state.currentPage === pageNumber) return;

    if (pageNumber === 1) {
        resetPage2();
    }

    const isForward = pageNumber > state.currentPage;

    currentPage.classList.remove('active');

    if (isForward) {
        currentPage.classList.add('slide-out-left');
    } else {
        currentPage.classList.add('slide-out-right');
    }

    setTimeout(() => {

        currentPage.classList.remove('slide-out-left', 'slide-out-right');
        currentPage.style.display = 'none';

        nextPage.style.display = 'block';
        nextPage.classList.add('active');

        if (isForward) {
            nextPage.classList.add('slide-in-right');
        } else {
            nextPage.classList.add('slide-in-left');
        }

        setTimeout(() => {
            nextPage.classList.remove('slide-in-right', 'slide-in-left');
        }, 400);

        state.currentPage = pageNumber;

        window.scrollTo(0, 0);
    }, 400);
}

function resetPage2() {
    elements.splitView.classList.remove('active');
    elements.splitView.classList.add('hidden');
    elements.selectionView.classList.remove('hidden');
    elements.selectionView.classList.remove('fade-out');
}

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

    if (platform === 'Custom') {
        const width = parseInt(elements.widthInput.value);
        const height = parseInt(elements.heightInput.value);

        if (!width || !height || width < 100 || height < 100) {
            alert('Please specify valid width and height (minimum 100px).');
            return;
        }

        payload.custom_dims = { width, height };
    }

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

function setDownloadLoading(isLoading) {
    if (isLoading) {
        elements.downloadBtn.disabled = true;
        elements.downloadBtn.textContent = 'Downloading...';
    } else {
        elements.downloadBtn.disabled = false;
        elements.downloadBtn.textContent = '⬇ Download Image';
    }
}
