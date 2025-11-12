const API_BASE = '/api';

export const queryAPI = async (question) => {
  try {
    const response = await fetch(`${API_BASE}/query`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({ question })
    });

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));
      throw new Error(errorData.error || `API error: ${response.statusText}`);
    }

    const data = await response.json();
    return data;
  } catch (error) {
    throw new Error(error.message || 'Failed to query the knowledge base');
  }
};

export const checkHealth = async () => {
  try {
    const response = await fetch(`${API_BASE}/health`);
    return response.ok;
  } catch {
    return false;
  }
};

export const fetchDocument = async (filename, segment = '') => {
  try {
    const params = new URLSearchParams();
    if (segment) params.append('segment', segment);

    const response = await fetch(`${API_BASE}/document/${encodeURIComponent(filename)}?${params}`);

    if (!response.ok) {
      throw new Error(`Failed to fetch document: ${response.statusText}`);
    }

    const data = await response.json();
    return data;
  } catch (error) {
    throw new Error(error.message || 'Failed to fetch document');
  }
};
