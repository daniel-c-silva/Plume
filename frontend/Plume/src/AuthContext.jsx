import { createContext, useContext, useState } from "react";

const AuthContext = createContext(null);

export function AuthProvider({ children })
{
    // read storage right away so there's no login-screen flash on launch
    const   [userId, setUserId] = useState(() => {
        try
        {
            const   saved = localStorage.getItem("userId");
            return saved ? Number(saved) : null;
        }
        catch
        {
            return null;
        }
    });

    function login(id)
    {
        setUserId(id);
        try { localStorage.setItem("userId", String(id)); } catch { /* storage unavailable, login lasts until the app closes */ }
    }

    function logout()
    {
        setUserId(null);
        try { localStorage.removeItem("userId"); } catch { /* nothing to clean up */ }
    }

    return (
        <AuthContext.Provider value={{ userId, login, logout }}>
            {children}
        </AuthContext.Provider>
    );
}

// eslint-disable-next-line react-refresh/only-export-components
export function useAuth()
{
    return useContext(AuthContext);
}