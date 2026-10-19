import { useState, useEffect } from "react";
import { useAuth } from "../AuthContext";
import Daily from "./daily";

export default function Friends() {
  const { userId, logout } = useAuth();
  const [friendUsername, setFriendUsername] = useState('');
  const [pendingRequests, setPendingRequests] = useState([]);
  const [message, setMessage] = useState('');
  const [page, setPage] = useState('');

  useEffect(() => {
    fetch('http://127.0.0', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ user_id: userId })
    })
    .then(res => res.json())
    .then(data => {
      if (data.pending) setPendingRequests(data.pending);
    });
  }, [userId]);

  if (page === "Daily") return <Daily />;

  const handleSendRequest = async (e) => {
    e.preventDefault();
    const res = await fetch('http://127.0.0', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ user_id: userId, friend_username: friendUsername })
    });
    const data = await res.json();
    setMessage(data.message || data.error);
    setFriendUsername('');
  };

  const handleAccept = async (senderUsername) => {
    const res = await fetch('http://127.0.0', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ user_id: userId, sender_username: senderUsername })
    });
    const data = await res.json();
    setMessage(data.message || data.error);
    setPendingRequests(pendingRequests.filter(name => name !== senderUsername));
  };

  return (
    <div className="daily-cont">
      <h1>Manage Friends</h1>

      <form onSubmit={handleSendRequest} className="daily-form">
        <h3>Add a Friend</h3>
        <input 
          type="text" 
          placeholder="Friend's username..." 
          value={friendUsername} 
          onChange={(e) => setFriendUsername(e.target.value)} 
          required 
        />
        <button type="submit" className="submit-button">Send Request</button>
      </form>

      <hr className="daily-divider" />

      <div className="pending-section">
        <h3>Friend Requests</h3>
        {pendingRequests.length === 0 ? (
          <p>No pending requests.</p>
        ) : (
          pendingRequests.map((username) => (
            <div key={username} className="request-card" style={{ display: 'flex', justifyContent: 'space-between', margin: '10px 0' }}>
              <span>{username} wants to be friends</span>
              <button onClick={() => handleAccept(username)} className="submit-button" style={{ width: 'auto', padding: '5px 15px' }}>
                Accept
              </button>
            </div>
          ))
        )}
      </div>

      {message && <p className="feedback-message">{message}</p>}
      <hr className="daily-divider" />

      <button type="button" onClick={() => setPage('Daily')} className="setpage-button">Back to Daily</button>
      <button type="button" onClick={logout} className="logout-button">Log out</button>
    </div>
  );
}
