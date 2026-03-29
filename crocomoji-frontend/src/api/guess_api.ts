import type { Guess } from '@/types/guess'
import { ref, type Ref } from 'vue'

const guessesByGame = new Map<number, Ref<Guess[]>>()

let nextGuessId = 10

function getOrCreate(game_id: number): Ref<Guess[]> {
  if (!guessesByGame.has(game_id)) {
    guessesByGame.set(game_id, ref<Guess[]>([]))
  }
  return guessesByGame.get(game_id)!
}

// Seed game 1 with initial mock guesses
const seeded = getOrCreate(1)
seeded.value = [
  { id: 1, playerId: 2, text: 'An old man in a house with a flashlight at night?', time: '6:42 pm' },
  { id: 2, playerId: 3, text: 'Someone dancing alone in a lighthouse',              time: '6:44 pm' },
  { id: 3, playerId: 4, text: 'A lighthouse keeper dancing with his shadow',         time: '6:46 pm' },
  { id: 4, playerId: 6, text: 'Old man dancing by moonlight near a tower',           time: '6:48 pm' },
]

export function get_guesses(game_id: number): Ref<Guess[]> {
  return getOrCreate(game_id)
}

export function add_guess(game_id: number, guess: Omit<Guess, 'id'>): void {
  getOrCreate(game_id).value.push({ ...guess, id: nextGuessId++ })
}

export function clear_guesses(game_id: number): void {
  getOrCreate(game_id).value = []
}
