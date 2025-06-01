// Navigation fix for GoDaddy Website Builder
// This script overrides the default behavior to enable normal page navigation

document.addEventListener('DOMContentLoaded', function() {
    // Wait for GoDaddy's scripts to load
    setTimeout(function() {
        // Find all navigation links
        const navLinks = document.querySelectorAll('a[href]:not([href^="#"]):not([href^="javascript:"]):not([target="_blank"])');
        
        navLinks.forEach(link => {
            // Remove any existing click handlers
            const newLink = link.cloneNode(true);
            link.parentNode.replaceChild(newLink, link);
            
            // Add new click handler for normal navigation
            newLink.addEventListener('click', function(e) {
                e.stopPropagation();
                e.stopImmediatePropagation();
                
                const href = this.getAttribute('href');
                if (href && href !== '#' && href !== 'javascript:void(0)') {
                    // Force normal navigation
                    window.location.href = href;
                }
            }, true);
        });
        
        // Also handle dynamically added links
        const observer = new MutationObserver(function(mutations) {
            mutations.forEach(function(mutation) {
                mutation.addedNodes.forEach(function(node) {
                    if (node.nodeType === 1 && node.tagName === 'A') {
                        const newLink = node.cloneNode(true);
                        node.parentNode.replaceChild(newLink, node);
                        
                        newLink.addEventListener('click', function(e) {
                            e.stopPropagation();
                            e.stopImmediatePropagation();
                            
                            const href = this.getAttribute('href');
                            if (href && href !== '#' && href !== 'javascript:void(0)') {
                                window.location.href = href;
                            }
                        }, true);
                    }
                });
            });
        });
        
        observer.observe(document.body, {
            childList: true,
            subtree: true
        });
    }, 1000);
});