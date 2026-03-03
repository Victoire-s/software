import React, { useState, useEffect } from 'react';
import ParkingMap from './ParkingMap';
import ReservationPanel from './ReservationPanel';
import UserReservations from './UserReservations';
import ManagerDashboard from './ManagerDashboard';
import AdminPanel from './AdminPanel';
import './ParkingReservationPage.css';
import { parkingApi, ParkingSpot, User } from '../services/api';

interface Reservation {
  spotId: string;
  date: string;
  userId: string;
  checkedIn: boolean;
}

interface UserReservation {
  id: number;
  spotId: string;
  startDate: string;
  endDate: string;
  checkedIn: boolean;
}

interface DateRange {
  startDate: string;
  endDate: string;
}

interface ParkingReservationPageProps {
  onLogout: () => void;
}

const ParkingReservationPage: React.FC<ParkingReservationPageProps> = ({ onLogout }) => {
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
  const [availableSpots, setAvailableSpots] = useState<ParkingSpot[]>([]);

  // Component mount: Just rely on loadData since we are authenticated
  useEffect(() => {
    loadData();
  }, [dateRange.startDate, dateRange.endDate, needsElectric]);

  // Removed redundant useEffect to prevent double fetching

  const loadData = async () => {
    try {
      setLoading(true);
      // 1. Get available spots
      const spots: ParkingSpot[] = await parkingApi.getAvailableSpots(needsElectric);
      setAvailableSpots(spots);

      // 2. Refresh user profile (to get current reservation)
      const me = await parkingApi.getMe();
      setCurrentUser(me);

      // Refresh user reservations
      const myReservations = await parkingApi.getMyReservations();
      const mappedMyRes = myReservations.map((r: any) => ({
        id: r.id,
        spotId: r.spot_id,
        startDate: r.start_date.split('T')[0],
        endDate: r.end_date.split('T')[0],
        checkedIn: r.checked_in
      }));
      setUserReservations(mappedMyRes);

      // (We could also fetch ALL reservations to show on map, but for now we only show User reservations and what "spots" are free)
      setReservations(mappedMyRes.map((r: any) => ({
        spotId: r.spotId,
        date: r.startDate,
        userId: String(me.id),
        checkedIn: r.checkedIn
      })));

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
      // Check for overlap on frontend (optional since backend will do it, but good practice to prevent spam)
      const isReserved = userReservations.some(r =>
        (r.startDate <= dateRange.endDate && r.endDate >= dateRange.startDate)
      );

      if (isReserved) {
        alert("Vous avez déjà une réservation qui chevauche ces dates.");
        return;
      }

      await parkingApi.reserveSpot(selectedSpot, dateRange.startDate, dateRange.endDate);

      alert(`Réservation confirmée pour la place ${selectedSpot}`);
      setSelectedSpot(null);
      await loadData();
    } catch (error: any) {
      alert(error.response?.data?.error || 'Erreur lors de la réservation');
      console.error(error);
    } finally {
      setLoading(false);
    }
  };

  const handleCancelReservation = async (reservationId: number): Promise<void> => {
    try {
      setLoading(true);
      await parkingApi.cancelReservation(reservationId);
      alert('Réservation annulée avec succès.');
      await loadData();
    } catch (error: any) {
      alert(error.response?.data?.error || 'Erreur lors de l\'annulation de la réservation');
      console.error(error);
    } finally {
      setLoading(false);
    }
  };

  const handleCheckIn = async (reservationId: number): Promise<void> => {
    try {
      await parkingApi.checkinReservation(reservationId);
      alert('Check-in réussi !');
      await loadData();
    } catch (error: any) {
      alert(error.response?.data?.error || 'Erreur lors du check-in');
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
          <button className="btn-logout" onClick={() => {
            parkingApi.logout();
            onLogout();
          }}>Déconnexion</button>
        </div>
      </header>

      <div className="page-content">
        <div className="main-section">
          <ParkingMap
            selectedSpot={selectedSpot}
            onSpotSelect={handleSpotSelect}
            reservations={reservations}
            availableSpots={availableSpots}
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
            currentUserRole={currentUser?.roles?.includes('MANAGER') ? 'MANAGER' : 'EMPLOYEE'}
          />

          <UserReservations
            reservations={userReservations}
            onCancel={handleCancelReservation}
            onCheckIn={handleCheckIn}
          />
        </aside>
      </div>

      {/* Admin / Manager views pushed below the main grid */}
      <div className="admin-views">
        {currentUser?.roles?.includes('MANAGER') && (
          <ManagerDashboard />
        )}

        {currentUser?.roles?.includes('SECRETAIRE') && (
          <AdminPanel />
        )}
      </div>
    </div>
  );
};

export default ParkingReservationPage;
