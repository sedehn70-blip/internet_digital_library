// Lazy Loading تصاویر با IntersectionObserver
document.addEventListener("DOMContentLoaded", function() {
    const lazyImages = document.querySelectorAll("img.lazyload");

    if ("IntersectionObserver" in window) {
        const observer = new IntersectionObserver((entries, observer) => {
            entries.forEach(entry => {
                if(entry.isIntersecting) {
                    const img = entry.target;
                    img.src = img.dataset.src;
                    img.classList.remove("lazyload");
                    img.classList.add("lazyloaded");
                    observer.unobserve(img);
                }
            });
        });

        lazyImages.forEach(img => observer.observe(img));
    } else {
        // fallback برای مرورگرهای قدیمی
        lazyImages.forEach(img => img.src = img.dataset.src);
    }
});

// Smooth Scroll برای Pagination
document.querySelectorAll(".pagination a").forEach(link => {
    link.addEventListener("click", function(e) {
        e.preventDefault();
        const url = this.href;
        fetch(url).then(resp => resp.text()).then(html => {
            document.querySelector("#books-grid").innerHTML = new DOMParser().parseFromString(html, "text/html").querySelector("#books-grid").innerHTML;
            window.scrollTo({top: 0, behavior: 'smooth'});
        });
    });
});
