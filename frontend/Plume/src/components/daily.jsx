import { useState } from "react";
import { useAuth } from "../AuthContext";
import plumeLogo from "../assets/plume-app-icon.svg";

export default function Daily() 
{
    const   {userId, logout} = useAuth();
    const   [answer, setAnswer] = useState('');
    const   [message, setMessage] = useState('');

    const   question = "what's your current favourite word?";

    const   handleSubmit = async (currentVal) => {
        currentVal.preventDefault();

        const   response = await fetch ('http://127.0.0.1:5000/daily', {
            method: 'POST',
            headers: {'Content-Type': 'application/json' },
            body: JSON.stringify({ user_id: userId ,answer: answer,question: question }),
        });

        const   data = await response.json();
        setMessage(data.message || data.error);
    };
    
return (
        <div className="daily-cont">
            <img
                src={plumeLogo}
                alt="Plume"
                className="plume-logo"
            />
            <h1>Today's question</h1>
            <p className="daily-question">{question}</p>

            <form onSubmit={handleSubmit} className="daily-form">
                <div className="form-group">
                    <textarea
                        placeholder="Your answer..."
                        value={answer}
                        onChange={(e) => setAnswer(e.target.value)}
                        required
                    />
                </div>
                <button type="submit" className="submit-button">Send</button>
            </form>

            {message && <p className="feedback-message">{message}</p>}

            <hr className="daily-divider" />

            <button type="button" onClick={logout} className="logout-button">
                Log out
            </button>
        </div>
    );
}