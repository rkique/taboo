<script>
  import { roomId, players, isLeader, playerName, startGame, renameSelf, addBots, errorMsg } from "../stores/gameStore.js";

  let editing = $state(false);
  let nameInput = $state("");
  let botCount = $state(0);
  let showOptions = $state(false);

  // Filter state — all checked by default
  let diffEasy = $state(true);
  let diffMedium = $state(true);
  let diffHard = $state(false);
  let catPeople = $state(true);
  let catPlaces = $state(true);
  let catThings = $state(true);

  function startEditing() {
    nameInput = $playerName || "";
    editing = true;
  }

  function saveName() {
    const trimmed = nameInput.trim();
    if (trimmed && trimmed !== $playerName) {
      renameSelf($roomId, trimmed);
    }
    editing = false;
  }

  function handleKeydown(e) {
    if (e.key === "Enter") saveName();
    if (e.key === "Escape") editing = false;
  }

  function getFilters() {
    const difficulties = [];
    if (diffEasy) difficulties.push("easy");
    if (diffMedium) difficulties.push("medium");
    if (diffHard) difficulties.push("hard");

    const categories = [];
    if (catPeople) categories.push("person");
    if (catPlaces) categories.push("place");
    if (catThings) categories.push("thing");

    return { difficulties, categories };
  }
</script>

<div class="lobby">
  <div class="content">
    <h2>Lobby</h2>
    <div class="code-display">
      <span class="label">Room Code</span>
      <span class="code">{$roomId}</span>
    </div>

