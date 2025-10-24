// static/store/js/main.js (FINAL UPDATED CODE)

document.addEventListener('DOMContentLoaded', () => {

    // 1. Search Bar Logic
    const input = document.querySelector('.search-bar input');
    const searchBar = document.querySelector('.search-bar');
    if (input && searchBar) {
        input.addEventListener('focus', () => searchBar.style.backgroundColor = '#fff');
        input.addEventListener('blur', () => searchBar.style.backgroundColor = '#f3f3f3');
    }

    // 2. Promo Card Auto-Swipe Logic (UPDATED TO PREVENT PAGE JUMP)
    const scrollBanner = document.querySelector('.scroll-banner');
    if (scrollBanner) {
        let currentCardIndex = 0;
        const promoCards = scrollBanner.querySelectorAll('.promo-card');
        if (promoCards.length > 1) {
            setInterval(() => {
                currentCardIndex = (currentCardIndex + 1) % promoCards.length;
                
                // --- YAHAN BADLAV KIYA GAYA HAI ---
                // Purana code page ko scroll kar raha tha.
                // Naya code sirf banner ke content ko scroll karega.
                const nextCard = promoCards[currentCardIndex];
                scrollBanner.scrollLeft = nextCard.offsetLeft;

            }, 3000); 
        }
    }

    // 3. AJAX Add to Cart (for all current and future buttons)
    document.body.addEventListener('click', function(event) {
        if (event.target.classList.contains('add-btn')) {
            event.preventDefault();
            const url = event.target.href;
            if (!url) return;

            fetch(url, {
                method: 'GET',
                headers: { 'X-Requested-With': 'XMLHttpRequest' }
            })
            .then(response => {
                if (!response.ok) throw new Error('Not logged in or server error');
                return response.json();
            })
            .then(data => {
                const cartCountSpan = document.querySelector('.cart-count');
                // Create the span if it doesn't exist
                let countSpan = cartCountSpan;
                if (!countSpan) {
                    const cartLink = document.querySelector('.cart-link');
                    if(cartLink) {
                        countSpan = document.createElement('span');
                        countSpan.className = 'cart-count';
                        cartLink.appendChild(countSpan);
                    }
                }
                
                if (countSpan && data.cart_item_count !== undefined) {
                    countSpan.textContent = data.cart_item_count;
                    countSpan.style.display = data.cart_item_count > 0 ? 'inline-block' : 'none';
                }
            })
            .catch(error => {
                console.error('Error adding to cart:', error);
                window.location.href = '/accounts/login/';
            });
        }
    });

    // 4. Lazy Loading for Product Sections (UPDATED LOGIC)
    const loadMoreTrigger = document.getElementById('load-more-trigger');
    const categoryContainer = document.getElementById('category-container');
    const loadingText = document.querySelector('.loading-text');

    if (categoryContainer && loadMoreTrigger) {
        let page = 2;
        let isLoading = false;
        let hasMore = categoryContainer.dataset.hasMore === 'true';

        const loadMoreCategories = () => {
            if (isLoading || !hasMore) {
                return;
            }

            isLoading = true;
            if (loadingText) loadingText.style.display = 'block';

            fetch(`/ajax/load-more-categories/?page=${page}`)
                .then(response => response.json())
                .then(data => {
                    if (data.html.trim() !== "") {
                        categoryContainer.insertAdjacentHTML('beforeend', data.html);
                        page++;
                    }
                    hasMore = data.has_more;
                })
                .catch(error => console.error('Error loading more categories:', error))
                .finally(() => {
                    isLoading = false;
                    if (loadingText) {
                        // Loading text ko hamesha chhupa dein
                        loadingText.style.display = 'none';
                    }
                    
                    if (!hasMore) {
                        // Trigger ko hi remove kar dein
                        loadMoreTrigger.style.display = 'none';

                        // Humara naya stylish message dikhayein
                        const endMessage = document.getElementById('end-of-list-message');
                        if (endMessage) {
                            endMessage.style.display = 'block';
                            // Animation ke liye thoda sa delay add karein
                            setTimeout(() => {
                                endMessage.classList.add('visible');
                            }, 50);
                        }
                    }
                });
        };

        const observer = new IntersectionObserver((entries) => {
            if (entries[0].isIntersecting) {
                loadMoreCategories();
            }
        }, {
            threshold: 0.1
        });
        observer.observe(loadMoreTrigger);
    }

    // 5. Dynamic Delivery Time Logic (YEH NAYA CODE HAI)
    const deliveryInfoSpan = document.getElementById('delivery-info');

    const successCallback = (position) => {
        const lat = position.coords.latitude;
        const lng = position.coords.longitude;

        // Django view ko AJAX call karein
        fetch(`/ajax/get-delivery-info/?lat=${lat}&lng=${lng}`)
            .then(response => response.json())
            .then(data => {
                if (data.delivery_message && deliveryInfoSpan) {
                    deliveryInfoSpan.textContent = data.delivery_message;
                }
            })
            .catch(error => {
                console.error("Error fetching delivery info:", error);
            });
    };

    const errorCallback = (error) => {
        console.warn(`Geolocation error: ${error.message}`);
        // Agar user location deny karta hai, to default message hi dikhega
    };

    // Browser se location poochhein
    if (navigator.geolocation) {
        navigator.geolocation.getCurrentPosition(successCallback, errorCallback);
    }
});