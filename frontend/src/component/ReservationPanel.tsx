import React, { useState, useEffect } from 'react';
import './ReservationPanel.css';

interface DateRange {
  startDate: string;
  endDate: string;
}

interface ValidationErrors {
  startDate?: string;
  endDate?: string;
  duration?: string;
}

interface ReservationPanelProps {
  selectedSpot: string | null;
  dateRange: DateRange;
  onDateRangeChange: (dateRange: DateRange) => void;
  needsElectric: boolean;
  onNeedsElectricChange: (needs: boolean) => void;
  onReserve: () => void;
  loading: boolean;
  currentUserRole: string;
}

const countWorkingDays = (start: Date, end: Date): number => {
  let count = 0;
  const current = new Date(start);
  current.setHours(0, 0, 0, 0);
  const endNorm = new Date(end);
  endNorm.setHours(0, 0, 0, 0);
  while (current <= endNorm) {
    const day = current.getDay();
    if (day !== 0 && day !== 6) count++;
    current.setDate(current.getDate() + 1);
  }
  return count;
};

const ReservationPanel: React.FC<ReservationPanelProps> = ({
  selectedSpot,
  dateRange,
  onDateRangeChange,
  needsElectric,
  onNeedsElectricChange,
  onReserve,
  loading,
  currentUserRole
}) => {
  const [errors, setErrors] = useState<ValidationErrors>({});
  const [isSingleDay, setIsSingleDay] = useState<boolean>(true);

  const validateDates = (): boolean => {
    const errors: ValidationErrors = {};
    const start = new Date(dateRange.startDate);
    const end = new Date(dateRange.endDate);
    const today = new Date();
    today.setHours(0, 0, 0, 0);

    // Vérifier que les dates sont valides
    if (isNaN(start.getTime())) {
      errors.startDate = 'Date de début invalide';
    }
    if (isNaN(end.getTime())) {
      errors.endDate = 'Date de fin invalide';
    }

    // Vérifier que la date de début n'est pas dans le passé
    if (!errors.startDate && start < today) {
      errors.startDate = 'La date de début ne peut pas être dans le passé';
    }

    // Vérifier que la date de fin est après la date de début
    if (!errors.endDate && !errors.startDate && end < start) {
      errors.endDate = 'La date de fin doit être après la date de début';
    }

    // Vérifier la durée maximale (5 jours ouvrables pour employés, 30 jours calendaires pour managers)
    const isManager = currentUserRole === 'MANAGER';

    if (!errors.startDate && !errors.endDate) {
      if (isManager) {
        const calendarDays = Math.ceil(Math.abs(end.getTime() - start.getTime()) / (1000 * 60 * 60 * 24)) + 1;
        if (calendarDays > 30) {
          errors.duration = `La durée maximale est de 30 jours calendaires`;
        }
      } else {
        const workingDays = countWorkingDays(start, end);
        if (workingDays > 5) {
          errors.duration = `La durée maximale est de 5 jours ouvrables (lun.–ven.)`;
        }
      }
    }

    setErrors(errors);
    return Object.keys(errors).length === 0;
  };

  useEffect(() => {
    validateDates();
  }, [dateRange]);

  const handleStartDateChange = (e: React.ChangeEvent<HTMLInputElement>): void => {
    const newStartDate = e.target.value;
    onDateRangeChange({
      ...dateRange,
      startDate: newStartDate,
      endDate: isSingleDay ? newStartDate : Math.max(new Date(dateRange.endDate).getTime(), new Date(newStartDate).getTime()) === new Date(newStartDate).getTime() ? newStartDate : dateRange.endDate
    });
  };

  const handleEndDateChange = (e: React.ChangeEvent<HTMLInputElement>): void => {
    onDateRangeChange({
      ...dateRange,
      endDate: e.target.value
    });
  };

  const handleSubmit = (e: React.FormEvent<HTMLFormElement>): void => {
    e.preventDefault();
    if (validateDates()) {
      onReserve();
    }
  };

  const getTodayDate = (): string => {
    return new Date().toISOString().split('T')[0];
  };

  return (
    <div className="reservation-panel">
      <h3>Nouvelle Réservation</h3>

      <form onSubmit={handleSubmit}>
        <div className="form-group checkbox-group" style={{ marginBottom: "0.5rem", padding: "0.5rem" }}>
          <label>
            <input
              type="checkbox"
              checked={isSingleDay}
              onChange={(e) => {
                setIsSingleDay(e.target.checked);
                if (e.target.checked) {
                  onDateRangeChange({ ...dateRange, endDate: dateRange.startDate });
                }
              }}
            />
            <span>Réserver pour un seul jour</span>
          </label>
        </div>

        <div className="form-group">
          <label htmlFor="start-date">{isSingleDay ? "Date" : "Date de début"}</label>
          <input
            type="date"
            id="start-date"
            value={dateRange.startDate}
            onChange={handleStartDateChange}
            min={getTodayDate()}
            required
          />
          {errors.startDate && <span className="error">{errors.startDate}</span>}
        </div>

        {!isSingleDay && (
          <div className="form-group">
            <label htmlFor="end-date">Date de fin</label>
            <input
              type="date"
              id="end-date"
              value={dateRange.endDate}
              onChange={handleEndDateChange}
              min={dateRange.startDate}
              required
            />
            {errors.endDate && <span className="error">{errors.endDate}</span>}
          </div>
        )}

        {errors.duration && (
          <div className="alert alert-warning">
            {errors.duration}
          </div>
        )}

        <div className="form-group checkbox-group">
          <label>
            <input
              type="checkbox"
              checked={needsElectric}
              onChange={(e) => onNeedsElectricChange(e.target.checked)}
            />
            <span>J'ai besoin d'une borne électrique</span>
          </label>
          <p className="help-text">
            Les places avec bornes électriques sont situées dans les rangées A et F
          </p>
        </div>

        <div className="selected-spot-info">
          {selectedSpot ? (
            <>
              <div className="spot-badge">
                Place sélectionnée: <strong>{selectedSpot}</strong>
              </div>
            </>
          ) : (
            <div className="no-selection">
              Veuillez sélectionner une place sur le plan
            </div>
          )}
        </div>

        <button
          type="submit"
          className="btn-primary btn-reserve"
          disabled={!selectedSpot || loading || Object.keys(errors).length > 0}
        >
          {loading ? 'Réservation en cours...' : 'Réserver'}
        </button>
      </form>
    </div>
  );
};

export default ReservationPanel;
