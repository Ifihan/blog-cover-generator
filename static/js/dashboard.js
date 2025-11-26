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

// Close modals with Escape key
document.addEventListener('keydown', (e) => {
    if (e.key === 'Escape') {
        closeImageModal();
    }
});
