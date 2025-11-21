const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

export const apiClient = {
  // Health check
  healthCheck: () => fetch(`${API_BASE_URL}/health`).then(r => r.json()),

  // Clubs
  getClubs: () => fetch(`${API_BASE_URL}/api/clubs`).then(r => r.json()),
  createClub: (club: any) => fetch(`${API_BASE_URL}/api/clubs`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(club)
  }).then(r => r.json()),

  // Players
  getPlayers: () => fetch(`${API_BASE_URL}/api/players`).then(r => r.json()),
  createPlayer: (player: any) => fetch(`${API_BASE_URL}/api/players`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(player)
  }).then(r => r.json()),

  // Events
  getEvents: () => fetch(`${API_BASE_URL}/api/events`).then(r => r.json()),
  createEvent: (event: any) => fetch(`${API_BASE_URL}/api/events`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(event)
  }).then(r => r.json()),

  // Registrations
  createRegistration: (registration: any) => fetch(`${API_BASE_URL}/api/registrations`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(registration)
  }).then(r => r.json()),

  getEventRegistrations: (eventId: string) => 
    fetch(`${API_BASE_URL}/api/registrations/event/${eventId}`).then(r => r.json()),

  // Tournaments
  getTournaments: () => fetch(`${API_BASE_URL}/api/tournaments`).then(r => r.json()),
  createTournament: (tournament: any) => fetch(`${API_BASE_URL}/api/tournaments`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(tournament)
  }).then(r => r.json()),

  // Courts
  getCourts: () => fetch(`${API_BASE_URL}/api/courts`).then(r => r.json()),
  getActiveCourts: () => fetch(`${API_BASE_URL}/api/courts/active`).then(r => r.json()),
  createCourt: (court: any) => fetch(`${API_BASE_URL}/api/courts`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(court)
  }).then(r => r.json()),

  // Matches
  getMatches: () => fetch(`${API_BASE_URL}/api/matches`).then(r => r.json()),
  getTournamentMatches: (tournamentId: string) => 
    fetch(`${API_BASE_URL}/api/matches/tournament/${tournamentId}`).then(r => r.json()),
  createMatch: (match: any) => fetch(`${API_BASE_URL}/api/matches`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(match)
  }).then(r => r.json()),
  updateMatchScore: (matchId: string, scoreData: any) => 
    fetch(`${API_BASE_URL}/api/matches/${matchId}/score`, {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(scoreData)
    }).then(r => r.json()),

  // Algorithms
  groupPlayers: (data: any) => fetch(`${API_BASE_URL}/api/algorithms/grouping`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(data)
  }).then(r => r.json()),

  generatePairings: (data: any) => fetch(`${API_BASE_URL}/api/algorithms/pairing`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(data)
  }).then(r => r.json()),

  generateRoundRobin: (data: any) => fetch(`${API_BASE_URL}/api/algorithms/round-robin`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(data)
  }).then(r => r.json()),

  generateKnockout: (data: any) => fetch(`${API_BASE_URL}/api/algorithms/knockout`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(data)
  }).then(r => r.json()),

  scheduleMatches: (data: any) => fetch(`${API_BASE_URL}/api/algorithms/scheduling`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(data)
  }).then(r => r.json()),

  generateMatchCode: (data: any) => fetch(`${API_BASE_URL}/api/algorithms/match-code`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(data)
  }).then(r => r.json()),

  validateMatchCode: (data: any) => fetch(`${API_BASE_URL}/api/algorithms/validate-match-code`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(data)
  }).then(r => r.json()),

  // Statistics
  getStatistics: () => fetch(`${API_BASE_URL}/api/statistics`).then(r => r.json()),
};