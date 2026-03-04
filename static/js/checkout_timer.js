/**
 * Checkout Timer - Displays a 10-minute countdown for ticket reservations
 * Automatically releases tickets if timer expires
 */

class CheckoutTimer {
    constructor(orderId, expiresAt) {
        this.orderId = orderId;
        this.expiresAt = new Date(expiresAt);
        this.timerElement = document.getElementById('reservation-timer');
        this.timerDisplay = document.getElementById('timer-display');
        this.expiredMessage = document.getElementById('expired-message');
        this.checkoutForm = document.getElementById('checkout-form');
        this.intervalId = null;
        this.isExpired = false;
        
        if (this.timerElement) {
            this.startTimer();
            // Check expiry status every 5 seconds
            this.checkExpiryInterval = setInterval(() => this.checkExpiry(), 5000);
        }
    }
    
    startTimer() {
        // Update immediately
        this.updateDisplay();
        
        // Update every second
        this.intervalId = setInterval(() => this.updateDisplay(), 1000);
    }
    
    updateDisplay() {
        const now = new Date();
        const timeRemaining = Math.max(0, Math.floor((this.expiresAt - now) / 1000));
        
        if (timeRemaining <= 0) {
            this.handleExpiration();
            return;
        }
        
        const minutes = Math.floor(timeRemaining / 60);
        const seconds = timeRemaining % 60;
        
        // Format as MM:SS
        const displayText = `${String(minutes).padStart(2, '0')}:${String(seconds).padStart(2, '0')}`;
        
        if (this.timerDisplay) {
            this.timerDisplay.textContent = displayText;
        }
        
        // Change color based on time remaining
        if (this.timerElement) {
            if (timeRemaining <= 60) {
                // Less than 1 minute - red
                this.timerElement.classList.remove('timer-warning');
                this.timerElement.classList.add('timer-critical');
            } else if (timeRemaining <= 300) {
                // Less than 5 minutes - orange
                this.timerElement.classList.remove('timer-critical');
                this.timerElement.classList.add('timer-warning');
            } else {
                // More than 5 minutes - green
                this.timerElement.classList.remove('timer-warning', 'timer-critical');
            }
        }
    }
    
    handleExpiration() {
        if (this.isExpired) return;
        
        this.isExpired = true;
        
        // Clear intervals
        if (this.intervalId) clearInterval(this.intervalId);
        if (this.checkExpiryInterval) clearInterval(this.checkExpiryInterval);
        
        // Hide timer, show expired message
        if (this.timerElement) {
            this.timerElement.style.display = 'none';
        }
        
        if (this.expiredMessage) {
            this.expiredMessage.style.display = 'block';
        }
        
        // Disable checkout form
        if (this.checkoutForm) {
            const inputs = this.checkoutForm.querySelectorAll('input, button, select, textarea');
            inputs.forEach(input => {
                input.disabled = true;
            });
        }
        
        // Show alert
        alert('Your reservation has expired. Please go back and select the tickets again.');
    }
    
    checkExpiry() {
        // Make API call to verify reservation status
        fetch(`/api/reservations/${this.orderId}/check-expiry/`)
            .then(response => response.json())
            .then(data => {
                if (data.expired) {
                    this.handleExpiration();
                }
            })
            .catch(error => {
                console.error('Error checking reservation expiry:', error);
            });
    }
    
    destroy() {
        if (this.intervalId) clearInterval(this.intervalId);
        if (this.checkExpiryInterval) clearInterval(this.checkExpiryInterval);
    }
}

// Initialize timer when page loads
document.addEventListener('DOMContentLoaded', function() {
    const timerElement = document.getElementById('reservation-timer');
    if (timerElement) {
        const orderId = timerElement.dataset.orderId;
        const expiresAt = timerElement.dataset.expiresAt;
        
        if (orderId && expiresAt) {
            window.checkoutTimer = new CheckoutTimer(orderId, expiresAt);
        }
    }
});

// Clean up timer when leaving page
window.addEventListener('beforeunload', function() {
    if (window.checkoutTimer) {
        window.checkoutTimer.destroy();
    }
});
