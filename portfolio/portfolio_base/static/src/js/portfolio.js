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

    if (typeof AOS !== 'undefined') {
        AOS.init({
            duration: 600,
            easing: 'ease-out-cubic',
            once: true,
            offset: 20, // Trigger much sooner on mobile
        });
        
        // Refresh AOS when all images/fonts are loaded to fix wrong offsets
        window.addEventListener('load', function() {
            AOS.refresh();
        });
    }

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
    
    // Scroll Progress Bar and Parallax effect for Hero section
    window.addEventListener('scroll', function() {
        const scrollY = window.scrollY;
        
        // GSAP will handle Hero parallax now

        // Scroll Progress Bar
        const scrollBar = document.getElementById('scrollBar');
        if (scrollBar) {
            const docHeight = document.body.scrollHeight - window.innerHeight;
            const scrollPercent = (scrollY / docHeight) * 100;
            scrollBar.style.width = scrollPercent + '%';
        }
    });

    // Run calculation
    adjustTimelineLine();
    window.addEventListener('resize', adjustTimelineLine);

    // Flying Button Animation (FLIP)
    const flyingBtn = document.getElementById('flying-contact-btn');
    const targetText = document.getElementById('contact-target-text');
    
    if (flyingBtn && targetText) {
        flyingBtn.addEventListener('click', function(e) {
            e.preventDefault(); // Prevent instant jump
            
            // 1. Get initial positions
            const initialRect = flyingBtn.getBoundingClientRect();
            
            // 2. Create the clone
            const clone = flyingBtn.cloneNode(true);
            clone.id = 'flying-button-clone';
            clone.style.position = 'fixed';
            clone.style.top = initialRect.top + 'px';
            clone.style.left = initialRect.left + 'px';
            clone.style.width = initialRect.width + 'px';
            clone.style.height = initialRect.height + 'px';
            clone.style.margin = '0';
            clone.style.zIndex = '99999';
            clone.style.transition = 'all 1.2s cubic-bezier(0.25, 1, 0.5, 1)';
            clone.style.pointerEvents = 'none';
            document.body.appendChild(clone);
            
            // Hide the original temporarily for magic effect
            flyingBtn.style.opacity = '0';
            
            // 3. Smooth scroll to contact section
            const contactSection = document.getElementById('contact');
            contactSection.scrollIntoView({ behavior: 'smooth' });
            
            // 4. Animate clone to target text position
            // Wait a tiny bit for the scroll to start and layout to update
            setTimeout(() => {
                const finalRect = targetText.getBoundingClientRect();
                
                // We calculate target position
                const targetDocTop = finalRect.top + window.scrollY;
                const targetDocLeft = finalRect.left + window.scrollX;
                
                clone.style.position = 'absolute';
                clone.style.top = (initialRect.top + window.scrollY) + 'px';
                clone.style.left = (initialRect.left + window.scrollX) + 'px';
                
                // Trigger reflow
                clone.offsetHeight; 
                
                // Animate position and size
                clone.style.top = targetDocTop + 'px';
                clone.style.left = targetDocLeft + 'px';
                clone.style.width = finalRect.width + 'px';
                clone.style.height = finalRect.height + 'px';
                
                // Animate text size and color to match the target gradually
                clone.style.fontSize = window.getComputedStyle(targetText).fontSize;
                clone.style.color = 'rgba(15, 23, 42, 0.5)'; // Fade text color to match target loosely
                
                // Let the background and border fade out slowly during flight
                clone.style.backgroundColor = 'transparent';
                clone.style.borderColor = 'transparent';
                clone.style.boxShadow = 'none';
                
                // Do NOT change innerHTML instantly, keep it looking like the button!
                
            }, 10);
            
            // 5. Cleanup after animation completes
            setTimeout(() => {
                clone.style.opacity = '0';
                
                // Flash the actual target text to complete the illusion
                targetText.style.opacity = '0';
                targetText.style.transform = 'scale(1.1)';
                targetText.style.transition = 'all 0.3s ease';
                
                setTimeout(() => {
                    targetText.style.opacity = '1';
                    targetText.style.transform = 'scale(1)';
                }, 50);
                
                setTimeout(() => {
                    if (clone.parentNode) clone.parentNode.removeChild(clone);
                    flyingBtn.style.opacity = '1'; // Restore original button for future clicks
                    targetText.style.transition = ''; // clear transition
                }, 400);
                
            }, 1200); // 1.2s matches CSS transition duration
        });
    }

    // AJAX Contact Form Submission
    const contactForm = document.getElementById('ajax-contact-form');
    if (contactForm) {
        contactForm.addEventListener('submit', function(e) {
            e.preventDefault(); // Prevent full page reload
            
            // Change button to show loading state
            const submitBtn = contactForm.querySelector('button[type="submit"]');
            const originalBtnHtml = submitBtn.innerHTML;
            submitBtn.innerHTML = '<i class="fa fa-spinner fa-spin me-2"></i> Sending...';
            submitBtn.disabled = true;

            const formData = new FormData(contactForm);

            fetch(contactForm.action, {
                method: 'POST',
                body: formData,
            })
            .then(response => {
                // The server will actually return a redirect (302) to /?submitted=1,
                // which fetch will follow transparently. Since it doesn't throw an error,
                // we just assume success.
                
                // Hide form and show success message
                contactForm.classList.add('d-none');
                document.getElementById('ajax-success-message').classList.remove('d-none');
                
                // Clear the form for next time
                contactForm.reset();
            })
            .catch(error => {
                console.error('Error submitting form:', error);
                alert("Something went wrong. Please try again.");
            })
            .finally(() => {
                // Restore button
                submitBtn.innerHTML = originalBtnHtml;
                submitBtn.disabled = false;
            });
        });
    }
}

