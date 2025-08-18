// Ping Monitor JavaScript for real-time updates and interactive features

class PingMonitor {
    constructor() {
        this.updateInterval = null;
        this.isMonitoring = false;
        this.init();
    }

    init() {
        this.setupEventListeners();
        this.initializeProgressBars();
        this.checkForActiveCampaigns();
    }

    setupEventListeners() {
        // Real-time monitoring toggle
        const monitorToggle = document.getElementById('realTimeMonitor');
        if (monitorToggle) {
            monitorToggle.addEventListener('change', (e) => {
                if (e.target.checked) {
                    this.startMonitoring();
                } else {
                    this.stopMonitoring();
                }
            });
        }

        // Campaign status refresh buttons
        document.querySelectorAll('.refresh-campaign').forEach(button => {
            button.addEventListener('click', (e) => {
                const campaignId = e.target.dataset.campaignId;
                if (campaignId) {
                    this.refreshCampaignStatus(campaignId);
                }
            });
        });

        // Progress bar animations
        this.animateProgressBars();

        // Notification handling
        this.setupNotifications();
    }

    startMonitoring() {
        if (this.isMonitoring) return;
        
        this.isMonitoring = true;
        console.log('Starting real-time ping monitoring...');
        
        // Update every 5 seconds for active campaigns
        this.updateInterval = setInterval(() => {
            this.checkCampaignUpdates();
        }, 5000);

        this.showNotification('Real-time monitoring started', 'success');
    }

    stopMonitoring() {
        if (!this.isMonitoring) return;
        
        this.isMonitoring = false;
        if (this.updateInterval) {
            clearInterval(this.updateInterval);
            this.updateInterval = null;
        }
        
        console.log('Stopped real-time ping monitoring');
        this.showNotification('Real-time monitoring stopped', 'info');
    }

    checkForActiveCampaigns() {
        // Check if there are any processing campaigns on page load
        const processingCampaigns = document.querySelectorAll('[data-status="processing"]');
        if (processingCampaigns.length > 0 && !this.isMonitoring) {
            this.startMonitoring();
            
            // Auto-enable monitoring toggle if it exists
            const monitorToggle = document.getElementById('realTimeMonitor');
            if (monitorToggle) {
                monitorToggle.checked = true;
            }
        }
    }

    async checkCampaignUpdates() {
        const processingCampaigns = document.querySelectorAll('[data-status="processing"]');
        
        if (processingCampaigns.length === 0) {
            this.stopMonitoring();
            return;
        }

        // In a real implementation, this would make AJAX calls to check status
        // For now, we'll simulate progress updates
        processingCampaigns.forEach(campaign => {
            this.updateCampaignProgress(campaign);
        });
    }

    updateCampaignProgress(campaignElement) {
        const progressBar = campaignElement.querySelector('.progress-bar');
        const statusBadge = campaignElement.querySelector('.badge');
        
        if (progressBar && !progressBar.dataset.animated) {
            // Simulate progress animation
            this.animateProgress(progressBar, 0, 100, 2000);
            progressBar.dataset.animated = 'true';
        }

        // Add pulsing effect to processing badges
        if (statusBadge && statusBadge.textContent.includes('Processing')) {
            statusBadge.classList.add('ping-pulse');
        }
    }

    animateProgress(progressBar, start, end, duration) {
        const startTime = performance.now();
        
        const animate = (currentTime) => {
            const elapsed = currentTime - startTime;
            const progress = Math.min(elapsed / duration, 1);
            const currentValue = start + (end - start) * this.easeOutCubic(progress);
            
            progressBar.style.width = `${currentValue}%`;
            progressBar.setAttribute('aria-valuenow', currentValue);
            
            if (progress < 1) {
                requestAnimationFrame(animate);
            }
        };
        
        requestAnimationFrame(animate);
    }

    easeOutCubic(t) {
        return 1 - Math.pow(1 - t, 3);
    }

    initializeProgressBars() {
        // Animate existing progress bars on page load
        document.querySelectorAll('.progress-bar').forEach((bar, index) => {
            const finalValue = parseFloat(bar.style.width) || parseFloat(bar.dataset.value) || 0;
            
            // Stagger animations
            setTimeout(() => {
                this.animateProgress(bar, 0, finalValue, 1000);
            }, index * 100);
        });
    }

    animateProgressBars() {
        // Add hover effects to progress bars
        document.querySelectorAll('.progress').forEach(progress => {
            progress.addEventListener('mouseenter', () => {
                progress.classList.add('progress-hover');
            });
            
            progress.addEventListener('mouseleave', () => {
                progress.classList.remove('progress-hover');
            });
        });
    }

    refreshCampaignStatus(campaignId) {
        console.log(`Refreshing status for campaign: ${campaignId}`);
        
        // Show loading state
        const refreshButton = document.querySelector(`[data-campaign-id="${campaignId}"]`);
        if (refreshButton) {
            const originalHTML = refreshButton.innerHTML;
            refreshButton.innerHTML = '<i class="fas fa-spinner fa-spin"></i>';
            refreshButton.disabled = true;
            
            // Simulate API call delay
            setTimeout(() => {
                refreshButton.innerHTML = originalHTML;
                refreshButton.disabled = false;
                this.showNotification(`Campaign ${campaignId} status updated`, 'success');
            }, 1000);
        }
    }

    setupNotifications() {
        // Check if browser supports notifications
        if ('Notification' in window) {
            // Request permission on first interaction
            document.addEventListener('click', () => {
                if (Notification.permission === 'default') {
                    Notification.requestPermission();
                }
            }, { once: true });
        }
    }

