// Plain JavaScript replacement for the previous React user table component.
// Fetches the user list and renders table rows dynamically.

(function() {
  const userTableBody = document.getElementById('user-table-body');
  if (!userTableBody) return;

  let usersHash = null;

  async function fetchAndRenderUsers() {
    userTableBody.innerHTML = '<tr><td colspan="7" class="text-center py-4 text-gray-400">Loading...</td></tr>';
    try {
      const response = await fetch('/api/admin/all-users');
      if (!response.ok) throw new Error('Failed to fetch users');
      const users = await response.json();
      const newHash = JSON.stringify(users);
      if (newHash === usersHash) return; // no change
      usersHash = newHash;
      renderUsers(Array.isArray(users) ? users : []);
    } catch (err) {
      console.error('Fetch users error:', err);
      userTableBody.innerHTML = '<tr><td colspan="7" class="text-center py-4 text-red-400">Error loading users.</td></tr>';
    }
  }

  function renderUsers(users) {
    userTableBody.innerHTML = '';
    if (users.length === 0) {
      userTableBody.innerHTML = '<tr><td colspan="7" class="text-center py-4 text-gray-400">No users found.</td></tr>';
      return;
    }
    window.allUsersData = users;
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

  // Expose refresh function to global scope for other scripts.
  window.refreshUsers = fetchAndRenderUsers;

  // Initial fetch when script loads.
  fetchAndRenderUsers();
})();
