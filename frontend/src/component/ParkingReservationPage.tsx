import React, { useState, useEffect } from 'react';
import ParkingMap from './Parkingmap';
import ReservationPanel from './Reservationpanel';
import UserReservations from './Userreservations';
import './ParkingReservationPage.css';

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

  // Simuler le chargement des réservations existantes
  useEffect(() => {
    fetchReservations();
    fetchUserReservations();
  }, [dateRange]);

  const fetchReservations = async () => {
    // TODO: Remplacer par l'appel API réel
    // const response = await fetch(`/api/reservations?startDate=${dateRange.startDate}&endDate=${dateRange.endDate}`);
    // const data = await response.json();
    // setReservations(data);
    
    // Données simulées pour le développement
    setReservations([
      { spotId: 'A01', date: new Date().toISOString().split('T')[0], userId: 'user123', checkedIn: true },
      { spotId: 'B05', date: new Date().toISOString().split('T')[0], userId: 'user456', checkedIn: false },
    ]);
  };

  const fetchUserReservations = async () => {
    // TODO: Remplacer par l'appel API réel
    // const response = await fetch('/api/user/reservations');
    // const data = await response.json();
    // setUserReservations(data);
    
    // Données simulées
    setUserReservations([
      {
        id: '1',
        spotId: 'A01',
        startDate: new Date().toISOString().split('T')[0],
        endDate: new Date().toISOString().split('T')[0],
        checkedIn: true
      }
    ]);
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
      // TODO: Remplacer par l'appel API réel
      // const response = await fetch('/api/reservations', {
      //   method: 'POST',
      //   headers: { 'Content-Type': 'application/json' },
      //   body: JSON.stringify({
      //     spotId: selectedSpot,
      //     startDate: dateRange.startDate,
      //     endDate: dateRange.endDate
      //   })
      // });
      
      // Simulation de la création de réservation
      await new Promise(resolve => setTimeout(resolve, 1000));
      
      alert(`Réservation confirmée pour la place ${selectedSpot}`);
      setSelectedSpot(null);
      fetchReservations();
      fetchUserReservations();
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
      // TODO: Appel API réel
      // await fetch(`/api/reservations/${reservationId}`, { method: 'DELETE' });
      
      await new Promise(resolve => setTimeout(resolve, 500));
      alert('Réservation annulée');
      fetchUserReservations();
      fetchReservations();
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
          <span className="user-name">Utilisateur</span>
          <button className="btn-logout">Déconnexion</button>
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
