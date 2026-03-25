<script setup lang="ts">
import EmojiInput from './components/EmojiInput.vue'
import StoryContent from './components/StoryContent.vue'
import ChatPanel from './components/ChatPanel.vue'
</script>

<template>
  <div
    class="flex w-screen h-screen overflow-hidden bg-swamp bg-[radial-gradient(ellipse_at_20%_80%,_rgba(42,90,58,0.15)_0%,_transparent_60%),radial-gradient(ellipse_at_80%_20%,_rgba(212,160,74,0.04)_0%,_transparent_50%)]">
    <main class="flex flex-1 flex-col min-w-0 overflow-hidden">
      <StoryContent />
      <EmojiInput />
    </main>
    <ChatPanel />
  </div>
</template>
