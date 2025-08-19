// Smart Glasses Interface JavaScript

class SmartGlassesApp {
    constructor() {
        this.cameraRunning = false;
        this.currentImages = [];
        this.selectedImage = null;
        
        this.init();
    }

    init() {
        this.bindEvents();
        this.checkCameraStatus();
        this.loadImages();
        this.loadChatHistory();
        
        // Auto-refresh images every 30 seconds
        setInterval(() => {
            if (this.cameraRunning) {
                this.loadImages();
            }
        }, 30000);
    }

    bindEvents() {
        // Camera controls
        document.getElementById('camera-toggle').addEventListener('click', () => this.toggleCamera());
        document.getElementById('capture-single').addEventListener('click', () => this.captureSingle());
        document.getElementById('refresh-images').addEventListener('click', () => this.loadImages());

        // Chat
        document.getElementById('chat-form').addEventListener('submit', (e) => this.submitChat(e));
        
        // Modal
        document.getElementById('close-modal').addEventListener('click', () => this.closeModal());
        document.getElementById('analyze-image').addEventListener('click', () => this.analyzeCurrentImage());
        
        // Click outside modal to close
        document.getElementById('image-modal').addEventListener('click', (e) => {
            if (e.target.id === 'image-modal') {
                this.closeModal();
            }
        });

        // Enter key in image question
        document.getElementById('image-question').addEventListener('keypress', (e) => {
            if (e.key === 'Enter') {
                this.analyzeCurrentImage();
            }
        });
    }

    async checkCameraStatus() {
        try {
            const response = await fetch('/api/camera/status');
            const status = await response.json();
            this.updateCameraStatus(status.running, status.connected);
        } catch (error) {
            console.error('Error checking camera status:', error);
            this.updateCameraStatus(false, false);
        }
    }

    updateCameraStatus(running, connected) {
        this.cameraRunning = running;
        const indicator = document.getElementById('status-indicator');
        const statusText = document.getElementById('status-text');
        const toggleButton = document.getElementById('camera-toggle');

        if (running) {
            indicator.className = 'w-3 h-3 bg-green-500 rounded-full status-pulse';
            statusText.textContent = 'Camera Running';
            toggleButton.innerHTML = '<i class="fas fa-stop mr-2"></i>Stop Camera';
            toggleButton.className = 'bg-red-600 hover:bg-red-700 px-4 py-2 rounded-lg transition-colors';
        } else if (connected) {
            indicator.className = 'w-3 h-3 bg-yellow-500 rounded-full';
            statusText.textContent = 'Camera Connected';
            toggleButton.innerHTML = '<i class="fas fa-play mr-2"></i>Start Camera';
            toggleButton.className = 'bg-blue-600 hover:bg-blue-700 px-4 py-2 rounded-lg transition-colors';
        } else {
            indicator.className = 'w-3 h-3 bg-red-500 rounded-full';
            statusText.textContent = 'Camera Disconnected';
            toggleButton.innerHTML = '<i class="fas fa-play mr-2"></i>Start Camera';
            toggleButton.className = 'bg-blue-600 hover:bg-blue-700 px-4 py-2 rounded-lg transition-colors';
        }
    }

    async toggleCamera() {
        const toggleButton = document.getElementById('camera-toggle');
        toggleButton.disabled = true;

        try {
            const endpoint = this.cameraRunning ? '/api/camera/stop' : '/api/camera/start';
            const response = await fetch(endpoint, { method: 'POST' });
            const result = await response.json();

            if (response.ok) {
                this.showToast(result.message, 'success');
                await this.checkCameraStatus();
            } else {
                this.showToast(result.error || 'Camera operation failed', 'error');
            }
        } catch (error) {
            this.showToast('Error communicating with camera', 'error');
            console.error('Camera toggle error:', error);
        }

        toggleButton.disabled = false;
    }

    async captureSingle() {
        const button = document.getElementById('capture-single');
        const originalText = button.innerHTML;
        button.disabled = true;
        button.innerHTML = '<i class="fas fa-spinner fa-spin mr-1"></i>Capturing...';

        try {
            const response = await fetch('/api/camera/capture', { method: 'POST' });
            const result = await response.json();

            if (response.ok) {
                this.showToast('Image captured successfully!', 'success');
                setTimeout(() => this.loadImages(), 1000); // Refresh images after 1 second
            } else {
                this.showToast(result.error || 'Capture failed', 'error');
            }
        } catch (error) {
            this.showToast('Error capturing image', 'error');
            console.error('Capture error:', error);
        }

        button.disabled = false;
        button.innerHTML = originalText;
    }

    async loadImages() {
        try {
            const response = await fetch('/api/images');
            const images = await response.json();
            this.currentImages = images;
            this.renderImages(images);
        } catch (error) {
            console.error('Error loading images:', error);
            this.showToast('Error loading images', 'error');
        }
    }

    renderImages(images) {
        const gallery = document.getElementById('image-gallery').querySelector('.grid');
        const noImages = document.getElementById('no-images');

        if (images.length === 0) {
            gallery.innerHTML = '';
            noImages.style.display = 'block';
            return;
        }

        noImages.style.display = 'none';
        gallery.innerHTML = images.map(image => `
            <div class="image-item bg-gray-700 rounded-lg cursor-pointer" data-filename="${image.filename}">
                <img src="/api/image/${image.filename}" alt="Captured at ${image.timestamp}" loading="lazy">
                <div class="image-overlay">
                    <i class="fas fa-search-plus"></i>
                </div>
                <div class="absolute bottom-0 left-0 right-0 bg-black bg-opacity-75 text-white text-xs p-2 rounded-b-lg">
                    <div class="font-medium">${image.filename}</div>
                    <div class="text-gray-300">${image.timestamp}</div>
                </div>
            </div>
        `).join('');

        // Add click handlers to images
        gallery.querySelectorAll('.image-item').forEach(item => {
            item.addEventListener('click', () => {
                const filename = item.dataset.filename;
                this.openImageModal(filename);
            });
        });
    }

