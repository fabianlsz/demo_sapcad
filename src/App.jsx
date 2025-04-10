import React, { useState } from 'react';
import ChatBox from './components/ChatBox';
import Result from './components/result';
import NeonButton from './components/general/NeonButton.jsx';
import StarryBackground from './components/general/StarryBackground.jsx';
import IfcViewer from './components/result/IfcViewer.jsx'; // Import the IfcViewer component
import { GlobalProvider } from './states/GlobalState';
import './App.css';

function App() {
  const [ifcFile, setIfcFile] = useState(null);
  const [resultKey, setResultKey] = useState(0);

  const resetResult = () => {
    setResultKey(prevKey => prevKey + 1);
  };

  return (
    <GlobalProvider>
      <StarryBackground />
      <div className="flex h-screen p-6 relative">
        <div className="h-full w-1/3 pr-4 bg-transparent relative">
          <ChatBox />
        </div>
        <div className="h-full w-2/3 relative">
          <Result key={resultKey} />
          {/*nothing breaks here if we comment this out, tho we should solve it later*/}
          {/* Reset Button */}
          <div className="absolute top-4 right-4">
            <NeonButton onClick={resetResult} color='pink'>
              Reset
            </NeonButton>
          </div>

          {/* IfcViewer Component */}
          {ifcFile && <IfcViewer file={ifcFile} />}
        </div>
      </div>

    </GlobalProvider>
  );
}

export default App;