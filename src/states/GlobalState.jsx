// GlobalState.js
import React, { createContext, useContext, useState, useEffect } from 'react';

const GlobalContext = createContext();

export const GlobalProvider = ({ children }) => {
  const [requestMsg, setRequestMsg] = useState('');
  const [responseMsg, setResponseMsg] = useState('');
  const [ifcData, setIfcData] = useState(null);
  const [isConnected, setIsConnected] = useState(false);
  const [socket, setSocket] = useState(null);

  // Initialize WebSocket connection
  useEffect(() => {
    const ws = new WebSocket(`ws://${window.location.hostname}:8000/ws`);

    ws.onopen = () => {
      console.log('WebSocket Connected');
      setIsConnected(true);
      setSocket(ws);
    };

    ws.onmessage = (event) => {
      const response = event.data;
      console.log('Received:', response);
      setResponseMsg(response);
    };

    ws.onclose = () => {
      console.log('WebSocket Disconnected');
      setIsConnected(false);
    };

    return () => {
      if (ws) {
        ws.close();
      }
    };
  }, []);

  // Send message to WebSocket when request changes
  useEffect(() => {
    if (socket && isConnected && requestMsg) {
      // Format message with IFC context if available
      const message = {
        message: requestMsg,
        context: ifcData ? {
          filename: ifcData.filename,
          projectName: ifcData.ProjectName,
          entities: ifcData.entities
        } : null
      };

      socket.send(JSON.stringify(message));
    }
  }, [requestMsg, socket, isConnected, ifcData]);

  return (
      <GlobalContext.Provider value={{
        requestMsg,
        setRequestMsg,
        responseMsg,
        setResponseMsg,
        ifcData,
        setIfcData,
        isConnected
      }}>
        {children}
      </GlobalContext.Provider>
  );
};

export const useGlobal = () => useContext(GlobalContext);