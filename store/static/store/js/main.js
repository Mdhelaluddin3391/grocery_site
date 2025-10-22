// static/store/js/main.js (FINAL CORRECTED CODE)

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
                promoCards[currentCardIndex].scrollIntoView({
                    behavior: 'smooth',
                    inline: 'start',
                    block: 'nearest'
                });
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
                if (cartCountSpan && data.cart_item_count !== undefined) {
                    cartCountSpan.textContent = data.cart_item_count;
                    cartCountSpan.style.display = data.cart_item_count > 0 ? 'inline-block' : 'none';
                }
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

    if (categoryContainer) {
        let page = 2;
        let isLoading = false;
        let hasMore = categoryContainer.dataset.hasMore === 'true';

        const loadMoreCategories = () => {
            if (isLoading || !hasMore) {
                if(!hasMore && loadingText) {
                    loadingText.style.display = 'block';
                    loadingText.textContent = 'Bas, itne hi products hain!';
                }
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
                    if (loadingText && hasMore) {
                         loadingText.style.display = 'none';
                    } else if (!hasMore && loadingText) {
                        loadingText.textContent = 'Bas, itne hi products hain!';
                    }
                });
        };

        if (loadMoreTrigger) {
            const observer = new IntersectionObserver((entries) => {
                if (entries[0].isIntersecting) {
                    loadMoreCategories();
                }
            }, {
                threshold: 0.1
            });
            observer.observe(loadMoreTrigger);
        }
    }
});