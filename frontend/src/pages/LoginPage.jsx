import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { Mail, Lock, Loader2 } from 'lucide-react';

const LoginPage = () => {

    // FORM STATE - track what user types in the form
    const [email, setEmail] = useState('');
    const [password, setPassword] = useState('');

    // UI STATE - track loading/ errors
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState('');

    // HOOKS
    const { login } = useAuth();

    const navigate = useNavigate();

    // FORM SUBMISSION HANDLER
    const handleSubmit = async (e) => {

        e.preventDefault();
        setError('');

        // start loading state (shows spinner, disables button)
        setLoading(true);


        const result = await login(email, password);


        if (result.success) {
            navigate('/dashboard');
        } else {
            setError(result.error);
        }
        setLoading(false);
    };

    // COMPONENT JSX -login form UI
    return (
        <div className="min-h-screen flex items-center justify-center py-12 px-4 sm:px-6 lg:px-8 bg-gray-50">

            {/* FORM CONTAINER */}
            <div className="max-w-md w-full space-y-8">

                {/* HEADER */}
                <div>
                    <h2 className="mt-6 text-center text-3xl font-bold text-gray-900">
                        Sign in to Medical Cleaned Notes
                    </h2>
                    <p className="mt-2 text-center text-sm text-gray-600">
                        Clean your medical documentation
                    </p>
                </div>

                {/* LOGIN FORM */}
                <form className="mt-8 space-y-6" onSubmit={handleSubmit}>

                    {/* INPUT FIELDS */}
                    <div className="space-y-4">

                        {/* EMAIL FIELD */}
                        <div>
                            <label htmlFor="email" className="block text-sm font-medium text-gray-700">
                                Email address
                            </label>
                            <div className="mt-1 relative">
                                {/* EMAIL ICON */}
                                <div className="absolute inset-y-0 left-0 pl-3 flex items-center">
                                    <Mail className="h-5 w-5 text-gray-400" />
                                </div>
                                {/* EMAIL INPUT */}
                                <input
                                    id="email"
                                    name="email"
                                    type="email"
                                    autoComplete="email"
                                    required
                                    value={email}
                                    onChange={(e) => setEmail(e.target.value)}
                                    className="input-field pl-10"
                                    placeholder="Enter your email"
                                />
                            </div>
                        </div>

                        {/* PASSWORD FIELD */}
                        <div>
                            <label htmlFor="password" className="block text-sm font-medium text-gray-700">
                                Password
                            </label>
                            <div className="mt-1 relative">
                                {/* PASSWORD ICON */}
                                <div className="absolute inset-y-0 left-0 pl-3 flex items-center">
                                    <Lock className="h-5 w-5 text-gray-400" />
                                </div>
                                {/* PASSWORD INPUT */}
                                <input
                                    id="password"
                                    name="password"
                                    type="password"
                                    autoComplete="current-password"
                                    required
                                    value={password}
                                    onChange={(e) => setPassword(e.target.value)}
                                    className="input-field pl-10"
                                    placeholder="Enter your password"
                                />
                            </div>
                        </div>
                    </div>

                    {/* ERROR MESSAGE */}
                    {/* Only shows if there's an error */}
                    {error && (
                        <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg">
                            {error}
                        </div>
                    )}

                    {/* TEST CREDENTIALS HELPER */}
                    <div className="bg-blue-50 border border-blue-200 text-blue-700 px-4 py-3 rounded-lg">
                        <p className="text-sm">
                            <strong>Test credentials:</strong><br />
                            Email: test@test.com<br />
                            Password: password
                        </p>
                    </div>

                    {/* SUBMIT BUTTON */}
                    <div>
                        <button
                            type="submit"
                            disabled={loading}
                            className="btn-primary w-full flex justify-center items-center"
                        >
                            {/* CONDITIONAL CONTENT - shows different text based on loading state */}
                            {loading ? (
                                <>
                                    <Loader2 className="animate-spin -ml-1 mr-3 h-5 w-5" />
                                    Signing in...
                                </>
                            ) : (
                                'Sign in'
                            )}
                        </button>
                    </div>
                </form>
            </div>
        </div>
    );
};

export default LoginPage;