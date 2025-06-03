/**
 * Carousel - Composant de carrousel interactif pour Ezayd
 * Fonctionnalités:
 * - Navigation par boutons (précédent/suivant)
 * - Indicateurs cliquables
 * - Autoplay avec pause au survol
 * - Navigation tactile (swipe)
 * - Navigation clavier (flèches, Home, End)
 * - Accessibilité (ARIA, annonces)
 * - Responsive
 */
class Carousel {
  /**
   * Initialise un nouveau carrousel
   * @param {HTMLElement} container - L'élément conteneur du carrousel
   */
  constructor(container) {
    // Éléments DOM
    this.container = container
    this.track = container.querySelector(".carousel-track")
    this.slides = Array.from(container.querySelectorAll(".carousel-slide"))
    this.prevBtn = container.querySelector(".carousel-prev")
    this.nextBtn = container.querySelector(".carousel-next")
    this.indicators = Array.from(container.querySelectorAll(".indicator"))

    // État
    this.currentSlide = 0
    this.slideCount = this.slides.length
    this.isAnimating = false
    this.autoplayInterval = null
    this.autoplayDelay = 5000 // 5 secondes
    this.touchStartX = 0
    this.touchEndX = 0

    // Initialisation
    if (this.slideCount > 0) {
      this.init()
    }
  }

  /**
   * Initialise le carrousel
   */
  init() {
    // Configuration initiale
    this.setupEventListeners()
    this.setupKeyboardNavigation()
    this.setupTouchNavigation()
    this.setupAccessibility()

    // Démarrer l'autoplay et afficher le premier slide
    this.startAutoplay()
    this.goToSlide(0)

    // Log pour débogage
    console.log(`Carousel initialized with ${this.slideCount} slides`)
  }

  /**
   * Configure les écouteurs d'événements
   */
  setupEventListeners() {
    // Boutons de navigation
    if (this.prevBtn) {
      this.prevBtn.addEventListener("click", () => this.prevSlide())
    }

    if (this.nextBtn) {
      this.nextBtn.addEventListener("click", () => this.nextSlide())
    }

    // Indicateurs
    this.indicators.forEach((indicator, index) => {
      indicator.addEventListener("click", () => this.goToSlide(index))
    })

    // Pause de l'autoplay au survol
    this.container.addEventListener("mouseenter", () => this.pauseAutoplay())
    this.container.addEventListener("mouseleave", () => this.startAutoplay())

    // Pause de l'autoplay quand la page n'est pas visible
    document.addEventListener("visibilitychange", () => {
      if (document.hidden) {
        this.pauseAutoplay()
      } else {
        this.startAutoplay()
      }
    })

    // Pause de l'autoplay au focus
    this.container.addEventListener("focusin", () => this.pauseAutoplay())
    this.container.addEventListener("focusout", () => this.startAutoplay())

    // Clic sur les miniatures
    const thumbnails = this.container.querySelectorAll(".thumbnail")
    thumbnails.forEach((thumbnail, slideIndex) => {
      const imageIndex = Math.floor(slideIndex / 2) // 2 miniatures par slide
      thumbnail.addEventListener("click", () => this.goToSlide(imageIndex))
    })
  }

  /**
   * Configure la navigation au clavier
   */
  setupKeyboardNavigation() {
    this.container.setAttribute("tabindex", "0")

    this.container.addEventListener("keydown", (e) => {
      // Empêcher le défilement de la page
      if (["ArrowLeft", "ArrowRight", "Home", "End"].includes(e.key)) {
        e.preventDefault()
      }

      switch (e.key) {
        case "ArrowLeft":
          this.prevSlide()
          break
        case "ArrowRight":
          this.nextSlide()
          break
        case "Home":
          this.goToSlide(0)
          break
        case "End":
          this.goToSlide(this.slideCount - 1)
          break
      }
    })
  }

