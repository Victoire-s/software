import React, { JSX } from 'react';
import ParkingSpot from './ParkingSpot';
import './ParkingMap.css';

interface Reservation {
  spotId: string;
  date: string;
  userId: string;
  checkedIn: boolean;
}

interface DateRange {
  startDate: string;
  endDate: string;
}

interface ParkingMapProps {
  selectedSpot: string | null;
  onSpotSelect: (spotId: string) => void;
  reservations: Reservation[];
  dateRange: DateRange;
  needsElectric: boolean;
}

const ParkingMap: React.FC<ParkingMapProps> = ({ 
  selectedSpot, 
  onSpotSelect, 
  reservations, 
  dateRange, 
  needsElectric 
}) => {
  const rows: string[] = ['A', 'B', 'C', 'D', 'E', 'F'];
  const spotsPerRow: number = 10;
  
  const isElectricRow = (row: string): boolean => row === 'A' || row === 'F';
  
  const isSpotReserved = (spotId: string): boolean => {
    return reservations.some(r => 
      r.spotId === spotId && 
      r.date >= dateRange.startDate && 
      r.date <= dateRange.endDate
    );
  };

  const isSpotAvailable = (spotId: string, row: string): boolean => {
    // Si l'utilisateur a besoin d'électrique, seules les rangées A et F sont disponibles
    if (needsElectric && !isElectricRow(row)) {
      return false;
    }
    
    // Vérifier si la place n'est pas déjà réservée
    return !isSpotReserved(spotId);
  };

  const renderRow = (row: string): JSX.Element[] => {
    const spots: JSX.Element[] = [];
    for (let i = 1; i <= spotsPerRow; i++) {
      const spotNumber = i.toString().padStart(2, '0');
      const spotId = `${row}${spotNumber}`;
      const hasElectric = isElectricRow(row);
      const isReserved = isSpotReserved(spotId);
      const isAvailable = isSpotAvailable(spotId, row);
      
      spots.push(
        <ParkingSpot
          key={spotId}
          spotId={spotId}
          isSelected={selectedSpot === spotId}
          isReserved={isReserved}
          isAvailable={isAvailable}
          hasElectric={hasElectric}
          onSelect={() => isAvailable && onSpotSelect(spotId)}
        />
      );
    }
    return spots;
  };

  return (
    <div className="parking-map">
      <div className="map-header">
        <h2>Plan du Parking</h2>
        <div className="legend">
          <div className="legend-item">
            <span className="legend-icon available"></span>
            <span>Disponible</span>
          </div>
          <div className="legend-item">
            <span className="legend-icon reserved"></span>
            <span>Réservé</span>
          </div>
          <div className="legend-item">
            <span className="legend-icon selected"></span>
            <span>Sélectionné</span>
          </div>
          <div className="legend-item">
            <span className="legend-icon electric">⚡</span>
            <span>Borne électrique</span>
          </div>
        </div>
      </div>

      <div className="parking-grid">
        <div className="entry-marker">
          <svg width="40" height="40" viewBox="0 0 24 24" fill="none">
            <path d="M12 4L12 20M12 20L6 14M12 20L18 14" stroke="currentColor" strokeWidth="2" strokeLinecap="round"/>
          </svg>
          <span>ENTRÉE</span>
        </div>

        {rows.map((row, index) => (
          <div key={row} className="parking-row-container">
            <div className={`parking-row row-${row}`}>
              <div className="row-label">{row}</div>
              <div className="spots-container">
                {renderRow(row)}
              </div>
            </div>
            
            {/* Ajouter des espaces entre les paires de rangées */}
            {(index === 0 || index === 2 || index === 4) && (
              <div className="row-separator">
                <svg width="40" height="40" viewBox="0 0 24 24" fill="none">
                  <path d="M4 12L20 12M20 12L14 6M20 12L14 18" stroke="currentColor" strokeWidth="2" strokeLinecap="round"/>
                </svg>
              </div>
            )}
          </div>
        ))}

        <div className="exit-marker">
          <svg width="40" height="40" viewBox="0 0 24 24" fill="none">
            <path d="M12 20L12 4M12 4L6 10M12 4L18 10" stroke="currentColor" strokeWidth="2" strokeLinecap="round"/>
          </svg>
          <span>SORTIE</span>
        </div>
      </div>

      <div className="parking-info">
        <p>60 places au total | {isElectricRow('A') ? '20' : '0'} places avec borne électrique (rangées A et F)</p>
      </div>
    </div>
  );
};

export default ParkingMap;
