import type { Player } from '@/types/player'
import { ref } from 'vue'

const players = ref<Player[]>([
  { id: 1, name: 'You',    avatar: '🧑', score: 0, room_id: 1 },
  { id: 2, name: 'Heron',  avatar: '🪶', score: 3, room_id: 1 },
  { id: 3, name: 'Turtle', avatar: '🐢', score: 1, room_id: 1 },
  { id: 4, name: 'Otter',  avatar: '🦦', score: 2, room_id: 1 },
  { id: 5, name: 'Owl',    avatar: '🦉', score: 4, room_id: 1 },
  { id: 6, name: 'Frog',   avatar: '🐸', score: 1, room_id: 1 },
])

export function get_players() {
  return players
}

export function get_player_by_id(id: number): Player {
  const player = players.value.find((p) => p.id === id)
  if (!player) throw new Error(`Player with id ${id} not found`)
  return player
}
