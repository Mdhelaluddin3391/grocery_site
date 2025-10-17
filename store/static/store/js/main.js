document.addEventListener('DOMContentLoaded', () => {

    // ===================================
    // 1. Search Bar Focus/Blur Logic (Aapka Existing Code)
    // ===================================
    const input = document.querySelector('.search-bar input');
    const searchBar = document.querySelector('.search-bar');
    
    if (input && searchBar) {
        // When the input is focused, the search-bar container's background becomes white
        input.addEventListener('focus', () => searchBar.style.backgroundColor = '#fff');
        
        // When the input loses focus, the search-bar container's background returns to light gray (#f3f3f3)
        // Note: You may want to ensure your CSS uses #f3f3f3 if you want this effect. 
        // In the original file, we didn't explicitly set this in JS.
        input.addEventListener('blur', () => searchBar.style.backgroundColor = '#f3f3f3');
    }


    // ===================================
    // 2. Promo Card Auto-Swipe Logic (Naya Code)
    // ===================================
    const scrollBanner = document.querySelector('.scroll-banner');
    const promoCards = document.querySelectorAll('.promo-card');
    
    // Check if the banner and cards exist on the page before running the slider logic
    if (scrollBanner && promoCards.length > 0) {
        let currentCardIndex = 0;
        const cardCount = promoCards.length;
        const intervalTime = 3000; // 3 seconds

        const autoScroll = () => {
            // Calculate the index for the next card (loops back to 0 after the last card)
            currentCardIndex = (currentCardIndex + 1) % cardCount; 

            const gapWidth = 15; // Gap set in CSS
            
            // Get the actual computed width of one card
            const cardWidth = promoCards[0].offsetWidth; 
            
            // Calculate the total scroll distance
            const finalScrollPosition = currentCardIndex * (cardWidth + gapWidth);
            
            // If index is 0, instantly jump back to the start (for a seamless loop)
            if (currentCardIndex === 0) {
                 scrollBanner.scrollTo({
                    left: 0,
                    behavior: 'auto' // Instant jump back
                });
            } else {
                // Smooth scroll to the next card
                scrollBanner.scrollTo({
                    left: finalScrollPosition,
                    behavior: 'smooth'
                });
            }
        };

        // Start the auto-scrolling every 3 seconds
        setInterval(autoScroll, intervalTime);
    }
});