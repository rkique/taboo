<script>
  import { roomId, players, isLeader, playerName, startGame, renameSelf, addBots, errorMsg } from "../stores/gameStore.js";

  let editing = $state(false);
  let nameInput = $state("");
  let botCount = $state(0);

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
</script>

<div class="lobby">
  <h2>Lobby</h2>
  <div class="code-display">
    <span class="label">Room Code</span>
    <span class="code">{$roomId}</span>
  </div>

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

  <div class="player-count">
    {$players.length} player{$players.length !== 1 ? "s" : ""} connected
  </div>

  <ul class="player-list">
    {#each $players as p}
      <li>{p.name}</li>
    {/each}
  </ul>

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
    <button class="btn primary" onclick={() => startGame($roomId)}>
      Start Game
    </button>
  {:else}
    <p class="waiting-msg">Waiting for the leader to start...</p>
  {/if}

  {#if $errorMsg}
    <p class="error">{$errorMsg}</p>
  {/if}
</div>

<style>
  .lobby {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    min-height: 100vh;
    font-family: system-ui, sans-serif;
    background: #faf8f5;
    color: #2c2c2c;
    gap: 1.25rem;
  }

  h2 {
    font-size: 2rem;
    margin: 0;
  }

  .code-display {
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 0.25rem;
  }

  .label {
    font-size: 0.8rem;
    color: #888;
    text-transform: uppercase;
    letter-spacing: 0.1em;
  }

  .code {
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
    border-bottom: 1px dashed #aaa;
  }

  .edit-btn {
    background: none;
    border: none;
    color: #aaa;
    font-size: 0.75rem;
    cursor: pointer;
    text-decoration: underline;
  }

  .your-name input {
    font-size: 1.1rem;
    font-weight: 600;
    padding: 0.25rem 0.5rem;
    border: 1px solid #2c2c2c;
    border-radius: 6px;
    text-align: center;
    width: 200px;
  }

  .your-name input:focus {
    outline: none;
  }

  .player-count {
    color: #666;
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
    background: #e8e4df;
    padding: 0.35rem 0.75rem;
    border-radius: 6px;
    font-size: 0.85rem;
  }

  .btn {
    padding: 0.75rem 2rem;
    border: none;
    border-radius: 8px;
    font-size: 1rem;
    cursor: pointer;
    transition: opacity 0.15s;
  }

  .btn:hover { opacity: 0.85; }

  .primary {
    background: #2c2c2c;
    color: #fff;
  }

  .waiting-msg {
    color: #888;
    font-style: italic;
  }

  .bot-selector {
    display: flex;
    align-items: center;
    gap: 0.4rem;
  }

  .bot-selector label {
    font-size: 0.9rem;
    color: #666;
    margin-right: 0.25rem;
  }

  .bot-btn {
    width: 2rem;
    height: 2rem;
    border: 1px solid #ccc;
    border-radius: 6px;
    background: #fff;
    cursor: pointer;
    font-size: 0.9rem;
    transition: all 0.15s;
  }

  .bot-btn.active {
    background: #2c2c2c;
    color: #fff;
    border-color: #2c2c2c;
  }

  .error {
    color: #c0392b;
    font-size: 0.9rem;
  }
</style>
