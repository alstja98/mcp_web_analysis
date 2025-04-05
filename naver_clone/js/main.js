document.addEventListener('DOMContentLoaded', function() {
    // Tab switching functionality
    const tabs = document.querySelectorAll('.header_tab a');
    
    tabs.forEach(tab => {
        tab.addEventListener('click', function(e) {
            e.preventDefault();
            
            // Remove active class from all tabs
            tabs.forEach(t => {
                t.classList.remove('active');
            });
            
            // Add active class to clicked tab
            this.classList.add('active');
        });
    });
    
    // View type switching functionality
    const listViewBtn = document.querySelector('.btn_view_list');
    const thumbViewBtn = document.querySelector('.btn_view_thumb');
    const mediaGrid = document.querySelector('.media_grid');
    
    if (listViewBtn && thumbViewBtn && mediaGrid) {
        listViewBtn.addEventListener('click', function() {
            thumbViewBtn.classList.remove('active');
            listViewBtn.classList.add('active');
            mediaGrid.classList.add('list_view');
            mediaGrid.classList.remove('thumb_view');
        });
        
        thumbViewBtn.addEventListener('click', function() {
            listViewBtn.classList.remove('active');
            thumbViewBtn.classList.add('active');
            mediaGrid.classList.add('thumb_view');
            mediaGrid.classList.remove('list_view');
        });
    }
    
    // News paging functionality
    const prevBtn = document.querySelector('.btn_prev');
    const nextBtn = document.querySelector('.btn_next');
    const currentPageEl = document.querySelector('.current');
    
    let currentPage = 1;
    const totalPages = 4;
    
    if (prevBtn && nextBtn && currentPageEl) {
        // Previous page button click
        prevBtn.addEventListener('click', function() {
            if (currentPage > 1) {
                currentPage--;
                updatePageIndicator();
            }
        });
        
        // Next page button click
        nextBtn.addEventListener('click', function() {
            if (currentPage < totalPages) {
                currentPage++;
                updatePageIndicator();
            }
        });
        
        // Update page indicator
        function updatePageIndicator() {
            currentPageEl.textContent = currentPage;
            
            // Disable/enable buttons based on current page
            prevBtn.disabled = currentPage === 1;
            nextBtn.disabled = currentPage === totalPages;
            
            // Add visual indication of disabled state
            if (prevBtn.disabled) {
                prevBtn.classList.add('disabled');
            } else {
                prevBtn.classList.remove('disabled');
            }
            
            if (nextBtn.disabled) {
                nextBtn.classList.add('disabled');
            } else {
                nextBtn.classList.remove('disabled');
            }
        }
        
        // Initialize page indicator
        updatePageIndicator();
    }
    
    // Shortcuts area toggle
    const shortcutsToggleBtn = document.querySelector('.shortcut_area a:last-child');
    const shortcutLinks = document.querySelectorAll('.shortcut_area a:not(:last-child)');
    let shortcutsExpanded = false;
    
    if (shortcutsToggleBtn && shortcutLinks.length > 0) {
        shortcutsToggleBtn.addEventListener('click', function(e) {
            e.preventDefault();
            
            shortcutsExpanded = !shortcutsExpanded;
            
            if (shortcutsExpanded) {
                shortcutsToggleBtn.textContent = '바로가기 접기';
                shortcutLinks.forEach(link => {
                    if (link.classList.contains('hidden')) {
                        link.classList.remove('hidden');
                    }
                });
            } else {
                shortcutsToggleBtn.textContent = '바로가기 펼침';
                // Hide links beyond a certain number
                for (let i = 10; i < shortcutLinks.length; i++) {
                    shortcutLinks[i].classList.add('hidden');
                }
            }
        });
    }
    
    // Auto-rotating banner functionality
    const bannerWrapper = document.querySelector('.banner_rolling');
    const bannerLink = document.querySelector('.link_banner');
    
    if (bannerWrapper && bannerLink) {
        // Sample banner images (in a real implementation, these would be loaded from a server)
        const bannerImages = [
            'images/banner1.png',
            'images/banner2.png',
            'images/banner3.png'
        ];
        
        let currentBannerIndex = 0;
        
        // Function to rotate banner
        function rotateBanner() {
            currentBannerIndex = (currentBannerIndex + 1) % bannerImages.length;
            const bannerImg = bannerLink.querySelector('img');
            
            if (bannerImg) {
                // Create a fade effect
                bannerImg.style.opacity = '0';
                
                setTimeout(() => {
                    bannerImg.src = bannerImages[currentBannerIndex];
                    bannerImg.style.opacity = '1';
                }, 300);
            }
        }
        
        // Set up the banner rotation interval
        setInterval(rotateBanner, 5000); // Rotate every 5 seconds
    }
    
    // Search form functionality
    const searchForm = document.getElementById('sform');
    const searchInput = document.getElementById('query');
    
    if (searchForm && searchInput) {
        searchForm.addEventListener('submit', function(e) {
            // Only submit if search input has a value
            if (!searchInput.value.trim()) {
                e.preventDefault();
                searchInput.focus();
            }
        });
        
        // Focus on search input when page loads
        searchInput.focus();
    }
    
    // Add hover effects for navigation items
    const serviceLinks = document.querySelectorAll('.link_service');
    
    serviceLinks.forEach(link => {
        link.addEventListener('mouseenter', function() {
            this.style.textDecoration = 'underline';
        });
        
        link.addEventListener('mouseleave', function() {
            this.style.textDecoration = 'none';
        });
    });
    
    // 배너 롤링 기능 구현
    initBannerRolling();
    
    // 네비게이션 아이템 초기 활성화
    const naviItems = document.querySelectorAll('.navi_item');
    if (naviItems.length > 0) {
        naviItems[0].classList.add('active');
    }
    
    // 미디어 아이템에 호버 효과 추가
    const mediaItems = document.querySelectorAll('.media_item');
    mediaItems.forEach(item => {
        item.addEventListener('mouseenter', function() {
            this.style.transform = 'translateY(-2px)';
            this.style.boxShadow = '0 2px 5px rgba(0,0,0,0.1)';
            this.style.borderColor = '#19ce60';
        });
        
        item.addEventListener('mouseleave', function() {
            this.style.transform = 'translateY(0)';
            this.style.boxShadow = 'none';
            this.style.borderColor = '#e3e5e8';
        });
    });
});

