import React, { useState } from 'react';
import './App.css'
import ParkingReservationPage from './component/ParkingReservationPage';
import LoginPage from './component/LoginPage';

function App() {
  const [isAuthenticated, setIsAuthenticated] = useState<boolean>(false);

  return (
    <div className="App">
      {!isAuthenticated ? (
        <LoginPage onLoginSuccess={() => setIsAuthenticated(true)} />
      ) : (
        <ParkingReservationPage onLogout={() => setIsAuthenticated(false)} />
      )}
    </div>
  )
}

export default App