function initThreeJSBackground() {
    const canvas = document.getElementById('webgl-canvas');
    if (!canvas || typeof THREE === 'undefined') return;

    const scene = new THREE.Scene();
    scene.fog = new THREE.FogExp2(0xf8fafc, 0.02);

    const camera = new THREE.PerspectiveCamera(60, window.innerWidth / window.innerHeight, 0.1, 1000);
    // Start camera a bit higher looking down
    camera.position.set(0, 15, 30);
    camera.lookAt(0, 0, 0);
    
    const renderer = new THREE.WebGLRenderer({ canvas: canvas, alpha: false, antialias: true });
    renderer.setClearColor(0xf8fafc, 1);
    renderer.setSize(window.innerWidth, window.innerHeight);
    renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));

    // Lighting for smooth wave shading
    const ambientLight = new THREE.AmbientLight(0xffffff, 0.6);
    scene.add(ambientLight);

    const dirLight1 = new THREE.DirectionalLight(0x0ea5e9, 0.5); // Light Blue
    dirLight1.position.set(20, 30, 20);
    scene.add(dirLight1);

    const dirLight2 = new THREE.DirectionalLight(0x3b82f6, 0.3); // Darker Blue
    dirLight2.position.set(-20, 20, -20);
    scene.add(dirLight2);

    // The Wave Plane
    // 150x150 size, 64x64 segments for smooth geometry
    const geometry = new THREE.PlaneGeometry(150, 150, 64, 64);
    
    // Rotate to lay flat
    geometry.rotateX(-Math.PI / 2);

    // Save original Y positions for math calculation later
    const posAttribute = geometry.attributes.position;
    const v3 = new THREE.Vector3();
    const originalPositions = [];
    for (let i = 0; i < posAttribute.count; i++) {
        v3.fromBufferAttribute(posAttribute, i);
        originalPositions.push(v3.clone());
    }

    const material = new THREE.MeshStandardMaterial({
        color: 0xffffff,
        roughness: 0.2,
        metalness: 0.1,
        wireframe: false,
        transparent: true,
        opacity: 0.9,
        side: THREE.DoubleSide
    });

    const waveMesh = new THREE.Mesh(geometry, material);
    waveMesh.position.y = -5; // Move slightly below the text
    scene.add(waveMesh);

    let mouseX = 0, mouseY = 0;
    document.addEventListener('mousemove', (e) => {
        mouseX = (e.clientX / window.innerWidth) * 2 - 1;
        mouseY = -(e.clientY / window.innerHeight) * 2 + 1;
    });

    let windowWidth = window.innerWidth;
    window.addEventListener('resize', () => {
        if (window.innerWidth !== windowWidth) {
            windowWidth = window.innerWidth;
            camera.aspect = window.innerWidth / window.innerHeight;
            camera.updateProjectionMatrix();
            renderer.setSize(window.innerWidth, window.innerHeight);
        }
    });

    const isMobile = window.innerWidth <= 768;

    // Make globally accessible for GSAP Scrubbing
    window.threeScene = {
        camera, scene, waveMesh, 
        currentMouseX: 0, currentMouseY: 0, 
        scrollProgress: 0,
        cameraZ: isMobile ? 80 : 30, // Push camera much further back on mobile
        cameraY: isMobile ? 40 : 15, // Look down from higher up on mobile
        waveAmplitude: isMobile ? 1.5 : 5 // Flatter, less chaotic wave on mobile
    };

    const clock = new THREE.Clock();

    function animate() {
        requestAnimationFrame(animate);
        
        const time = clock.getElapsedTime() * 0.5;

        // Modify vertices for wave effect
        const positions = waveMesh.geometry.attributes.position;
        for (let i = 0; i < positions.count; i++) {
            const orig = originalPositions[i];
            
            // Calculate a complex wave using sine and cosine on X and Z axes
            const waveX1 = 0.5 * Math.sin(orig.x * 0.05 + time);
            const waveZ1 = 0.5 * Math.sin(orig.z * 0.05 + time);
            
            const waveX2 = 0.2 * Math.sin(orig.x * 0.1 - time * 1.5);
            const waveZ2 = 0.2 * Math.sin(orig.z * 0.1 + time * 0.8);

            // Combine waves and exaggerate amplitude slightly
            positions.setY(i, (waveX1 + waveZ1 + waveX2 + waveZ2) * window.threeScene.waveAmplitude);
        }
        positions.needsUpdate = true;
        // Recompute normals for accurate lighting on the new surface
        waveMesh.geometry.computeVertexNormals();

        // Smooth mouse follow parallax
        window.threeScene.currentMouseX += (mouseX - window.threeScene.currentMouseX) * 0.05;
        window.threeScene.currentMouseY += (mouseY - window.threeScene.currentMouseY) * 0.05;

        // Apply GSAP scroll values and Mouse Parallax
        camera.position.z = window.threeScene.cameraZ + window.threeScene.currentMouseX * 5;
        camera.position.y = window.threeScene.cameraY + window.threeScene.currentMouseY * 2;
        
        // Gentle rotation based on scroll progress
        camera.lookAt(0, 0, -window.threeScene.scrollProgress * 20);

        renderer.render(scene, camera);
    }
    
    animate();
}

