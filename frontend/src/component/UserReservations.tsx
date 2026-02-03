import React from 'react';
import './UserReservations.css';

interface UserReservation {
  id: string;
  spotId: string;
  startDate: string;
  endDate: string;
  checkedIn: boolean;
}

interface UserReservationsProps {
  reservations: UserReservation[];
  onCancel: (reservationId: string) => void;
}

const UserReservations: React.FC<UserReservationsProps> = ({ reservations, onCancel }) => {
  const formatDate = (dateString: string): string => {
    const date = new Date(dateString);
    return date.toLocaleDateString('fr-FR', {
      day: '2-digit',
      month: '2-digit',
      year: 'numeric'
    });
  };

  const isToday = (dateString: string): boolean => {
    const date = new Date(dateString);
    const today = new Date();
    return date.toDateString() === today.toDateString();
  };

  const isPast = (dateString: string): boolean => {
    const date = new Date(dateString);
    const today = new Date();
    today.setHours(0, 0, 0, 0);
    return date < today;
  };

  const canCheckIn = (reservation: UserReservation): boolean => {
    return isToday(reservation.startDate) && !reservation.checkedIn;
  };

  const handleCheckIn = (reservationId: string): void => {
    // TODO: Implémenter le check-in via API
    // window.location.href = `/checkin/${reservationId}`;
    alert('Fonctionnalité de check-in à venir (via QR code)');
  };

  if (!reservations || reservations.length === 0) {
    return (
      <div className="user-reservations">
        <h3>Mes Réservations</h3>
        <div className="no-reservations">
          <p>Vous n'avez aucune réservation en cours</p>
        </div>
      </div>
    );
  }

  return (
    <div className="user-reservations">
      <h3>Mes Réservations</h3>
      
      <div className="reservations-list">
        {reservations.map((reservation) => (
          <div 
            key={reservation.id} 
            className={`reservation-card ${isPast(reservation.endDate) ? 'past' : ''}`}
          >
            <div className="reservation-header">
              <span className="spot-badge-large">{reservation.spotId}</span>
              {reservation.checkedIn && (
                <span className="badge badge-success">✓ Check-in effectué</span>
              )}
              {canCheckIn(reservation) && (
                <span className="badge badge-warning">⚠ Check-in requis</span>
              )}
            </div>

            <div className="reservation-dates">
              <div className="date-info">
                <span className="date-label">Du:</span>
                <span className="date-value">{formatDate(reservation.startDate)}</span>
              </div>
              <div className="date-info">
                <span className="date-label">Au:</span>
                <span className="date-value">{formatDate(reservation.endDate)}</span>
              </div>
            </div>

            {isToday(reservation.startDate) && (
              <div className="today-notice">
                <strong>Aujourd'hui</strong> - N'oubliez pas de faire votre check-in avant 11h
              </div>
            )}

            <div className="reservation-actions">
              {canCheckIn(reservation) && (
                <button 
                  className="btn-secondary btn-checkin"
                  onClick={() => handleCheckIn(reservation.id)}
                >
                  Check-in
                </button>
              )}
              
              {!isPast(reservation.endDate) && (
                <button 
                  className="btn-danger btn-cancel"
                  onClick={() => onCancel(reservation.id)}
                >
                  Annuler
                </button>
              )}
            </div>
          </div>
        ))}
      </div>

      <div className="reservation-info">
        <p className="info-text">
          ⚠️ <strong>Important:</strong> Effectuez votre check-in avant 11h le jour de votre réservation, 
          sinon votre place sera libérée automatiquement.
        </p>
      </div>
    </div>
  );
};

export default UserReservations;
