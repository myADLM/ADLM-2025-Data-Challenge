const API_BASE = '/api';

export const queryKG = async (query, limit = 30) => {
  try {
    const response = await fetch(`${API_BASE}/kg_query`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({ query, limit })
    });

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));
      throw new Error(errorData.error || `API error: ${response.statusText}`);
    }

    const data = await response.json();
    return data;
  } catch (error) {
    throw new Error(error.message || 'Failed to query the knowledge graph');
  }
};

export const chatKG = async (message, sessionId = null, limit = 30) => {
  try {
    const response = await fetch(`${API_BASE}/kg_chat`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({ message, session_id: sessionId, limit })
    });

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));
      throw new Error(errorData.error || `API error: ${response.statusText}`);
    }

    const data = await response.json();
    return data;
  } catch (error) {
    throw new Error(error.message || 'Failed to send chat message');
  }
};

export const clearChatSession = async (sessionId) => {
  try {
    const response = await fetch(`${API_BASE}/kg_chat/${sessionId}`, {
      method: 'DELETE'
    });

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));
      throw new Error(errorData.error || `API error: ${response.statusText}`);
    }

    return await response.json();
  } catch (error) {
    throw new Error(error.message || 'Failed to clear chat session');
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

export const getQuerySuggestions = async () => {
  try {
    const response = await fetch(`${API_BASE}/kg_suggestions`);

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));
      throw new Error(errorData.error || `API error: ${response.statusText}`);
    }

    const data = await response.json();
    return data;
  } catch (error) {
    throw new Error(error.message || 'Failed to fetch query suggestions');
  }
};

export const getDocuments = async (filters = {}) => {
  try {
    const params = new URLSearchParams();
    if (filters.doc_type) params.append('doc_type', filters.doc_type);
    if (filters.section) params.append('section', filters.section);
    if (filters.search) params.append('search', filters.search);

    const response = await fetch(`${API_BASE}/documents?${params}`);

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));
      throw new Error(errorData.error || `API error: ${response.statusText}`);
    }

    const data = await response.json();
    return data;
  } catch (error) {
    throw new Error(error.message || 'Failed to fetch documents');
  }
};

export const getNodeGraph = async (nodeName, relationshipType = null, limit = 20) => {
  try {
    const response = await fetch(`${API_BASE}/kg_node_graph`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({ 
        node_name: nodeName, 
        relationship_type: relationshipType,
        limit 
      })
    });

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));
      throw new Error(errorData.error || `API error: ${response.statusText}`);
    }

    const data = await response.json();
    return data;
  } catch (error) {
    throw new Error(error.message || 'Failed to fetch node graph');
  }
};

export const fetchDocument = async (filename, filepath = '', segment = '') => {
  try {
    const params = new URLSearchParams();
    if (segment) params.append('segment', segment);
    if (filepath) params.append('filepath', filepath);

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
