import React, { useState } from 'react';
import { parkingApi } from '../services/api';
import './LoginPage.css';

interface LoginPageProps {
    onLoginSuccess: () => void;
}

const LoginPage: React.FC<LoginPageProps> = ({ onLoginSuccess }) => {
    const [email, setEmail] = useState('');
    const [isRegistering, setIsRegistering] = useState(false);
    const [nom, setNom] = useState('');
    const [prenom, setPrenom] = useState('');
    const [error, setError] = useState<string | null>(null);
    const [loading, setLoading] = useState(false);

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        setError(null);
        setLoading(true);

        try {
            if (isRegistering) {
                await parkingApi.register(email, nom, prenom);
            } else {
                await parkingApi.login(email);
            }
            onLoginSuccess();
        } catch (err: any) {
            console.error(err);
            setError(err.response?.data?.error || "Erreur de connexion");
            // If error is 401 on login, suggest registering
            if (!isRegistering && err.response?.status === 401) {
                setError("Utilisateur non trouvé. Veuillez vous inscrire.");
                setIsRegistering(true);
            }
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="login-container">
            <div className="login-card">
                <h2>{isRegistering ? 'Inscription' : 'Connexion'}</h2>
                <p className="subtitle">Application de réservation de parking</p>

                {error && <div className="alert alert-danger">{error}</div>}

                <form onSubmit={handleSubmit}>
                    <div className="form-group">
                        <label>Email</label>
                        <input
                            type="email"
                            value={email}
                            onChange={(e) => setEmail(e.target.value)}
                            placeholder="votre.email@entreprise.com"
                            required
                        />
                    </div>

                    {isRegistering && (
                        <>
                            <div className="form-group">
                                <label>Nom</label>
                                <input
                                    type="text"
                                    value={nom}
                                    onChange={(e) => setNom(e.target.value)}
                                    required
                                />
                            </div>
                            <div className="form-group">
                                <label>Prénom</label>
                                <input
                                    type="text"
                                    value={prenom}
                                    onChange={(e) => setPrenom(e.target.value)}
                                    required
                                />
                            </div>
                        </>
                    )}

                    <button type="submit" className="btn-primary w-100" disabled={loading}>
                        {loading ? 'Chargement...' : (isRegistering ? "S'inscrire" : "Se connecter")}
                    </button>
                </form>

                <div className="toggle-mode">
                    <button
                        type="button"
                        className="btn-link"
                        onClick={() => setIsRegistering(!isRegistering)}
                    >
                        {isRegistering ? 'Déjà un compte ? Se connecter' : "Pas de compte ? S'inscrire"}
                    </button>
                </div>
            </div>
        </div>
    );
};

export default LoginPage;
