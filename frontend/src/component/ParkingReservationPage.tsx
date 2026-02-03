import React, { useState, useEffect } from 'react';
import ParkingMap from './ParkingMap';
import ReservationPanel from './ReservationPanel';
import UserReservations from './UserReservations';
import './ParkingReservationPage.css';
import { parkingApi, ParkingSpot, User } from '../services/api';

interface Reservation {
  spotId: string;
  date: string;
  userId: string;
  checkedIn: boolean;
}

interface UserReservation {
  id: string;
  spotId: string;
  startDate: string;
  endDate: string;
  checkedIn: boolean;
}

interface DateRange {
  startDate: string;
  endDate: string;
}

const ParkingReservationPage: React.FC = () => {
  const [selectedSpot, setSelectedSpot] = useState<string | null>(null);
  const [reservations, setReservations] = useState<Reservation[]>([]);
  const [userReservations, setUserReservations] = useState<UserReservation[]>([]);
  const [dateRange, setDateRange] = useState<DateRange>({
    startDate: new Date().toISOString().split('T')[0],
    endDate: new Date().toISOString().split('T')[0]
  });
  const [needsElectric, setNeedsElectric] = useState<boolean>(false);
  const [loading, setLoading] = useState<boolean>(false);
  const [currentUser, setCurrentUser] = useState<User | null>(null);

  // Auto-login test user on mount
  useEffect(() => {
    const initAuth = async () => {
      try {
        console.log("Attempting auto-login...");
        const user = await parkingApi.login("test@test.com");
        console.log("Logged in as:", user);
        setCurrentUser(user.user);
      } catch (e: any) {
        console.error("Auto-login failed", e);
        if (e.response && e.response.status === 401) {
          // Try register if login fails (first run)
          try {
            console.log("Login failed, trying register...");
            const reg = await parkingApi.register("test@test.com", "Test", "User");
            setCurrentUser(reg.user);
          } catch (regError) {
            console.error("Register failed", regError);
          }
        }
      }
    };
    initAuth();
  }, []);

  // Fetch spots when user or dependencies change
  useEffect(() => {
    if (currentUser) {
      loadData();
    }
  }, [dateRange, currentUser, needsElectric]);

  const loadData = async () => {
    try {
      setLoading(true);
      // 1. Get available spots
      const spots: ParkingSpot[] = await parkingApi.getAvailableSpots(needsElectric);
      console.log("Available spots:", spots);

      // 2. Refresh user profile (to get current reservation)
      const me = await parkingApi.getMe();
      setCurrentUser(me);

      
      if (me.spot_associe) {
        setUserReservations([{
          id: 'my-res',
          spotId: me.spot_associe,
          startDate: dateRange.startDate,
          endDate: dateRange.endDate,
          checkedIn: true
        }]);

        setReservations([{
          spotId: me.spot_associe,
          date: dateRange.startDate,
          userId: String(me.id),
          checkedIn: true
        }]);
      } else {
        setUserReservations([]);
        setReservations([]);
      }

    } catch (e) {
      console.error("Error loading data", e);
    } finally {
      setLoading(false);
    }
  };

  const handleSpotSelect = (spotId: string): void => {
    setSelectedSpot(spotId);
  };

  const handleReservation = async (): Promise<void> => {
    if (!selectedSpot) {
      alert('Veuillez sélectionner une place de parking');
      return;
    }

    setLoading(true);

    try {
      if (currentUser?.spot_associe) {
        alert("Vous avez déjà une réservation. Veuillez d'abord l'annuler.");
        return;
      }

      await parkingApi.reserveSpot(selectedSpot);

      alert(`Réservation confirmée pour la place ${selectedSpot}`);
      setSelectedSpot(null);
      await loadData();
    } catch (error) {
      alert('Erreur lors de la réservation');
      console.error(error);
    } finally {
      setLoading(false);
    }
  };

  const handleCancelReservation = async (reservationId: string): Promise<void> => {
    if (!window.confirm('Êtes-vous sûr de vouloir annuler cette réservation ?')) {
      return;
    }

    try {
      await parkingApi.cancelReservation();
      alert('Réservation annulée');
      await loadData();
    } catch (error) {
      alert('Erreur lors de l\'annulation');
      console.error(error);
    }
  };

  return (
    <div className="parking-reservation-page">
      <header className="page-header">
        <h1>Réservation de Parking</h1>
        <div className="user-info">
          {currentUser ? (
            <>
              <span className="user-name">{currentUser.email}</span>
              <span className="user-role">({(currentUser.roles || []).join(', ')})</span>
              {currentUser.spot_associe && <span className="user-spot">Spot: {currentUser.spot_associe}</span>}
            </>
          ) : (
            <span className="user-name">Chargement...</span>
          )}
          <button className="btn-logout" onClick={() => window.location.reload()}>Déconnexion</button>
        </div>
      </header>

      <div className="page-content">
        <div className="main-section">
          <ParkingMap
            selectedSpot={selectedSpot}
            onSpotSelect={handleSpotSelect}
            reservations={reservations}
            dateRange={dateRange}
            needsElectric={needsElectric}
          />
        </div>

        <aside className="sidebar">
          <ReservationPanel
            selectedSpot={selectedSpot}
            dateRange={dateRange}
            onDateRangeChange={setDateRange}
            needsElectric={needsElectric}
            onNeedsElectricChange={setNeedsElectric}
            onReserve={handleReservation}
            loading={loading}
          />

          <UserReservations
            reservations={userReservations}
            onCancel={handleCancelReservation}
          />
        </aside>
      </div>
    </div>
  );
};

export default ParkingReservationPage;
