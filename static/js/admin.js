// Admin Dashboard JavaScript

// Load Statistics
async function loadStats() {
    try {
        const response = await fetch('/admin/api/stats');
        const data = await response.json();

        const statsGrid = document.getElementById('stats-grid');
        statsGrid.innerHTML = `
            <div class="stat-card">
                <div class="stat-label">Total Users</div>
                <div class="stat-value">${data.total_users.toLocaleString()}</div>
                <div class="stat-change">+${data.users_this_week} this week</div>
            </div>
            <div class="stat-card">
                <div class="stat-label">Total Generations</div>
                <div class="stat-value">${data.total_generations.toLocaleString()}</div>
                <div class="stat-change">+${data.generations_this_week} this week</div>
            </div>
            <div class="stat-card">
                <div class="stat-label">Total Images</div>
                <div class="stat-value">${data.total_images.toLocaleString()}</div>
                <div class="stat-change">${(data.total_images / data.total_generations).toFixed(1)} avg/gen</div>
            </div>
            <div class="stat-card">
                <div class="stat-label">Today's Activity</div>
                <div class="stat-value">${data.generations_today}</div>
                <div class="stat-change">${data.users_today} new users</div>
            </div>
        `;
    } catch (error) {
        console.error('Error loading stats:', error);
    }
}

// User Management
let allUsersData = [];

async function loadAllUsers() {
    try {
        const response = await fetch('/admin/api/users');
        allUsersData = await response.json();
        renderUsers(allUsersData);
    } catch (error) {
        console.error('Error loading users:', error);
    }
}

function renderUsers(users) {
    const tbody = document.querySelector('#users-table tbody');
    
    if (users.length === 0) {
        tbody.innerHTML = '<tr><td colspan="6" style="text-align: center; padding: 40px; color: #666;">No users found</td></tr>';
        return;
    }

    tbody.innerHTML = users.map(user => `
            <tr>
                <td><strong>${user.username}</strong></td>
                <td>${user.email}</td>
                <td>
                    ${user.is_admin 
                        ? '<span class="badge badge-warning">Admin</span>' 
                        : '<span class="badge badge-primary">User</span>'}
                </td>
                <td><span class="badge badge-primary">${user.generation_count}</span></td>
                <td>${new Date(user.created_at).toLocaleDateString()}</td>
                <td>
                    <div style="display: flex; gap: 8px;">
                        ${!user.is_admin 
                            ? `<button class="btn-action btn-promote" onclick="promoteUser(${user.id}, '${user.username}')">Make Admin</button>`
                            : `<button class="btn-action btn-demote" onclick="demoteUser(${user.id}, '${user.username}')">Remove Admin</button>`}
                        <button class="btn-action btn-delete" onclick="deleteUser(${user.id}, '${user.username}')">Delete</button>
                    </div>
                </td>
            </tr>
        `).join('');
}

function searchUsers(query) {
    const lowercaseQuery = query.toLowerCase().trim();
    
    if (!lowercaseQuery) {
        renderUsers(allUsersData);
        return;
    }
    
    const filtered = allUsersData.filter(user => 
        user.username.toLowerCase().includes(lowercaseQuery) ||
        user.email.toLowerCase().includes(lowercaseQuery)
    );
    
    renderUsers(filtered);
}

async function promoteUser(userId, username) {
    if (!confirm(`Make ${username} an admin?`)) return;

    try {
        const response = await fetch(`/admin/api/users/${userId}/promote`, {
            method: 'POST'
        });
        const data = await response.json();

        if (data.success) {
            alert(data.message);
            loadAllUsers();
        } else {
            alert(data.error || 'Failed to promote user');
        }
    } catch (error) {
        console.error('Error promoting user:', error);
        alert('An error occurred');
    }
}

async function demoteUser(userId, username) {
    if (!confirm(`Remove admin privileges from ${username}?`)) return;

    try {
        const response = await fetch(`/admin/api/users/${userId}/demote`, {
            method: 'POST'
        });
        const data = await response.json();

        if (data.success) {
            alert(data.message);
            loadAllUsers();
        } else {
            alert(data.error || 'Failed to demote user');
        }
    } catch (error) {
        console.error('Error demoting user:', error);
        alert('An error occurred');
    }
}

async function deleteUser(userId, username) {
    if (!confirm(`Are you sure you want to delete user "${username}"? This action cannot be undone and will delete all their generations.`)) return;

    try {
        const response = await fetch(`/admin/api/users/${userId}`, {
            method: 'DELETE'
        });
        const data = await response.json();

        if (data.success) {
            alert(data.message);
            loadAllUsers();
            loadStats();
        } else {
            alert(data.error || 'Failed to delete user');
        }
    } catch (error) {
        console.error('Error deleting user:', error);
        alert('An error occurred');
    }
}

// Recent Generations
async function loadRecentGenerations() {
    try {
        const response = await fetch('/admin/api/recent-generations');
        const generations = await response.json();

        const tbody = document.querySelector('#recent-generations-table tbody');
        tbody.innerHTML = generations.map(gen => `
            <tr>
                <td><strong>${gen.username}</strong></td>
                <td>${gen.title}</td>
                <td><span class="badge badge-success">${gen.style}</span></td>
                <td>${gen.image_count}</td>
                <td>${new Date(gen.created_at).toLocaleDateString()}</td>
            </tr>
        `).join('');
    } catch (error) {
        console.error('Error loading recent generations:', error);
    }
}

