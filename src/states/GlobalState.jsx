// GlobalState.js
import React, { createContext, useContext, useState } from 'react';

const GlobalContext = createContext();

export const GlobalProvider = ({ children }) => {
  const [requestMsg, setRequestMsg] = useState(''); 

  return (
    <GlobalContext.Provider value={{ requestMsg, setRequestMsg }}>
      {children}
    </GlobalContext.Provider>
  );
};

export const useGlobal = () => useContext(GlobalContext);