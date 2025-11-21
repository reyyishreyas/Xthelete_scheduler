// API Configuration for Python FastAPI Backend
const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

export const apiConfig = {
  baseURL: API_BASE_URL,
  endpoints: {
    // Health
    health: '/health',
    
    // Clubs
    clubs: '/api/clubs',
    
    // Players
    players: '/api/players',
    
    // Events
    events: '/api/events',
    
    // Tournaments
    tournaments: '/api/tournaments',
    
    // Courts
    courts: '/api/courts',
    
    // Matches
    matches: '/api/matches',
    
    // Algorithms
    grouping: '/api/algorithms/grouping',
    pairing: '/api/algorithms/pairing',
    scheduling: '/api/algorithms/scheduling',
    matchCode: '/api/algorithms/match-code',
    validateMatchCode: '/api/algorithms/validate-match-code',
    roundRobin: '/api/algorithms/round-robin',
    knockout: '/api/algorithms/knockout',
    
    // Statistics
    statistics: '/api/statistics',
  }
};

// API Client helper functions
export const apiClient = {
  async get(endpoint: string) {
    try {
      const response = await fetch(`${API_BASE_URL}${endpoint}`);
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      return await response.json();
    } catch (error) {
      console.error('API GET Error:', error);
      throw error;
    }
  },

  async post(endpoint: string, data: any) {
    try {
      const response = await fetch(`${API_BASE_URL}${endpoint}`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(data),
      });
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      return await response.json();
    } catch (error) {
      console.error('API POST Error:', error);
      throw error;
    }
  },

  async put(endpoint: string, data: any) {
    try {
      const response = await fetch(`${API_BASE_URL}${endpoint}`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(data),
      });
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      return await response.json();
    } catch (error) {
      console.error('API PUT Error:', error);
      throw error;
    }
  },

  async delete(endpoint: string) {
    try {
      const response = await fetch(`${API_BASE_URL}${endpoint}`, {
        method: 'DELETE',
      });
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      return await response.json();
    } catch (error) {
      console.error('API DELETE Error:', error);
      throw error;
    }
  },
};

export default apiConfig;