// Style Distribution
async function loadStyleDistribution() {
    try {
        const response = await fetch('/admin/api/style-distribution');
        const styles = await response.json();

        const maxCount = Math.max(...styles.map(s => s.count));
        const chartDiv = document.getElementById('style-chart');

        chartDiv.innerHTML = styles.map(style => `
            <div class="style-bar">
                <div class="style-name">${style.style}</div>
                <div class="style-bar-bg">
                    <div class="style-bar-fill" style="width: ${(style.count / maxCount) * 100}%">
                        <span class="style-count">${style.count}</span>
                    </div>
                </div>
            </div>
        `).join('');
    } catch (error) {
        console.error('Error loading style distribution:', error);
    }
}

// Top Users
async function loadTopUsers() {
    try {
        const response = await fetch('/admin/api/top-users');
        const users = await response.json();

        const topUsersDiv = document.getElementById('top-users');
        topUsersDiv.innerHTML = `
            <table class="table">
                <thead>
                    <tr>
                        <th>Username</th>
                        <th>Generations</th>
                        <th>Joined</th>
                    </tr>
                </thead>
                <tbody>
                    ${users.map((user, index) => `
                        <tr>
                            <td><strong>${user.username}</strong></td>
                            <td><span class="badge badge-warning">${user.generation_count}</span></td>
                            <td>${new Date(user.created_at).toLocaleDateString()}</td>
                        </tr>
                    `).join('')}
                </tbody>
            </table>
        `;
    } catch (error) {
        console.error('Error loading top users:', error);
    }
}

// Feedback Management
let allFeedbackData = [];

async function loadFeedback() {
    try {
        const response = await fetch('/admin/api/feedback');
        allFeedbackData = await response.json();

        filterAndRenderFeedback();
    } catch (error) {
        console.error('Error loading feedback:', error);
    }
}

function filterAndRenderFeedback() {
    const typeFilter = document.getElementById('feedback-type-filter').value;
    const tbody = document.querySelector('#feedback-table tbody');

    let filteredFeedback = allFeedbackData;
    if (typeFilter !== 'all') {
        filteredFeedback = allFeedbackData.filter(fb => fb.type === typeFilter);
    }

    if (filteredFeedback.length === 0) {
        tbody.innerHTML = '<tr><td colspan="6" class="loading">No feedback found</td></tr>';
        return;
    }

    tbody.innerHTML = filteredFeedback.map(fb => `
        <tr>
            <td>
                <span class="feedback-type-badge feedback-type-${fb.type}">
                    ${fb.type === 'bug' ? '🐛' : fb.type === 'feature' ? '💡' : fb.type === 'improvement' ? '⚡' : '💬'} ${fb.type}
                </span>
            </td>
            <td>
                <strong>${fb.user.username}</strong>
                ${fb.user.email ? `<br><small>${fb.user.email}</small>` : ''}
            </td>
            <td>
                ${fb.rating ? `<span class="feedback-rating">${'★'.repeat(fb.rating)}${'☆'.repeat(5 - fb.rating)}</span>` : '-'}
            </td>
            <td>
                <div class="feedback-message-cell" title="${fb.message}">
                    ${fb.message}
                </div>
            </td>
            <td>${new Date(fb.created_at).toLocaleDateString()}</td>
            <td>
                <div class="feedback-actions">
                    <button onclick="deleteFeedback(${fb.id})" class="btn-action btn-danger" title="Delete">🗑️</button>
                </div>
            </td>
        </tr>
    `).join('');
}

async function deleteFeedback(feedbackId) {
    if (!confirm('Are you sure you want to delete this feedback?')) {
        return;
    }

    try {
        const response = await fetch(`/admin/api/feedback/${feedbackId}`, {
            method: 'DELETE'
        });

        if (response.ok) {
            loadFeedback();
        } else {
            alert('Failed to delete feedback');
        }
    } catch (error) {
        console.error('Error deleting feedback:', error);
        alert('An error occurred');
    }
}

function exportFeedbackCSV() {
    const typeFilter = document.getElementById('feedback-type-filter').value;
    let feedbackToExport = allFeedbackData;

    if (typeFilter !== 'all') {
        feedbackToExport = allFeedbackData.filter(fb => fb.type === typeFilter);
    }

    if (feedbackToExport.length === 0) {
        alert('No feedback to export');
        return;
    }

    const headers = ['Type', 'Username', 'Email', 'Rating', 'Message', 'Date'];
    const rows = feedbackToExport.map(fb => [
        fb.type,
        fb.user.username,
        fb.user.email || '',
        fb.rating || '',
        `"${fb.message.replace(/"/g, '""')}"`,
        new Date(fb.created_at).toLocaleDateString()
    ]);

    const csvContent = [
        headers.join(','),
        ...rows.map(row => row.join(','))
    ].join('\n');

    const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
    const link = document.createElement('a');
    const url = URL.createObjectURL(blob);

    link.setAttribute('href', url);
    link.setAttribute('download', `feedback_${typeFilter}_${new Date().toISOString().split('T')[0]}.csv`);
    link.style.visibility = 'hidden';

    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
}

// Initialize on DOM load
document.addEventListener('DOMContentLoaded', () => {
    loadStats();
    loadAllUsers();
    loadRecentGenerations();
    loadStyleDistribution();
    loadTopUsers();
    loadFeedback();

    const searchInput = document.getElementById('user-search');
    searchInput.addEventListener('input', (e) => {
        searchUsers(e.target.value);
    });

    // Auto-refresh every 30 seconds
    setInterval(() => {
        loadStats();
        loadAllUsers();
        loadRecentGenerations();
        loadFeedback();
    }, 30000);
});
