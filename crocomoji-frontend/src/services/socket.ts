import { ref } from 'vue'
import { usePlayerStore } from '@/stores/player'
import { useGameStore } from '@/stores/game'
import { useRoundStore } from '@/stores/round'
import router from '@/router'

const BASE_URL = import.meta.env.VITE_API_URL ?? 'http://localhost:8000'

let abortController: AbortController | null = null
let reconnectTimer: ReturnType<typeof setTimeout> | null = null

export const connected = ref(false)

export function connect(roomName: string, playerId: string) {
  connected.value = false
  if (reconnectTimer) {
    clearTimeout(reconnectTimer)
    reconnectTimer = null
  }
  if (abortController) {
    abortController.abort()
    abortController = null
  }
  openStream(roomName, playerId)
}

async function openStream(roomName: string, playerId: string) {
  abortController = new AbortController()
  try {
    const response = await fetch(
      `${BASE_URL}/rooms/${roomName}/events/${playerId}`,
      { signal: abortController.signal },
    )

    if (response.status === 404) {
      usePlayerStore().clear()
      router.replace('/')
      return
    }

    if (!response.ok || !response.body) {
      scheduleReconnect()
      return
    }

    connected.value = true
    const reader = response.body.getReader()
    const decoder = new TextDecoder()
    let buffer = ''

    try {
      while (true) {
        const { done, value } = await reader.read()
        if (done) break
        buffer += decoder.decode(value, { stream: true })
        const parts = buffer.split('\n\n')
        buffer = parts.pop() ?? ''
        for (const part of parts) {
          for (const line of part.split('\n')) {
            if (line.startsWith('data: ')) {
              try {
                const { action, data } = JSON.parse(line.slice(6))
                dispatch(action, data)
              } catch {
                // ignore malformed messages
              }
            }
          }
        }
      }
    } finally {
      reader.releaseLock()
    }
  } catch (err) {
    if ((err as Error).name === 'AbortError') return
  }

  connected.value = false
  scheduleReconnect()
}

function scheduleReconnect() {
  if (reconnectTimer) return
  reconnectTimer = setTimeout(() => {
    reconnectTimer = null
    const player = usePlayerStore()
    if (player.playerId && player.roomName) {
      connect(player.roomName, player.playerId)
    }
  }, 2000)
}

export async function send(action: string, data: Record<string, unknown> = {}): Promise<boolean> {
  const player = usePlayerStore()
  if (!player.playerId || !player.roomName) return false
  try {
    const res = await fetch(`${BASE_URL}/rooms/${player.roomName}/actions/${player.playerId}`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ action, data }),
    })
    return res.ok
  } catch {
    return false
  }
}

export function disconnect() {
  if (reconnectTimer) {
    clearTimeout(reconnectTimer)
    reconnectTimer = null
  }
  if (abortController) {
    abortController.abort()
    abortController = null
  }
  connected.value = false
}

function dispatch(action: string, data: Record<string, unknown>) {
  const game = useGameStore()
  const round = useRoundStore()

  switch (action) {
    case 'room_sync': {
      const sync = data as { players: { id: string; display_name: string; stars: number }[]; status: string }
      game.setPlayersFromRoom(sync.players)
      game.setStatus(sync.status as 'waiting' | 'playing' | 'finished')
      break
    }
    case 'player_connected':
      game.onPlayerConnected(data as { player_id: string; display_name: string })
      break
    case 'player_disconnected':
      game.onPlayerDisconnected(data as { player_id: string })
      break
    case 'game_started':
      game.onGameStarted(data as { num_rounds: number; joke_time_seconds: number; voting_time_seconds: number })
      break
    case 'round_started':
      round.onRoundStarted(data as {
        round_index: number
        setup: string
        phase: string
        joke_time_seconds: number
        total_rounds: number
      })
      break
    case 'player_submitted':
      round.onPlayerSubmitted(data as { player_id: string; display_name: string; submitted_count: number; total_players: number })
      break
    case 'voting_started':
      round.onVotingStarted(data as { submissions: Record<string, { display_name: string; text: string }>; voting_time_seconds: number })
      break
    case 'vote_received':
      round.onVoteReceived(data as { voter_id: string; voter_name: string; voted_count: number })
      break
    case 'round_over':
      round.onRoundOver(data as {
        results: import('@/stores/round').RoundResult[]
        scores: Record<string, number>
        actual_punchline?: string
      })
      game.onStarsUpdated((data as { scores: Record<string, number> }).scores)
      break
    case 'game_over':
      game.onGameOver((data as { scores: Record<string, number> }).scores)
      break
    case 'error':
      console.warn('Server error:', (data as { message: string }).message)
      break
    default:
      break
  }
}
