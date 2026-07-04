function initPortfolioTimeline() {
    const observerOptions = {
        root: null,
        rootMargin: '0px',
        threshold: 0.1
    };

    const observer = new IntersectionObserver((entries, observer) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('visible');
                observer.unobserve(entry.target);
            }
        });
    }, observerOptions);

    const timelineContainers = document.querySelectorAll('.portfolio-timeline-container');
    timelineContainers.forEach(container => {
        observer.observe(container);
    });

    // JS specifically to calculate and set the exact line height matching the dots
    function adjustTimelineLine() {
        const timeline = document.querySelector('.portfolio-timeline');
        if (!timeline) return;
        
        const containers = timeline.querySelectorAll('.portfolio-timeline-container');
        if (containers.length > 0) {
            const firstContainer = containers[0];
            const lastContainer = containers[containers.length - 1];
            
            // The dot is exactly 40px from the top of its container (top: 30px + 10px center)
            // We extend the line 30px above the first dot and 30px below the last dot
            const startY = (firstContainer.offsetTop + 40) - 30;
            const endY = (lastContainer.offsetTop + 40) + 30;
            
            const totalHeight = timeline.offsetHeight;
            const bottomOffset = totalHeight - endY;
            
            // Set CSS variables for the exact start and end pixel
            timeline.style.setProperty('--line-start', startY + 'px');
            timeline.style.setProperty('--line-end', bottomOffset + 'px');
        }
    }
    
    // Run calculation
    adjustTimelineLine();
    window.addEventListener('resize', adjustTimelineLine);
}

if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initPortfolioTimeline);
} else {
    initPortfolioTimeline();
}
