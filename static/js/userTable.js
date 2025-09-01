// Plain JavaScript replacement for the previous React user table component.
// Fetches the user list and renders table rows dynamically.

(function() {
  // Wait for SecureDOM to be available
  if (typeof SecureDOM === 'undefined') {
    console.error('SecureDOM is not available. Retrying in 100ms...');
    setTimeout(arguments.callee, 100);
    return;
  }
  
  const userTableBody = document.getElementById('user-table-body');
  if (!userTableBody) return;
  const filterInput = document.getElementById('user-filter');
  const filterColumnSelect = document.getElementById('user-filter-column');

  let allUsers = [];

  let usersVersion = null;
  let usersHash = null;

  async function fetchAndRenderUsers() {
    SecureDOM.setLoadingState(userTableBody, 'Loading...');
    try {
      // Get authentication token from localStorage
      const token = localStorage.getItem('token');
      const headers = token ? {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${token}`
      } : {
        'Content-Type': 'application/json'
      };
      
      const response = await fetch('/api/admin/all-users', {
        method: 'GET',
        headers: headers,
        credentials: 'same-origin'
      });
      if (!response.ok) throw new Error('Failed to fetch users');
      const users = await response.json();
      const newHash = JSON.stringify(users);
      if (newHash === usersHash) {
        // Data is unchanged; re-render existing rows so the table doesn't stay on loading state.
        renderUsers(allUsers);
        return;
      }
      usersHash = newHash;
      allUsers = Array.isArray(users) ? users : [];
      window.allUsersData = allUsers;
      applyFilter();
    } catch (err) {
      console.error('Fetch users error:', err);
      SecureDOM.setErrorState(userTableBody, 'Error loading users.');
    }
  }
  async function refreshIfChanged() {
    try {
      // Get authentication token from localStorage
      const token = localStorage.getItem('token');
      const headers = token ? {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${token}`
      } : {
        'Content-Type': 'application/json'
      };
      
      const verRes = await fetch('/api/admin/users-version', {
        method: 'GET',
        headers: headers,
        credentials: 'same-origin'
      });
      if (!verRes.ok) throw new Error("Failed to fetch version");
      const { version } = await verRes.json();
      if (version !== usersVersion) {
        usersVersion = version;
        await fetchAndRenderUsers();
      }
    } catch (err) {
      console.error("Version check error:", err);
    }
  }

  function renderUsers(users) {
    SecureDOM.replaceContent(userTableBody);
    if (users.length === 0) {
      SecureDOM.setEmptyState(userTableBody, 'No users found.');
      return;
    }
    users.forEach(user => {
      const isUserAdmin = user.UserType === 'Admin';
      const row = SecureDOM.createElement('tr', {
        className: 'border-b border-slate-700 hover:bg-slate-700/50'
      });

      const subText = user.SubscriptionDaysLeft !== null && user.SubscriptionDaysLeft !== undefined
        ? `${user.SubscriptionDaysLeft} days`
        : 'None';

      // Create cells with secure DOM manipulation
      const idCell = SecureDOM.createElement('td', { className: 'px-6 py-4' }, String(user.ID));
      const usernameCell = SecureDOM.createElement('td', { className: 'px-6 py-4 font-medium' }, user.Username);
      const emailCell = SecureDOM.createElement('td', { className: 'px-6 py-4' }, user.Email || 'N/A');
      
      // User type badge
      const userTypeCell = SecureDOM.createElement('td', { className: 'px-6 py-4' });
      const badge = SecureDOM.createElement('span', {
        className: `px-2 py-1 text-xs font-semibold rounded-full ${
          isUserAdmin ? 'bg-red-500/20 text-red-300' : 
          (user.UserType === 'Parent' ? 'bg-blue-500/20 text-blue-300' : 'bg-green-500/20 text-green-300')
        }`
      }, user.UserType);
      userTypeCell.appendChild(badge);

      const parentCell = SecureDOM.createElement('td', { className: 'px-6 py-4' }, user.ParentUsername || 'N/A');
      const dateCell = SecureDOM.createElement('td', { className: 'px-6 py-4' }, new Date(user.CreatedOn).toLocaleDateString());
      const subCell = SecureDOM.createElement('td', { className: 'px-6 py-4' }, subText);
      
      // Actions cell
      const actionsCell = SecureDOM.createElement('td', { className: 'px-6 py-4 text-center flex justify-center space-x-2' });
      
      // Edit button
      const editBtn = SecureDOM.createElement('button', {
        className: `edit-user-btn bg-blue-800 text-white font-semibold py-1 px-3 text-sm rounded-full hover:bg-blue-700 ${isUserAdmin ? 'opacity-50 cursor-not-allowed' : ''}`,
        'data-userid': user.ID
      }, 'Edit');
      if (isUserAdmin) editBtn.disabled = true;
      
      // Delete button
      const deleteBtn = SecureDOM.createElement('button', {
        className: `delete-user-btn bg-red-800 text-white font-semibold py-1 px-3 text-sm rounded-full hover:bg-red-700 ${isUserAdmin ? 'opacity-50 cursor-not-allowed' : ''}`,
        'data-userid': user.ID,
        'data-username': user.Username
      }, 'Delete');
      if (isUserAdmin) deleteBtn.disabled = true;
      
      actionsCell.appendChild(editBtn);
      actionsCell.appendChild(deleteBtn);
      
      // Renew button (if not admin)
      if (!isUserAdmin) {
        const renewBtn = SecureDOM.createElement('button', {
          className: 'renew-sub-btn bg-green-800 text-white font-semibold py-1 px-3 text-sm rounded-full hover:bg-green-700',
          'data-userid': user.ID
        }, 'Renew');
        actionsCell.appendChild(renewBtn);
      }

      // Append all cells to row
      SecureDOM.appendContent(row, idCell, usernameCell, emailCell, userTypeCell, parentCell, dateCell, subCell, actionsCell);
      userTableBody.appendChild(row);
    });
  }

  function applyFilter() {
    if (!filterInput) {
      renderUsers(allUsers);
      return;
    }
    const query = filterInput.value.trim().toLowerCase();
    if (!query) {
      renderUsers(allUsers);
      return;
    }

    const column = filterColumnSelect ? filterColumnSelect.value : 'all';
    let filtered;
    if (column === 'all') {
      filtered = allUsers.filter(u =>
        String(u.ID).toLowerCase().includes(query) ||
        u.Username.toLowerCase().includes(query) ||
        (u.Email || '').toLowerCase().includes(query) ||
        (u.UserType || '').toLowerCase().includes(query) ||
        (u.ParentUsername || '').toLowerCase().includes(query) ||
        String(u.SubscriptionDaysLeft ?? '').toLowerCase().includes(query)
      );
    } else {
      filtered = allUsers.filter(u => {
        const val = u[column] !== undefined && u[column] !== null ? String(u[column]).toLowerCase() : '';
        return val.includes(query);
      });
    }
    renderUsers(filtered);
  }

  // Expose refresh function to global scope for other scripts.
  window.refreshUsers = refreshIfChanged;
  window.forceRefreshUsers = fetchAndRenderUsers;

  if (filterInput) {
    filterInput.addEventListener('input', applyFilter);
  }
  if (filterColumnSelect) {
    filterColumnSelect.addEventListener('change', applyFilter);
  }

  // Initial fetch when script loads.
  refreshIfChanged();
})();
