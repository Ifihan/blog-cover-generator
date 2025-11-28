// Image Modal Functions
function openImageModal(imageUrl) {
    const modal = document.getElementById('image-modal');
    const modalImage = document.getElementById('modal-image');

    modalImage.src = imageUrl;
    modal.classList.add('active');
}

function closeImageModal() {
    const modal = document.getElementById('image-modal');
    modal.classList.remove('active');
}

// Delete Modal Functions
let pendingDeleteId = null;

function deleteGeneration(generationId, title) {
    pendingDeleteId = generationId;
    const modal = document.getElementById('delete-modal');
    const titleSpan = document.getElementById('delete-gen-title');

    titleSpan.textContent = title;
    modal.classList.add('active');
}

function closeDeleteModal() {
    const modal = document.getElementById('delete-modal');
    modal.classList.remove('active');
    pendingDeleteId = null;
}

async function confirmDelete() {
    if (!pendingDeleteId) return;

    const confirmBtn = document.getElementById('confirm-delete-btn');
    const originalText = confirmBtn.textContent;

    confirmBtn.disabled = true;
    confirmBtn.textContent = 'Deleting...';

    try {
        const response = await fetch(`/api/generation/${pendingDeleteId}`, {
            method: 'DELETE'
        });

        const data = await response.json();

        if (response.ok) {
            const card = document.querySelector(`[data-generation-id="${pendingDeleteId}"]`);
            if (card) {
                card.style.opacity = '0';
                card.style.transform = 'scale(0.9)';
                setTimeout(() => {
                    card.remove();

                    const remaining = document.querySelectorAll('.generation-card-modern').length;
                    if (remaining === 0) {
                        window.location.reload();
                    }
                }, 300);
            }

            closeDeleteModal();
        } else {
            alert(data.error || 'Failed to delete generation');
            confirmBtn.disabled = false;
            confirmBtn.textContent = originalText;
        }
    } catch (error) {
        console.error('Error deleting generation:', error);
        alert('An error occurred while deleting');
        confirmBtn.disabled = false;
        confirmBtn.textContent = originalText;
    }
}

// Initialize on DOM load
document.addEventListener('DOMContentLoaded', () => {
    const confirmBtn = document.getElementById('confirm-delete-btn');
    if (confirmBtn) {
        confirmBtn.addEventListener('click', confirmDelete);
    }
});

// Download from dashboard
async function downloadFromDashboard(generationId, imageIndex, title) {
    const payload = {
        generation_id: generationId,
        selected_image_index: imageIndex,
        platform: 'Hashnode' // Default platform for dashboard downloads
    };

    try {
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
            a.download = `${title.toLowerCase().replace(/\s+/g, '-')}-cover.png`;
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
    }
}

// Close modals with Escape key
document.addEventListener('keydown', (e) => {
    if (e.key === 'Escape') {
        closeImageModal();
        closeDeleteModal();
    }
});