function initGSAPScrollytelling() {
    if (typeof gsap === 'undefined' || typeof ScrollTrigger === 'undefined') return;
    
    gsap.registerPlugin(ScrollTrigger);

    // Cinematic 3D Wave Camera Glide
    if (window.threeScene) {
        const isMobile = window.innerWidth <= 768;
        gsap.to(window.threeScene, {
            scrollTrigger: {
                trigger: document.body,
                start: 'top top',
                end: 'bottom bottom',
                scrub: 1
            },
            scrollProgress: 1,
            cameraZ: isMobile ? 0 : -50,   // Don't glide as far forward on mobile
            cameraY: isMobile ? 20 : 5      // Don't drop as low on mobile
        });
    }

    // Hero Section Parallax
    gsap.to('.hero-container', {
        scrollTrigger: {
            trigger: '#hero',
            start: 'top top',
            end: 'bottom top',
            scrub: true
        },
        opacity: 0,
        y: -100,
        scale: 0.9
    });

    // Skills Card Toggle Interaction
    document.querySelectorAll('.card-toggle-btn').forEach(btn => {
        btn.addEventListener('click', function() {
            this.classList.toggle('expanded');
            const desc = this.previousElementSibling;
            if (desc && desc.classList.contains('card-desc-modern')) {
                desc.classList.toggle('expanded');
            }
        });
    });

    // Latest Work Cards 3D Tilt Effect on Hover
    document.querySelectorAll('.module-blog-card').forEach(card => {
        card.addEventListener('mousemove', function(e) {
            const rect = this.getBoundingClientRect();
            const x = e.clientX - rect.left;
            const y = e.clientY - rect.top;
            const centerX = rect.width / 2;
            const centerY = rect.height / 2;
            const rotateX = ((y - centerY) / centerY) * -8;
            const rotateY = ((x - centerX) / centerX) * 8;
            
            this.style.transform = `perspective(1000px) rotateX(${rotateX}deg) rotateY(${rotateY}deg) scale3d(1.02, 1.02, 1.02)`;
            this.style.transition = 'none';
            this.style.zIndex = '10';
        });
        
        card.addEventListener('mouseleave', function() {
            this.style.transform = `perspective(1000px) rotateX(0deg) rotateY(0deg) scale3d(1, 1, 1)`;
            this.style.transition = 'transform 0.5s cubic-bezier(0.25, 0.8, 0.25, 1)';
            this.style.zIndex = '1';
        });
    });
}

