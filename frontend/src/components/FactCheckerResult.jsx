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

  // Multimodal-specific fields
  const mediaType = result.media_type || null;
  const mediaFilename = result.media_filename || null;
  const extractedText = result.extracted_text || null;
  const researchSummary = result.research_summary || null;

  // URL-specific fields
  const url = result.url || null;
  const articleTitle = result.article_title || null;
  const articleSource = result.article_source || null;
  const articlePreview = result.article_preview || null;

  // Get media type emoji
  const getMediaEmoji = (type) => {
    if (type?.startsWith('image/')) return '📸';
    if (type?.startsWith('video/')) return '🎥';
    if (type?.startsWith('audio/')) return '🎤';
    return '📄';
  };

  // Helper function to render text with clickable URLs
  const renderTextWithLinks = (text) => {
    if (!text) return null;

    // Regular expression to match URLs
    const urlRegex = /(https?:\/\/[^\s]+)/g;
    const parts = text.split(urlRegex);

    return parts.map((part, index) => {
      if (part.match(urlRegex)) {
        return (
          <a
            key={index}
            href={part}
            target="_blank"
            rel="noopener noreferrer"
            style={{ color: '#4A90E2', textDecoration: 'underline' }}
          >
            {part}
          </a>
        );
      }
      return <span key={index}>{part}</span>;
    });
  };

  return (
    <div className="result">
      <h2>Fact-Check Result</h2>

      {url && (
        <div className="result-section url-info">
          <strong>🔗 Source URL:</strong>
          <p>
            <a href={url} target="_blank" rel="noopener noreferrer" style={{ color: '#4A90E2' }}>
              {url}
            </a>
          </p>
          {articleTitle && (
            <p style={{ marginTop: '0.5rem' }}>
              <strong>Article:</strong> {articleTitle}
            </p>
          )}
          {articleSource && (
            <p style={{ marginTop: '0.25rem', fontSize: '0.9em', color: '#666' }}>
              <strong>Publisher:</strong> {articleSource}
            </p>
          )}
        </div>
      )}

      {mediaType && mediaFilename && (
        <div className="result-section media-info">
          <strong>{getMediaEmoji(mediaType)} Media File:</strong>
          <p>{mediaFilename}</p>
        </div>
      )}

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
          <p>{renderTextWithLinks(explanation)}</p>
        </div>
      )}

      {/* {extractedText && (
        <div className="result-section extracted-text">
          <strong>Extracted Content:</strong>
          <p style={{ whiteSpace: 'pre-wrap', fontSize: '0.9em', color: '#666' }}>
            {extractedText}
          </p>
        </div>
      )} */}

      {researchSummary && (
        <div className="result-section">
          <strong>🔍 Research Summary:</strong>
          <p>{renderTextWithLinks(researchSummary)}</p>
        </div>
      )}

      {findings && findings.length > 0 && (
        <div className="result-section">
          <strong>Key Findings:</strong>
          <ul>
            {findings.map((finding, index) => (
              <li key={index}>{renderTextWithLinks(finding)}</li>
            ))}
          </ul>
        </div>
      )}

      {sources && sources.length > 0 && (
        <div className="result-section">
          <strong>Sources:</strong>
          <ul>
            {sources.map((source, index) => (
              <li key={index}>{renderTextWithLinks(source)}</li>
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

