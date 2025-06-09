// Main JavaScript functionality
class EzaydApp {
    constructor() {
        this.init();
    }

    init() {
        this.setupEventListeners();
        this.setupAccessibility();
        this.setupLazyLoading();
        this.setupServiceWorker();
    }

    setupEventListeners() {
        // Mobile menu toggle
        const mobileToggle = document.querySelector(".mobile-menu-toggle");
        if (mobileToggle) {
            mobileToggle.addEventListener("click", this.toggleMobileMenu.bind(this));
        }

        // Login modal
        const loginBtn = document.querySelector(".login-btn");
        const modal = document.getElementById("login-modal");
        const closeBtn = document.querySelector(".modal-close");

        if (loginBtn && modal) {
            loginBtn.addEventListener("click", () => this.openModal(modal));
        }

        if (closeBtn && modal) {
            closeBtn.addEventListener("click", () => this.closeModal(modal));
        }

        // Close modal on outside click
        if (modal) {
            modal.addEventListener("click", (e) => {
                if (e.target === modal) {
                    this.closeModal(modal);
                }
            });
        }

        // Escape key to close modal
        document.addEventListener("keydown", (e) => {
            if (e.key === "Escape" && modal && !modal.hasAttribute("aria-hidden")) {
                this.closeModal(modal);
            }
        });

        // Bookmark functionality
        document.addEventListener("click", (e) => {
            if (e.target.closest(".bookmark-btn")) {
                this.toggleBookmark(e.target.closest(".bookmark-btn"));
            }
        });

        // Search functionality
        const searchInput = document.querySelector(".search-input");
        if (searchInput) {
            searchInput.addEventListener("change", this.handleSearch.bind(this));
        }

        // Filter functionality
        this.setupFilters();
    }

    setupAccessibility() {
        // Focus management for dropdowns
        const dropdownButtons = document.querySelectorAll('[aria-haspopup="true"]');
        dropdownButtons.forEach((button) => {
            button.addEventListener("click", this.toggleDropdown.bind(this));
            button.addEventListener("keydown", this.handleDropdownKeydown.bind(this));
        });

        // Skip link functionality
        const skipLink = document.querySelector(".skip-link");
        if (skipLink) {
            skipLink.addEventListener("click", (e) => {
                e.preventDefault();
                const target = document.querySelector(skipLink.getAttribute("href"));
                if (target) {
                    target.focus();
                    target.scrollIntoView();
                }
            });
        }
    }

    setupLazyLoading() {
        // Intersection Observer for lazy loading images
        if ("IntersectionObserver" in window) {
            const imageObserver = new IntersectionObserver((entries, observer) => {
                entries.forEach((entry) => {
                    if (entry.isIntersecting) {
                        const img = entry.target;
                        img.src = img.dataset.src;
                        img.classList.remove("lazy");
                        observer.unobserve(img);
                    }
                });
            });

            document.querySelectorAll("img[data-src]").forEach((img) => {
                imageObserver.observe(img);
            });
        }
    }

    setupServiceWorker() {
        // Register service worker for offline functionality
        if ("serviceWorker" in navigator) {
            window.addEventListener("load", () => {
                navigator.serviceWorker
                    .register("/sw.js")
                    .then((registration) => {
                        console.log("SW registered: ", registration);
                    })
                    .catch((registrationError) => {
                        console.log("SW registration failed: ", registrationError);
                    });
            });
        }
    }

    toggleMobileMenu() {
        const toggle = document.querySelector(".mobile-menu-toggle");
        const navList = document.querySelector(".nav-list");
        if (toggle && navList) {
            const isExpanded = toggle.getAttribute("aria-expanded") === "true";
            toggle.setAttribute("aria-expanded", !isExpanded);
            navList.classList.toggle("mobile-open");
        }
    }

    openModal(modal) {
        modal.style.display = "flex";
        modal.setAttribute("aria-hidden", "false");
        modal.classList.add("show");

        // Focus first input
        const firstInput = modal.querySelector("input");
        if (firstInput) {
            firstInput.focus();
        }

        // Trap focus
        this.trapFocus(modal);

        // Prevent body scroll
        document.body.style.overflow = "hidden";
    }

    closeModal(modal) {
        modal.classList.remove("show");
        modal.setAttribute("aria-hidden", "true");
        setTimeout(() => {
            modal.style.display = "none";
        }, 300);

        // Restore body scroll
        document.body.style.overflow = "";

        // Return focus to trigger
        const loginBtn = document.querySelector(".login-btn");
        if (loginBtn) {
            loginBtn.focus();
        }
    }

    trapFocus(element) {
        const focusableElements = element.querySelectorAll(
            'button, [href], input, select, textarea, [tabindex]:not([tabindex="-1"])'
        );
        const firstElement = focusableElements[0];
        const lastElement = focusableElements[focusableElements.length - 1];

        element.addEventListener("keydown", (e) => {
            if (e.key === "Tab") {
                if (e.shiftKey) {
                    if (document.activeElement === firstElement) {
                        lastElement.focus();
                        e.preventDefault();
                    }
                } else {
                    if (document.activeElement === lastElement) {
                        firstElement.focus();
                        e.preventDefault();
                    }
                }
            }
        });
    }

