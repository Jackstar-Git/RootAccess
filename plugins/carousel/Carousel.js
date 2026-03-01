class Carousel {
    constructor(carouselElement) {
        this.carouselElement = carouselElement;
        this.items = [...this.carouselElement.querySelectorAll(".carousel-item")];
        this.totalItems = this.items.length;
        this.currentIndex = 0;
        this.isAnimating = false;
        this.reducedMotion = window.matchMedia("(prefers-reduced-motion)").matches;
        this.disableIndicators = this.carouselElement.dataset.disableIndicators;

        this.prevButton = this.carouselElement.querySelector(".prev-btn");
        this.nextButton = this.carouselElement.querySelector(".next-btn");

        this.prevButton.addEventListener("click", () => this.showPrevImage());
        this.nextButton.addEventListener("click", () => this.showNextImage());

        if (!this.disableIndicators) {
            this.indicators = [];
            const indicatorContainer = document.createElement("div");
            indicatorContainer.classList.add("carousel-indicators");
        
            this.items.forEach((_, index) => {
                const indicator = document.createElement("button");
                indicator.setAttribute("data-slide-to", index.toString());
                indicator.setAttribute("aria-label", `Slide ${index + 1}`);
                indicator.addEventListener("click", () => this.showSlide(index));
                indicatorContainer.append(indicator);
                this.indicators.push(indicator);
            });
            this.carouselElement.append(indicatorContainer);
            this.indicators[this.currentIndex].classList.add("active");
        }

        this.items[this.currentIndex].classList.add("active");

        this.speed = parseFloat(this.carouselElement.dataset.speed) / 1000 || 0.8;
        this.carouselElement.style.setProperty("--speed", `${this.speed}s`);
        this.delay = parseFloat(this.carouselElement.dataset.delay) || 5000;

        this.autoSlide = this.carouselElement.dataset.auto === "true";
        if (this.autoSlide) {
            this.startAutoSlide();
        }
    }

    startAutoSlide() {
        this.stopAutoSlide();
        this.autoSlideInterval = setInterval(() => {
            if (!this.isAnimating) {
                this.showNextImage();
            }
        }, this.delay);
    }

    stopAutoSlide() {
        clearInterval(this.autoSlideInterval);
    }

    showNextImage() {
        const nextIndex = (this.currentIndex + 1) % this.totalItems;
        this.showSlide(nextIndex);
    }

    showPrevImage() {
        const prevIndex = (this.currentIndex - 1 + this.totalItems) % this.totalItems;
        this.showSlide(prevIndex);
    }

    showSlide(index) {
        if (this.isAnimating || index === this.currentIndex) return;

        const activeItem = this.items[this.currentIndex];
        const targetItem = this.items[index];

        if (this.reducedMotion) {
            this.instantSlide(index);
        } else {
            this.isAnimating = true;
            if ((index > this.currentIndex && !(index === this.totalItems - 1 && this.currentIndex === 0)) ||
                (this.currentIndex === this.totalItems - 1 && index === 0)) {
                targetItem.classList.add("carousel-item-next");
                targetItem.offsetHeight;

                requestAnimationFrame(() => {
                    activeItem.classList.add("carousel-item-left");
                    targetItem.classList.remove("carousel-item-next");
                    targetItem.classList.add("active");

                    targetItem.addEventListener("transitionend", () => {
                        activeItem.classList.remove("carousel-item-left", "active");
                        this.updateIndicators(index);
                        this.currentIndex = index;
                        this.isAnimating = false;
                    }, { once: true });
                });
            } else {
                targetItem.classList.add("carousel-item-prev");
                targetItem.offsetHeight;

                requestAnimationFrame(() => {
                    activeItem.classList.add("carousel-item-right");
                    targetItem.classList.remove("carousel-item-prev");
                    targetItem.classList.add("active");

                    targetItem.addEventListener("transitionend", () => {
                        activeItem.classList.remove("carousel-item-right", "active");
                        this.updateIndicators(index);
                        this.currentIndex = index;
                        this.isAnimating = false;
                    }, { once: true });
                });
            }
        }
    }

    instantSlide(index) {
        const activeItem = this.items[this.currentIndex];
        const targetItem = this.items[index];

        activeItem.classList.remove("active");
        targetItem.classList.add("active");

        this.updateIndicators(index);
        this.currentIndex = index;
        this.isAnimating = false;
    }

    updateIndicators(index) {
        if (!this.disableIndicators) {
            this.indicators[this.currentIndex].classList.remove("active");
            this.indicators[index].classList.add("active");
        }
    }
}

document.querySelectorAll(".carousel").forEach(carouselElement => {
    new Carousel(carouselElement);
});
