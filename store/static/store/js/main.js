document.addEventListener('DOMContentLoaded', () => {

    // 1. Search Bar Focus/Blur Logic
    const input = document.querySelector('.search-bar input');
    const searchBar = document.querySelector('.search-bar');
    
    if (input && searchBar) {
        input.addEventListener('focus', () => searchBar.style.backgroundColor = '#fff');
        input.addEventListener('blur', () => searchBar.style.backgroundColor = '#f3f3f3');
    }

    // 2. Promo Card Auto-Swipe Logic
    const scrollBanner = document.querySelector('.scroll-banner');
    if (scrollBanner) {
        let currentCardIndex = 0;
        const promoCards = scrollBanner.querySelectorAll('.promo-card');
        if (promoCards.length > 1) {
            setInterval(() => {
                currentCardIndex = (currentCardIndex + 1) % promoCards.length;
                promoCards[currentCardIndex].scrollIntoView({
                    behavior: 'smooth',
                    inline: 'start',
                    block: 'nearest'
                });
            }, 3000);
        }
    }
    
    // --- 3. "ADD" BUTTON FUNCTIONALITY (NEW) ---
    // Select all buttons with the class 'add-btn'
    const addButtons = document.querySelectorAll('.add-btn');

    addButtons.forEach(button => {
        button.addEventListener('click', (event) => {
            const productId = event.target.dataset.productId;
            
            // Placeholder action: Show a simple alert
            alert(`Product (ID: ${productId}) added to cart! (This is a demo)`);
            
            // You can replace the alert with a real AJAX call to your Django backend
            // to add the product to the user's cart session.
        });
    });
});