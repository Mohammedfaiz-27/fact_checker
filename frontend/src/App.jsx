import React, { useState } from 'react';
import FactCheckerInput from './components/FactCheckerInput';
import FactCheckerResult from './components/FactCheckerResult';
import './App.css';

function App() {
  const [result, setResult] = useState(null);
  return (
    <div className="container">
      <header className="app-header">
        <h1 className="app-title">Fact Checker</h1>
        {/* <p className="app-subtitle">Verify claims with AI-powered research</p> */}
      </header>
      <FactCheckerInput onResult={setResult} />
      <FactCheckerResult result={result} />
    </div>
  );
}

export default App;
