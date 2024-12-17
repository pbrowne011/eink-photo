interface UploadResponse {
    message?: string;
    error?: string;
}

interface PhotoInfo {
    filename: string;
    path: string;
}

class PhotoUploader {
    private readonly MAX_TOASTS = 3;
    private dropZone: HTMLElement;
    private photoDirElement: HTMLElement;
    private statusContainer: HTMLElement | null = null;
    private activeToasts: number = 0;

    constructor() {
        this.dropZone = document.getElementById('drop-zone')!;
        this.photoDirElement = document.getElementById('photo-dir')!;
        
        this.initializeEventListeners();
        this.loadPhotos();
        this.initializeStatusContainer();
    }

    private initializeEventListeners(): void {
        this.dropZone.addEventListener('dragover', (e: DragEvent) => {
            e.preventDefault();
            e.stopPropagation();
            this.dropZone.classList.add('dragover');
        });

        this.dropZone.addEventListener('dragleave', () => {
            this.dropZone.classList.remove('dragover');
        });

        this.dropZone.addEventListener('drop', async (e: DragEvent) => {
            e.preventDefault();
            e.stopPropagation();
            this.dropZone.classList.remove('dragover');

            const files = e.dataTransfer?.files;
            if (files) {
                await this.handleFiles(files);
            }
        });

        // Also handle click-to-upload
        this.dropZone.addEventListener('click', () => {
            const input = document.createElement('input');
            input.type = 'file';
            input.accept = 'image/*';
            input.multiple = true;
            input.onchange = (e: Event) => {
                const target = e.target as HTMLInputElement;
                if (target.files) {
                    this.handleFiles(target.files);
                }
            };
            input.click();
        });
    }

    private async handleFiles(files: FileList): Promise<void> {
        for (const file of Array.from(files)) {
            if (file.type.startsWith('image/')) {
                await this.uploadFile(file);
            } else {
                this.updateStatus(`Skipped ${file.name} - not an image`, 'error');
            }
        }
        await this.loadPhotos();
    }

    private async uploadFile(file: File): Promise<void> {
        const formData = new FormData();
        formData.append('file', file);

        try {
            const response = await fetch('/upload', {
                method: 'POST',
                body: formData
            });

            const data: UploadResponse = await response.json();
            
            if (response.ok) {
                this.updateStatus(`Uploaded ${file.name} successfully`, 'success');
            } else {
                this.updateStatus(`Failed to upload ${file.name}: ${data.error}`, 'error');
            }
        } catch (error) {
            this.updateStatus(`Error uploading ${file.name}`, 'error');
            console.error('Upload error:', error);
        }
    }

    private async loadPhotos(): Promise<void> {
        try {
            const response = await fetch('/photos/list');
            if (!response.ok) {
                throw new Error('Failed to fetch photos');
            }
            const photos: PhotoInfo[] = await response.json();

            this.photoDirElement.innerHTML = '';
            const photoGrid = document.createElement('div');
            photoGrid.className = 'photo-grid';

            photos.forEach(photo => {
                const photoContainer = document.createElement('div');
                photoContainer.className = 'photo-container';
                const img = document.createElement('img');
                img.src = photo.path;
                img.alt = photo.filename;
                const deleteBtn = document.createElement('button');
                deleteBtn.textContent = 'Delete';
                deleteBtn.className = 'delete-btn';
                deleteBtn.addEventListener('click', () =>
                    this.deletePhoto(photo.filename));
                photoContainer.appendChild(img);
                photoContainer.appendChild(deleteBtn);
                photoGrid.appendChild(photoContainer);
            });
            
            this.photoDirElement.appendChild(photoGrid);    
        } catch (error) {
            this.updateStatus('Failed to load photos', 'error');
            console.error('Error loading photos:', error);
        }
    }

    private async deletePhoto(filename: string): Promise<void> {
        try {
            const response = await fetch(`/photos/delete/${filename}`, {
                method: 'DELETE'
            });
            if (response.ok) {
                this.updateStatus(`Deleted ${filename} successfully`,
                                  'success');
                await this.loadPhotos();
            } else {
                const errorData = await response.json();
                this.updateStatus(`Failed to delete ${filename}: ${errorData.error}`, 'error');
            }
        } catch (error) {
            this.updateStatus(`Error deleting ${filename}`, 'error');
            console.error('Error deleting photo:', 'error');
        }
    }

    private initializeStatusContainer(): void {
        this.statusContainer = document.querySelector('.status-container');
        if (!this.statusContainer) {
            this.statusContainer = document.createElement('div');
            this.statusContainer.className = 'status-container';
            document.body.appendChild(this.statusContainer);
        }
    }

    private updateStatus(message: string, type: 'success' | 'error'): void {
        if (!this.statusContainer) return;
        
        const statusDiv = document.createElement('div');
        statusDiv.textContent = message;
        statusDiv.className = `status-message ${type} pending`;

        if (this.activeToasts >= this.MAX_TOASTS) {
            const oldestToast = this.statusContainer.firstChild as HTMLElement;
            if (oldestToast) {
                oldestToast.classList.add('hiding');
                setTimeout(() => {
                    oldestToast.remove();
                    this.activeToasts--;
                }, 300);
            }
        }
        
        this.statusContainer!.appendChild(statusDiv);
        statusDiv.offsetHeight;
        statusDiv.classList.remove('pending');        
        this.activeToasts++;
        
        setTimeout(() => {
            statusDiv.classList.add('hiding');
            setTimeout(() => {
                statusDiv.remove();
                this.activeToasts--;
            }, 300);
        }, 3000);
    }
}

// Initialize when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    new PhotoUploader();
});
