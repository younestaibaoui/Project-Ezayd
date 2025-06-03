// Modal functionality
class Modal {
  constructor(element) {
    this.modal = element
    this.isOpen = false
    this.previouslyFocused = null
    this.focusableElements = []

    this.init()
  }

  init() {
    this.setupEventListeners()
    this.updateFocusableElements()
  }

  setupEventListeners() {
    // Close button
    const closeBtn = this.modal.querySelector(".modal-close")
    if (closeBtn) {
      closeBtn.addEventListener("click", () => this.close())
    }

    // Backdrop click
    this.modal.addEventListener("click", (e) => {
      if (e.target === this.modal) {
        this.close()
      }
    })

    // Keyboard events
    this.modal.addEventListener("keydown", (e) => this.handleKeydown(e))
  }

  updateFocusableElements() {
    const selectors = [
      "button:not([disabled])",
      "[href]",
      "input:not([disabled])",
      "select:not([disabled])",
      "textarea:not([disabled])",
      '[tabindex]:not([tabindex="-1"])',
    ]

    this.focusableElements = Array.from(this.modal.querySelectorAll(selectors.join(", ")))
  }

  open() {
    if (this.isOpen) return

    this.previouslyFocused = document.activeElement
    this.isOpen = true

    // Show modal
    this.modal.style.display = "flex"
    this.modal.setAttribute("aria-hidden", "false")
    this.modal.classList.add("show")

    // Prevent body scroll
    document.body.style.overflow = "hidden"
    document.body.setAttribute("aria-hidden", "true")

    // Focus first element
    setTimeout(() => {
      if (this.focusableElements.length > 0) {
        this.focusableElements[0].focus()
      }
    }, 100)

    // Announce to screen readers
    this.announce("Modal ouvert")
  }

  close() {
    if (!this.isOpen) return

    this.isOpen = false

    // Hide modal
    this.modal.classList.remove("show")
    this.modal.setAttribute("aria-hidden", "true")

    setTimeout(() => {
      this.modal.style.display = "none"
    }, 300)

    // Restore body scroll
    document.body.style.overflow = ""
    document.body.removeAttribute("aria-hidden")

    // Return focus
    if (this.previouslyFocused) {
      this.previouslyFocused.focus()
    }

    // Announce to screen readers
    this.announce("Modal fermé")
  }

  handleKeydown(e) {
    if (!this.isOpen) return

    switch (e.key) {
      case "Escape":
        e.preventDefault()
        this.close()
        break

      case "Tab":
        this.handleTabKey(e)
        break
    }
  }

  handleTabKey(e) {
    if (this.focusableElements.length === 0) return

    const firstElement = this.focusableElements[0]
    const lastElement = this.focusableElements[this.focusableElements.length - 1]

    if (e.shiftKey) {
      // Shift + Tab
      if (document.activeElement === firstElement) {
        e.preventDefault()
        lastElement.focus()
      }
    } else {
      // Tab
      if (document.activeElement === lastElement) {
        e.preventDefault()
        firstElement.focus()
      }
    }
  }

  announce(message) {
    const announcement = document.createElement("div")
    announcement.setAttribute("aria-live", "polite")
    announcement.setAttribute("aria-atomic", "true")
    announcement.className = "sr-only"
    announcement.textContent = message

    document.body.appendChild(announcement)

    setTimeout(() => {
      document.body.removeChild(announcement)
    }, 1000)
  }
}

// Initialize modals when DOM is loaded
document.addEventListener("DOMContentLoaded", () => {
  const modals = document.querySelectorAll(".modal")
  modals.forEach((modal) => {
    const modalInstance = new Modal(modal)

    // Store instance for external access
    modal.modalInstance = modalInstance
  })

  // Setup modal triggers
  document.addEventListener("click", (e) => {
    const trigger = e.target.closest("[data-modal-target]")
    if (trigger) {
      const targetId = trigger.getAttribute("data-modal-target")
      const modal = document.getElementById(targetId)
      if (modal && modal.modalInstance) {
        modal.modalInstance.open()
      }
    }
  })
})
