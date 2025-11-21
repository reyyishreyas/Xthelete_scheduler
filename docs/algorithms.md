# Algorithm Documentation

## Overview

The XTHLETE tournament management system implements several advanced algorithms to ensure fair, efficient, and optimal tournament organization. This document provides detailed technical documentation for each algorithm.

## 1. Anti-Cluster Distribution Algorithm

### Purpose
Minimize same-club matchups in group stages by distributing players evenly across groups.

### Algorithm Steps

1. **Bucket Players by Club**
   ```typescript
   const clubBuckets = new Map<string, Player[]>();
   for (const player of players) {
     const clubId = player.clubId;
     if (!clubBuckets.has(clubId)) {
       clubBuckets.set(clubId, []);
     }
     clubBuckets.get(clubId)!.push(player);
   }
   ```

2. **Sort Clubs by Size**
   ```typescript
   const sortedClubs = Array.from(clubBuckets.entries())
     .sort((a, b) => b[1].length - a[1].length);
   ```

3. **Round-Robin Distribution**
   ```typescript
   for (const [clubId, clubPlayers] of sortedClubs) {
     for (let i = 0; i < clubPlayers.length; i++) {
       const targetGroupIndex = i % numGroups;
       groups[targetGroupIndex].players.push(clubPlayers[i]);
     }
   }
   ```

### Penalty Calculation
Each same-club pair in a group adds +1 penalty:
```typescript
private calculateGroupPenalty(group: Player[]): number {
  const clubCounts = new Map<string, number>();
  let penalty = 0;
  
  for (const player of group) {
    const clubId = player.clubId;
    const count = clubCounts.get(clubId) || 0;
    clubCounts.set(clubId, count + 1);
    
    if (count > 0) {
      penalty += count;
    }
  }
  
  return penalty;
}
```

### Complexity Analysis
- **Time**: O(N) - Single pass through all players
- **Space**: O(N) - Storage for club buckets and groups

### Example
Input: 8 players from 3 clubs
- Club A: 4 players
- Club B: 2 players  
- Club C: 2 players

Output (2 groups):
- Group 1: A1, B1, C1, A3
- Group 2: A2, B2, C2, A4

## 2. Backtracking Pairing Algorithm

### Purpose
Generate optimal pairings that minimize same-club matchups using backtracking search.

### Algorithm Steps

1. **Handle Odd Players**
   ```typescript
   if (players.length % 2 !== 0) {
     players.push(this.createByePlayer());
   }
   ```

2. **Backtracking Search**
   ```typescript
   private findOptimalPairing(
     players: Player[],
     currentMatches: Match[] = [],
     currentPenalty: number = 0
   ): void {
     // Base case: all players paired
     if (players.length === 0) {
       // Update best solution
       return;
     }
     
     // Prune if current penalty exceeds best found
     if (this.bestResult && currentPenalty >= this.bestResult.totalPenalty) {
       return;
     }
     
     // Fix first player, try pairing with others
     const firstPlayer = players[0];
     const remainingPlayers = players.slice(1);
     
     for (let i = 0; i < remainingPlayers.length; i++) {
       const secondPlayer = remainingPlayers[i];
       const penalty = this.calculateMatchPenalty(firstPlayer, secondPlayer);
       
       // Recursively pair remaining players
       this.findOptimalPairing(
         newRemaining,
         [...currentMatches, match],
         currentPenalty + penalty
       );
     }
   }
   ```

### Penalty System
- Different clubs: 0 penalty
- Same club: 1 penalty

### Optimization Techniques
1. **Memoization**: Cache visited states to avoid redundant computation
2. **Pruning**: Stop exploring branches that exceed current best penalty
3. **Sorting**: Process players consistently for reproducible results

### Complexity Analysis
- **Worst Case**: O(N!) - All possible pairings
- **Practical**: Much better due to pruning and constraints
- **Space**: O(N) - Recursion stack

### Example
Input: 4 players (A1, A2, B1, B2)
- A1, A2 from Club A
- B1, B2 from Club B

Optimal pairing:
- A1 vs B1 (penalty: 0)
- A2 vs B2 (penalty: 0)
Total penalty: 0

## 3. Round Robin Rotation Algorithm

### Purpose
Generate balanced round-robin schedules using circle method.

### Algorithm Steps

1. **Initialize Circle**
   ```typescript
   const fixed = players.slice(0, 1); // First player stays fixed
   const rotating = players.slice(1); // Others rotate
   ```