if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', function() {
    // Prevent browser from restoring previous scroll position which causes jumps on refresh
    if ('scrollRestoration' in history) {
        history.scrollRestoration = 'manual';
    }
    window.scrollTo(0, 0);

    initPortfolioTimeline();
    initThreeJSBackground();
    initGSAPScrollytelling();
    });
} else {
    initPortfolioTimeline();
    initThreeJSBackground();
    initGSAPScrollytelling();
}

/* --- Contact Form Validation --- */
window.validateContactForm = function(form) {
    const emailInput = form.querySelector('input[name="email"]');
    const phoneInput = form.querySelector('input[name="phone"]');
    
    if (emailInput && phoneInput) {
        if (!emailInput.value.trim() && !phoneInput.value.trim()) {
            alert('Please provide either an Email Address or a Phone Number so I can get back to you.');
            // Optionally, focus one of the inputs
            emailInput.focus();
            return false;
        }
    }
    return true;
};

/* --- Custom File Uploader Logic --- */
const dt = new DataTransfer();

/* --- Text Counter Animation --- */
function animateTextCounters() {
    const elements = document.querySelectorAll('.portfolio-counter-text');
    
    elements.forEach(el => {
        const text = el.getAttribute('data-text');
        if (!text) return;
        
        // Find all numbers in the string
        const regex = /(\d+)/g;
        let match;
        const numberTokens = [];
        let lastIndex = 0;
        let templateParts = [];
        
        while ((match = regex.exec(text)) !== null) {
            templateParts.push(text.substring(lastIndex, match.index));
            numberTokens.push({
                target: parseInt(match[0], 10),
                current: 0
            });
            templateParts.push(''); // placeholder for the number
            lastIndex = match.index + match[0].length;
        }
        templateParts.push(text.substring(lastIndex));
        
        if (numberTokens.length === 0) return;
        
        const duration = 2000; // 2 seconds
        const frameRate = 30; // 30ms per frame
        const totalFrames = duration / frameRate;
        let frame = 0;
        
        const updateText = () => {
            let res = '';
            let tokenIdx = 0;
            for (let i = 0; i < templateParts.length; i++) {
                if (i % 2 === 1) { // this is where a number goes
                    res += Math.floor(numberTokens[tokenIdx].current);
                    tokenIdx++;
                } else {
                    res += templateParts[i];
                }
            }
            el.innerText = res;
        };
        
        const timer = setInterval(() => {
            frame++;
            let finished = true;
            for (let token of numberTokens) {
                // Ease out quad
                const progress = frame / totalFrames;
                const easedProgress = progress * (2 - progress);
                token.current = token.target * easedProgress;
                
                if (frame >= totalFrames) {
                    token.current = token.target;
                } else {
                    finished = false;
                }
            }
            
            updateText();
            
            if (finished) {
                clearInterval(timer);
            }
        }, frameRate);
    });
}

