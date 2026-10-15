import { useState, useEffect } from "react";
import { useAuth } from "../AuthContext";
import Daily from "./daily";

export default function Answered(){

    const   {userId, logout} = useAuth();
    const   [answers, setAnswers] = useState([]);
    const   [message, setMessage] = useState('');
    const   [page, setPage] = useState('');

    useEffect(() => {
        const   getData = async () => {
            const   response = await fetch('http://127.0.0.1:5000/answers', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json'},
                body: JSON.stringify({user_id: userId}),
            });

            const   data = await response.json();
            setAnswers(data.answers || []);
            setMessage(data.error);
        };
        getData();
    }, [userId]);

    if (page === "Daily")
    {
        return <Daily/>
    }

    return(
        <div className="daily-cont">
            <h1>Your answers</h1>

            {answers.map((item, i) => (
                <div key={i} className="answer-card">
                    <p className="answer-question">{item.question}</p>
                    <p className="answer-text">{item.answer}</p>
                </div>
            ))}

            {message && <p className="feedback-message">{message}</p>}


            <button type="button" onClick={() => setPage('Daily')} className="setpage-button">
                Back to Daily Question
            </button>

            <button type="button" onClick={logout} className="logout-button">
                Log out
            </button>
        </div>
    );
}