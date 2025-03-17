// client/src/App.js

import React, { useEffect, useState } from 'react';
import logo from './logo.svg';
import './App.css';

function App() {
  const [alerts, setAlerts] = useState([]);
  const [wsConnected, setWsConnected] = useState(false);

  useEffect(() => {
    const ws = new WebSocket('ws://localhost:3000'); // Ensure this matches your backend port

    ws.onopen = () => {
        console.log('Connected to WebSocket server');
    };
    
    ws.onmessage = (event) => {
        const data = JSON.parse(event.data);
        if (data.type === 'LOW_STOCK_ALERT') {
            console.log('Received low stock alert:', data.items);
        }
    };

    ws.onerror = (error) => {
      console.error('WebSocket error:', error);
      setWsConnected(false);
    };

    ws.onclose = () => {
      console.log('WebSocket disconnected');
      setWsConnected(false);
    };

    return () => {
      if (ws.readyState === WebSocket.OPEN) {
        ws.close();
      }
    };
  }, []);

  return (
    <div className="App">
      {!wsConnected && (
        <div
          style={{
            position: 'fixed',
            top: 0,
            left: 0,
            right: 0,
            backgroundColor: 'orange',
            color: 'white',
            padding: '10px',
            textAlign: 'center',
            zIndex: 9999,
          }}
        >
          Connecting to server...
        </div>
      )}

      {alerts.length > 0 && (
        <div
          style={{
            position: 'fixed',
            top: 0,
            left: 0,
            right: 0,
            backgroundColor: 'red',
            color: 'white',
            padding: '20px',
            zIndex: 9999,
          }}
        >
          <h3>Low Stock Alert!</h3>
          {alerts.map((item) => (
            <div key={item.id}>
              {item.NAME}: {item.QUANTITY} {item.UNIT}
            </div>
          ))}
        </div>
      )}

      <header className="App-header">
        <img src={logo} className="App-logo" alt="logo" />
        <p>Inventory Management System</p>
      </header>
    </div>
  );
}

export default App;