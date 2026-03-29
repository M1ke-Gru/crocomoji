import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { usePlayerStore } from '@/stores/player'

export interface GamePlayer {
  id: string
  display_name: string
  stars: number
}

export const useGameStore = defineStore('game', () => {
  const status = ref<'waiting' | 'playing' | 'finished'>('waiting')
  const players = ref<Record<string, GamePlayer>>({})
  const numRounds = ref(0)

  const playerStore = usePlayerStore()
  const playerList = computed(() => Object.values(players.value))

  function onPlayerConnected(data: { player_id: string; display_name: string }) {
    players.value[data.player_id] = { id: data.player_id, display_name: data.display_name, stars: 0 }
  }

  function onPlayerDisconnected(data: { player_id: string }) {
    delete players.value[data.player_id]
  }

  function onGameStarted(data: { num_rounds: number; joke_time_seconds: number; voting_time_seconds: number }) {
    status.value = 'playing'
    numRounds.value = data.num_rounds
  }

  function onStarsUpdated(scores: Record<string, number>) {
    for (const [id, stars] of Object.entries(scores)) {
      if (players.value[id]) players.value[id].stars = stars
    }
  }

  function onGameOver(scores: Record<string, number>) {
    status.value = 'finished'
    onStarsUpdated(scores)
  }

  function setPlayersFromRoom(roomPlayers: { id: string; display_name: string; stars?: number }[]) {
    players.value = Object.fromEntries(
      roomPlayers.map((p) => [p.id, { id: p.id, display_name: p.display_name, stars: p.stars ?? 0 }]),
    )
  }

  return {
    status,
    players,
    numRounds,
    playerList,
    onPlayerConnected,
    onPlayerDisconnected,
    onGameStarted,
    onStarsUpdated,
    onGameOver,
    setPlayersFromRoom,
  }
})
