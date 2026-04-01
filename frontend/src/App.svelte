<script>
  import { screen } from "./stores/gameStore.js";
  import Landing from "./components/Landing.svelte";
  import Lobby from "./components/Lobby.svelte";
  import CluePhase from "./components/CluePhase.svelte";
  import GuessPhase from "./components/GuessPhase.svelte";
</script>

{#if $screen === "landing"}
  <Landing />
{:else if $screen === "lobby"}
  <Lobby />
{:else if $screen === "clue"}
  <CluePhase />
{:else if $screen === "guess"}
  <GuessPhase />
{/if}

<style>
  :global(body) {
    margin: 0;
    padding: 0;
    font-family: system-ui, -apple-system, sans-serif;
    background: #faf8f5;
  }

  :global(*) {
    box-sizing: border-box;
  }
</style>
