import type { Room } from '@/types/room'
import type { Player } from '@/types/player'
import { ref } from 'vue'
import { get_players } from '@/api/player_api'

const rooms = ref<Room[]>([
  { id: 1, name: 'Room 1' },
  { id: 2, name: 'Room 2' },
])

export function get_room_by_id(id: number): Room {
  const room = rooms.value.find((r) => r.id === id)
  if (!room) throw new Error(`Room with id ${id} not found`)
  return room
}

export function get_players_in_room(room_id: number): Player[] {
  return get_players().value.filter((p) => p.room_id === room_id)
}
