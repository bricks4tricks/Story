// Plain JavaScript replacement for the previous React user table component.
// Fetches the user list and renders table rows dynamically.

(function() {
  const userTableBody = document.getElementById('user-table-body');
  if (!userTableBody) return;
  const filterInput = document.getElementById('user-filter');
  const filterColumnSelect = document.getElementById('user-filter-column');

  let allUsers = [];

  let usersVersion = null;
  let usersHash = null;

  async function fetchAndRenderUsers() {
    userTableBody.innerHTML = '<tr><td colspan="7" class="text-center py-4 text-gray-400">Loading...</td></tr>';
    try {
      const response = await fetch('/api/admin/all-users');
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
      userTableBody.innerHTML = '<tr><td colspan="7" class="text-center py-4 text-red-400">Error loading users.</td></tr>';
    }
  }
  async function refreshIfChanged() {
    try {
      const verRes = await fetch('/api/admin/users-version');
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
    userTableBody.innerHTML = '';
    if (users.length === 0) {
      userTableBody.innerHTML = '<tr><td colspan="7" class="text-center py-4 text-gray-400">No users found.</td></tr>';
      return;
    }
    users.forEach(user => {
      const isUserAdmin = user.UserType === 'Admin';
      const row = document.createElement('tr');
      row.className = 'border-b border-slate-700 hover:bg-slate-700/50';
      row.innerHTML = `
        <td class="px-6 py-4">${user.ID}</td>
        <td class="px-6 py-4 font-medium">${user.Username}</td>
        <td class="px-6 py-4">${user.Email || 'N/A'}</td>
        <td class="px-6 py-4"><span class="px-2 py-1 text-xs font-semibold rounded-full ${isUserAdmin ? 'bg-red-500/20 text-red-300' : (user.UserType === 'Parent' ? 'bg-blue-500/20 text-blue-300' : 'bg-green-500/20 text-green-300')}">${user.UserType}</span></td>
        <td class="px-6 py-4">${user.ParentUsername || 'N/A'}</td>
        <td class="px-6 py-4">${new Date(user.CreatedOn).toLocaleDateString()}</td>
        <td class="px-6 py-4 text-center flex justify-center space-x-2">
          <button data-userid="${user.ID}" class="edit-user-btn bg-blue-800 text-white font-semibold py-1 px-3 text-sm rounded-full hover:bg-blue-700 ${isUserAdmin ? 'opacity-50 cursor-not-allowed' : ''}" ${isUserAdmin ? 'disabled' : ''}>Edit</button>
          <button data-userid="${user.ID}" data-username="${user.Username}" class="delete-user-btn bg-red-800 text-white font-semibold py-1 px-3 text-sm rounded-full hover:bg-red-700 ${isUserAdmin ? 'opacity-50 cursor-not-allowed' : ''}" ${isUserAdmin ? 'disabled' : ''}>Delete</button>
        </td>`;
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
        (u.ParentUsername || '').toLowerCase().includes(query)
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
