import React, { useState, useEffect } from 'react';
import { api, parkingApi, Reservation } from '../services/api';
import './AdminPanel.css';

interface UserData {
    id: number;
    email: string;
    nom: string;
    prenom: string;
    roles: string[];
}

const AdminPanel: React.FC = () => {
    const [users, setUsers] = useState<UserData[]>([]);
    const [reservations, setReservations] = useState<Reservation[]>([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);

    // Form State
    const [showUserForm, setShowUserForm] = useState(false);
    const [editingUser, setEditingUser] = useState<UserData | null>(null);
    const [formData, setFormData] = useState({
        email: '',
        nom: '',
        prenom: '',
        roles: ['EMPLOYEE']
    });

    useEffect(() => {
        loadData();
    }, []);

    const loadData = async () => {
        try {
            setLoading(true);
            const [usersRes, reservationsRes] = await Promise.all([
                parkingApi.getUsers(),
                api.get('/reservations/')
            ]);
            setUsers(usersRes);
            setReservations(reservationsRes.data);
        } catch (err: any) {
            setError(err.response?.data?.error || "Erreur lors du chargement des données");
        } finally {
            setLoading(false);
        }
    };

    const cancelReservation = async (id: number) => {
        if (window.confirm('Voulez-vous vraiment annuler cette réservation ?')) {
            try {
                setLoading(true);
                await parkingApi.cancelReservation(id);
                alert('Réservation annulée avec succès');
                await loadData();
            } catch (err: any) {
                alert(err.response?.data?.error || "Erreur lors de l'annulation");
            } finally {
                setLoading(false);
            }
        }
    };

    const handleDeleteUser = async (id: number) => {
        if (window.confirm('Voulez-vous vraiment supprimer cet utilisateur ? Cette action est irréversible.')) {
            try {
                setLoading(true);
                await parkingApi.deleteUser(id);
                alert('Utilisateur supprimé.');
                await loadData();
            } catch (err: any) {
                alert(err.response?.data?.error || "Erreur lors de la suppression");
                setLoading(false);
            }
        }
    };

    const handleOpenForm = (user?: UserData) => {
        if (user) {
            setEditingUser(user);
            setFormData({
                email: user.email,
                nom: user.nom,
                prenom: user.prenom,
                roles: [...user.roles]
            });
        } else {
            setEditingUser(null);
            setFormData({ email: '', nom: '', prenom: '', roles: ['EMPLOYEE'] });
        }
        setShowUserForm(true);
    };

    const handleRoleChange = (role: string) => {
        setFormData(prev => ({
            ...prev,
            roles: prev.roles.includes(role) ? prev.roles.filter(r => r !== role) : [...prev.roles, role]
        }));
    };

    const handleFormSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        try {
            setLoading(true);
            if (editingUser) {
                // Update User Info
                await parkingApi.updateUser(editingUser.id, {
                    email: formData.email,
                    nom: formData.nom,
                    prenom: formData.prenom
                });

                // Update Roles Separately if needed
                const currRoles = [...editingUser.roles].sort().join(',');
                const newRoles = [...formData.roles].sort().join(',');
                if (currRoles !== newRoles) {
                    await parkingApi.setUserRoles(editingUser.id, formData.roles);
                }
                alert('Utilisateur modifié avec succès.');
            } else {
                // Create New User
                await parkingApi.createUser(formData);
                alert('Utilisateur créé avec succès.');
            }
            setShowUserForm(false);
            await loadData();
        } catch (err: any) {
            alert(err.response?.data?.error || "Erreur de formulaire");
            setLoading(false);
        }
    };

    if (loading && users.length === 0) return <div>Chargement de l'administration...</div>;
    if (error) return <div className="alert alert-danger">{error}</div>;

    return (
        <div className="admin-panel">
            <div className="admin-header d-flex justify-content-between align-items-center mb-4">
                <h3>Administration Secrétaire</h3>
                <button className="btn btn-primary" onClick={() => handleOpenForm()}>
                    Ajouter un Utilisateur
                </button>
            </div>

            {showUserForm && (
                <div className="glass-panel admin-user-form mb-4 p-4">
                    <h4>{editingUser ? 'Modifier Utilisateur' : 'Nouvel Utilisateur'}</h4>
                    <form onSubmit={handleFormSubmit}>
                        <div className="row">
                            <div className="col-md-6 mb-3">
                                <label className="form-label">Prénom</label>
                                <input type="text" className="form-control" required value={formData.prenom} onChange={e => setFormData({ ...formData, prenom: e.target.value })} />
                            </div>
                            <div className="col-md-6 mb-3">
                                <label className="form-label">Nom</label>
                                <input type="text" className="form-control" required value={formData.nom} onChange={e => setFormData({ ...formData, nom: e.target.value })} />
                            </div>
                        </div>
                        <div className="mb-3">
                            <label className="form-label">Email</label>
                            <input type="email" className="form-control" required value={formData.email} onChange={e => setFormData({ ...formData, email: e.target.value })} />
                        </div>
                        <div className="mb-3">
                            <label className="form-label">Rôles</label>
                            <div className="roles-checkboxes">
                                {['EMPLOYEE', 'MANAGER', 'SECRETAIRE'].map(role => (
                                    <div className="form-check form-check-inline" key={role}>
                                        <input className="form-check-input" type="checkbox" id={`role-${role}`} checked={formData.roles.includes(role)} onChange={() => handleRoleChange(role)} />
                                        <label className="form-check-label" htmlFor={`role-${role}`}>{role}</label>
                                    </div>
                                ))}
                            </div>
                        </div>
                        <div className="d-flex gap-2">
                            <button type="submit" className="btn btn-success" disabled={loading}>
                                {loading ? 'Enregistrement...' : 'Enregistrer'}
                            </button>
                            <button type="button" className="btn btn-secondary" onClick={() => setShowUserForm(false)} disabled={loading}>
                                Annuler
                            </button>
                        </div>
                    </form>
                </div>
            )}

            <div className="admin-section">
                <h4>Utilisateurs ({users.length})</h4>
                <div className="table-responsive">
                    <table className="admin-table">
                        <thead>
                            <tr>
                                <th>ID</th>
                                <th>Nom</th>
                                <th>Email</th>
                                <th>Rôles</th>
                                <th>Actions</th>
                            </tr>
                        </thead>
                        <tbody>
                            {users.map(u => (
                                <tr key={u.id}>
                                    <td>{u.id}</td>
                                    <td>{u.prenom} {u.nom}</td>
                                    <td>{u.email}</td>
                                    <td>
                                        <div className="role-badges">
                                            {u.roles.map(r => <span key={r} className="badge badge-info me-1">{r}</span>)}
                                        </div>
                                    </td>
                                    <td>
                                        <button className="btn-sm btn-primary me-2" onClick={() => handleOpenForm(u)}>Éditer</button>
                                        <button className="btn-sm btn-danger" onClick={() => handleDeleteUser(u.id)}>Suppr.</button>
                                    </td>
                                </tr>
                            ))}
                        </tbody>
                    </table>
                </div>
            </div>

            <div className="admin-section">
                <h4>Toutes les réservations ({reservations.length})</h4>
                <div className="table-responsive">
                    <table className="admin-table">
                        <thead>
                            <tr>
                                <th>ID</th>
                                <th>Place</th>
                                <th>User ID</th>
                                <th>Dates</th>
                                <th>Check-in</th>
                                <th>Action</th>
                            </tr>
                        </thead>
                        <tbody>
                            {reservations.map(r => (
                                <tr key={r.id}>
                                    <td>{r.id}</td>
                                    <td><span className="spot-badge">{r.spot_id}</span></td>
                                    <td>{r.user_id}</td>
                                    <td>{new Date(r.start_date).toLocaleDateString()} - {new Date(r.end_date).toLocaleDateString()}</td>
                                    <td>
                                        {r.checked_in ?
                                            <span className="badge badge-success">Oui</span> :
                                            <span className="badge badge-warning">Non</span>
                                        }
                                    </td>
                                    <td>
                                        <button className="btn-sm btn-danger" onClick={() => cancelReservation(r.id)} disabled={loading}>
                                            Annuler
                                        </button>
                                    </td>
                                </tr>
                            ))}
                        </tbody>
                    </table>
                </div>
            </div>
        </div>
    );
};

export default AdminPanel;
