class AuthManager {
  constructor() {
    this.currentForm = "register"
    this.init()
  }

  init() {
    this.bindEvents()
    this.setupPasswordToggle()
    this.setupFormValidation()
  }

  bindEvents() {
    // Form switching
    document.querySelectorAll(".link-btn").forEach((btn) => {
      btn.addEventListener("click", (e) => {
        const target = e.target.dataset.target
        this.switchForm(target)
      })
    })

    // Form submissions
    document.querySelectorAll(".auth-form").forEach((form) => {
      form.addEventListener("submit", (e) => {
        e.preventDefault()
        this.handleFormSubmit(form)
      })
    })

    // Google Sign-in
    document.querySelectorAll(".btn-google").forEach((btn) => {
      btn.addEventListener("click", () => {
        this.handleGoogleSignIn()
      })
    })
  }

  switchForm(targetForm) {
    const registerContainer = document.querySelector(".form-container-register")
    const loginContainer = document.querySelector(".form-container-login")

    if (targetForm === "login") {
      registerContainer.classList.remove("active")
      loginContainer.classList.add("active", "slide-left")
      this.currentForm = "login"
    } else {
      loginContainer.classList.remove("active")
      registerContainer.classList.add("active", "slide-right")
      this.currentForm = "register"
    }

    // Remove animation classes after animation completes
    setTimeout(() => {
      registerContainer.classList.remove("slide-left", "slide-right")
      loginContainer.classList.remove("slide-left", "slide-right")
    }, 500)
  }

  setupPasswordToggle() {
    document.querySelectorAll(".toggle-visibility").forEach((btn) => {
      btn.addEventListener("click", () => {
        const input = btn.previousElementSibling
        const icon = btn.querySelector("i")

        if (input.type === "password") {
          input.type = "text"
          icon.classList.remove("fa-eye-slash")
          icon.classList.add("fa-eye")
        } else {
          input.type = "password"
          icon.classList.remove("fa-eye")
          icon.classList.add("fa-eye-slash")
        }
      })
    })
  }

  setupFormValidation() {
    document.querySelectorAll("input").forEach((input) => {
      input.addEventListener("blur", () => {
        this.validateField(input)
      })

      input.addEventListener("input", () => {
        this.clearFieldError(input)
      })
    })
  }

  validateField(input) {
    const container = input.closest(".input-container")
    const value = input.value.trim()
    let isValid = true
    let errorMessage = ""

    // Remove existing error
    this.clearFieldError(input)

    // Email validation
    if (input.type === "email") {
      const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/
      if (!emailRegex.test(value)) {
        isValid = false
        errorMessage = "Please enter a valid email address"
      }
    }

    // Password validation
    if (input.name === "password") {
      if (value.length < 8) {
        isValid = false
        errorMessage = "Password must be at least 8 characters long"
      } else if (!/(?=.*[a-z])(?=.*[A-Z])(?=.*\d)/.test(value)) {
        isValid = false
        errorMessage = "Password must contain uppercase, lowercase, and number"
      }
    }

    // Confirm password validation
    if (input.name === "confirmPassword") {
      const passwordInput = document.querySelector('input[name="password"]')
      if (value !== passwordInput.value) {
        isValid = false
        errorMessage = "Passwords do not match"
      }
    }

    // Required field validation
    if (input.required && !value) {
      isValid = false
      errorMessage = "This field is required"
    }

    // Name validation
    if ((input.name === "firstName" || input.name === "lastName") && value) {
      if (!/^[a-zA-Z\s]+$/.test(value)) {
        isValid = false
        errorMessage = "Name can only contain letters and spaces"
      }
    }

    if (!isValid) {
      this.showFieldError(input, errorMessage)
    } else {
      this.showFieldSuccess(input)
    }

    return isValid
  }

  showFieldError(input, message) {
    const container = input.closest(".input-container")
    container.classList.add("error")
    container.classList.remove("success")

    // Remove existing error message
    const existingError = container.querySelector(".error-message")
    if (existingError) {
      existingError.remove()
    }

    // Add new error message
    const errorDiv = document.createElement("div")
    errorDiv.className = "error-message"
    errorDiv.innerHTML = `<i class="fas fa-exclamation-circle"></i> ${message}`
    container.appendChild(errorDiv)
  }

  showFieldSuccess(input) {
    const container = input.closest(".input-container")
    container.classList.add("success")
    container.classList.remove("error")

    // Remove error message
    const existingError = container.querySelector(".error-message")
    if (existingError) {
      existingError.remove()
    }
  }

  clearFieldError(input) {
    const container = input.closest(".input-container")
    container.classList.remove("error", "success")

    const existingError = container.querySelector(".error-message")
    if (existingError) {
      existingError.remove()
    }
  }

  async handleFormSubmit(form) {
    const formData = new FormData(form)
    const data = Object.fromEntries(formData.entries())

    // Validate all fields
    const inputs = form.querySelectorAll("input[required]")
    let isFormValid = true

    inputs.forEach((input) => {
      if (!this.validateField(input)) {
        isFormValid = false
      }
    })

    if (!isFormValid) {
      this.showNotification("Please fix the errors above", "error")
      return
    }

    // Show loading state
    const submitBtn = form.querySelector('button[type="submit"]')
    const originalText = submitBtn.innerHTML
    submitBtn.innerHTML = '<span class="spinner"></span> Processing...'
    submitBtn.disabled = true

    try {
      if (this.currentForm === "register") {
        await this.handleRegistration(data)
      } else {
        await this.handleLogin(data)
      }
    } catch (error) {
      this.showNotification(error.message, "error")
    } finally {
      // Restore button state
      submitBtn.innerHTML = originalText
      submitBtn.disabled = false
    }
  }