    openImageModal(filename) {
        this.selectedImage = filename;
        const image = this.currentImages.find(img => img.filename === filename);
        
        if (image) {
            document.getElementById('modal-title').textContent = `${image.filename} - ${image.timestamp}`;
            document.getElementById('modal-image').src = `/api/image/${filename}`;
            document.getElementById('image-analysis').innerHTML = '<span class="text-gray-400">Click "Analyze Image" to get AI insights</span>';
            document.getElementById('image-question').value = '';
            document.getElementById('image-modal').classList.remove('hidden');
        }
    }

    closeModal() {
        document.getElementById('image-modal').classList.add('hidden');
        this.selectedImage = null;
    }

    async analyzeCurrentImage() {
        if (!this.selectedImage) return;

        const button = document.getElementById('analyze-image');
        const analysisDiv = document.getElementById('image-analysis');
        const question = document.getElementById('image-question').value.trim();

        button.disabled = true;
        button.innerHTML = '<i class="fas fa-spinner fa-spin mr-1"></i>Analyzing...';
        analysisDiv.innerHTML = '<div class="loading-spinner"></div> Analyzing image...';

        try {
            const response = await fetch(`/api/analyze/${this.selectedImage}`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ question: question || null })
            });

            const result = await response.json();

            if (response.ok) {
                analysisDiv.innerHTML = this.formatAnalysis(result.analysis);
            } else {
                analysisDiv.innerHTML = `<span class="text-red-400">Error: ${result.error}</span>`;
            }
        } catch (error) {
            analysisDiv.innerHTML = '<span class="text-red-400">Error analyzing image</span>';
            console.error('Analysis error:', error);
        }

        button.disabled = false;
        button.innerHTML = '<i class="fas fa-search mr-1"></i>Analyze Image';
    }

    formatAnalysis(text) {
        // Format the analysis text with better styling
        return text.replace(/\n/g, '<br>').replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');
    }

    async submitChat(e) {
        e.preventDefault();
        
        const input = document.getElementById('chat-input');
        const message = input.value.trim();
        
        if (!message) return;

        input.value = '';
        this.addChatMessage(message, 'user');
        this.addTypingIndicator();

        try {
            const response = await fetch('/api/chat', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ message })
            });

            const result = await response.json();
            this.removeTypingIndicator();

            if (response.ok) {
                this.addChatMessage(result.response, 'ai');
            } else {
                this.addChatMessage(`Error: ${result.error}`, 'ai');
            }
        } catch (error) {
            this.removeTypingIndicator();
            this.addChatMessage('Error communicating with AI assistant', 'ai');
            console.error('Chat error:', error);
        }
    }

    addChatMessage(message, sender) {
        const messagesContainer = document.getElementById('chat-messages');
        const messageDiv = document.createElement('div');
        messageDiv.className = `chat-message ${sender}`;
        
        const timestamp = new Date().toLocaleTimeString();
        messageDiv.innerHTML = `
            <div class="message-content">${this.formatMessage(message)}</div>
            <div class="timestamp">${timestamp}</div>
        `;

        messagesContainer.appendChild(messageDiv);
        messagesContainer.scrollTop = messagesContainer.scrollHeight;

        // Remove welcome message if it exists
        const welcomeMessage = messagesContainer.querySelector('.text-center');
        if (welcomeMessage) {
            welcomeMessage.remove();
        }
    }

    addTypingIndicator() {
        const messagesContainer = document.getElementById('chat-messages');
        const typingDiv = document.createElement('div');
        typingDiv.className = 'chat-message ai typing-indicator';
        typingDiv.innerHTML = `
            <div class="message-content">
                <div class="loading-spinner"></div> AI is thinking...
            </div>
        `;
        messagesContainer.appendChild(typingDiv);
        messagesContainer.scrollTop = messagesContainer.scrollHeight;
    }

    removeTypingIndicator() {
        const typingIndicator = document.querySelector('.typing-indicator');
        if (typingIndicator) {
            typingIndicator.remove();
        }
    }

    formatMessage(text) {
        // Format message text with basic markdown-like styling
        return text
            .replace(/\n/g, '<br>')
            .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
            .replace(/\*(.*?)\*/g, '<em>$1</em>');
    }

    async loadChatHistory() {
        try {
            const response = await fetch('/api/chat/history');
            const history = await response.json();
            
            history.forEach(chat => {
                this.addChatMessage(chat.user_message, 'user');
                this.addChatMessage(chat.ai_response, 'ai');
            });
        } catch (error) {
            console.error('Error loading chat history:', error);
        }
    }

    showToast(message, type = 'info') {
        const container = document.getElementById('toast-container');
        const toast = document.createElement('div');
        toast.className = `toast ${type}`;
        toast.innerHTML = `
            <div class="flex items-center justify-between">
                <span>${message}</span>
                <button class="ml-2 text-gray-300 hover:text-white" onclick="this.parentElement.parentElement.remove()">
                    <i class="fas fa-times"></i>
                </button>
            </div>
        `;
        
        container.appendChild(toast);

        // Auto-remove after 5 seconds
        setTimeout(() => {
            if (toast.parentElement) {
                toast.remove();
            }
        }, 5000);
    }
}

// Initialize the app when the page loads
document.addEventListener('DOMContentLoaded', () => {
    new SmartGlassesApp();
});
