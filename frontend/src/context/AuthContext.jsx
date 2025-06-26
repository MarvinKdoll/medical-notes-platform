// FILE: src/context/AuthContext.jsx

import { createContext, useContext, useState, useEffect } from 'react';

// Create the authentication context
const AuthContext = createContext();

// Custom hook to use auth context
export const useAuth = () => {
    const context = useContext(AuthContext);
    if (!context) {
        throw new Error('useAuth must be used within an AuthProvider');
    }
    return context;
};

// AuthProvider component - manages all authentication state
export const AuthProvider = ({ children }) => {

    // STATE: Current user information
    const [user, setUser] = useState(null);

    // STATE: JWT token for API calls
    const [token, setToken] = useState(localStorage.getItem('token'));

    // STATE: Loading spinner while checking existing session
    const [loading, setLoading] = useState(true);

    // INITIALIZATION: Check if user was already logged in
    useEffect(() => {
        const savedToken = localStorage.getItem('token');
        const savedUser = localStorage.getItem('user');

        if (savedToken && savedUser) {
            setToken(savedToken);
            setUser(JSON.parse(savedUser));
        }

        setLoading(false);
    }, []);

    // LOGIN FUNCTION: Authenticate user with email/password
    const login = async (email, password) => {
        try {
            // TODO: Replace with actual API call to your Lambda function
            // For now, we'll use mock authentication

            // Simulate API delay
            await new Promise(resolve => setTimeout(resolve, 1000));

            // Mock authentication - accepts any email/password for demo
            const mockUser = {
                id: "user_123",
                email: email,
                full_name: email.includes('@') ? email.split('@')[0] : 'User'
            };
            const mockToken = `mock-token-${Date.now()}`;

            // Update state
            setToken(mockToken);
            setUser(mockUser);

            // Persist to localStorage
            localStorage.setItem('token', mockToken);
            localStorage.setItem('user', JSON.stringify(mockUser));

            return { success: true };

        } catch (error) {
            console.error('Login error:', error);
            return {
                success: false,
                error: 'Login failed. Please try again.'
            };
        }
    };

    // SIGNUP FUNCTION: Create new user account
    const signup = async (email, password, fullName) => {
        try {
            // TODO: Replace with actual API call

            // Simulate API delay
            await new Promise(resolve => setTimeout(resolve, 1000));

            // Mock signup - always succeeds for demo
            const mockUser = {
                id: `user_${Date.now()}`,
                email: email,
                full_name: fullName
            };
            const mockToken = `mock-token-${Date.now()}`;

            // Update state
            setToken(mockToken);
            setUser(mockUser);

            // Persist to localStorage
            localStorage.setItem('token', mockToken);
            localStorage.setItem('user', JSON.stringify(mockUser));

            return { success: true };

        } catch (error) {
            return {
                success: false,
                error: 'Signup failed. Please try again.'
            };
        }
    };

    // LOGOUT FUNCTION: Clear all user data
    const logout = () => {
        setUser(null);
        setToken(null);
        localStorage.removeItem('token');
        localStorage.removeItem('user');
    };

    // CONTEXT VALUE: All auth data and functions
    const value = {
        user,                           // Current user object
        token,                          // JWT token
        login,                          // Login function
        signup,                         // Signup function
        logout,                         // Logout function
        isAuthenticated: !!token,       // Boolean: is user logged in?
        loading                         // Boolean: still checking auth state?
    };

    return (
        <AuthContext.Provider value={value}>
            {children}
        </AuthContext.Provider>
    );
};