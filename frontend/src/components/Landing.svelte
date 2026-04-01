<script>
  import { createRoom, joinRoom, errorMsg } from "../stores/gameStore.js";

  let joinCode = $state("");

  function handleCreate() {
    createRoom();
  }

  function handleJoin() {
    if (joinCode.trim()) {
      joinRoom(joinCode.trim());
    }
  }

  function handleKeydown(e) {
    if (e.key === "Enter") handleJoin();
  }
</script>

<div class="landing">
  <h1>T@b00</h1>

  <img class="box-img" src="/images/box.png" alt="Taboo box" />

  <div class="how-to">
    <p><strong>1.</strong> Write clues for others to guess. The faster they get guessed, the better you do.</p>
    <p><strong>2.</strong> Guess clues from others.</p>
    <p class="tagline">The best guesser + writer wins!</p>
  </div>

  <div class="actions">
    <button class="btn primary" onclick={handleCreate}>
      Make Lobby
    </button>

    <div class="divider">or</div>

    <div class="join-group">
      <input
        type="text"
        bind:value={joinCode}
        placeholder="Enter room code"
        maxlength="6"
        onkeydown={handleKeydown}
      />
      <button class="btn secondary" onclick={handleJoin} disabled={!joinCode.trim()}>
        Join Lobby
      </button>
    </div>
  </div>

  {#if $errorMsg}
    <p class="error">{$errorMsg}</p>
  {/if}
</div>

<style>
  .landing {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    min-height: 100vh;
    font-family: system-ui, sans-serif;
    background: #faf8f5;
    color: #2c2c2c;
  }

  h1 {
    font-size: 3rem;
    margin: 0;
    letter-spacing: -0.02em;
  }

  .subtitle {
    color: #888;
    margin: 0.25rem 0 2.5rem;
    font-size: 1rem;
  }

  .box-img {

    width: 180px;
    margin: 1.5rem;
  }

  .how-to {
    max-width: 300px;
    text-align: left;
    margin-bottom: 1.5rem;
    color: #555;
    font-size: 0.9rem;
    line-height: 1.5;
  }

  .how-to p {
    margin: 0.4rem 0;
  }

  .how-to .tagline {
    margin-top: 0.75rem;
    text-align: center;
    font-weight: 600;
    color: #2c2c2c;
  }

  .actions {
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 1rem;
    width: 280px;
  }

  .btn {
    width: 100%;
    padding: 0.75rem 1.5rem;
    border: none;
    border-radius: 8px;
    font-size: 1rem;
    cursor: pointer;
    transition: opacity 0.15s;
  }

  .btn:hover { opacity: 0.85; }
  .btn:disabled { opacity: 0.4; cursor: default; }

  .primary {
    background: #2c2c2c;
    color: #fff;
  }

  .secondary {
    background: #e8e4df;
    color: #2c2c2c;
  }

  .divider {
    color: #aaa;
    font-size: 0.85rem;
  }

  .join-group {
    display: flex;
    flex-direction: column;
    gap: 0.5rem;
    width: 100%;
  }

  input {
    width: 100%;
    padding: 0.75rem;
    border: 1px solid #ddd;
    border-radius: 8px;
    font-size: 1rem;
    text-align: center;
    text-transform: uppercase;
    letter-spacing: 0.15em;
    box-sizing: border-box;
  }

  input:focus {
    outline: none;
    border-color: #2c2c2c;
  }

  .error {
    color: #c0392b;
    margin-top: 1rem;
    font-size: 0.9rem;
  }
</style>
