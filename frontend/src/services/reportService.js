import api from './api';

export const reportService = {
    // Get all reports for the current user's interviews
    async getReports() {
        try {
            const response = await api.get('/reports');
            return response.data;
        } catch (error) {
            throw error;
        }
    },

    // Get a specific interview report
    async getReport(sessionId) {
        try {
            const response = await api.get(`/public/session/${sessionId}/report`);
            return response.data;
        } catch (error) {
            throw error;
        }
    },

    // Get all sessions for an interview config
    async getInterviewSessions(configId) {
        try {
            const response = await api.get(`/interviews/configs/${configId}/sessions`);
            return response.data;
        } catch (error) {
            throw error;
        }
    },

    // Get completed sessions with reports
    async getCompletedSessions() {
        try {
            const response = await api.get('/interviews/sessions/completed');
            return response.data;
        } catch (error) {
            throw error;
        }
    },

    // Generate/regenerate report for a session
    async generateReport(sessionId) {
        try {
            const response = await api.post(`/public/session/${sessionId}/report`);
            return response.data;
        } catch (error) {
            throw error;
        }
    },

    // Helper: Format score as percentage
    formatScore(score) {
        if (score === null || score === undefined) return 'N/A';
        return `${Math.round(score)}%`;
    },

    // Helper: Get rating color class
    getRatingColor(rating) {
        const colors = {
            'Excellent': 'text-green-600 bg-green-100',
            'Good': 'text-blue-600 bg-blue-100',
            'Satisfactory': 'text-yellow-600 bg-yellow-100',
            'Needs Improvement': 'text-orange-600 bg-orange-100',
            'Poor': 'text-red-600 bg-red-100'
        };
        return colors[rating] || 'text-gray-600 bg-gray-100';
    },

    // Helper: Get score color class
    getScoreColor(score) {
        if (score >= 80) return 'text-green-600';
        if (score >= 60) return 'text-blue-600';
        if (score >= 40) return 'text-yellow-600';
        return 'text-red-600';
    },

    // Helper: Format duration
    formatDuration(minutes) {
        if (!minutes) return 'N/A';
        if (minutes < 60) return `${minutes} min`;
        const hours = Math.floor(minutes / 60);
        const mins = minutes % 60;
        return `${hours}h ${mins}m`;
    }
};
