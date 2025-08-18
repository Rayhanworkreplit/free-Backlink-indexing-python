/**
 * Real-time Progress Tracker for Ping Campaigns
 * Shows live progress, percentage completion, and current service submissions
 */

class ProgressTracker {
    constructor() {
        this.campaignId = null;
        this.progressInterval = null;
        this.updateFrequency = 1000; // Update every second
        this.totalServices = 0;
        this.processedServices = 0;
        this.currentService = '';
        this.isRunning = false;
        this.setupEventListeners();
    }

    setupEventListeners() {
        // Listen for campaign start events
        document.addEventListener('campaignStarted', (event) => {
            this.startTracking(event.detail);
        });

        // Listen for campaign completion
        document.addEventListener('campaignCompleted', (event) => {
            this.stopTracking();
        });
    }

    startTracking(campaignData) {
        this.campaignId = campaignData.id;
        this.totalServices = campaignData.totalServices || 0;
        this.processedServices = 0;
        this.isRunning = true;

        // Create or update progress UI
        this.createProgressUI();
        
        // Start polling for updates
        this.progressInterval = setInterval(() => {
            this.fetchProgressUpdate();
        }, this.updateFrequency);

        console.log(`Started tracking campaign: ${this.campaignId}`);
    }

    stopTracking() {
        if (this.progressInterval) {
            clearInterval(this.progressInterval);
            this.progressInterval = null;
        }
        this.isRunning = false;
        this.finalizeProgressUI();
    }

    createProgressUI() {
        // Find or create progress container
        let progressContainer = document.getElementById('live-progress');
        
        if (!progressContainer) {
            progressContainer = document.createElement('div');
            progressContainer.id = 'live-progress';
            progressContainer.className = 'card mt-4';
            
            // Insert after campaign form or at top of page
            const targetElement = document.querySelector('.card') || document.body;
            targetElement.parentNode.insertBefore(progressContainer, targetElement.nextSibling);
        }

        progressContainer.innerHTML = `
            <div class="card-header bg-primary text-white">
                <h5 class="mb-0">
                    <i class="fas fa-sync fa-spin me-2"></i>
                    Live Ping Progress - Campaign ${this.campaignId}
                </h5>
            </div>
            <div class="card-body">
                <div class="row mb-3">
                    <div class="col-md-8">
                        <div class="progress mb-2" style="height: 25px;">
                            <div id="main-progress-bar" class="progress-bar progress-bar-striped progress-bar-animated bg-success" 
                                 role="progressbar" style="width: 0%" aria-valuenow="0" aria-valuemin="0" aria-valuemax="100">
                                <span id="progress-percentage">0%</span>
                            </div>
                        </div>
                        <small class="text-muted">
                            <span id="progress-stats">0 of ${this.totalServices} services processed</span>
                        </small>
                    </div>
                    <div class="col-md-4 text-end">
                        <div class="d-flex flex-column">
                            <span class="badge bg-info mb-1" id="current-status">Starting...</span>
                            <small class="text-muted" id="estimated-time">Estimating time...</small>
                        </div>
                    </div>
                </div>
                
                <div class="row">
                    <div class="col-md-6">
                        <h6>Currently Submitting To:</h6>
                        <div id="current-service" class="alert alert-info py-2">
                            <i class="fas fa-clock me-2"></i>Initializing...
                        </div>
                    </div>
                    <div class="col-md-6">
                        <h6>Recent Activity:</h6>
                        <div id="activity-log" class="bg-light p-2 rounded" style="height: 120px; overflow-y: auto; font-size: 0.85em;">
                            <div class="text-muted">Campaign started...</div>
                        </div>
                    </div>
                </div>

                <div class="row mt-3">
                    <div class="col-md-12">
                        <div class="row text-center">
                            <div class="col-3">
                                <div class="card bg-success text-white">
                                    <div class="card-body py-2">
                                        <div class="h4 mb-0" id="success-count">0</div>
                                        <small>Successful</small>
                                    </div>
                                </div>
                            </div>
                            <div class="col-3">
                                <div class="card bg-danger text-white">
                                    <div class="card-body py-2">
                                        <div class="h4 mb-0" id="failed-count">0</div>
                                        <small>Failed</small>
                                    </div>
                                </div>
                            </div>
                            <div class="col-3">
                                <div class="card bg-warning text-white">
                                    <div class="card-body py-2">
                                        <div class="h4 mb-0" id="pending-count">${this.totalServices}</div>
                                        <small>Pending</small>
                                    </div>
                                </div>
                            </div>
                            <div class="col-3">
                                <div class="card bg-info text-white">
                                    <div class="card-body py-2">
                                        <div class="h4 mb-0" id="success-rate">0%</div>
                                        <small>Success Rate</small>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        `;
    }

    async fetchProgressUpdate() {
        if (!this.campaignId || !this.isRunning) return;

        try {
            const response = await fetch(`/api/campaign-progress/${this.campaignId}`);
            if (!response.ok) {
                console.warn('Failed to fetch progress update');
                return;
            }

            const data = await response.json();
            this.updateProgressDisplay(data);

        } catch (error) {
            console.error('Error fetching progress update:', error);
        }
    }