2. **Generate Rounds**
   ```typescript
   for (let round = 0; round < numRounds; round++) {
     const currentRoundPlayers = [...fixed, ...rotating];
     
     // Pair across the circle
     for (let i = 0; i < matchesPerRound; i++) {
       const player1 = currentRoundPlayers[i];
       const player2 = currentRoundPlayers[numPlayers - 1 - i];
       
       // Create match
       matches.push({ player1, player2, penalty });
     }
     
     // Rotate for next round
     if (round < numRounds - 1) {
       const lastPlayer = rotating.pop()!;
       rotating.unshift(lastPlayer);
     }
   }
   ```

3. **Optimize Match Order**
   ```typescript
   const sortedMatches = this.sortMatchesByPenalty(roundMatches);
   ```

### Handling Odd Players
Add BYE player when odd number of players:
```typescript
if (players.length % 2 !== 0) {
  players.push(this.createByePlayer());
}
```

### Complexity Analysis
- **Time**: O(N²) - N rounds with N/2 matches each
- **Space**: O(N²) - Store all rounds and matches

### Example
Input: 4 players (A, B, C, D)

Round 1: A vs D, B vs C
Round 2: A vs C, D vs B  
Round 3: A vs B, C vs D

## 4. Smart Scheduling Engine

### Purpose
Schedule matches across multiple courts while enforcing constraints.

### Core Data Structure: Min-Heap
```typescript
interface CourtAvailability {
  court: Court;
  nextAvailableTime: Date;
  currentMatch?: ScheduledMatch;
}

// Courts sorted by next available time
private courtsHeap: CourtAvailability[];
```

### Algorithm Steps

1. **Initialize Courts Heap**
   ```typescript
   this.courtsHeap = courts.map(court => ({
     court,
     nextAvailableTime: startTime
   }));
   ```

2. **Schedule Each Match**
   ```typescript
   private scheduleMatch(match: Match): ScheduledMatch {
     const courtAvailability = this.getEarliestAvailableCourt();
     
     // Calculate earliest start time
     const earliestStartTime = this.calculateEarliestStartTime(
       courtAvailability,
       match.player1.id,
       match.player2.id
     );
     
     // Update court availability
     this.updateCourtAvailability(courtAvailability, endTime);
     
     return scheduledMatch;
   }
   ```

3. **Player Rest Time Enforcement**
   ```typescript
   private isPlayerAvailable(playerId: string, proposedTime: Date): boolean {
     const restInfo = this.playerRestMap.get(playerId);
     if (!restInfo) return true;
     
     return proposedTime.getTime() >= restInfo.nextAvailableTime.getTime();
   }
   ```

### Constraint Handling
- **Minimum Rest Time**: Players need specified rest between matches
- **Court Availability**: Matches scheduled when courts are free
- **Working Hours**: Only schedule within specified hours
- **Buffer Time**: Time between matches on same court

### Delay Handling
```typescript
public handleDelay(delayedMatchId: string, delayMinutes: number): ScheduledMatch[] {
  // Find affected matches
  const affectedMatches = currentSchedule.filter(m => 
    m.court.id === delayedMatch.court.id &&
    m.scheduledStartTime > delayedMatch.scheduledStartTime
  );
  
  // Reschedule with cumulative delay
  let cumulativeDelay = delayMinutes;
  affectedMatches.forEach(match => {
    match.scheduledStartTime = new Date(
      match.scheduledStartTime.getTime() + cumulativeDelay * 60 * 1000
    );
  });
  
  return updatedSchedule;
}
```

### Complexity Analysis
- **Time**: O(M log C) - M matches, C courts (heap operations)
- **Space**: O(M + C) - Store schedule and court heap

## 5. Knockout Bracket Engine

### Purpose
Generate seeded knockout brackets with fair player distribution.

### Seeding Strategy

1. **Standard Tournament Seeding**
   ```typescript
   private placeSeed(player: Player, position: number, interval: number): void {
     seededPositions[position] = player;
     
     if (interval > 1) {
       const nextInterval = interval / 2;
       placeSeed(sortedPlayers[position + nextInterval], position + nextInterval, nextInterval);
       placeSeed(sortedPlayers[position + interval * 2 - nextInterval], position + interval * 2 - nextInterval, nextInterval);
     }
   }
   ```

2. **BYE Handling**
   ```typescript
   const byesNeeded = this.calculateByesNeeded(numPlayers);
   const actualMatches = firstRound.length - byesNeeded;
   ```

### Bracket Generation