    toggleBookmark(button) {
        const isPressed = button.getAttribute("aria-pressed") === "true";
        button.setAttribute("aria-pressed", !isPressed);
        const icon = button.querySelector("i");
        if (icon) {
            icon.classList.toggle("fas");
            icon.classList.toggle("far");
        }
        this.showNotification(isPressed ? "Retiré des favoris" : "Ajouté aux favoris", "success");
    }

    handleSearch(e) {
        const searchTerm = e.target.value;
        if (searchTerm) {
            console.log("Searching for:", searchTerm);
            // Implement search functionality if needed
        }
    }

    setupFilters() {
        const sortButtons = document.querySelectorAll(".sort-btn");
        sortButtons.forEach((button) => {
            button.addEventListener("click", () => {
                sortButtons.forEach((btn) => {
                    btn.classList.remove("active");
                    btn.setAttribute("aria-pressed", "false");
                });
                button.classList.add("active");
                button.setAttribute("aria-pressed", "true");
                const sortType = button.textContent.trim();
                this.sortAuctions(sortType);
            });
        });

        const yearFrom = document.getElementById("year-from");
        const yearTo = document.getElementById("year-to");
        const wilayaFilter = document.getElementById("wilaya-filter");
        [yearFrom, yearTo, wilayaFilter].forEach((filter) => {
            if (filter) {
                filter.addEventListener("change", this.applyFilters.bind(this));
            }
        });
    }

    sortAuctions(sortType) {
        const auctionGrid = document.querySelector(".auction-grid");
        const auctions = Array.from(auctionGrid.children);
        auctions.sort((a, b) => {
            switch (sortType) {
                case "Bientôt fini":
                    return this.getTimeRemaining(a) - this.getTimeRemaining(b);
                case "Récemment ajouté":
                    return this.getDateAdded(b) - this.getDateAdded(a);
                default:
                    return 0;
            }
        });
        auctions.forEach((auction) => auctionGrid.appendChild(auction));
    }

    applyFilters() {
        const yearFrom = document.getElementById("year-from")?.value;
        const yearTo = document.getElementById("year-to")?.value;
        const wilaya = document.getElementById("wilaya-filter")?.value;
        const auctions = document.querySelectorAll(".auction-card");

        auctions.forEach((auction) => {
            let shouldShow = true;
            if (yearFrom || yearTo) {
                const auctionYear = this.getAuctionYear(auction);
                if (yearFrom && auctionYear < Number.parseInt(yearFrom)) shouldShow = false;
                if (yearTo && auctionYear > Number.parseInt(yearTo)) shouldShow = false;
            }
            if (wilaya) {
                const auctionWilaya = this.getAuctionWilaya(auction);
                if (auctionWilaya !== wilaya) shouldShow = false;
            }
            auction.style.display = shouldShow ? "block" : "none";
        });
    }

    getTimeRemaining(auction) {
        const timeElement = auction.querySelector(".time-remaining");
        if (timeElement) {
            const text = timeElement.textContent;
            const days = Number.parseInt(text.match(/(\d+) jours?/)?.[1] || "0");
            return days;
        }
        return 0;
    }

    getDateAdded(auction) {
        return new Date(auction.dataset.dateAdded || Date.now());
    }

    getAuctionYear(auction) {
        const title = auction.querySelector(".card-title")?.textContent || "";
        const yearMatch = title.match(/(\d{4})/);
        return yearMatch ? Number.parseInt(yearMatch[1]) : 0;
    }

    getAuctionWilaya(auction) {
        return auction.dataset.wilaya || "";
    }

    toggleDropdown(e) {
        const button = e.target.closest('[aria-haspopup="true"]');
        const dropdown = button.nextElementSibling;
        if (dropdown) {
            const isExpanded = button.getAttribute("aria-expanded") === "true";
            button.setAttribute("aria-expanded", !isExpanded);
            dropdown.classList.toggle("show");
        }
    }

    handleDropdownKeydown(e) {
        if (e.key === "Enter" || e.key === " ") {
            e.preventDefault();
            this.toggleDropdown(e);
        }
    }

    showNotification(message, type = "info") {
        const notification = document.createElement("div");
        notification.className = `notification notification-${type}`;
        notification.textContent = message;
        notification.setAttribute("role", "alert");
        notification.setAttribute("aria-live", "polite");

        Object.assign(notification.style, {
            position: "fixed",
            top: "20px",
            right: "20px",
            padding: "1rem 1.5rem",
            borderRadius: "6px",
            color: "white",
            fontWeight: "600",
            zIndex: "3000",
            transform: "translateX(100%)",
            transition: "transform 0.3s ease",
            maxWidth: "300px",
        });

        const colors = {
            success: "#28a745",
            error: "#dc3545",
            warning: "#ffc107",
            info: "#17a2b8",
        };
        notification.style.backgroundColor = colors[type] || colors.info;

        document.body.appendChild(notification);
        setTimeout(() => {
            notification.style.transform = "translateX(0)";
        }, 100);
        setTimeout(() => {
            notification.style.transform = "translateX(100%)";
            setTimeout(() => {
                if (notification.parentNode) {
                    notification.parentNode.removeChild(notification);
                }
            }, 300);
        }, 3000);
    }
}

// Initialize app when DOM is loaded
document.addEventListener("DOMContentLoaded", () => {
    new EzaydApp();
});

// Export for module usage
if (typeof module !== "undefined" && module.exports) {
    module.exports = EzaydApp;
}