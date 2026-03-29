import { ref } from 'vue'
import { usePlayerStore } from '@/stores/player'
import { useGameStore } from '@/stores/game'
import { useRoundStore } from '@/stores/round'

const WS_BASE = import.meta.env.VITE_WS_URL ?? 'ws://localhost:8000'

let ws: WebSocket | null = null
let reconnectTimer: ReturnType<typeof setTimeout> | null = null

export const connected = ref(false)

export function connect(roomName: string, playerId: string) {
  if (ws) {
    ws.onclose = null
    ws.close()
  }
  ws = new WebSocket(`${WS_BASE}/ws/${roomName}/${playerId}`)

  ws.onopen = () => {
    connected.value = true
    if (reconnectTimer) {
      clearTimeout(reconnectTimer)
      reconnectTimer = null
    }
  }

  ws.onmessage = (event) => {
    try {
      const { action, data } = JSON.parse(event.data)
      dispatch(action, data)
    } catch {
      // ignore malformed messages
    }
  }

  ws.onclose = () => {
    connected.value = false
    scheduleReconnect()
  }

  ws.onerror = () => {
    connected.value = false
  }
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

export function send(action: string, data: Record<string, unknown> = {}): boolean {
  if (ws?.readyState === WebSocket.OPEN) {
    ws.send(JSON.stringify({ action, data }))
    return true
  }
  return false
}

export function disconnect() {
  if (reconnectTimer) {
    clearTimeout(reconnectTimer)
    reconnectTimer = null
  }
  if (ws) {
    ws.onclose = null
    ws.close()
    ws = null
  }
  connected.value = false
}

function dispatch(action: string, data: Record<string, unknown>) {
  const game = useGameStore()
  const round = useRoundStore()

  switch (action) {
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
      round.onRoundOver(data as { results: import('@/stores/round').RoundResult[]; scores: Record<string, number> })
      game.onStarsUpdated((data as { scores: Record<string, number> }).scores)
      break
    case 'game_over':
      game.onGameOver((data as { scores: Record<string, number> }).scores)
      break
    default:
      break
  }
}
