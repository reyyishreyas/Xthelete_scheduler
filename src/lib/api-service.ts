import { apiClient, apiConfig } from './api-config';

// Types for API responses
export interface Club {
  id: string;
  name: string;
  code: string;
  created_at: string;
  updated_at: string;
}

export interface Player {
  id: string;
  name: string;
  phone: string;
  age: number;
  club_id: string;
  created_at: string;
  updated_at: string;
  club?: Club;
}

export interface Event {
  id: string;
  name: string;
  category: string;
  type: string;
  created_at: string;
  updated_at: string;
}

export interface Tournament {
  id: string;
  name: string;
  event_id: string;
  type: string;
  status: string;
  created_at: string;
  updated_at: string;
  event?: Event;
}

export interface Court {
  id: string;
  name: string;
  location?: string;
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

export interface Match {
  id: string;
  tournament_id: string;
  round_id: string;
  match_number: number;
  player1_id?: string;
  player2_id?: string;
  team1_id?: string;
  team2_id?: string;
  court_id?: string;
  scheduled_time?: string;
  start_time?: string;
  end_time?: string;
  status: string;
  player1_score?: number;
  player2_score?: number;
  winner_id?: string;
  match_code?: string;
  created_at: string;
  updated_at: string;
  player1?: Player;
  player2?: Player;
  court?: Court;
}

// API Service Functions
export const clubService = {
  async getAll(): Promise<Club[]> {
    const response = await apiClient.get(apiConfig.endpoints.clubs);
    return response;
  },

  async create(club: Omit<Club, 'id' | 'created_at' | 'updated_at'>): Promise<Club> {
    const response = await apiClient.post(apiConfig.endpoints.clubs, club);
    return response;
  },

  async getById(id: string): Promise<Club> {
    const response = await apiClient.get(`${apiConfig.endpoints.clubs}/${id}`);
    return response;
  },
};

export const playerService = {
  async getAll(): Promise<Player[]> {
    const response = await apiClient.get(apiConfig.endpoints.players);
    return response;
  },

  async create(player: Omit<Player, 'id' | 'created_at' | 'updated_at'>): Promise<Player> {
    const response = await apiClient.post(apiConfig.endpoints.players, player);
    return response;
  },

  async getById(id: string): Promise<Player> {
    const response = await apiClient.get(`${apiConfig.endpoints.players}/${id}`);
    return response;
  },

  async getByClub(clubId: string): Promise<Player[]> {
    const response = await apiClient.get(`${apiConfig.endpoints.players}?club_id=${clubId}`);
    return response;
  },
};

export const eventService = {
  async getAll(): Promise<Event[]> {
    const response = await apiClient.get(apiConfig.endpoints.events);
    return response;
  },

  async create(event: Omit<Event, 'id' | 'created_at' | 'updated_at'>): Promise<Event> {
    const response = await apiClient.post(apiConfig.endpoints.events, event);
    return response;
  },

  async getById(id: string): Promise<Event> {
    const response = await apiClient.get(`${apiConfig.endpoints.events}/${id}`);
    return response;
  },
};

export const tournamentService = {
  async getAll(): Promise<Tournament[]> {
    const response = await apiClient.get(apiConfig.endpoints.tournaments);
    return response;
  },

  async create(tournament: Omit<Tournament, 'id' | 'created_at' | 'updated_at'>): Promise<Tournament> {
    const response = await apiClient.post(apiConfig.endpoints.tournaments, tournament);
    return response;
  },

  async getById(id: string): Promise<Tournament> {
    const response = await apiClient.get(`${apiConfig.endpoints.tournaments}/${id}`);
    return response;
  },
};

export const courtService = {
  async getAll(): Promise<Court[]> {
    const response = await apiClient.get(apiConfig.endpoints.courts);
    return response;
  },

  async create(court: Omit<Court, 'id' | 'created_at' | 'updated_at'>): Promise<Court> {
    const response = await apiClient.post(apiConfig.endpoints.courts, court);
    return response;
  },

  async getActive(): Promise<Court[]> {
    const response = await apiClient.get(`${apiConfig.endpoints.courts}?is_active=true`);
    return response;
  },
};

export const matchService = {
  async getAll(): Promise<Match[]> {
    const response = await apiClient.get(apiConfig.endpoints.matches);
    return response;
  },

  async create(match: Omit<Match, 'id' | 'created_at' | 'updated_at'>): Promise<Match> {
    const response = await apiClient.post(apiConfig.endpoints.matches, match);
    return response;
  },

  async getById(id: string): Promise<Match> {
    const response = await apiClient.get(`${apiConfig.endpoints.matches}/${id}`);
    return response;
  },

  async getByTournament(tournamentId: string): Promise<Match[]> {
    const response = await apiClient.get(`${apiConfig.endpoints.matches}?tournament_id=${tournamentId}`);
    return response;
  },

  async update(id: string, match: Partial<Match>): Promise<Match> {
    const response = await apiClient.put(`${apiConfig.endpoints.matches}/${id}`, match);
    return response;
  },
};

// Algorithm Services
export const algorithmService = {
  async groupPlayers(playerIds: string[], numGroups: number) {
    const response = await apiClient.post(apiConfig.endpoints.grouping, {
      player_ids: playerIds,
      num_groups: numGroups,
    });
    return response;
  },

  async generatePairings(playerIds: string[]) {
    const response = await apiClient.post(apiConfig.endpoints.pairing, {
      player_ids: playerIds,
    });
    return response;
  },

  async scheduleMatches(matchIds: string[], courtIds: string[], startTime: string, constraints?: any) {
    const response = await apiClient.post(apiConfig.endpoints.scheduling, {
      match_ids: matchIds,
      court_ids: courtIds,
      start_time: startTime,
      constraints,
    });
    return response;
  },

  async generateMatchCode(matchId: string, playerIds: string[], courtId?: string, tournamentId?: string) {
    const response = await apiClient.post(apiConfig.endpoints.matchCode, {
      match_id: matchId,
      player_ids: playerIds,
      court_id: courtId,
      tournament_id: tournamentId,
    });
    return response;
  },

  async validateMatchCode(code: string) {
    const response = await apiClient.post(apiConfig.endpoints.validateMatchCode, {
      code,
    });
    return response;
  },

  async generateRoundRobin(playerIds: string[]) {
    const response = await apiClient.post(apiConfig.endpoints.roundRobin, {
      player_ids: playerIds,
    });
    return response;
  },

  async generateKnockout(playerIds: string[]) {
    const response = await apiClient.post(apiConfig.endpoints.knockout, {
      player_ids: playerIds,
    });
    return response;
  },
};

// Health Check
export const healthService = {
  async checkHealth() {
    const response = await apiClient.get(apiConfig.endpoints.health);
    return response;
  },
};

// Statistics
export const statsService = {
  async getStatistics() {
    const response = await apiClient.get(apiConfig.endpoints.statistics);
    return response;
  },
};

export default {
  club: clubService,
  player: playerService,
  event: eventService,
  tournament: tournamentService,
  court: courtService,
  match: matchService,
  algorithm: algorithmService,
  health: healthService,
  stats: statsService,
};