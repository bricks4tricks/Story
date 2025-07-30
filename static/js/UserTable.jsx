const { useState, useEffect } = React;

function UsersTable() {
  const [users, setUsers] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const fetchUsers = async () => {
    setLoading(true);
    setError(null);
    try {
      const response = await fetch('/api/admin/all-users');
      if (!response.ok) throw new Error('Failed to fetch users');
      const data = await response.json();
      setUsers(Array.isArray(data) ? data : []);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    window.refreshUsers = fetchUsers;
    fetchUsers();
  }, []);

  window.setUsersData = (data) => setUsers(data);

  if (loading) {
    return (
      <tr><td colSpan="7" className="text-center py-4 text-gray-400">Loading...</td></tr>
    );
  }

  if (error) {
    return (
      <tr><td colSpan="7" className="text-center py-4 text-red-400">Error: {error}</td></tr>
    );
  }

  if (users.length === 0) {
    return (
      <tr><td colSpan="7" className="text-center py-4 text-gray-400">No users found.</td></tr>
    );
  }

  return (
    <>
      {users.map(user => {
        const isUserAdmin = user.UserType === 'Admin';
        return (
          <tr key={user.ID} className="border-b border-slate-700 hover:bg-slate-700/50">
            <td className="px-6 py-4">{user.ID}</td>
            <td className="px-6 py-4 font-medium">{user.Username}</td>
            <td className="px-6 py-4">{user.Email || 'N/A'}</td>
            <td className="px-6 py-4">
              <span className={`px-2 py-1 text-xs font-semibold rounded-full ${isUserAdmin ? 'bg-red-500/20 text-red-300' : (user.UserType === 'Parent' ? 'bg-blue-500/20 text-blue-300' : 'bg-green-500/20 text-green-300')}`}>{user.UserType}</span>
            </td>
            <td className="px-6 py-4">{user.ParentUsername || 'N/A'}</td>
            <td className="px-6 py-4">{new Date(user.CreatedOn).toLocaleDateString()}</td>
            <td className="px-6 py-4 text-center flex justify-center space-x-2">
              <button onClick={() => handleOpenEditModal(user.ID)} className={`edit-user-btn bg-blue-800 text-white font-semibold py-1 px-3 text-sm rounded-full hover:bg-blue-700 ${isUserAdmin ? 'opacity-50 cursor-not-allowed' : ''}`} disabled={isUserAdmin}>Edit</button>
              <button onClick={() => handleDeleteUser(user.ID, user.Username)} className={`delete-user-btn bg-red-800 text-white font-semibold py-1 px-3 text-sm rounded-full hover:bg-red-700 ${isUserAdmin ? 'opacity-50 cursor-not-allowed' : ''}`} disabled={isUserAdmin}>Delete</button>
            </td>
          </tr>
        );
      })}
    </>
  );
}

ReactDOM.createRoot(document.getElementById('user-table-body')).render(<UsersTable />);