document.addEventListener('DOMContentLoaded', function() {
    // Start text counter animations
    animateTextCounters();
    
    // Clear DataTransfer and form on load if it was a redirect after submission
    if (window.location.search.includes('submitted=1')) {
        const form = document.getElementById('ajax-contact-form');
        if (form) form.reset();
        dt.items.clear();
        const fileInput = document.getElementById('attachment');
        if (fileInput) fileInput.value = '';
        updateFilePreviews();
    }
    
    // Exit-Intent Popup Logic
    document.addEventListener("mouseleave", (event) => {
        if (event.clientY <= 0) {
            if (!sessionStorage.getItem('exitIntentShown')) {
                const exitModalEl = document.getElementById('exitIntentModal');
                if (exitModalEl && typeof bootstrap !== 'undefined') {
                    const exitModal = new bootstrap.Modal(exitModalEl);
                    exitModal.show();
                    sessionStorage.setItem('exitIntentShown', 'true');
                }
            }
        }
    });

    // Auto-redirect when scrolling past latest-modules
    const latestModulesSection = document.getElementById('latest-modules');
    if (latestModulesSection && typeof IntersectionObserver !== 'undefined') {
        const observer = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                // Trigger when the bottom of the section passes the top of the viewport (meaning user scrolled past it)
                if (!entry.isIntersecting && entry.boundingClientRect.bottom < 0) {
                    if (!sessionStorage.getItem('autoRedirectTriggered')) {
                        sessionStorage.setItem('autoRedirectTriggered', 'true');
                        const redirectModalEl = document.getElementById('autoRedirectModal');
                        if (redirectModalEl && typeof bootstrap !== 'undefined') {
                            const redirectModal = new bootstrap.Modal(redirectModalEl);
                            redirectModal.show();
                            
                            let count = 4;
                            const countEl = document.getElementById('redirectCountdown');
                            window.autoRedirectInterval = setInterval(() => {
                                count--;
                                if (countEl) countEl.innerText = count;
                                if (count <= 0) {
                                    clearInterval(window.autoRedirectInterval);
                                    window.location.href = '/my-modules';
                                }
                            }, 1000);
                        }
                    }
                }
            });
        }, { threshold: 0 });
        
        observer.observe(latestModulesSection);
    }
    
    window.cancelAutoRedirect = function() {
        if (window.autoRedirectInterval) {
            clearInterval(window.autoRedirectInterval);
        }
    };
});

window.resetContactForm = function() {
    const form = document.getElementById('ajax-contact-form');
    if (form) form.reset();
    dt.items.clear();
    const fileInput = document.getElementById('attachment');
    if (fileInput) fileInput.value = '';
    updateFilePreviews();
    
    const successMsg = document.getElementById('ajax-success-message');
    if (successMsg) successMsg.classList.add('d-none');
    if (form) form.classList.remove('d-none');
    return false;
};

window.handleFilesSelected = function(event) {
    const files = event.target.files;
    for (let i = 0; i < files.length; i++) {
        dt.items.add(files[i]);
    }
    updateFilePreviews();
    // Update the input files property
    document.getElementById('attachment').files = dt.files;
};

window.removeFile = function(index) {
    dt.items.remove(index);
    updateFilePreviews();
    // Update the input files property
    document.getElementById('attachment').files = dt.files;
};

function updateFilePreviews() {
    const container = document.getElementById('file-preview-container');
    if (!container) return;
    
    container.innerHTML = '';
    
    for (let i = 0; i < dt.files.length; i++) {
        const file = dt.files[i];
        
        const previewItem = document.createElement('div');
        previewItem.className = 'file-preview-item';
        
        const deleteBtn = document.createElement('div');
        deleteBtn.className = 'file-preview-delete';
        deleteBtn.innerHTML = '<i class="fa fa-times"></i>';
        deleteBtn.onclick = function(e) {
            e.stopPropagation();
            removeFile(i);
        };
        
        previewItem.appendChild(deleteBtn);
        
        if (file.type.startsWith('image/')) {
            const img = document.createElement('img');
            img.src = URL.createObjectURL(file);
            previewItem.appendChild(img);
        } else if (file.type.startsWith('video/')) {
            const icon = document.createElement('i');
            icon.className = 'fa fa-file-video-o file-icon video-icon';
            previewItem.appendChild(icon);
        } else if (file.name.endsWith('.zip') || file.type.includes('zip') || file.type.includes('compressed')) {
            const icon = document.createElement('i');
            icon.className = 'fa fa-file-archive-o file-icon zip-icon';
            previewItem.appendChild(icon);
        } else if (file.type === 'application/pdf' || file.name.endsWith('.pdf')) {
            const icon = document.createElement('i');
            icon.className = 'fa fa-file-pdf-o file-icon pdf-icon';
            previewItem.appendChild(icon);
        } else {
            const icon = document.createElement('i');
            icon.className = 'fa fa-file-o file-icon generic-icon';
            previewItem.appendChild(icon);
        }
        
        const nameLabel = document.createElement('div');
        nameLabel.className = 'file-name';
        nameLabel.innerText = file.name;
        previewItem.appendChild(nameLabel);
        
        container.appendChild(previewItem);
    }
}
