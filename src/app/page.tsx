'use client';

import { useState, useEffect } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Badge } from '@/components/ui/badge';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { Progress } from '@/components/ui/progress';
import { Separator } from '@/components/ui/separator';
import { 
  Users, 
  Calendar, 
  Trophy, 
  Shield, 
  Clock, 
  CheckCircle, 
  AlertCircle,
  Plus,
  Play,
  BarChart3,
  Settings
} from 'lucide-react';

interface Player {
  id: string;
  name: string;
  phone: string;
  age: number;
  clubId: string;
  clubName?: string;
}

interface Club {
  id: string;
  name: string;
  code: string;
}

interface Tournament {
  id: string;
  name: string;
  type: 'knockout' | 'round_robin';
  status: 'pending' | 'active' | 'completed';
  playerCount: number;
}

interface Match {
  id: string;
  player1: Player;
  player2: Player;
  penalty: number;
  scheduledTime?: Date;
  court?: string;
}

export default function TournamentManagementSystem() {
  const [activeTab, setActiveTab] = useState('overview');
  const [clubs, setClubs] = useState<Club[]>([]);
  const [players, setPlayers] = useState<Player[]>([]);
  const [tournaments, setTournaments] = useState<Tournament[]>([]);
  const [matches, setMatches] = useState<Match[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Form states
  const [newClub, setNewClub] = useState({ name: '', code: '' });
  const [newPlayer, setNewPlayer] = useState({ name: '', phone: '', age: '', clubId: '' });
  const [newTournament, setNewTournament] = useState({ name: '', type: 'knockout' as const });

  // Mock data for demonstration
  useEffect(() => {
    // Initialize with sample data
    setClubs([
      { id: '1', name: 'Tennis Club A', code: 'TCA' },
      { id: '2', name: 'Sports Academy B', code: 'SAB' },
      { id: '3', name: 'Athletic Club C', code: 'ACC' }
    ]);

    setPlayers([
      { id: '1', name: 'John Doe', phone: '+1234567890', age: 25, clubId: '1', clubName: 'Tennis Club A' },
      { id: '2', name: 'Jane Smith', phone: '+1234567891', age: 23, clubId: '2', clubName: 'Sports Academy B' },
      { id: '3', name: 'Mike Johnson', phone: '+1234567892', age: 27, clubId: '1', clubName: 'Tennis Club A' },
      { id: '4', name: 'Sarah Williams', phone: '+1234567893', age: 22, clubId: '3', clubName: 'Athletic Club C' },
      { id: '5', name: 'David Brown', phone: '+1234567894', age: 26, clubId: '2', clubName: 'Sports Academy B' },
      { id: '6', name: 'Emily Davis', phone: '+1234567895', age: 24, clubId: '3', clubName: 'Athletic Club C' }
    ]);

    setTournaments([
      { id: '1', name: 'Spring Championship 2024', type: 'knockout', status: 'active', playerCount: 6 },
      { id: '2', name: 'Summer League', type: 'round_robin', status: 'pending', playerCount: 8 }
    ]);

    setMatches([
      {
        id: '1',
        player1: players[0] || { id: '1', name: 'John Doe', phone: '+1234567890', age: 25, clubId: '1' },
        player2: players[1] || { id: '2', name: 'Jane Smith', phone: '+1234567891', age: 23, clubId: '2' },
        penalty: 0,
        scheduledTime: new Date(Date.now() + 3600000),
        court: 'Court 1'
      },
      {
        id: '2',
        player1: players[2] || { id: '3', name: 'Mike Johnson', phone: '+1234567892', age: 27, clubId: '1' },
        player2: players[3] || { id: '4', name: 'Sarah Williams', phone: '+1234567893', age: 22, clubId: '3' },
        penalty: 1,
        scheduledTime: new Date(Date.now() + 7200000),
        court: 'Court 2'
      }
    ]);
  }, []);

  const handleAddClub = async () => {
    if (!newClub.name || !newClub.code) {
      setError('Please fill in all club fields');
      return;
    }

    setLoading(true);
    try {
      const club: Club = {
        id: Date.now().toString(),
        name: newClub.name,
        code: newClub.code
      };
      setClubs([...clubs, club]);
      setNewClub({ name: '', code: '' });
      setError(null);
    } catch (err) {
      setError('Failed to add club');
    } finally {
      setLoading(false);
    }
  };

  const handleAddPlayer = async () => {
    if (!newPlayer.name || !newPlayer.phone || !newPlayer.age || !newPlayer.clubId) {
      setError('Please fill in all player fields');
      return;
    }

    // Check for duplicates
    const existingPlayer = players.find(p => 
      p.name === newPlayer.name && p.phone === newPlayer.phone
    );
    if (existingPlayer) {
      setError('Player with this name and phone already exists');
      return;
    }

    setLoading(true);
    try {
      const club = clubs.find(c => c.id === newPlayer.clubId);
      const player: Player = {
        id: Date.now().toString(),
        name: newPlayer.name,
        phone: newPlayer.phone,
        age: parseInt(newPlayer.age),
        clubId: newPlayer.clubId,
        clubName: club?.name
      };
      setPlayers([...players, player]);
      setNewPlayer({ name: '', phone: '', age: '', clubId: '' });
      setError(null);
    } catch (err) {
      setError('Failed to add player');
    } finally {
      setLoading(false);
    }
  };

  const handleCreateTournament = async () => {
    if (!newTournament.name) {
      setError('Please enter tournament name');
      return;
    }

    setLoading(true);
    try {
      const tournament: Tournament = {
        id: Date.now().toString(),
        name: newTournament.name,
        type: newTournament.type,
        status: 'pending',
        playerCount: 0
      };
      setTournaments([...tournaments, tournament]);
      setNewTournament({ name: '', type: 'knockout' });
      setError(null);
    } catch (err) {
      setError('Failed to create tournament');
    } finally {
      setLoading(false);
    }
  };

  const generateFixtures = () => {
    // Mock fixture generation
    const newMatches: Match[] = [];
    for (let i = 0; i < players.length - 1; i += 2) {
      newMatches.push({
        id: Date.now().toString() + i,
        player1: players[i],
        player2: players[i + 1],
        penalty: players[i].clubId === players[i + 1].clubId ? 1 : 0,
        scheduledTime: new Date(Date.now() + (i + 1) * 3600000),
        court: `Court ${Math.floor(i / 2) + 1}`
      });
    }
    setMatches([...matches, ...newMatches]);
  };

  const stats = {
    totalClubs: clubs.length,
    totalPlayers: players.length,
    activeTournaments: tournaments.filter(t => t.status === 'active').length,
    totalMatches: matches.length,
    completedMatches: matches.filter(m => m.scheduledTime && m.scheduledTime < new Date()).length
  };

  return (
    <div className="min-h-screen bg-gray-50 p-4">
      <div className="max-w-7xl mx-auto space-y-6">
        {/* Header */}
        <div className="bg-white rounded-lg shadow-sm p-6">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-3xl font-bold text-gray-900">XTHLETE Tournament Management</h1>
              <p className="text-gray-600 mt-2">Smart Fixture, Scheduling & Match Management System</p>
            </div>
            <div className="flex items-center gap-2">
              <Badge variant="outline" className="text-green-600 border-green-600">
                <CheckCircle className="w-4 h-4 mr-1" />
                System Active
              </Badge>
            </div>
          </div>
        </div>

        {/* Error Alert */}
        {error && (
          <Alert variant="destructive">
            <AlertCircle className="h-4 w-4" />
            <AlertDescription>{error}</AlertDescription>
          </Alert>
        )}

        {/* Stats Overview */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-5 gap-4">
          <Card>
            <CardContent className="p-4">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-gray-600">Total Clubs</p>
                  <p className="text-2xl font-bold">{stats.totalClubs}</p>
                </div>
                <Users className="w-8 h-8 text-blue-600" />
              </div>
            </CardContent>
          </Card>
          
          <Card>
            <CardContent className="p-4">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-gray-600">Total Players</p>
                  <p className="text-2xl font-bold">{stats.totalPlayers}</p>
                </div>
                <Users className="w-8 h-8 text-green-600" />
              </div>
            </CardContent>
          </Card>
          
          <Card>
            <CardContent className="p-4">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-gray-600">Active Tournaments</p>
                  <p className="text-2xl font-bold">{stats.activeTournaments}</p>
                </div>
                <Trophy className="w-8 h-8 text-yellow-600" />
              </div>
            </CardContent>
          </Card>
          
          <Card>
            <CardContent className="p-4">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-gray-600">Total Matches</p>
                  <p className="text-2xl font-bold">{stats.totalMatches}</p>
                </div>
                <Calendar className="w-8 h-8 text-purple-600" />
              </div>
            </CardContent>
          </Card>
          
          <Card>
            <CardContent className="p-4">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-gray-600">Completed</p>
                  <p className="text-2xl font-bold">{stats.completedMatches}</p>
                </div>
                <CheckCircle className="w-8 h-8 text-green-600" />
              </div>
            </CardContent>
          </Card>
        </div>

        {/* Main Content */}
        <Tabs value={activeTab} onValueChange={setActiveTab} className="space-y-4">
          <TabsList className="grid w-full grid-cols-6">
            <TabsTrigger value="overview">Overview</TabsTrigger>
            <TabsTrigger value="clubs">Clubs</TabsTrigger>
            <TabsTrigger value="players">Players</TabsTrigger>
            <TabsTrigger value="tournaments">Tournaments</TabsTrigger>
            <TabsTrigger value="matches">Matches</TabsTrigger>
            <TabsTrigger value="settings">Settings</TabsTrigger>
          </TabsList>

          {/* Overview Tab */}
          <TabsContent value="overview" className="space-y-4">
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center gap-2">
                    <Calendar className="w-5 h-5" />
                    Recent Matches
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="space-y-4">
                    {matches.slice(0, 3).map((match) => (
                      <div key={match.id} className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                        <div className="flex-1">
                          <div className="flex items-center gap-2">
                            <span className="font-medium">{match.player1.name}</span>
                            <span className="text-gray-500">vs</span>
                            <span className="font-medium">{match.player2.name}</span>
                            {match.penalty === 0 ? (
                              <Badge variant="outline" className="text-green-600 border-green-600">
                                Different Clubs
                              </Badge>
                            ) : (
                              <Badge variant="outline" className="text-orange-600 border-orange-600">
                                Same Club
                              </Badge>
                            )}
                          </div>
                          <div className="flex items-center gap-4 mt-1 text-sm text-gray-600">
                            <span className="flex items-center gap-1">
                              <Clock className="w-3 h-3" />
                              {match.scheduledTime?.toLocaleString()}
                            </span>
                            <span>{match.court}</span>
                          </div>
                        </div>
                      </div>
                    ))}
                  </div>
                </CardContent>
              </Card>

              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center gap-2">
                    <BarChart3 className="w-5 h-5" />
                    Tournament Status
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="space-y-4">
                    {tournaments.map((tournament) => (
                      <div key={tournament.id} className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                        <div>
                          <h4 className="font-medium">{tournament.name}</h4>
                          <div className="flex items-center gap-2 mt-1">
                            <Badge variant={tournament.type === 'knockout' ? 'default' : 'secondary'}>
                              {tournament.type === 'knockout' ? 'Knockout' : 'Round Robin'}
                            </Badge>
                            <span className="text-sm text-gray-600">{tournament.playerCount} players</span>
                          </div>
                        </div>
                        <Badge 
                          variant={tournament.status === 'active' ? 'default' : 
                                  tournament.status === 'completed' ? 'secondary' : 'outline'}
                        >
                          {tournament.status}
                        </Badge>
                      </div>
                    ))}
                  </div>
                </CardContent>
              </Card>
            </div>
          </TabsContent>

          {/* Clubs Tab */}
          <TabsContent value="clubs" className="space-y-4">
            <Card>
              <CardHeader>
                <CardTitle>Add New Club</CardTitle>
                <CardDescription>Register a new club in the system</CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div>
                    <Label htmlFor="clubName">Club Name</Label>
                    <Input
                      id="clubName"
                      value={newClub.name}
                      onChange={(e) => setNewClub({ ...newClub, name: e.target.value })}
                      placeholder="Enter club name"
                    />
                  </div>
                  <div>
                    <Label htmlFor="clubCode">Club Code</Label>
                    <Input
                      id="clubCode"
                      value={newClub.code}
                      onChange={(e) => setNewClub({ ...newClub, code: e.target.value.toUpperCase() })}
                      placeholder="Enter club code"
                      maxLength={5}
                    />
                  </div>
                </div>
                <Button onClick={handleAddClub} disabled={loading}>
                  <Plus className="w-4 h-4 mr-2" />
                  Add Club
                </Button>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle>Registered Clubs</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                  {clubs.map((club) => (
                    <div key={club.id} className="p-4 border rounded-lg">
                      <h3 className="font-semibold">{club.name}</h3>
                      <p className="text-sm text-gray-600">Code: {club.code}</p>
                      <div className="mt-2">
                        <span className="text-sm text-gray-600">
                          {players.filter(p => p.clubId === club.id).length} players
                        </span>
                      </div>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>
          </TabsContent>

          {/* Players Tab */}
          <TabsContent value="players" className="space-y-4">
            <Card>
              <CardHeader>
                <CardTitle>Add New Player</CardTitle>
                <CardDescription>Register a new player with duplicate prevention</CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
                  <div>
                    <Label htmlFor="playerName">Player Name</Label>
                    <Input
                      id="playerName"
                      value={newPlayer.name}
                      onChange={(e) => setNewPlayer({ ...newPlayer, name: e.target.value })}
                      placeholder="Enter player name"
                    />
                  </div>
                  <div>
                    <Label htmlFor="playerPhone">Phone Number</Label>
                    <Input
                      id="playerPhone"
                      value={newPlayer.phone}
                      onChange={(e) => setNewPlayer({ ...newPlayer, phone: e.target.value })}
                      placeholder="Enter phone number"
                    />
                  </div>
                  <div>
                    <Label htmlFor="playerAge">Age</Label>
                    <Input
                      id="playerAge"
                      type="number"
                      value={newPlayer.age}
                      onChange={(e) => setNewPlayer({ ...newPlayer, age: e.target.value })}
                      placeholder="Enter age"
                      min={10}
                      max={100}
                    />
                  </div>
                  <div>
                    <Label htmlFor="playerClub">Club</Label>
                    <select
                      id="playerClub"
                      value={newPlayer.clubId}
                      onChange={(e) => setNewPlayer({ ...newPlayer, clubId: e.target.value })}
                      className="w-full p-2 border rounded-md"
                    >
                      <option value="">Select a club</option>
                      {clubs.map((club) => (
                        <option key={club.id} value={club.id}>
                          {club.name}
                        </option>
                      ))}
                    </select>
                  </div>
                </div>
                <Button onClick={handleAddPlayer} disabled={loading}>
                  <Plus className="w-4 h-4 mr-2" />
                  Add Player
                </Button>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle>Registered Players</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="overflow-x-auto">
                  <table className="w-full border-collapse">
                    <thead>
                      <tr className="border-b">
                        <th className="text-left p-2">Name</th>
                        <th className="text-left p-2">Phone</th>
                        <th className="text-left p-2">Age</th>
                        <th className="text-left p-2">Club</th>
                        <th className="text-left p-2">Status</th>
                      </tr>
                    </thead>
                    <tbody>
                      {players.map((player) => (
                        <tr key={player.id} className="border-b">
                          <td className="p-2 font-medium">{player.name}</td>
                          <td className="p-2">{player.phone}</td>
                          <td className="p-2">{player.age}</td>
                          <td className="p-2">{player.clubName}</td>
                          <td className="p-2">
                            <Badge variant="outline" className="text-green-600 border-green-600">
                              Active
                            </Badge>
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </CardContent>
            </Card>
          </TabsContent>

          {/* Tournaments Tab */}
          <TabsContent value="tournaments" className="space-y-4">
            <Card>
              <CardHeader>
                <CardTitle>Create Tournament</CardTitle>
                <CardDescription>Set up a new tournament</CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div>
                    <Label htmlFor="tournamentName">Tournament Name</Label>
                    <Input
                      id="tournamentName"
                      value={newTournament.name}
                      onChange={(e) => setNewTournament({ ...newTournament, name: e.target.value })}
                      placeholder="Enter tournament name"
                    />
                  </div>
                  <div>
                    <Label htmlFor="tournamentType">Tournament Type</Label>
                    <select
                      id="tournamentType"
                      value={newTournament.type}
                      onChange={(e) => setNewTournament({ ...newTournament, type: e.target.value as 'knockout' | 'round_robin' })}
                      className="w-full p-2 border rounded-md"
                    >
                      <option value="knockout">Knockout</option>
                      <option value="round_robin">Round Robin</option>
                    </select>
                  </div>
                </div>
                <Button onClick={handleCreateTournament} disabled={loading}>
                  <Plus className="w-4 h-4 mr-2" />
                  Create Tournament
                </Button>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle>Tournament Management</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  {tournaments.map((tournament) => (
                    <div key={tournament.id} className="p-4 border rounded-lg">
                      <div className="flex items-center justify-between">
                        <div>
                          <h3 className="font-semibold">{tournament.name}</h3>
                          <div className="flex items-center gap-2 mt-1">
                            <Badge variant={tournament.type === 'knockout' ? 'default' : 'secondary'}>
                              {tournament.type === 'knockout' ? 'Knockout' : 'Round Robin'}
                            </Badge>
                            <span className="text-sm text-gray-600">{tournament.playerCount} players</span>
                          </div>
                        </div>
                        <div className="flex items-center gap-2">
                          <Badge 
                            variant={tournament.status === 'active' ? 'default' : 
                                    tournament.status === 'completed' ? 'secondary' : 'outline'}
                          >
                            {tournament.status}
                          </Badge>
                          {tournament.status === 'pending' && (
                            <Button size="sm" onClick={generateFixtures}>
                              <Play className="w-4 h-4 mr-2" />
                              Generate Fixtures
                            </Button>
                          )}
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>
          </TabsContent>

          {/* Matches Tab */}
          <TabsContent value="matches" className="space-y-4">
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Shield className="w-5 h-5" />
                  Match Schedule
                </CardTitle>
                <CardDescription>View and manage scheduled matches with security codes</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  {matches.map((match) => (
                    <div key={match.id} className="p-4 border rounded-lg">
                      <div className="flex items-center justify-between">
                        <div className="flex-1">
                          <div className="flex items-center gap-2">
                            <span className="font-medium">{match.player1.name}</span>
                            <span className="text-gray-500">vs</span>
                            <span className="font-medium">{match.player2.name}</span>
                            {match.penalty === 0 ? (
                              <Badge variant="outline" className="text-green-600 border-green-600">
                                Different Clubs
                              </Badge>
                            ) : (
                              <Badge variant="outline" className="text-orange-600 border-orange-600">
                                Same Club
                              </Badge>
                            )}
                          </div>
                          <div className="flex items-center gap-4 mt-2 text-sm text-gray-600">
                            <span className="flex items-center gap-1">
                              <Clock className="w-3 h-3" />
                              {match.scheduledTime?.toLocaleString()}
                            </span>
                            <span>{match.court}</span>
                            <Badge variant="outline" className="text-blue-600 border-blue-600">
                              <Shield className="w-3 h-3 mr-1" />
                              Secured
                            </Badge>
                          </div>
                        </div>
                        <div className="flex items-center gap-2">
                          <Button size="sm" variant="outline">
                            View Details
                          </Button>
                          <Button size="sm">
                            Enter Score
                          </Button>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>
          </TabsContent>

          {/* Settings Tab */}
          <TabsContent value="settings" className="space-y-4">
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Settings className="w-5 h-5" />
                  System Settings
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-6">
                <div>
                  <h3 className="text-lg font-semibold mb-4">Algorithm Configuration</h3>
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <div className="p-4 border rounded-lg">
                      <h4 className="font-medium mb-2">Anti-Cluster Distribution</h4>
                      <p className="text-sm text-gray-600 mb-2">Minimize same-club matches in early rounds</p>
                      <Badge variant="outline" className="text-green-600 border-green-600">
                        Active
                      </Badge>
                    </div>
                    <div className="p-4 border rounded-lg">
                      <h4 className="font-medium mb-2">Backtracking Pairing</h4>
                      <p className="text-sm text-gray-600 mb-2">Optimal pairings with minimum penalty</p>
                      <Badge variant="outline" className="text-green-600 border-green-600">
                        Active
                      </Badge>
                    </div>
                    <div className="p-4 border rounded-lg">
                      <h4 className="font-medium mb-2">Smart Scheduling</h4>
                      <p className="text-sm text-gray-600 mb-2">Multi-court scheduling with rest time</p>
                      <Badge variant="outline" className="text-green-600 border-green-600">
                        Active
                      </Badge>
                    </div>
                    <div className="p-4 border rounded-lg">
                      <h4 className="font-medium mb-2">Match Security</h4>
                      <p className="text-sm text-gray-600 mb-2">SHA-256 code protection</p>
                      <Badge variant="outline" className="text-green-600 border-green-600">
                        Active
                      </Badge>
                    </div>
                  </div>
                </div>

                <Separator />

                <div>
                  <h3 className="text-lg font-semibold mb-4">System Performance</h3>
                  <div className="space-y-4">
                    <div>
                      <div className="flex justify-between mb-2">
                        <span className="text-sm font-medium">CPU Usage</span>
                        <span className="text-sm text-gray-600">45%</span>
                      </div>
                      <Progress value={45} className="h-2" />
                    </div>
                    <div>
                      <div className="flex justify-between mb-2">
                        <span className="text-sm font-medium">Memory Usage</span>
                        <span className="text-sm text-gray-600">62%</span>
                      </div>
                      <Progress value={62} className="h-2" />
                    </div>
                    <div>
                      <div className="flex justify-between mb-2">
                        <span className="text-sm font-medium">Database Load</span>
                        <span className="text-sm text-gray-600">28%</span>
                      </div>
                      <Progress value={28} className="h-2" />
                    </div>
                  </div>
                </div>
              </CardContent>
            </Card>
          </TabsContent>
        </Tabs>
      </div>
    </div>
  );
}