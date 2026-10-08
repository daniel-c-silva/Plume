import { useState } from "react";

export default function Register() {
    const   [username, setUserName] = useState('');
    const   [password, setPassword] = useState('');
    const   [message, setMessage] = useState('');

    const   handleSubmit = async (currentVal) => {
        currentVal.preventDefault();

        // * Send username and password to the backend for registration
        const   response = await fetch('http://127.0.0.1:5000/register', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ username, password }),
        });

        const   data = await response.json();
        setMessage(data.message || data.error);
    };

    return (
        <div className="register-cont">
            <h2>Register</h2>
            <form onSubmit={handleSubmit} className="register-form">
                <div className="form-group">
                    <label htmlFor="username">Username</label>
                    <input
                        id="username"
                        type="text"
                        placeholder="Enter Username: ex:*Dr-Dumanglh*"
                        value={username}
                        onChange={(currentVal) => setUserName(currentVal.target.value)}
                        required
                    />
                </div>

                <div className="form-group">
                    <label htmlFor="password">Password</label>
                    <input
                        id="password"
                        type="password"
                        placeholder="Enter password:"
                        value={password}
                        onChange={(currentVal) => setPassword(currentVal.target.value)}
                        required
                    />
                </div>

                <button type="submit" className="submit-button">Submit</button>
            </form>
            {message && <p className="feedback-message">{message}</p>}
        </div>
    );
}


