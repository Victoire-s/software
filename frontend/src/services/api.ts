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

    reserveSpot: async (spotId: string) => {
        // User creates reservation by associating the spot to themselves
        const response = await api.patch('/users/me', { spot_associe: spotId });
        return response.data;
    },

    cancelReservation: async () => {
        // User cancels by setting spot_associe to null
        const response = await api.patch('/users/me', { spot_associe: null });
        return response.data;
    }
};
