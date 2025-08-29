class ImageGenerator {
    constructor() {
        this.canvas = null;
        this.ctx = null;
        this.generatedImages = [];
        this.currentTool = 'rectangle';
        this.currentColor = '#3b82f6';
        this.isDrawing = false;
        this.startPos = { x: 0, y: 0 };
        this.endPos = { x: 0, y: 0 };
        
        this.init();
    }
    
    init() {
        this.loadGeneratedImages();
        this.setupEventListeners();
    }
    
    setupEventListeners() {
        // Tool selection
        document.addEventListener('change', (e) => {
            if (e.target.id === 'diagram-type') {
                this.currentTool = e.target.value;
            }
            if (e.target.id === 'diagram-color') {
                this.currentColor = e.target.value;
            }
        });
        
        // Generate diagram button
        document.addEventListener('click', (e) => {
            if (e.target.id === 'generate-diagram-btn') {
                this.generateDiagram();
            }
            if (e.target.id === 'generate-math-btn') {
                this.generateMathDiagram();
            }
            if (e.target.id === 'upload-image-btn') {
                this.handleImageUpload();
            }
            if (e.target.classList.contains('delete-image-btn')) {
                const imageId = e.target.dataset.imageId;
                this.deleteImage(imageId);
            }
            if (e.target.classList.contains('use-image-btn')) {
                const imagePath = e.target.dataset.imagePath;
                this.useImage(imagePath);
            }
        });
        
        // File input change
        document.addEventListener('change', (e) => {
            if (e.target.id === 'image-file-input') {
                this.uploadFile(e.target.files[0]);
            }
        });
    }
    
    initCanvas(containerId, width = 400, height = 300) {
        const container = document.getElementById(containerId);
        if (!container) return;
        
        // Clear existing canvas
        container.innerHTML = '';
        
        // Create canvas
        this.canvas = document.createElement('canvas');
        this.canvas.width = width;
        this.canvas.height = height;
        this.canvas.className = 'border border-slate-600 rounded-lg bg-slate-800';
        this.canvas.style.cursor = 'crosshair';
        
        container.appendChild(this.canvas);
        this.ctx = this.canvas.getContext('2d');
        
        // Setup canvas event listeners
        this.canvas.addEventListener('mousedown', this.handleMouseDown.bind(this));
        this.canvas.addEventListener('mousemove', this.handleMouseMove.bind(this));
        this.canvas.addEventListener('mouseup', this.handleMouseUp.bind(this));
        
        // Clear and draw background
        this.clearCanvas();
    }
    
    clearCanvas() {
        if (!this.ctx) return;
        
        // Clear canvas
        this.ctx.clearRect(0, 0, this.canvas.width, this.canvas.height);
        
        // Draw background
        this.ctx.fillStyle = '#1e293b';
        this.ctx.fillRect(0, 0, this.canvas.width, this.canvas.height);
        
        // Draw grid
        this.drawGrid();
    }
    
    drawGrid() {
        if (!this.ctx) return;
        
        this.ctx.strokeStyle = '#334155';
        this.ctx.lineWidth = 1;
        
        const gridSize = 20;
        
        // Vertical lines
        for (let x = 0; x <= this.canvas.width; x += gridSize) {
            this.ctx.beginPath();
            this.ctx.moveTo(x, 0);
            this.ctx.lineTo(x, this.canvas.height);
            this.ctx.stroke();
        }
        
        // Horizontal lines
        for (let y = 0; y <= this.canvas.height; y += gridSize) {
            this.ctx.beginPath();
            this.ctx.moveTo(0, y);
            this.ctx.lineTo(this.canvas.width, y);
            this.ctx.stroke();
        }
    }
    
    handleMouseDown(e) {
        if (!this.ctx) return;
        
        const rect = this.canvas.getBoundingClientRect();
        this.startPos = {
            x: e.clientX - rect.left,
            y: e.clientY - rect.top
        };
        this.isDrawing = true;
    }
    
    handleMouseMove(e) {
        if (!this.ctx || !this.isDrawing) return;
        
        const rect = this.canvas.getBoundingClientRect();
        this.endPos = {
            x: e.clientX - rect.left,
            y: e.clientY - rect.top
        };
        
        // Redraw canvas with preview
        this.redrawWithPreview();
    }
    
    handleMouseUp(e) {
        if (!this.ctx || !this.isDrawing) return;
        
        const rect = this.canvas.getBoundingClientRect();
        this.endPos = {
            x: e.clientX - rect.left,
            y: e.clientY - rect.top
        };
        
        this.isDrawing = false;
        this.drawShape(this.currentTool, this.startPos, this.endPos, this.currentColor, false);
    }
    
    redrawWithPreview() {
        this.clearCanvas();
        this.drawShape(this.currentTool, this.startPos, this.endPos, this.currentColor, true);
    }
    
    drawShape(type, start, end, color, isPreview) {
        if (!this.ctx) return;
        
        this.ctx.strokeStyle = color;
        this.ctx.lineWidth = isPreview ? 1 : 2;
        
        switch (type) {
            case 'rectangle':
                this.ctx.strokeRect(
                    start.x,
                    start.y,
                    end.x - start.x,
                    end.y - start.y
                );
                break;
                
            case 'circle':
                const radius = Math.sqrt(
                    Math.pow(end.x - start.x, 2) + Math.pow(end.y - start.y, 2)
                );
                this.ctx.beginPath();
                this.ctx.arc(start.x, start.y, radius, 0, 2 * Math.PI);
                this.ctx.stroke();
                break;
                
            case 'line':
                this.ctx.beginPath();
                this.ctx.moveTo(start.x, start.y);
                this.ctx.lineTo(end.x, end.y);
                this.ctx.stroke();
                break;
                
            case 'arrow':
                this.drawArrow(start, end);
                break;
        }
    }
    
    drawArrow(start, end) {
        if (!this.ctx) return;
        
        const headLength = 15;
        const angle = Math.atan2(end.y - start.y, end.x - start.x);
        
        // Draw line
        this.ctx.beginPath();
        this.ctx.moveTo(start.x, start.y);
        this.ctx.lineTo(end.x, end.y);
        this.ctx.stroke();
        
        // Draw arrowhead
        this.ctx.beginPath();
        this.ctx.moveTo(end.x, end.y);
        this.ctx.lineTo(
            end.x - headLength * Math.cos(angle - Math.PI / 6),
            end.y - headLength * Math.sin(angle - Math.PI / 6)
        );
        this.ctx.moveTo(end.x, end.y);
        this.ctx.lineTo(
            end.x - headLength * Math.cos(angle + Math.PI / 6),
            end.y - headLength * Math.sin(angle + Math.PI / 6)
        );
        this.ctx.stroke();
    }
    
    generateDiagram() {
        const diagramType = document.getElementById('diagram-type')?.value || 'rectangle';
        const width = parseInt(document.getElementById('diagram-width')?.value) || 400;
        const height = parseInt(document.getElementById('diagram-height')?.value) || 300;
        const color = document.getElementById('diagram-color')?.value || '#3b82f6';
        
        const parameters = {
            diagram_type: diagramType,
            width: width,
            height: height,
            color: color,
            x1: 50,
            y1: 50,
            x2: 200,
            y2: 150,
            cx: width / 2,
            cy: height / 2,
            radius: 60
        };
        
        this.sendGenerateRequest('diagram', '', parameters);
    }
    
    generateMathDiagram() {
        const functionType = document.getElementById('function-type')?.value || 'linear';
        const width = parseInt(document.getElementById('math-width')?.value) || 400;
        const height = parseInt(document.getElementById('math-height')?.value) || 300;
        const color = document.getElementById('math-color')?.value || '#3b82f6';
        
        const parameters = {
            function_type: functionType,
            width: width,
            height: height,
            color: color
        };
        
        // Add function-specific parameters
        if (functionType === 'linear') {
            parameters.slope = parseFloat(document.getElementById('slope')?.value) || 1;
            parameters.intercept = parseFloat(document.getElementById('intercept')?.value) || 0;
        } else if (functionType === 'parabola') {
            parameters.a = parseFloat(document.getElementById('param-a')?.value) || 1;
            parameters.b = parseFloat(document.getElementById('param-b')?.value) || 0;
            parameters.c = parseFloat(document.getElementById('param-c')?.value) || 0;
        }
        
        this.sendGenerateRequest('math', `${functionType} function`, parameters);
    }
    
    async sendGenerateRequest(type, prompt, parameters) {
        try {
            this.showMessage('Generating image...', 'info');
            
            const response = await fetch('/api/admin/generate-image', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': this.getCSRFToken()
                },
                body: JSON.stringify({
                    type: type,
                    prompt: prompt,
                    parameters: parameters
                })
            });
            
            const result = await response.json();
            
            if (result.status === 'success') {
                this.showMessage('Image generated successfully!', 'success');
                this.loadGeneratedImages();
            } else {
                this.showMessage(result.message || 'Failed to generate image', 'error');
            }
        } catch (error) {
            console.error('Generate image error:', error);
            this.showMessage('Failed to generate image', 'error');
        }
    }
    
    handleImageUpload() {
        const fileInput = document.getElementById('image-file-input');
        if (fileInput) {
            fileInput.click();
        }
    }
    
    async uploadFile(file) {
        if (!file) return;
        
        // Validate file type
        if (!file.type.startsWith('image/')) {
            this.showMessage('Please select an image file', 'error');
            return;
        }
        
        // Validate file size (5MB limit)
        if (file.size > 5 * 1024 * 1024) {
            this.showMessage('File size must be less than 5MB', 'error');
            return;
        }
        
        try {
            this.showMessage('Uploading image...', 'info');
            
            const formData = new FormData();
            formData.append('file', file);
            
            const response = await fetch('/api/admin/upload-image', {
                method: 'POST',
                body: formData
            });
            
            const result = await response.json();
            
            if (result.status === 'success') {
                this.showMessage('Image uploaded successfully!', 'success');
                this.loadGeneratedImages();
            } else {
                this.showMessage(result.message || 'Failed to upload image', 'error');
            }
        } catch (error) {
            console.error('Upload error:', error);
            this.showMessage('Failed to upload image', 'error');
        }
    }
    
    async loadGeneratedImages() {
        try {
            const response = await fetch('/api/admin/images?limit=20');
            const result = await response.json();
            
            if (result.status === 'success') {
                this.generatedImages = result.images;
                this.displayImages();
            }
        } catch (error) {
            console.error('Load images error:', error);
        }
    }
    
    displayImages() {
        const container = document.getElementById('generated-images-list');
        if (!container) return;
        
        if (this.generatedImages.length === 0) {
            container.innerHTML = '<p class="text-gray-400 text-center">No images generated yet</p>';
            return;
        }
        
        container.innerHTML = this.generatedImages.map(img => `
            <div class="bg-slate-700 rounded-lg p-4 border border-slate-600">
                <div class="aspect-video bg-slate-800 rounded mb-3 flex items-center justify-center overflow-hidden">
                    <img src="${img.path}" alt="${img.type}" class="max-w-full max-h-full object-contain" 
                         onerror="this.src='/static/favicon.svg'; this.alt='Failed to load';">
                </div>
                <div class="space-y-2">
                    <div class="flex justify-between items-start">
                        <div>
                            <p class="text-white font-medium capitalize">${img.type}</p>
                            <p class="text-sm text-gray-400">${img.width}×${img.height}</p>
                        </div>
                        <span class="px-2 py-1 bg-slate-600 text-xs rounded text-gray-300">${this.formatFileSize(img.file_size)}</span>
                    </div>
                    ${img.prompt ? `<p class="text-sm text-gray-300">${img.prompt}</p>` : ''}
                    <p class="text-xs text-gray-500">${this.formatDate(img.created_at)}</p>
                    <div class="flex space-x-2 mt-3">
                        <button class="use-image-btn bg-green-600 hover:bg-green-500 text-white text-xs px-3 py-1 rounded" 
                                data-image-path="${img.path}">Use</button>
                        <button class="delete-image-btn bg-red-600 hover:bg-red-500 text-white text-xs px-3 py-1 rounded" 
                                data-image-id="${img.id}">Delete</button>
                    </div>
                </div>
            </div>
        `).join('');
    }
    
    async deleteImage(imageId) {
        if (!confirm('Are you sure you want to delete this image?')) return;
        
        try {
            const response = await fetch(`/api/admin/images/${imageId}`, {
                method: 'DELETE',
                headers: {
                    'X-CSRFToken': this.getCSRFToken()
                }
            });
            
            const result = await response.json();
            
            if (result.status === 'success') {
                this.showMessage('Image deleted successfully', 'success');
                this.loadGeneratedImages();
            } else {
                this.showMessage(result.message || 'Failed to delete image', 'error');
            }
        } catch (error) {
            console.error('Delete error:', error);
            this.showMessage('Failed to delete image', 'error');
        }
    }
    
    useImage(imagePath) {
        // This method can be customized based on where the image should be used
        // For now, copy the path to clipboard
        navigator.clipboard.writeText(imagePath).then(() => {
            this.showMessage('Image path copied to clipboard!', 'success');
        }).catch(() => {
            this.showMessage(`Image path: ${imagePath}`, 'info');
        });
    }
    
    showMessage(message, type = 'info') {
        const messageContainer = document.getElementById('image-generator-message') || 
                                document.getElementById('admin-message');
        
        if (messageContainer) {
            messageContainer.className = `text-center text-lg font-bold mb-4 h-6 ${
                type === 'success' ? 'text-green-400' : 
                type === 'error' ? 'text-red-400' : 'text-blue-400'
            }`;
            messageContainer.textContent = message;
            
            // Clear message after 3 seconds
            setTimeout(() => {
                messageContainer.textContent = '';
                messageContainer.className = 'text-center text-lg font-bold mb-4 h-6';
            }, 3000);
        }
    }
    
    formatFileSize(bytes) {
        if (bytes === 0) return '0 B';
        const k = 1024;
        const sizes = ['B', 'KB', 'MB', 'GB'];
        const i = Math.floor(Math.log(bytes) / Math.log(k));
        return parseFloat((bytes / Math.pow(k, i)).toFixed(1)) + ' ' + sizes[i];
    }
    
    formatDate(dateString) {
        if (!dateString) return '';
        const date = new Date(dateString);
        return date.toLocaleDateString() + ' ' + date.toLocaleTimeString([], {hour: '2-digit', minute:'2-digit'});
    }
    
    getCSRFToken() {
        const token = document.querySelector('meta[name="csrf-token"]')?.getAttribute('content') ||
                     document.querySelector('input[name="csrf_token"]')?.value ||
                     '';
        return token;
    }
}

// Export for use in admin dashboard
window.ImageGenerator = ImageGenerator;