// 배너 롤링 초기화 함수
function initBannerRolling() {
    const rollingPanel = document.querySelector('.rolling_panel');
    const naviItems = document.querySelectorAll('.navi_item');
    const banners = document.querySelectorAll('.link_banner');
    
    if (!rollingPanel || !naviItems.length || !banners.length) return;
    
    // 배너의 너비를 설정
    const containerWidth = rollingPanel.parentElement.offsetWidth;
    banners.forEach(banner => {
        banner.style.width = `${containerWidth}px`;
    });
    
    // 첫 번째 네비게이션 아이템 활성화
    naviItems[0].classList.add('active');
    
    let currentIndex = 0;
    const totalBanners = banners.length;
    
    // 네비게이션 아이템 클릭 이벤트
    naviItems.forEach((item, index) => {
        item.addEventListener('click', () => {
            clearInterval(autoRolling);
            moveBanner(index);
            autoRolling = setInterval(autoRoll, 4000);
        });
    });
    
    // 배너 이동 함수
    function moveBanner(index) {
        if (index === currentIndex) return;
        
        // 이전 배너 페이드 아웃
        banners[currentIndex].style.opacity = '0.5';
        
        currentIndex = index;
        
        // 롤링 패널 이동
        rollingPanel.style.transform = `translateX(-${index * containerWidth}px)`;
        
        // 현재 배너 페이드 인
        setTimeout(() => {
            banners.forEach(banner => {
                banner.style.opacity = '0.5';
            });
            banners[currentIndex].style.opacity = '1';
        }, 100);
        
        // 네비게이션 활성화 상태 변경
        naviItems.forEach((navi, i) => {
            if (i === index) {
                navi.classList.add('active');
            } else {
                navi.classList.remove('active');
            }
        });
    }
    
    // 초기 배너 투명도 설정
    banners.forEach((banner, i) => {
        banner.style.opacity = i === 0 ? '1' : '0.5';
        banner.style.transition = 'opacity 0.3s ease';
    });
    
    // 자동 롤링 설정
    function autoRoll() {
        const nextIndex = (currentIndex + 1) % totalBanners;
        moveBanner(nextIndex);
    }
    
    let autoRolling = setInterval(autoRoll, 4000);
    
    // 배너에 마우스 올리면 자동 롤링 정지
    rollingPanel.parentElement.addEventListener('mouseenter', () => {
        clearInterval(autoRolling);
    });
    
    // 배너에서 마우스 나가면 자동 롤링 재개
    rollingPanel.parentElement.addEventListener('mouseleave', () => {
        clearInterval(autoRolling);
        autoRolling = setInterval(autoRoll, 4000);
    });
    
    // 윈도우 크기 변경 시 배너 너비 조정
    window.addEventListener('resize', () => {
        const newWidth = rollingPanel.parentElement.offsetWidth;
        banners.forEach(banner => {
            banner.style.width = `${newWidth}px`;
        });
        rollingPanel.style.transform = `translateX(-${currentIndex * newWidth}px)`;
    });
} 