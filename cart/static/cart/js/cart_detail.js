// cart/static/cart/js/cart_detail.js

document.addEventListener('DOMContentLoaded', () => {

    // Yeh function server se mile data ke basis par cart summary ko update karega
    function updateCartSummary(data) {
        document.getElementById('summary-subtotal').textContent = parseFloat(data.cart_subtotal).toFixed(2);
        document.getElementById('summary-grand-total').textContent = parseFloat(data.cart_grand_total).toFixed(2);
        document.getElementById('summary-item-count').textContent = data.cart_item_count;
        
        const itemText = data.cart_item_count === 1 ? ' item' : ' items';
        document.getElementById('cart-title').textContent = `🛒 Your Cart (${data.cart_item_count}${itemText})`;

        const headerCartCount = document.querySelector('.cart-count');
        if (headerCartCount) {
            if (data.cart_item_count > 0) {
                headerCartCount.textContent = data.cart_item_count;
                headerCartCount.style.display = 'inline-block';
            } else {
                headerCartCount.style.display = 'none';
            }
        }

        if (data.cart_item_count === 0) {
            document.getElementById('cart-content-wrapper').style.display = 'none';
            document.getElementById('empty-cart-container').style.display = 'block';
        }
    }

    // Quantity buttons ke liye event listener
    document.querySelectorAll('.quantity-btn').forEach(button => {
        button.addEventListener('click', (event) => { 
            event.preventDefault();

            const action = button.dataset.action;
            const itemId = button.dataset.itemId;
            let url = '';

            if (action === 'increment') {
                url = `/cart/increment/${itemId}/`;
            } else if (action === 'decrement') {
                url = `/cart/decrement/${itemId}/`;
            } else {
                return;
            }

            fetch(url, {
                method: 'GET',
                headers: { 'X-Requested-With': 'XMLHttpRequest' }
            })
            .then(response => {
                if (!response.ok) {
                    throw new Error('Network response was not ok');
                }
                return response.json();
            })
            .then(data => {
                if (data.item_removed) {
                    const itemCard = document.getElementById(`cart-item-${data.item_id}`);
                    if (itemCard) {
                        itemCard.style.opacity = '0';
                        setTimeout(() => itemCard.remove(), 300);
                    }
                } else {
                    document.getElementById(`quantity-${itemId}`).textContent = data.item_quantity;
                    document.getElementById(`subtotal-${itemId}`).textContent = parseFloat(data.item_subtotal).toFixed(2);
                }
                updateCartSummary(data); // Summary update karein
            })
            .catch(error => {
                console.error('There has been a problem with your fetch operation:', error);
            });
        });
    });

    // Remove buttons ke liye event listener
    document.querySelectorAll('.remove-btn').forEach(button => {
        button.addEventListener('click', (event) => {
            event.preventDefault(); // Page reload ko rokein

            const url = button.href; // URL link se lein

            fetch(url, {
                method: 'GET',
                headers: { 'X-Requested-With': 'XMLHttpRequest' }
            })
            .then(response => response.json())
            .then(data => {
                if (data.item_removed) {
                    // Item card ko fade out karke remove karein
                    const itemCard = document.getElementById(`cart-item-${data.item_id}`);
                    if (itemCard) {
                        itemCard.style.opacity = '0';
                        setTimeout(() => itemCard.remove(), 300);
                    }
                    updateCartSummary(data); // Summary update karein
                }
            })
            .catch(error => console.error('Error:', error));
        });
    });
});