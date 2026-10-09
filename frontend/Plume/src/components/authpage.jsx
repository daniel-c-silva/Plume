import { useState } from "react";
import Register from "./register";
import plumeLogo from "../assets/plume-app-icon.svg";
import { useAuth } from "../AuthContext";


export default function Authpage() 
{
    const   [username, setUserName] = useState('');
    const   [password, setPassword] = useState('');
    const   [message, setMessage] = useState('');
    const   [page, setPage] = useState('login');
    const   { login } = useAuth();

    if  (page === 'register')
    {
        return <Register/>;
    }

    const   handleSubmit = async (currentVal) => {
        currentVal.preventDefault();

        try
        {
            const   response = await fetch('http://127.0.0.1:5000/login', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({username, password}),
            });

            const   data = await response.json();

            if (data.User)
                login(data.User);
            else
                setMessage(data.error || 'Login failed');
        }
        catch
        {
            setMessage('Could not reach the server');
        }
    }

    return (
        <div className="login-cont">
            <img
                src={plumeLogo}
                alt="Plume"
                className="plume-logo"
            />

            <h1>Welcome Back</h1>
            <p>Sign in to your account to continue</p>
            <form onSubmit={handleSubmit} className="login-form">

                <div className="form-group">
                    <label htmlFor="username">Username</label>
                    <input 
                    id="username"
                    type="text"
                    placeholder="Enter your username: ex... berpinhe"
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
                    placeholder="Enter your password"
                    value={password}
                    onChange={(currentVal) => setPassword(currentVal.target.value)}
                    required
                    />
                </div>

                <button type="submit" className="submit-button">Submit</button>

            </form>
            {message && <p className="feedback-message">{message}</p>}

            <hr />

            <p>Don't Have an account?</p>
            <button onClick={() => setPage('register')}>
                Register
            </button>
        </div>
    );
}