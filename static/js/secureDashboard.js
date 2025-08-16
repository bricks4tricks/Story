/**
 * Secure Dashboard Utilities
 * Demonstrates safe DOM manipulation for dashboard components
 */

class SecureDashboard {
    static displayError(container, message) {
        SecureDOM.setErrorState(container, SecureDOM.sanitizeHTML(message));
    }

    static displayLoading(container, message = 'Loading...') {
        SecureDOM.setLoadingState(container, message);
    }

    static displayCurriculums(container, curriculums) {
        if (!Array.isArray(curriculums) || curriculums.length === 0) {
            SecureDOM.setEmptyState(container, 'No curriculums available');
            return;
        }

        const curriculumElements = curriculums.map(curriculum => {
            return SecureDOM.createElement('div', {
                className: 'curriculum-item p-4 border rounded',
                'data-curriculum-id': curriculum.id
            }, SecureDOM.sanitizeHTML(curriculum.name));
        });

        SecureDOM.replaceContent(container, ...curriculumElements);
    }

    static displayTopics(container, topics) {
        if (!Array.isArray(topics) || topics.length === 0) {
            SecureDOM.setEmptyState(container, 'No topics found');
            return;
        }

        const topicsList = SecureDOM.createElement('div', {
            className: 'topics-grid grid gap-4'
        });

        topics.forEach(topic => {
            const topicCard = SecureDOM.createElement('div', {
                className: 'topic-card bg-slate-800 p-4 rounded-lg border border-slate-700',
                'data-topic-id': topic.id
            });

            const topicTitle = SecureDOM.createElement('h3', {
                className: 'text-lg font-semibold text-white mb-2'
            }, SecureDOM.sanitizeHTML(topic.name));

            const topicDescription = SecureDOM.createElement('p', {
                className: 'text-gray-400 text-sm'
            }, SecureDOM.sanitizeHTML(topic.description || 'No description available'));

            const viewButton = SecureDOM.createElement('button', {
                className: 'mt-3 bg-yellow-400 text-slate-900 px-4 py-2 rounded hover:bg-yellow-300 transition',
                'data-action': 'view-topic',
                'data-topic-id': topic.id
            }, 'View Topic');

            SecureDOM.appendContent(topicCard, topicTitle, topicDescription, viewButton);
            SecureDOM.appendContent(topicsList, topicCard);
        });

        SecureDOM.replaceContent(container, topicsList);
    }

    static displayUsers(container, users) {
        if (!Array.isArray(users) || users.length === 0) {
            SecureDOM.setEmptyState(container, 'No users found');
            return;
        }

        const tableElement = SecureDOM.createElement('table', {
            className: 'w-full table-auto border-collapse'
        });

        const headerRow = SecureDOM.createElement('tr', {
            className: 'bg-slate-700'
        });

        ['Username', 'Email', 'Type', 'Actions'].forEach(header => {
            const th = SecureDOM.createElement('th', {
                className: 'border border-slate-600 px-4 py-2 text-left'
            }, header);
            SecureDOM.appendContent(headerRow, th);
        });

        const tbody = SecureDOM.createElement('tbody');
        SecureDOM.appendContent(tbody, headerRow);

        users.forEach(user => {
            const row = SecureDOM.createElement('tr', {
                className: 'hover:bg-slate-800',
                'data-user-id': user.id
            });

            const usernameCell = SecureDOM.createElement('td', {
                className: 'border border-slate-600 px-4 py-2'
            }, SecureDOM.sanitizeHTML(user.username));

            const emailCell = SecureDOM.createElement('td', {
                className: 'border border-slate-600 px-4 py-2'
            }, SecureDOM.sanitizeHTML(user.email));

            const typeCell = SecureDOM.createElement('td', {
                className: 'border border-slate-600 px-4 py-2'
            }, SecureDOM.sanitizeHTML(user.usertype));

            const actionsCell = SecureDOM.createElement('td', {
                className: 'border border-slate-600 px-4 py-2'
            });

            const editButton = SecureDOM.createElement('button', {
                className: 'bg-blue-500 text-white px-3 py-1 rounded text-sm mr-2 hover:bg-blue-600',
                'data-action': 'edit-user',
                'data-user-id': user.id
            }, 'Edit');

            const deleteButton = SecureDOM.createElement('button', {
                className: 'bg-red-500 text-white px-3 py-1 rounded text-sm hover:bg-red-600',
                'data-action': 'delete-user',
                'data-user-id': user.id
            }, 'Delete');

            SecureDOM.appendContent(actionsCell, editButton, deleteButton);
            SecureDOM.appendContent(row, usernameCell, emailCell, typeCell, actionsCell);
            SecureDOM.appendContent(tbody, row);
        });

        SecureDOM.appendContent(tableElement, tbody);
        SecureDOM.replaceContent(container, tableElement);
    }

    static showMessage(container, message, type = 'info') {
        const messageClasses = {
            info: 'text-blue-400',
            success: 'text-green-400',
            warning: 'text-yellow-400',
            error: 'text-red-400'
        };

        const messageElement = SecureDOM.createElement('div', {
            className: `message ${messageClasses[type] || messageClasses.info} text-center p-4`
        }, SecureDOM.sanitizeHTML(message));

        SecureDOM.replaceContent(container, messageElement);

        // Auto-hide success/info messages after 5 seconds
        if (type === 'success' || type === 'info') {
            SecureDOM.safeTimeout(() => {
                if (container.contains(messageElement)) {
                    container.removeChild(messageElement);
                }
            }, 5000);
        }
    }
}

// Make available globally
window.SecureDashboard = SecureDashboard;