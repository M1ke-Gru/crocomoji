import type { Game } from '@/types/game'
import { GamePhase } from '@/enums/GamePhase'
import { computed, ref, type Ref } from 'vue'

const games = ref<Game[]>([
  {
    id: 1,
    room_id: 1,
    round: 3,
    narrator_id: 5,
    phase: GamePhase.Playing,
    hidden_sentence: 'The old lighthouse keeper danced with his shadow under the full moon',
    emoji_clue: '🏠🔦👴💃🕺👤🌕',
    chosen_guess_id: null,
  },
])

export function get_current_game(room_id: number): Ref<Game> {
  return computed(() => {
    const game = games.value.find((g) => g.room_id === room_id)
    if (!game) throw new Error(`No active game for room ${room_id}`)
    return game
  }) as Ref<Game>
}

export function update_game(id: number, patch: Partial<Game>): void {
  const game = games.value.find((g) => g.id === id)
  if (!game) throw new Error(`Game with id ${id} not found`)
  Object.assign(game, patch)
}
