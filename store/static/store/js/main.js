        const input = document.querySelector('.search-bar input');
        const searchBar = document.querySelector('.search-bar');
        
        // When the input is focused, the search-bar container's background becomes white
        input.addEventListener('focus', () => searchBar.style.backgroundColor = '#fff');
        
        // When the input loses focus, the search-bar container's background returns to light gray (#f3f3f3)
        input.addEventListener('blur', () => searchBar.style.backgroundColor = '#f3f3f3');