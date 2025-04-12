// static/project_tasks/js/api.js
class ProjectTasksAPI {
    static async getInternalTasks() {
        const response = await fetch('/project-tasks/api/internal-tasks/');
        if (!response.ok) {
            throw new Error('Failed to fetch internal tasks');
        }
        return await response.json();
    }
    
    static async getExternalTasks() {
        const response = await fetch('/project-tasks/api/external-tasks/');
        if (!response.ok) {
            throw new Error('Failed to fetch external tasks');
        }
        return await response.json();
    }
    
    static async getInternalTaskById(taskId) {
        const response = await fetch(`/project-tasks/api/internal-tasks/${taskId}/`);
        if (!response.ok) {
            throw new Error(`Failed to fetch internal task with ID ${taskId}`);
        }
        return await response.json();
    }
    
    static async getExternalTaskById(taskId) {
        const response = await fetch(`/project-tasks/api/external-tasks/${taskId}/`);
        if (!response.ok) {
            throw new Error(`Failed to fetch external task with ID ${taskId}`);
        }
        return await response.json();
    }
    
    static async createInternalTask(taskData) {
        const response = await fetch('/project-tasks/api/internal-tasks/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': this.getCsrfToken()
            },
            body: JSON.stringify(taskData)
        });
        
        if (!response.ok) {
            throw new Error('Failed to create internal task');
        }
        return await response.json();
    }
    
    static async createExternalTask(taskData) {
        const response = await fetch('/project-tasks/api/external-tasks/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': this.getCsrfToken()
            },
            body: JSON.stringify(taskData)
        });
        
        if (!response.ok) {
            throw new Error('Failed to create external task');
        }
        return await response.json();
    }
    
    static async updateInternalTask(taskId, taskData) {
        const response = await fetch(`/project-tasks/api/internal-tasks/${taskId}/`, {
            method: 'PUT',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': this.getCsrfToken()
            },
            body: JSON.stringify(taskData)
        });
        
        if (!response.ok) {
            throw new Error(`Failed to update internal task with ID ${taskId}`);
        }
        return await response.json();
    }
    
    static async updateExternalTask(taskId, taskData) {
        const response = await fetch(`/project-tasks/api/external-tasks/${taskId}/`, {
            method: 'PUT',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': this.getCsrfToken()
            },
            body: JSON.stringify(taskData)
        });
        
        if (!response.ok) {
            throw new Error(`Failed to update external task with ID ${taskId}`);
        }
        return await response.json();
    }
    
    static getCsrfToken() {
        const cookieValue = document.cookie
            .split('; ')
            .find(row => row.startsWith('csrftoken='))
            ?.split('=')[1];
        
        return cookieValue || '';
    }
}