  /**
   * Configure la navigation tactile (swipe)
   */
  setupTouchNavigation() {
    // Événements tactiles
    this.container.addEventListener(
      "touchstart",
      (e) => {
        this.touchStartX = e.changedTouches[0].screenX
        this.pauseAutoplay()
      },
      { passive: true },
    )

    this.container.addEventListener(
      "touchend",
      (e) => {
        this.touchEndX = e.changedTouches[0].screenX
        this.handleSwipe()
        this.startAutoplay()
      },
      { passive: true },
    )

    // Événements de souris pour simuler le swipe
    let isDragging = false

    this.container.addEventListener("mousedown", (e) => {
      isDragging = true
      this.touchStartX = e.screenX
      this.pauseAutoplay()
      this.container.style.cursor = "grabbing"
    })

    this.container.addEventListener("mousemove", (e) => {
      if (!isDragging) return
      e.preventDefault() // Empêcher la sélection de texte
    })

    this.container.addEventListener("mouseup", (e) => {
      if (!isDragging) return

      isDragging = false
      this.touchEndX = e.screenX
      this.handleSwipe()
      this.startAutoplay()
      this.container.style.cursor = ""
    })

    // Annuler le drag si la souris quitte le conteneur
    this.container.addEventListener("mouseleave", () => {
      if (isDragging) {
        isDragging = false
        this.container.style.cursor = ""
        this.startAutoplay()
      }
    })
  }

  /**
   * Configure l'accessibilité
   */
  setupAccessibility() {
    // Attributs ARIA pour le conteneur
    this.container.setAttribute("role", "region")
    this.container.setAttribute("aria-roledescription", "carousel")
    this.container.setAttribute("aria-label", "Carrousel des enchères en vedette")

    // Attributs ARIA pour les slides
    this.slides.forEach((slide, index) => {
      slide.setAttribute("role", "group")
      slide.setAttribute("aria-roledescription", "slide")
      slide.setAttribute("aria-label", `Slide ${index + 1} sur ${this.slideCount}`)
      slide.setAttribute("aria-hidden", index === 0 ? "false" : "true")
    })

    // Attributs ARIA pour les boutons
    if (this.prevBtn) {
      this.prevBtn.setAttribute("aria-label", "Slide précédent")
      this.prevBtn.setAttribute("aria-controls", "carousel-track")
    }

    if (this.nextBtn) {
      this.nextBtn.setAttribute("aria-label", "Slide suivant")
      this.nextBtn.setAttribute("aria-controls", "carousel-track")
    }

    // Attributs ARIA pour les indicateurs
    this.indicators.forEach((indicator, index) => {
      indicator.setAttribute("role", "tab")
      indicator.setAttribute("aria-label", `Aller au slide ${index + 1}`)
      indicator.setAttribute("aria-selected", index === 0 ? "true" : "false")
      indicator.setAttribute("aria-controls", `slide-${index}`)
    })

    // Créer une région live pour les annonces
    this.liveRegion = document.createElement("div")
    this.liveRegion.className = "sr-only"
    this.liveRegion.setAttribute("aria-live", "polite")
    this.liveRegion.setAttribute("aria-atomic", "true")
    this.container.appendChild(this.liveRegion)
  }

  /**
   * Gère les événements de swipe
   */
  handleSwipe() {
    const swipeThreshold = 50 // Seuil de détection du swipe
    const swipeDistance = this.touchEndX - this.touchStartX

    if (Math.abs(swipeDistance) > swipeThreshold) {
      if (swipeDistance > 0) {
        this.prevSlide()
      } else {
        this.nextSlide()
      }
    }
  }

  /**
   * Va au slide précédent
   */
  prevSlide() {
    if (this.isAnimating) return

    const prevIndex = this.currentSlide === 0 ? this.slideCount - 1 : this.currentSlide - 1
    this.goToSlide(prevIndex, "prev")
  }

