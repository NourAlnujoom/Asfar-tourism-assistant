// Chatbot functionality
class Chatbot {
    constructor() {
        this.messagesContainer = document.querySelector('.chat-messages');
        this.inputField = document.querySelector('.chat-input input');
        this.sendButton = document.querySelector('.chat-input button');
        this.isLoading = false;
        
        this.init();
    }
    
    init() {
        // Add event listeners
        this.sendButton.addEventListener('click', () => this.sendMessage());
        this.inputField.addEventListener('keypress', (e) => {
            if (e.key === 'Enter') {
                this.sendMessage();
            }
        });
        
        // Add welcome message
        this.addBotMessage("Hello! I'm your Jordan travel assistant.Please enter the place you plan to visit, your intended time, and your current location. I'll help you find the best time to go and suggest other interesting stops along the way.");
    }
    
    async sendMessage() {
        const message = this.inputField.value.trim();
        if (!message || this.isLoading) return;
        
        // Add user message
        this.addUserMessage(message);
        this.inputField.value = '';
        
        // Show loading
        this.showLoading();
        
        try {
            const response = await fetch('/chat', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ message: message })
            });
            
            const data = await response.json();
            
            // Hide loading
            this.hideLoading();
            
            if (data.status === 'success') {
                this.addBotMessage(data.response);
            } else {
                this.addBotMessage("Sorry, I encountered an error. Please try again.");
            }
        } catch (error) {
            this.hideLoading();
            this.addBotMessage("Sorry, I'm having trouble connecting. Please check your internet connection and try again.");
        }
    }
    
    addUserMessage(message) {
        const messageDiv = document.createElement('div');
        messageDiv.className = 'message user';
        messageDiv.innerHTML = `
            <div class="message-content">
                ${this.escapeHtml(message)}
            </div>
        `;
        this.messagesContainer.appendChild(messageDiv);
        this.scrollToBottom();
    }
    
    addBotMessage(message) {
        const messageDiv = document.createElement('div');
        messageDiv.className = 'message bot';
        messageDiv.innerHTML = `
            <div class="message-content">
                ${this.escapeHtml(message)}
            </div>
        `;
        this.messagesContainer.appendChild(messageDiv);
        this.scrollToBottom();
    }
    
    showLoading() {
        this.isLoading = true;
        const loadingDiv = document.createElement('div');
        loadingDiv.className = 'message bot';
        loadingDiv.id = 'loading-message';
        loadingDiv.innerHTML = `
            <div class="message-content">
                <div class="loading"></div> Thinking...
            </div>
        `;
        this.messagesContainer.appendChild(loadingDiv);
        this.scrollToBottom();
    }
    
    hideLoading() {
        this.isLoading = false;
        const loadingMessage = document.getElementById('loading-message');
        if (loadingMessage) {
            loadingMessage.remove();
        }
    }
    
    scrollToBottom() {
        this.messagesContainer.scrollTop = this.messagesContainer.scrollHeight;
    }
    
    escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }
}

// Initialize chatbot when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    if (document.querySelector('.chat-container')) {
        new Chatbot();
    }
});

// Smooth scrolling for navigation links
document.addEventListener('DOMContentLoaded', function() {
    const navLinks = document.querySelectorAll('a[href^="#"]');
    
    navLinks.forEach(link => {
        link.addEventListener('click', function(e) {
            e.preventDefault();
            const targetId = this.getAttribute('href');
            const targetSection = document.querySelector(targetId);
            
            if (targetSection) {
                targetSection.scrollIntoView({
                    behavior: 'smooth',
                    block: 'start'
                });
            }
        });
    });
});

// Mobile menu toggle (if needed)
document.addEventListener('DOMContentLoaded', function() {
    const mobileMenuButton = document.querySelector('.mobile-menu-button');
    const navLinks = document.querySelector('.nav-links');
    
    if (mobileMenuButton && navLinks) {
        mobileMenuButton.addEventListener('click', function() {
            navLinks.classList.toggle('active');
        });
    }
});

// Add some interactive features
document.addEventListener('DOMContentLoaded', function() {
    // Add hover effects to cards
    const cards = document.querySelectorAll('.card, .audio-card');
    cards.forEach(card => {
        card.addEventListener('mouseenter', function() {
            this.style.transform = 'translateY(-5px)';
        });
        
        card.addEventListener('mouseleave', function() {
            this.style.transform = 'translateY(0)';
        });
    });
    
    // Add click effects to buttons
    const buttons = document.querySelectorAll('.btn');
    buttons.forEach(button => {
        button.addEventListener('click', function() {
            this.style.transform = 'scale(0.95)';
            setTimeout(() => {
                this.style.transform = '';
            }, 150);
        });
    });
}); 