// static/store/js/main.js (FINAL UPDATED CODE WITH VISUAL FEEDBACK)

document.addEventListener('DOMContentLoaded', () => {

    // 1. Search Bar Logic
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
                const nextCard = promoCards[currentCardIndex];
                scrollBanner.scroll({
                    left: nextCard.offsetLeft,
                    behavior: 'smooth'
                });
            }, 3000);
        }
    }

    // 3. AJAX Add to Cart (UPDATED WITH VISUAL FEEDBACK)
    document.body.addEventListener('click', function(event) {
        const addButton = event.target.closest('.add-btn');
        if (addButton) {
            event.preventDefault();
            const url = addButton.href;
            if (!url) return;

            const originalText = addButton.textContent;
            addButton.textContent = 'Adding...';

            fetch(url, {
                method: 'GET',
                headers: { 'X-Requested-With': 'XMLHttpRequest' }
            })
            .then(response => {
                if (!response.ok) {
                    throw new Error('Not logged in or server error');
                }
                return response.json();
            })
            .then(data => {
                const cartLink = document.querySelector('.cart-link');
                let countSpan = cartLink.querySelector('.cart-count');
                if (!countSpan) {
                    countSpan = document.createElement('span');
                    countSpan.className = 'cart-count';
                    cartLink.appendChild(countSpan);
                }
                
                if (data.cart_item_count !== undefined) {
                    countSpan.textContent = data.cart_item_count;
                    countSpan.style.display = 'inline-block';
                }

                addButton.style.backgroundColor = '#28a745';
                addButton.style.color = '#fff';
                addButton.textContent = 'Added!';
                
                setTimeout(() => {
                    addButton.textContent = originalText;
                    addButton.style.backgroundColor = '';
                    addButton.style.color = '';
                }, 1500);
            })
            .catch(error => {
                console.error('Error adding to cart:', error);
                window.location.href = '/accounts/login/';
            });
        }
    });

    // 4. Lazy Loading for Product Sections
    const loadMoreTrigger = document.getElementById('load-more-trigger');
    const categoryContainer = document.getElementById('category-container');
    const loadingText = document.querySelector('.loading-text');

    if (categoryContainer && loadMoreTrigger) {
        let page = 2;
        let isLoading = false;
        let hasMore = categoryContainer.dataset.hasMore === 'true';

        const loadMoreCategories = () => {
            if (isLoading || !hasMore) return;
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
                    if (loadingText) loadingText.style.display = 'none';
                    if (!hasMore) {
                        loadMoreTrigger.style.display = 'none';
                        const endMessage = document.getElementById('end-of-list-message');
                        if (endMessage) {
                            endMessage.style.display = 'block';
                            setTimeout(() => { endMessage.classList.add('visible'); }, 50);
                        }
                    }
                });
        };

        const observer = new IntersectionObserver((entries) => {
            if (entries[0].isIntersecting) {
                loadMoreCategories();
            }
        }, { threshold: 0.1 });
        observer.observe(loadMoreTrigger);
    }

    // 5. Dynamic Delivery Time Logic
    const deliveryInfoSpan = document.getElementById('delivery-info');
    const successCallback = (position) => {
        const lat = position.coords.latitude;
        const lng = position.coords.longitude;
        fetch(`/ajax/get-delivery-info/?lat=${lat}&lng=${lng}`)
            .then(response => response.json())
            .then(data => {
                if (data.delivery_message && deliveryInfoSpan) {
                    deliveryInfoSpan.textContent = data.delivery_message;
                }
            })
            .catch(error => console.error("Error fetching delivery info:", error));
    };
    const errorCallback = (error) => {
        console.warn(`Geolocation error: ${error.message}`);
    };
    if (navigator.geolocation) {
        navigator.geolocation.getCurrentPosition(successCallback, errorCallback);
    }
});