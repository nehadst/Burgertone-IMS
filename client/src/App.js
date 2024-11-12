// client/src/App.js
import React, { useEffect, useState } from 'react';
import logo from './logo.svg';
import './App.css';

function App() {
  const [alerts, setAlerts] = useState([]);
  const [wsConnected, setWsConnected] = useState(false);

  useEffect(() => {
    const ws = new WebSocket('ws://localhost:3000');
    
    ws.onopen = () => {
      console.log('WebSocket Connected');
      setWsConnected(true);
    };

    ws.onmessage = (event) => {
      console.log('Received message:', event.data);
      try {
        const data = JSON.parse(event.data);
        if (data.type === 'LOW_STOCK_ALERT') {
          console.log('Setting alerts:', data.items);
          setAlerts(data.items);
        }
      } catch (error) {
        console.error('Parse error:', error);
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

  const testAlert = () => {
    if (alerts.length > 0) {
      setAlerts([]); // Clear alerts
    } else {
      setAlerts([{
        id: 999,
        NAME: 'Test Alert',
        QUANTITY: 5,
        UNIT: 'test'
      }]);
    }
  };

  return (
    <div className="App">
      {alerts.length > 0 && (
        <div style={{
          position: 'fixed',
          top: 0,
          left: 0,
          right: 0,
          backgroundColor: 'red',
          color: 'white',
          padding: '20px',
          zIndex: 9999
        }}>
          <h3>Low Stock Alert!</h3>
          {alerts.map(item => (
            <div key={item.id}>{item.NAME}: {item.QUANTITY} {item.UNIT}</div>
          ))}
        </div>
      )}
      
      <header className="App-header">
        <img src={logo} className="App-logo" alt="logo" />
        <p>Inventory Management System</p>
        <button onClick={testAlert} style={{
          padding: '10px 20px',
          fontSize: '16px',
          margin: '20px',
          cursor: 'pointer'
        }}>
          {alerts.length > 0 ? 'Clear Alert' : 'Test Alert'}
        </button>
      </header>
    </div>
  );
}

export default App;