<script>
  import { screen, setupStaticCluePhase } from "./stores/gameStore.js";
  import { onMount } from "svelte";
  import Landing from "./components/Landing.svelte";
  import Lobby from "./components/Lobby.svelte";
  import CluePhase from "./components/CluePhase.svelte";
  import GuessPhase from "./components/GuessPhase.svelte";

  onMount(() => {
    const params = new URLSearchParams(window.location.search);
    const staticMode = params.get("static");
    if (staticMode === "clue") setupStaticCluePhase();
  });
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
    font-family: "Instrument Serif", "Georgia", serif;
    background: #faf8f5;
  }

  :global(*) {
    box-sizing: border-box;
  }

  :global(h1, h2, h3) {
    font-family: "Archivo Black", sans-serif;
  }

  :global(button) {
    font-family: "Instrument Sans", sans-serif;
  }
</style>