    showNotification(message, type = 'info', duration = 3000) {
        // Create toast notification
        const toast = document.createElement('div');
        toast.className = `alert alert-${type} alert-dismissible fade show position-fixed`;
        toast.style.cssText = `
            top: 20px;
            right: 20px;
            z-index: 9999;
            max-width: 300px;
            box-shadow: 0 4px 12px rgba(0,0,0,0.15);
        `;
        
        toast.innerHTML = `
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        `;
        
        document.body.appendChild(toast);
        
        // Auto-remove after duration
        setTimeout(() => {
            if (toast.parentNode) {
                toast.remove();
            }
        }, duration);

        // Browser notification for important events
        if ('Notification' in window && Notification.permission === 'granted' && type === 'success') {
            new Notification('Ping Indexer Pro', {
                body: message,
                icon: '/favicon.ico'
            });
        }
    }

    // Utility methods for campaign monitoring
    getCampaignStatus(campaignId) {
        // This would normally make an AJAX request to get current status
        return new Promise((resolve) => {
            setTimeout(() => {
                resolve({
                    status: 'processing',
                    progress: Math.random() * 100,
                    successful_pings: Math.floor(Math.random() * 50),
                    failed_pings: Math.floor(Math.random() * 10)
                });
            }, 500);
        });
    }

    updateCampaignDisplay(campaignId, data) {
        const campaignRow = document.querySelector(`[data-campaign-id="${campaignId}"]`);
        if (!campaignRow) return;

        // Update status badge
        const statusBadge = campaignRow.querySelector('.badge');
        if (statusBadge) {
            statusBadge.textContent = data.status;
            statusBadge.className = `badge bg-${this.getStatusColor(data.status)}`;
        }

        // Update progress if exists
        const progressBar = campaignRow.querySelector('.progress-bar');
        if (progressBar && data.progress) {
            progressBar.style.width = `${data.progress}%`;
        }

        // Update ping counts
        const pingCounts = campaignRow.querySelector('.ping-counts');
        if (pingCounts && data.successful_pings !== undefined) {
            pingCounts.textContent = `${data.successful_pings}/${data.successful_pings + data.failed_pings} pings`;
        }
    }

    getStatusColor(status) {
        const colors = {
            'completed': 'success',
            'processing': 'warning',
            'failed': 'danger',
            'pending': 'secondary'
        };
        return colors[status] || 'secondary';
    }

    // URL validation helpers
    validateURL(url) {
        try {
            new URL(url);
            return true;
        } catch {
            return false;
        }
    }

    // Statistics helpers
    calculateSuccessRate(successful, total) {
        return total > 0 ? Math.round((successful / total) * 100 * 10) / 10 : 0;
    }

    formatNumber(num) {
        return new Intl.NumberFormat().format(num);
    }

    // Export functionality
    exportTableData(tableId, filename) {
        const table = document.getElementById(tableId);
        if (!table) return;

        const rows = Array.from(table.querySelectorAll('tr'));
        const csvContent = rows.map(row => {
            const cells = Array.from(row.querySelectorAll('th, td'));
            return cells.map(cell => `"${cell.textContent.trim()}"`).join(',');
        }).join('\n');

        this.downloadCSV(csvContent, filename);
    }

    downloadCSV(content, filename) {
        const blob = new Blob([content], { type: 'text/csv;charset=utf-8;' });
        const link = document.createElement('a');
        
        if (link.download !== undefined) {
            const url = URL.createObjectURL(blob);
            link.setAttribute('href', url);
            link.setAttribute('download', filename);
            link.style.visibility = 'hidden';
            document.body.appendChild(link);
            link.click();
            document.body.removeChild(link);
        }
    }
}

// Initialize ping monitor when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    window.pingMonitor = new PingMonitor();
});

// Add CSS animations
const style = document.createElement('style');
style.textContent = `
    @keyframes ping-pulse {
        0%, 100% { opacity: 1; }
        50% { opacity: 0.5; }
    }
    
    .ping-pulse {
        animation: ping-pulse 2s infinite;
    }
    
    .progress-hover .progress-bar {
        transform: scaleY(1.1);
        transition: transform 0.2s ease;
    }
    
    .campaign-row:hover {
        background-color: rgba(255, 255, 255, 0.05);
        transition: background-color 0.2s ease;
    }
    
    .fade-in {
        animation: fadeIn 0.5s ease-in;
    }
    
    @keyframes fadeIn {
        from { opacity: 0; transform: translateY(10px); }
        to { opacity: 1; transform: translateY(0); }
    }
    
    .loading-shimmer {
        background: linear-gradient(90deg, transparent, rgba(255,255,255,0.1), transparent);
        background-size: 200% 100%;
        animation: shimmer 1.5s infinite;
    }
    
    @keyframes shimmer {
        0% { background-position: -200% 0; }
        100% { background-position: 200% 0; }
    }
`;
document.head.appendChild(style);

// Global utility functions
window.PingMonitorUtils = {
    formatDate: (dateString) => {
        return new Date(dateString).toLocaleDateString();
    },
    
    formatDateTime: (dateString) => {
        return new Date(dateString).toLocaleString();
    },
    
    copyToClipboard: (text) => {
        navigator.clipboard.writeText(text).then(() => {
            window.pingMonitor.showNotification('Copied to clipboard!', 'success', 1000);
        });
    },
    
    shareResults: (campaignId) => {
        if (navigator.share) {
            navigator.share({
                title: 'Ping Campaign Results',
                text: `Check out my ping campaign results: Campaign ${campaignId}`,
                url: window.location.href
            });
        } else {
            PingMonitorUtils.copyToClipboard(window.location.href);
        }
    }
};
