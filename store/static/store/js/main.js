// static/store/js/main.js (Updated Code)

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
    
});