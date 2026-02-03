import React from 'react';
import './ParkingSpot.css';

interface ParkingSpotProps {
  spotId: string;
  isSelected: boolean;
  isReserved: boolean;
  isAvailable: boolean;
  hasElectric: boolean;
  onSelect: () => void;
}

const ParkingSpot: React.FC<ParkingSpotProps> = ({ 
  spotId, 
  isSelected, 
  isReserved, 
  isAvailable,
  hasElectric,
  onSelect 
}) => {
  const getSpotClassName = (): string => {
    const classes = ['parking-spot'];
    
    if (isSelected) classes.push('selected');
    else if (isReserved) classes.push('reserved');
    else if (!isAvailable) classes.push('unavailable');
    else classes.push('available');
    
    if (hasElectric) classes.push('has-electric');
    
    return classes.join(' ');
  };

  return (
    <div 
      className={getSpotClassName()}
      onClick={onSelect}
      title={`Place ${spotId}${hasElectric ? ' - Borne électrique' : ''}`}
    >
      <div className="spot-content">
        <span className="spot-id">{spotId}</span>
        {hasElectric && (
          <span className="electric-icon" aria-label="Borne électrique">⚡</span>
        )}
      </div>
    </div>
  );
};

export default ParkingSpot;
