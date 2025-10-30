export default function FactCheckerResult({ result }) {
  if (!result) return null;

  // Handle both old and new response formats
  const status = result.status || result.verdict || 'Unknown';
  const claim = result.claim_text || '';
  const explanation = result.explanation || result.response_text || '';
  const sources = result.sources || [];
  const findings = result.findings || [];
  const cached = result.cached || false;
  const cacheNote = result.cache_note || '';

  return (
    <div className="result">
      <h2>Fact-Check Result</h2>

      <div className="result-section">
        <strong>Claim:</strong>
        <p>{claim}</p>
      </div>

      <div className="result-section">
        <strong>Status:</strong>
        <p className="status">{status}</p>
      </div>

      {explanation && (
        <div className="result-section">
          <strong>Explanation:</strong>
          <p>{explanation}</p>
        </div>
      )}

      {findings && findings.length > 0 && (
        <div className="result-section">
          <strong>Key Findings:</strong>
          <ul>
            {findings.map((finding, index) => (
              <li key={index}>{finding}</li>
            ))}
          </ul>
        </div>
      )}

      {sources && sources.length > 0 && (
        <div className="result-section">
          <strong>Sources:</strong>
          <ul>
            {sources.map((source, index) => (
              <li key={index}>{source}</li>
            ))}
          </ul>
        </div>
      )}

      {cached && cacheNote && (
        <div className="result-section cache-note">
          <small>{cacheNote}</small>
        </div>
      )}
    </div>
  );
}