<!-- 
    <div class="player-count">
      {$players.length} player{$players.length !== 1 ? "s" : ""} connected
    </div> -->

    <ul class="player-list">
      {#each $players as p}
        <li>{p.name}</li>
      {/each}
    </ul>

    <div class="your-name">
      {#if editing}
        <input
          type="text"
          bind:value={nameInput}
          onkeydown={handleKeydown}
          onblur={saveName}
          maxlength="30"
          autofocus
        />
      {:else}
        <span class="name-display" onclick={startEditing} title="Click to edit">
          {$playerName}
        </span>
        <button class="edit-btn" onclick={startEditing}>edit</button>
      {/if}
    </div>

    {#if $isLeader}
      <div class="bot-selector">
        <label>Bots:</label>
        {#each [0, 1, 2, 3, 4, 5] as n}
          <button
            class="bot-btn"
            class:active={botCount === n}
            onclick={() => { botCount = n; addBots($roomId, n); }}
          >{n}</button>
        {/each}
      </div>

      <button class="btn options-toggle" onclick={() => showOptions = !showOptions}>
        {showOptions ? "Hide Options" : "Options"}
      </button>

      {#if showOptions}
        <div class="options-panel">
          <div class="filter-group">
            <span class="filter-label">Difficulty</span>
            <div class="filter-row">
              <label class="chip" class:checked={diffEasy}>
                <input type="checkbox" bind:checked={diffEasy} /> Easy
              </label>
              <label class="chip" class:checked={diffMedium}>
                <input type="checkbox" bind:checked={diffMedium} /> Medium
              </label>
              <label class="chip" class:checked={diffHard}>
                <input type="checkbox" bind:checked={diffHard} /> Hard
              </label>
            </div>
          </div>
          <div class="filter-group">
            <span class="filter-label">Category</span>
            <div class="filter-row">
              <label class="chip" class:checked={catPeople}>
                <input type="checkbox" bind:checked={catPeople} /> People
              </label>
              <label class="chip" class:checked={catPlaces}>
                <input type="checkbox" bind:checked={catPlaces} /> Places
              </label>
              <label class="chip" class:checked={catThings}>
                <input type="checkbox" bind:checked={catThings} /> Things
              </label>
            </div>
          </div>
        </div>
      {/if}

      <button class="btn primary" onclick={() => startGame($roomId, getFilters())}>
        Start Game
      </button>
    {:else}
      <p class="waiting-msg">Waiting for the leader to start...</p>
    {/if}

    {#if $errorMsg}
      <p class="error">{$errorMsg}</p>
    {/if}
  </div>
</div>

<style>
  .lobby {
    position: relative;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    min-height: 100vh;
    padding: 1.5rem;
    background: url("/images/eniko_eged_2.jpg") center center / cover no-repeat;
    color: #ffffff;
    overflow: hidden;
  }

  .lobby::before {
    content: "";
    position: absolute;
    inset: 0;
    background: radial-gradient(ellipse 80% 90% at center, rgba(0, 0, 0, 0.9) 0%, rgba(0, 0, 0, 0.3) 100%);
    z-index: 0;
  }

  .content {
    position: relative;
    z-index: 1;
    display: flex;
    flex-direction: column;
    align-items: center;
    width: min(92vw, 360px);
    gap: 1.25rem;
  }

  h2 {
    font-size: 2.8rem;
    margin: 0;
    letter-spacing: 0.05em;
  }

  .code-display {
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 0.25rem;
  }

  .label {
    font-size: 0.8rem;
    color: rgba(255, 255, 255, 0.6);
    text-transform: uppercase;
    letter-spacing: 0.1em;
  }

  .code {
    font-family: "Archivo Black", sans-serif;
    font-size: 2.5rem;
    font-weight: 700;
    letter-spacing: 0.2em;
  }

  .your-name {
    display: flex;
    align-items: center;
    gap: 0.5rem;
  }

  .name-display {
    font-size: 1.1rem;
    font-weight: 600;
    cursor: pointer;
    border-bottom: 1px dashed rgba(255, 255, 255, 0.5);
  }

  .edit-btn {
    background: none;
    border: none;
    color: rgba(255, 255, 255, 0.5);
    font-size: 0.75rem;
    cursor: pointer;
    text-decoration: underline;
  }

  .your-name input {
    font-size: 1.1rem;
    font-weight: 600;
    padding: 0.25rem 0.5rem;
    border: 1px solid #ffffff;
    border-radius: 6px;
    text-align: center;
    width: 200px;
    background: transparent;
    color: #ffffff;
  }

  .your-name input:focus {
    outline: none;
  }

  .player-count {
    color: rgba(255, 255, 255, 0.6);
    font-size: 0.95rem;
  }

  .player-list {
    list-style: none;
    padding: 0;
    margin: 0;
    display: flex;
    flex-wrap: wrap;
    gap: 0.5rem;
    justify-content: center;
  }

  .player-list li {
    background: rgba(255, 255, 255, 0.15);
    padding: 0.35rem 0.75rem;
    border-radius: 6px;
    font-size: 0.85rem;
    color: #ffffff;
  }

  .btn {
    width: 100%;
    padding: 0.75rem 1.5rem;
    border: 1px solid #ffffff;
    border-radius: 8px;
    font-size: 1rem;
    cursor: pointer;
    transition: opacity 0.15s ease, transform 0.15s ease;
  }

  .btn:hover { opacity: 0.85; }
  .btn:active { transform: scale(0.95); }

  .primary {
    background: #ffffff;
    color: #000000;
    font-weight: 600;
  }

  .waiting-msg {
    color: rgba(255, 255, 255, 0.6);
    font-style: italic;
  }

  .bot-selector {
    display: flex;
    align-items: center;
    gap: 0.4rem;
  }

  .bot-selector label {
    font-size: 0.9rem;
    color: rgba(255, 255, 255, 0.6);
    margin-right: 0.25rem;
  }

  .bot-btn {
    width: 2rem;
    height: 2rem;
    border: 1px solid rgba(255, 255, 255, 0.3);
    border-radius: 6px;
    background: transparent;
    color: #ffffff;
    cursor: pointer;
    font-size: 0.9rem;
    transition: all 0.15s, transform 0.15s ease;
  }

  .bot-btn:active { transform: scale(0.9); }

  .bot-btn.active {
    background: #ffffff;
    color: #000000;
    border-color: #ffffff;
  }

  .error {
    color: #ffe7e2;
    font-size: 0.9rem;
  }

  .options-toggle {
    background: transparent;
    color: #ffffff;
    font-size: 0.9rem;
  }

  .options-panel {
    width: 100%;
    display: flex;
    flex-direction: column;
    gap: 0.75rem;
    padding: 0.75rem;
    border: 1px solid rgba(255, 255, 255, 0.2);
    border-radius: 8px;
    background: rgba(0, 0, 0, 0.3);
  }

  .filter-group {
    display: flex;
    flex-direction: column;
    gap: 0.35rem;
  }

  .filter-label {
    font-size: 0.75rem;
    color: rgba(255, 255, 255, 0.7);
    font-family: 'Instrument Sans', sans-serif;
    text-transform: lowercase;
    letter-spacing: 0.08em;
  }

  .filter-row {
    display: flex;
    gap: 0.4rem;
    flex-wrap: wrap;
  }

  .chip {
    display: flex;
    align-items: center;
    gap: 0.3rem;
    padding: 0.3rem 0.65rem;
    font-family: "Instrument Sans", sans-serif;
    border: 1px solid rgba(255, 255, 255, 0.25);
    border-radius: 20px;
    font-size: 0.85rem;
    color: rgba(255, 255, 255, 0.6);
    cursor: pointer;
    transition: all 0.15s;
    user-select: none;
  }

  .chip input[type="checkbox"] {
    display: none;
  }

  .chip.checked {
    background: rgba(255, 255, 255, 0.15);
    border-color: #ffffff;
    color: #ffffff;
  }
</style>