    updateProgressDisplay(data) {
        // Update progress bar
        const percentage = data.percentage || 0;
        const progressBar = document.getElementById('main-progress-bar');
        const progressPercentage = document.getElementById('progress-percentage');
        const progressStats = document.getElementById('progress-stats');

        if (progressBar && progressPercentage && progressStats) {
            progressBar.style.width = `${percentage}%`;
            progressBar.setAttribute('aria-valuenow', percentage);
            progressPercentage.textContent = `${percentage.toFixed(1)}%`;
            progressStats.textContent = `${data.processed || 0} of ${data.total || this.totalServices} services processed`;
        }

        // Update current service
        const currentServiceElement = document.getElementById('current-service');
        if (currentServiceElement && data.currentService) {
            const serviceName = this.extractServiceName(data.currentService);
            currentServiceElement.innerHTML = `
                <i class="fas fa-paper-plane me-2"></i>
                <strong>${serviceName}</strong>
                <br><small class="text-muted">${data.currentService}</small>
            `;
        }

        // Update status and stats
        this.updateStats(data);
        this.updateActivityLog(data);
        this.updateEstimatedTime(data);
    }

    updateStats(data) {
        const successCount = document.getElementById('success-count');
        const failedCount = document.getElementById('failed-count');
        const pendingCount = document.getElementById('pending-count');
        const successRate = document.getElementById('success-rate');

        if (successCount) successCount.textContent = data.successful || 0;
        if (failedCount) failedCount.textContent = data.failed || 0;
        if (pendingCount) pendingCount.textContent = data.pending || this.totalServices;
        
        if (successRate && data.processed > 0) {
            const rate = ((data.successful || 0) / data.processed * 100).toFixed(1);
            successRate.textContent = `${rate}%`;
        }
    }

    updateActivityLog(data) {
        const activityLog = document.getElementById('activity-log');
        if (!activityLog) return;

        // Add new activities
        if (data.recentActivities && data.recentActivities.length > 0) {
            data.recentActivities.forEach(activity => {
                const activityElement = document.createElement('div');
                activityElement.className = `mb-1 ${activity.success ? 'text-success' : 'text-danger'}`;
                activityElement.innerHTML = `
                    <i class="fas ${activity.success ? 'fa-check' : 'fa-times'} me-1"></i>
                    <small>${this.extractServiceName(activity.service)} - ${activity.timestamp}</small>
                `;
                activityLog.insertBefore(activityElement, activityLog.firstChild);
            });

            // Keep only last 5 activities visible
            while (activityLog.children.length > 5) {
                activityLog.removeChild(activityLog.lastChild);
            }
        }
    }

    updateEstimatedTime(data) {
        const estimatedTimeElement = document.getElementById('estimated-time');
        if (estimatedTimeElement && data.estimatedTimeRemaining) {
            estimatedTimeElement.textContent = `ETA: ${data.estimatedTimeRemaining}`;
        }
    }

    extractServiceName(url) {
        try {
            const domain = new URL(url).hostname;
            return domain.replace('www.', '').split('.')[0];
        } catch {
            return 'Service';
        }
    }

    finalizeProgressUI() {
        const progressContainer = document.getElementById('live-progress');
        if (!progressContainer) return;

        // Update header to show completion
        const header = progressContainer.querySelector('.card-header h5');
        if (header) {
            header.innerHTML = `
                <i class="fas fa-check-circle me-2"></i>
                Campaign Complete - ${this.campaignId}
            `;
            header.parentElement.className = 'card-header bg-success text-white';
        }

        // Stop animations
        const progressBar = document.getElementById('main-progress-bar');
        if (progressBar) {
            progressBar.classList.remove('progress-bar-animated');
        }

        // Add completion message
        const currentServiceElement = document.getElementById('current-service');
        if (currentServiceElement) {
            currentServiceElement.innerHTML = `
                <i class="fas fa-check-circle me-2 text-success"></i>
                <strong>All services completed!</strong>
            `;
            currentServiceElement.className = 'alert alert-success py-2';
        }

        console.log(`Campaign ${this.campaignId} tracking completed`);
    }

    // Manual trigger for testing
    simulateProgress(totalServices = 50) {
        this.startTracking({
            id: `test_${Date.now()}`,
            totalServices: totalServices
        });

        // Simulate progress updates
        let processed = 0;
        const simulationInterval = setInterval(() => {
            processed += Math.floor(Math.random() * 3) + 1;
            
            if (processed >= totalServices) {
                processed = totalServices;
                clearInterval(simulationInterval);
                this.stopTracking();
            }

            const mockData = {
                percentage: (processed / totalServices) * 100,
                processed: processed,
                total: totalServices,
                successful: Math.floor(processed * 0.8),
                failed: Math.floor(processed * 0.2),
                pending: totalServices - processed,
                currentService: `https://example-service-${processed}.com/ping`,
                recentActivities: [{
                    service: `https://service-${processed}.com/ping`,
                    success: Math.random() > 0.2,
                    timestamp: new Date().toLocaleTimeString()
                }],
                estimatedTimeRemaining: `${Math.max(0, Math.floor((totalServices - processed) / 2))}s`
            };

            this.updateProgressDisplay(mockData);
        }, 500);
    }
}

// Initialize the progress tracker
const progressTracker = new ProgressTracker();

// Expose for debugging
window.progressTracker = progressTracker;