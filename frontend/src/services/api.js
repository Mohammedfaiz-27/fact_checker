export async function checkClaim(claimText) {
  const res = await fetch('/api/claims/', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ claim_text: claimText }),
  });
  if (!res.ok) {
    throw new Error(`API error: ${res.status}`);
  }
  return res.json();
}

export async function checkMultimodalClaim(claimText, file) {
  const formData = new FormData();

  if (claimText) {
    formData.append('claim_text', claimText);
  }

  if (file) {
    formData.append('file', file);
  }

  const res = await fetch('/api/claims/multimodal', {
    method: 'POST',
    body: formData,
    // Don't set Content-Type header - browser will set it with boundary for multipart/form-data
  });

  if (!res.ok) {
    throw new Error(`API error: ${res.status}`);
  }

  return res.json();
}