  /**
   * Va au slide suivant
   */
  nextSlide() {
    if (this.isAnimating) return

    const nextIndex = (this.currentSlide + 1) % this.slideCount
    this.goToSlide(nextIndex, "next")
  }

  /**
   * Va à un slide spécifique
   * @param {number} index - L'index du slide cible
   * @param {string} direction - La direction de la transition (next/prev)
   */
  goToSlide(index, direction = "next") {
    // Vérifier si l'index est valide
    if (index < 0 || index >= this.slideCount || index === this.currentSlide || this.isAnimating) {
      return
    }

    this.isAnimating = true

    // Mettre à jour l'état actuel
    const previousSlide = this.currentSlide
    this.currentSlide = index

    // Mettre à jour la position du track
    const translateX = -index * 100
    this.track.style.transform = `translateX(${translateX}%)`

    // Mettre à jour les indicateurs
    this.indicators.forEach((indicator, i) => {
      indicator.classList.toggle("active", i === index)
      indicator.setAttribute("aria-selected", i === index)
    })

    // Mettre à jour la visibilité des slides pour les lecteurs d'écran
    this.slides.forEach((slide, i) => {
      slide.setAttribute("aria-hidden", i !== index)
    })

    // Mettre à jour l'état des boutons
    if (this.prevBtn) {
      this.prevBtn.disabled = false
      this.prevBtn.setAttribute("aria-disabled", "false")
    }

    if (this.nextBtn) {
      this.nextBtn.disabled = false
      this.nextBtn.setAttribute("aria-disabled", "false")
    }

    // Annoncer le changement de slide aux lecteurs d'écran
    this.announceSlideChange(index)

    // Réinitialiser l'état d'animation après la transition
    setTimeout(() => {
      this.isAnimating = false
    }, 500) // Correspond à la durée de transition CSS
  }

  /**
   * Démarre l'autoplay
   */
  startAutoplay() {
    // Arrêter l'autoplay existant
    this.pauseAutoplay()

    // Démarrer un nouvel autoplay
    this.autoplayInterval = setInterval(() => {
      this.nextSlide()
    }, this.autoplayDelay)
  }

  /**
   * Met en pause l'autoplay
   */
  pauseAutoplay() {
    if (this.autoplayInterval) {
      clearInterval(this.autoplayInterval)
      this.autoplayInterval = null
    }
  }

  /**
   * Annonce le changement de slide aux lecteurs d'écran
   * @param {number} index - L'index du nouveau slide
   */
  announceSlideChange(index) {
    const slide = this.slides[index]
    const title = slide.querySelector(".slide-title")?.textContent || ""
    const price = slide.querySelector(".price-value")?.textContent || ""
    const time = slide.querySelector(".time-remaining")?.textContent || ""

    const announcement = `Slide ${index + 1} sur ${this.slideCount}: ${title}. Prix: ${price}. ${time}`

    if (this.liveRegion) {
      this.liveRegion.textContent = announcement
    }
  }

  /**
   * Détruit le carrousel et nettoie les ressources
   */
  destroy() {
    // Arrêter l'autoplay
    this.pauseAutoplay()

    // Supprimer les écouteurs d'événements (si nécessaire)

    // Réinitialiser les styles
    this.track.style.transform = ""

    // Log pour débogage
    console.log("Carousel destroyed")
  }
}

/**
 * Initialise tous les carrousels sur la page
 */
function initCarousels() {
  const carouselContainers = document.querySelectorAll(".carousel-container")

  // Créer une instance de carrousel pour chaque conteneur
  const carousels = Array.from(carouselContainers).map((container) => new Carousel(container))

  // Exposer les instances pour un accès externe (débogage)
  window.ezaydCarousels = carousels

  return carousels
}

// Initialiser les carrousels lorsque le DOM est chargé
if (document.readyState === "loading") {
  document.addEventListener("DOMContentLoaded", initCarousels)
} else {
  initCarousels()
}