  async handleRegistration(data) {
    // Simulate API call
    await this.simulateApiCall()

    // Show verification message
    const verificationMessage = document.querySelector(".verification-message")
    verificationMessage.classList.remove("hidden")

    // Hide form
    const form = document.querySelector(".register-form")
    form.style.display = "none"

    this.showNotification("Registration successful! Please check your email.", "success")
  }

  async handleLogin(data) {
    // Simulate API call
    await this.simulateApiCall()

    this.showNotification("Login successful! Redirecting...", "success")

    // Simulate redirect
    setTimeout(() => {
      window.location.href = "/dashboard"
    }, 2000)
  }

  async handleGoogleSignIn() {
    try {
      // Simulate Google Sign-in
      await this.simulateApiCall()
      this.showNotification("Google Sign-in successful!", "success")
    } catch (error) {
      this.showNotification("Google Sign-in failed. Please try again.", "error")
    }
  }

  simulateApiCall() {
    return new Promise((resolve, reject) => {
      setTimeout(() => {
        // Simulate random success/failure for demo
        if (Math.random() > 0.1) {
          resolve()
        } else {
          reject(new Error("Network error. Please try again."))
        }
      }, 2000)
    })
  }

  showNotification(message, type = "info") {
    // Remove existing notifications
    const existingNotifications = document.querySelectorAll(".notification")
    existingNotifications.forEach((notification) => notification.remove())

    // Create notification
    const notification = document.createElement("div")
    notification.className = `notification notification-${type}`
    notification.innerHTML = `
            <div class="notification-content">
                <i class="fas ${this.getNotificationIcon(type)}"></i>
                <span>${message}</span>
                <button class="notification-close">
                    <i class="fas fa-times"></i>
                </button>
            </div>
        `

    // Add styles
    Object.assign(notification.style, {
      position: "fixed",
      top: "20px",
      right: "20px",
      background: type === "error" ? "#dc3545" : type === "success" ? "#28a745" : "#17a2b8",
      color: "white",
      padding: "15px 20px",
      borderRadius: "8px",
      boxShadow: "0 4px 8px rgba(0,0,0,0.3)",
      zIndex: "10000",
      animation: "slideInRight 0.3s ease-out",
      maxWidth: "400px",
    })

    // Add to page
    document.body.appendChild(notification)

    // Auto remove after 5 seconds
    setTimeout(() => {
      if (notification.parentNode) {
        notification.style.animation = "slideOutRight 0.3s ease-out"
        setTimeout(() => notification.remove(), 300)
      }
    }, 5000)

    // Close button functionality
    notification.querySelector(".notification-close").addEventListener("click", () => {
      notification.style.animation = "slideOutRight 0.3s ease-out"
      setTimeout(() => notification.remove(), 300)
    })
  }

  getNotificationIcon(type) {
    switch (type) {
      case "success":
        return "fa-check-circle"
      case "error":
        return "fa-exclamation-circle"
      case "warning":
        return "fa-exclamation-triangle"
      default:
        return "fa-info-circle"
    }
  }
}

// Utility functions
const Utils = {
  debounce(func, wait) {
    let timeout
    return function executedFunction(...args) {
      const later = () => {
        clearTimeout(timeout)
        func(...args)
      }
      clearTimeout(timeout)
      timeout = setTimeout(later, wait)
    }
  },

  throttle(func, limit) {
    let inThrottle
    return function () {
      const args = arguments
      
      if (!inThrottle) {
        func.apply(this, args)
        inThrottle = true
        setTimeout(() => (inThrottle = false), limit)
      }
    }
  },
}

// Add notification animations to CSS
const style = document.createElement("style")
style.textContent = `
    @keyframes slideInRight {
        from {
            transform: translateX(100%);
            opacity: 0;
        }
        to {
            transform: translateX(0);
            opacity: 1;
        }
    }

    @keyframes slideOutRight {
        from {
            transform: translateX(0);
            opacity: 1;
        }
        to {
            transform: translateX(100%);
            opacity: 0;
        }
    }

    .notification-content {
        display: flex;
        align-items: center;
        gap: 10px;
    }

    .notification-close {
        background: none;
        border: none;
        color: white;
        cursor: pointer;
        padding: 0;
        margin-left: auto;
    }

    .notification-close:hover {
        opacity: 0.7;
    }
`
document.head.appendChild(style)

// Initialize the application
document.addEventListener("DOMContentLoaded", () => {
  new AuthManager()
})

// Handle page visibility for better UX
document.addEventListener("visibilitychange", () => {
  if (document.visibilityState === "visible") {
    // Page became visible, could refresh data or check auth status
    console.log("Page is now visible")
  }
})

// Handle online/offline status
window.addEventListener("online", () => {
  console.log("Connection restored")
})

window.addEventListener("offline", () => {
  console.log("Connection lost")
})
