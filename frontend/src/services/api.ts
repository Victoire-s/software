import axios from 'axios';

const API_URL = '/api'; // Use proxy

export const api = axios.create({
    baseURL: API_URL,
    headers: {
        'Content-Type': 'application/json',
    },
});

// Types from Backend
export interface User {
    id: number;
    email: string;
    nom: string;
    prenom: string;
    roles: string[];
    spot_associe?: string | null;
}

export interface ParkingSpot {
    id: string; // "A01"
    electrical: boolean;
    is_free: boolean;
    reserved_from?: string; // ISO
    reserved_to?: string; // ISO
}

export interface Reservation {
    id: number;
    spot_id: string;
    user_id: number;
    start_date: string;
    end_date: string;
    checked_in: boolean;
    created_at: string;
}


// Store auth headers
let authHeaders: Record<string, string> = {};

export const setAuthHeaders = (headers: Record<string, string>) => {
    authHeaders = headers;
    api.defaults.headers.common = { ...api.defaults.headers.common, ...headers };
};

export const parkingApi = {
    // Auth
    login: async (email: string) => {
        const response = await api.post('/auth/login', { email });
        if (response.data.headers_to_use) {
            setAuthHeaders(response.data.headers_to_use);
        }
        return response.data;
    },

    logout: () => {
        setAuthHeaders({});
    },

    register: async (email: string, nom: string, prenom: string) => {
        const response = await api.post('/auth/register', { email, nom, prenom });
        if (response.data.headers_to_use) {
            setAuthHeaders(response.data.headers_to_use);
        }
        return response.data;
    },

    // Spots
    getAvailableSpots: async (electricalRequired: boolean = false) => {
        const response = await api.get(`/spots/available?electrical_required=${electricalRequired}`);
        return response.data;
    },

    // User Profile & Reservations
    getMe: async () => {
        const response = await api.get('/users/me');
        return response.data;
    },

    reserveSpot: async (spotId: string, startDate: string, endDate: string) => {
        const response = await api.post('/reservations/', {
            spot_id: spotId,
            start_date: startDate + "T00:00:00",
            end_date: endDate + "T23:59:59"
        });
        return response.data;
    },

    getMyReservations: async () => {
        const response = await api.get('/reservations/me');
        return response.data;
    },

    checkinReservation: async (reservationId: number) => {
        const response = await api.patch(`/reservations/${reservationId}/checkin`);
        return response.data;
    },

    cancelReservation: async (reservationId: number) => {
        const response = await api.delete(`/reservations/${reservationId}`);
        return response.data;
    },

    // --- Admin (Secretaries Only) ---
    getUsers: async () => {
        const response = await api.get('/users/');
        return response.data;
    },

    createUser: async (data: { email: string; nom: string; prenom: string; roles: string[]; spot_associe?: string | null }) => {
        const response = await api.post('/users/', data);
        return response.data;
    },

    updateUser: async (userId: number, data: { email?: string; nom?: string; prenom?: string; spot_associe?: string | null }) => {
        const response = await api.patch(`/users/${userId}`, data);
        return response.data;
    },

    deleteUser: async (userId: number) => {
        const response = await api.delete(`/users/${userId}`);
        return response.data;
    },

    setUserRoles: async (userId: number, roles: string[]) => {
        const response = await api.put(`/users/${userId}/roles`, { roles });
        return response.data;
    }
};
