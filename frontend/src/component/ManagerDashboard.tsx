import React, { useState, useEffect } from 'react';
import { api } from '../services/api';
import './ManagerDashboard.css';

interface DashboardStats {
    slots: number;
    slots_max: number;
    occupied: number;
    free: number;
    occupation_rate: number;
    electric_spots: number;
    electric_ratio: number;
    no_shows: number;
}

const ManagerDashboard: React.FC = () => {
    const [stats, setStats] = useState<DashboardStats | null>(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);

    useEffect(() => {
        loadStats();
    }, []);

    const loadStats = async () => {
        try {
            setLoading(true);
            const res = await api.get('/parking/view');
            setStats(res.data);
        } catch (err: any) {
            setError(err.response?.data?.error || "Erreur de chargement des statistiques");
        } finally {
            setLoading(false);
        }
    };

    if (loading) return <div className="p-4">Chargement des statistiques...</div>;
    if (error) return <div className="alert alert-danger">{error}</div>;
    if (!stats) return null;

    return (
        <div className="manager-dashboard">
            <h3>Tableau de bord Manager</h3>

            <div className="stats-grid">
                <div className="stat-card">
                    <div className="stat-value">{stats.occupation_rate.toFixed(1)}%</div>
                    <div className="stat-label">Taux d'occupation</div>
                    <div className="stat-subtext">{stats.occupied} / {stats.slots_max} places</div>
                </div>

                <div className="stat-card">
                    <div className="stat-value text-danger">{stats.no_shows || 0}</div>
                    <div className="stat-label">No-shows aujourd'hui</div>
                    <div className="stat-subtext">Réservé mais pas check-in (avant 11h)</div>
                </div>

                <div className="stat-card">
                    <div className="stat-value text-success">{stats.electric_ratio.toFixed(1)}%</div>
                    <div className="stat-label">Places électriques</div>
                    <div className="stat-subtext">{stats.electric_spots} bornes disponibles</div>
                </div>

                <div className="stat-card">
                    <div className="stat-value text-primary">{stats.free}</div>
                    <div className="stat-label">Places libres</div>
                    <div className="stat-subtext">Actuellement disponibles</div>
                </div>
            </div>
        </div>
    );
};

export default ManagerDashboard;
