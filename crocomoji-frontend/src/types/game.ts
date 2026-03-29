import type { GamePhase } from '@/enums/GamePhase'

export interface Game {
  id: number
  room_id: number
  round: number
  narrator_id: number
  phase: GamePhase
  hidden_sentence: string
  emoji_clue: string
  chosen_guess_id: number | null
}
