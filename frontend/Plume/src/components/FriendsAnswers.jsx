import { useState, useEffect } from "react";
import { useAuth } from "../AuthContext";
import Daily from "./daily";

export default function FriendsAnswers() {
    const { userId, logout } = useAuth();
    const [feed, setFeed] = useState([]);
    const [message, setMessage] = useState('');
    const [page, setPage] = useState('');

    useEffect(() => {
        const fetchFeed = async () => {
            try {
                const response = await fetch('http://127.0.0.1:5000/friends-answers', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ user_id: userId }),
                });

                const data = await response.json();
                setFeed(data.feed || []);
                if (data.error) setMessage(data.error);
            } catch {
                setMessage('Could not load feed.');
            }
        };

        fetchFeed();
    }, [userId]);

    if (page === "Daily") {
        return <Daily />;
    }

    return (
        <div className="daily-cont">
            <h1>Friends Feed</h1>

            {feed.length === 0 ? (
                <p>No answers from friends yet!</p>
            ) : (
                feed.map((item, i) => (
                    <div key={i} className="answer-card" style={{ marginBottom: '15px', textAlign: 'left' }}>
                        <p className="answer-question" style={{ fontWeight: 'bold' }}>
                            {item.question}
                        </p>
                        <p className="answer-text">
                            <strong>{item.username}:</strong> {item.answer}
                        </p>
                    </div>
                ))
            )}

            {message && <p className="feedback-message">{message}</p>}

            <hr className="daily-divider" />

            <button type="button" onClick={() => setPage('Daily')} className="setpage-button">
                Back to Daily Question
            </button>

            <button type="button" onClick={logout} className="logout-button">
                Log out
            </button>
        </div>
    );
}