// Global variables
let currentProjectId = null;

// Initialize the application
document.addEventListener('DOMContentLoaded', function() {
    setupEventListeners();
    loadProjects();
});

function setupEventListeners() {
    // Create project form
    const createForm = document.getElementById('createProjectForm');
    if (createForm) {
        createForm.addEventListener('submit', handleCreateProject);
    }
}

async function handleCreateProject(e) {
    e.preventDefault();
    
    const projectName = document.getElementById('projectName').value.trim();
    const websiteUrl = document.getElementById('websiteUrl').value.trim();
    
    if (!projectName || !websiteUrl) {
        showError('Please fill in all fields.');
        return;
    }
    
    try {
        const response = await fetch('/api/projects', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                name: projectName,
                website_url: websiteUrl
            })
        });
        
        const data = await response.json();
        
        if (response.ok) {
            showSuccess('Project created successfully!');
            document.getElementById('createProjectForm').reset();
            loadProjects(); // Refresh the projects list
        } else {
            showError('Failed to create project: ' + data.error);
        }
    } catch (error) {
        showError('Network error: ' + error.message);
    }
}

async function loadProjects() {
    const projectsList = document.getElementById('projectsList');
    
    try {
        const response = await fetch('/api/projects');
        const data = await response.json();
        
        if (response.ok) {
            updateProjectsList(data.projects);
        } else {
            showError('Failed to load projects: ' + data.error);
        }
    } catch (error) {
        showError('Network error: ' + error.message);
        projectsList.innerHTML = `
            <div class="text-center py-4">
                <i class="fas fa-exclamation-triangle fa-2x text-warning mb-3"></i>
                <h5 class="text-muted">Error Loading Projects</h5>
                <p class="text-muted">${error.message}</p>
            </div>
        `;
    }
}

function updateProjectsList(projects) {
    const projectsList = document.getElementById('projectsList');
    
    if (projects.length === 0) {
        projectsList.innerHTML = `
            <div class="text-center py-5">
                <i class="fas fa-folder-plus fa-3x text-muted mb-3"></i>
                <h5 class="text-muted">No Projects Yet</h5>
                <p class="text-muted">Create your first project to get started with screenshot generation.</p>
            </div>
        `;
        return;
    }
    
    let html = '<div class="row">';
    
    projects.forEach(project => {
        html += `
            <div class="col-md-6 col-lg-4 mb-3">
                <div class="card h-100">
                    <div class="card-body">
                        <h5 class="card-title">
                            <i class="fas fa-folder me-2"></i>
                            ${escapeHtml(project.name)}
                        </h5>
                        <p class="card-text text-muted">
                            <i class="fas fa-link me-1"></i>
                            <small>${escapeHtml(project.website_url)}</small>
                        </p>
                        <div class="d-flex justify-content-between align-items-center">
                            <small class="text-muted">
                                <i class="fas fa-images me-1"></i>
                                ${project.screenshot_count} screenshots
                            </small>
                            <div class="btn-group">
                                <button class="btn btn-sm btn-primary" onclick="viewProject(${project.id})">
                                    <i class="fas fa-eye me-1"></i>
                                    View
                                </button>
                                <button class="btn btn-sm btn-outline-primary" onclick="openDeviceModalForProject(${project.id})">
                                    <i class="fas fa-camera me-1"></i>
                                    Generate
                                </button>
                            </div>
                        </div>
                    </div>
                    <div class="card-footer text-muted small">
                        <i class="fas fa-clock me-1"></i>
                        Created: ${new Date(project.created_at).toLocaleDateString()}
                    </div>
                </div>
            </div>
        `;
    });
    
    html += '</div>';
    projectsList.innerHTML = html;
}

function viewProject(projectId) {
    window.location.href = `/project/${projectId}`;
}

function openDeviceModalForProject(projectId) {
    currentProjectId = projectId;
    const modal = new bootstrap.Modal(document.getElementById('deviceModal'));
    modal.show();
}

async function generateScreenshots() {
    if (!currentProjectId) {
        showError('No project selected.');
        return;
    }
    
    const devices = [];
    if (document.getElementById('deviceMobile').checked) devices.push('mobile');
    if (document.getElementById('deviceTablet').checked) devices.push('tablet');
    if (document.getElementById('deviceDesktop').checked) devices.push('desktop');
    
    if (devices.length === 0) {
        showError('Please select at least one device type.');
        return;
    }
    
    // Close device modal and show loading modal
    bootstrap.Modal.getInstance(document.getElementById('deviceModal')).hide();
    const loadingModal = new bootstrap.Modal(document.getElementById('loadingModal'));
    loadingModal.show();
    
    try {
        const response = await fetch(`/api/projects/${currentProjectId}/screenshots`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ devices })
        });
        
        const data = await response.json();
        loadingModal.hide();
        
        if (response.ok) {
            showSuccess(`Generated ${data.screenshots.length} screenshots successfully!`);
            loadProjects(); // Refresh the projects list
        } else {
            showError('Failed to generate screenshots: ' + data.error);
        }
    } catch (error) {
        loadingModal.hide();
        showError('Network error: ' + error.message);
    }
    
    currentProjectId = null;
}

function showSuccess(message) {
    // Create a simple toast notification
    const toast = document.createElement('div');
    toast.className = 'toast-notification success';
    toast.innerHTML = `
        <i class="fas fa-check-circle me-2"></i>
        ${message}
    `;
    document.body.appendChild(toast);
    
    setTimeout(() => {
        toast.remove();
    }, 3000);
}

function showError(message) {
    // Create a simple toast notification
    const toast = document.createElement('div');
    toast.className = 'toast-notification error';
    toast.innerHTML = `
        <i class="fas fa-exclamation-circle me-2"></i>
        ${message}
    `;
    document.body.appendChild(toast);
    
    setTimeout(() => {
        toast.remove();
    }, 5000);
}

function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}