1. **Calculate Bracket Size**
   ```typescript
   private nextPowerOf2(n: number): number {
     return Math.pow(2, Math.ceil(Math.log2(n)));
   }
   ```

2. **Create Bracket Structure**
   ```typescript
   private generateBracketStructure(rounds: number): KnockoutMatch[][] {
     const bracket: KnockoutMatch[][] = [];
     
     for (let round = 0; round < rounds; round++) {
       const matchesInRound = Math.pow(2, rounds - round - 1);
       // Create matches for this round
     }
     
     return bracket;
   }
   ```

### Progression Logic
```typescript
public updateMatchResult(matchId: string, score1: number, score2: number): void {
  // Determine winner
  const winner = score1 > score2 ? match.player1 : match.player2;
  
  // Advance to next round
  if (roundIndex < bracket.matches.length - 1) {
    const nextRound = bracket.matches[roundIndex + 1];
    const nextMatchIndex = Math.floor(matchIndex / 2);
    const nextMatch = nextRound[nextMatchIndex];
    
    // Place winner in appropriate position
    if (matchIndex % 2 === 0) {
      nextMatch.player1 = winner;
    } else {
      nextMatch.player2 = winner;
    }
  }
}
```

### Complexity Analysis
- **Time**: O(N log N) - Initial bracket generation
- **Space**: O(N) - Store bracket structure

## 6. Match Code Security System

### Purpose
Generate secure, time-limited access codes for match management.

### Code Generation

1. **Create Match Data**
   ```typescript
   const matchData: MatchCodeData = {
     matchId,
     playerIds: [...playerIds].sort(),
     courtId,
     timestamp: Date.now(),
     tournamentId,
     expiresAt: Date.now() + (this.CODE_EXPIRY_MINUTES * 60 * 1000)
   };
   ```

2. **Generate Secure Code**
   ```typescript
   const baseCode = this.generateRandomCode(this.CODE_LENGTH);
   const payload = this.serializeMatchData(matchData);
   const hash = this.generateHash(payload + baseCode);
   const finalCode = `${baseCode}-${hash.substring(0, 16)}`;
   ```

### Security Features

1. **SHA-256 Hashing**
   ```typescript
   private generateHash(data: string): string {
     return createHash('sha256')
       .update(data + this.SALT)
       .digest('hex');
   }
   ```

2. **Timestamp Expiration**
   ```typescript
   if (now > matchData.expiresAt) {
     this.activeCodes.delete(code);
     return { isValid: false, error: 'Code has expired' };
   }
   ```

3. **One-Time Use**
   ```typescript
   if (this.usedCodes.has(code)) {
     return { isValid: false, error: 'Code has already been used' };
   }
   ```

### Validation Process
```typescript
public validateMatchCode(code: string): CodeValidationResult {
  // Check if used
  if (this.usedCodes.has(code)) return invalid;
  
  // Check if exists and not expired
  const matchData = this.activeCodes.get(code);
  if (!matchData || now > matchData.expiresAt) return invalid;
  
  // Verify hash integrity
  const [baseCode, hashPart] = code.split('-');
  const expectedHash = this.generateHash(payload + baseCode);
  
  if (expectedHash.substring(0, 16) !== hashPart) {
    return { isValid: false, error: 'Code integrity check failed' };
  }
  
  return { isValid: true, matchData };
}
```

### Complexity Analysis
- **Time**: O(1) - Hash operations and map lookups
- **Space**: O(N) - Store active codes

## Algorithm Integration

The algorithms work together to provide a complete tournament management solution:

1. **Registration Phase**: Anti-Cluster groups players for fair distribution
2. **Fixture Generation**: Backtracking/Round-Robin creates optimal match pairings
3. **Scheduling Phase**: Smart Scheduling assigns courts and times
4. **Match Management**: Security codes control access to scoring
5. **Results Phase**: Leaderboard updates automatically track standings

## Performance Considerations

- **Caching**: Algorithm results cached where appropriate
- **Lazy Loading**: Heavy computations only when needed
- **Batch Processing**: Multiple operations processed together
- **Memory Management**: Cleanup of expired codes and temporary data

## Edge Case Handling

- **Odd Player Counts**: BYE players automatically added
- **Tie Situations**: Tie-break rules implemented
- **Schedule Conflicts**: Automatic resolution and notification
- **Security Breaches**: Code invalidation and reissuance
- **Data Corruption**: Validation and recovery mechanisms

This comprehensive algorithm suite ensures fair, efficient, and secure tournament management for the XTHLETE platform.