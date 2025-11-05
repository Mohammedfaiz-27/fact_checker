import React, { useState } from 'react';
import FactCheckerInput from './components/FactCheckerInput';
import FactCheckerResult from './components/FactCheckerResult';
import LoadingAnimation from './components/LoadingAnimation';
import './App.css';

function App() {
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);

  return (
    <div className="container">
      <header className="app-header">
        <h1 className="app-title">Fact Checker</h1>
        {/* <p className="app-subtitle">Verify claims with AI-powered research</p> */}
      </header>
      <FactCheckerInput onResult={setResult} loading={loading} setLoading={setLoading} />
      {loading && <LoadingAnimation />}
      {!loading && <FactCheckerResult result={result} />}
    </div>
  );
}

export default App;
