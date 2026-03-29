import type { Guess } from '@/types/guess'

export interface RichGuess extends Guess {
  playerName: string
  playerAvatar: string
}
