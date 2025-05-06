import React, { useState } from 'react';
import ChatBox from './components/chatBox';
import Result from './components/result';
import NeonButton from './components/general/NeonButton.jsx';
import StarryBackground from './components/general/StarryBackground.jsx';
import { GlobalProvider } from './states/GlobalState';
import './App.css';

function App() {
  const [resultKey, setResultKey] = useState(0);

  const resetResult = () => {
    setResultKey(prevKey => prevKey + 1);
    // Clear any stored IFC data from localStorage if you implement persistence
    localStorage.removeItem('ifcData');
    window.location.reload(); // Force a full reload to clear all states
  };

  return (
      <GlobalProvider>
        <StarryBackground />
        <div className="flex h-screen p-6 relative">
          <div className="h-full w-1/3 pr-4 bg-transparent relative backdrop-blur-sm rounded-lg overflow-hidden border border-white/10">
            <ChatBox />
          </div>
          <div className="h-full w-2/3 relative backdrop-blur-sm rounded-lg border border-white/10">
            <Result key={resultKey} />

            {/* Reset Button */}
            <div className="absolute top-4 right-4 z-10">
              <NeonButton onClick={resetResult} color='pink'>
                Reset
              </NeonButton>
            </div>
          </div>
        </div>
      </GlobalProvider>
  );
}

export default App;