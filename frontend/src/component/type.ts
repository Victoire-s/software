// Types partagés pour l'application de réservation de parking

export interface Reservation {
  spotId: string;
  date: string;
  userId: string;
  checkedIn: boolean;
}

export interface UserReservation {
  id: string;
  spotId: string;
  startDate: string;
  endDate: string;
  checkedIn: boolean;
}

export interface DateRange {
  startDate: string;
  endDate: string;
}

export interface ParkingSpot {
  id: string;
  row: string;
  number: number;
  hasElectric: boolean;
  isAvailable: boolean;
}

export interface User {
  id: string;
  name: string;
  email: string;
  role: 'employee' | 'manager' | 'secretary';
}

export interface ValidationErrors {
  startDate?: string;
  endDate?: string;
  duration?: string;
  [key: string]: string | undefined;
}

export type SpotStatus = 'available' | 'reserved' | 'selected' | 'unavailable';