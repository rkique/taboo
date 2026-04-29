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
  <div class="content">
    <h1>T@b00</h1>
    <div class="how-to">
      <p> Describe words without using t@boos.</p>
      <p> Compete with others to guess them first.</p>
      </div>

    <div class="actions">
      <button class="btn primary" onclick={handleCreate}>
        Make Lobby
      </button>

      <div class="join-row">
        <input
          type="text"
          bind:value={joinCode}
          placeholder="Room Code"
          maxlength="6"
          onkeydown={handleKeydown}
        />
        <button class="arrow-btn" onclick={handleJoin} disabled={!joinCode.trim()} aria-label="Join lobby">
          &#8594;
        </button>
      </div>
    </div>

    {#if $errorMsg}
      <p class="error">{$errorMsg}</p>
    {/if}
  </div>
  <footer class="credit">By Eric Xia </footer>
</div>

<style>
  .landing {
    position: relative;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    min-height: 100vh;
    padding: 1.5rem;
    background: url("/images/eniko_eged.webp") center center / cover no-repeat;
    color: #ffffff;
    overflow: hidden;
  }

  .landing::before {
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
  }

  h1 {
    font-size: 4.5rem;
    margin: 0;
    letter-spacing: -0.02em;
    text-transform: uppercase;
  }

  .how-to {
    max-width: 360px;
    text-align: center;
    margin: 1em 1em 1em 1em;
    color: #ffffff;
    /* font-variant:small-caps; */
    font-size: 1.3em;
    font-weight: 600;
    line-height: 1.3;
  }

  .how-to p {
    margin: 0rem 0;
  }

  .how-to .tagline {
    margin-top: 0.75rem;
    text-align: center;
    font-weight: 300;
    color: #ffffff;
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
    border: 1px solid #ffffff;
    border-radius: 8px;
    font-size: 1rem;
    cursor: pointer;
    transition: opacity 0.15s ease, transform 0.15s ease;
  }

  .btn:hover { opacity: 0.85; }
  .btn:active { transform: scale(0.95); }
  .btn:disabled { opacity: 0.9; cursor: default; }
  .btn:disabled:active { transform: none; }

  .primary {
    background: rgba(0, 0, 0, 0.35);
    color: #ffffff;
  }

  .join-row {
    display: flex;
    width: 100%;
    border: 1px solid #ffffff;
    border-radius: 8px;
    overflow: hidden;
  }

  .join-row input {
    flex: 1;
    padding: 0.75rem 1rem;
    border: none;
    border-radius: 0;
    font-size: 1rem;
    text-align: center;
    text-transform: uppercase;
    letter-spacing: 2px;
    background: transparent;
    color: #ffffff;
    outline: none;
  }

  .join-row input::placeholder {
    color: #cdcdcd;
    text-transform: none;
    letter-spacing: normal;
  }

  .arrow-btn {
    display: flex;
    align-items: center;
    justify-content: center;
    width: 3rem;
    border: none;
    border-left: 1px solid rgba(255, 255, 255, 0.3);
    background: #ffffff;
    color: #000000;
    font-size: 1.25rem;
    cursor: pointer;
    transition: opacity 0.15s ease, transform 0.15s ease;
  }

  .arrow-btn:hover { opacity: 0.85; }
  .arrow-btn:active { transform: scale(0.9); }
  .arrow-btn:disabled { opacity: 0.8; cursor: default; }
  .arrow-btn:disabled:active { transform: none; }

  .error {
    color: #ffe7e2;
    margin-top: 1rem;
    font-size: 0.9rem;
  }

  .credit {
    font-family: 'Instrument Sans', sans-serif;
    position: absolute;
    bottom: 1rem;
    left: 0;
    right: 0;
    text-align: center;
    font-size: 0.8rem;
    color: rgba(255, 255, 255, 0.7);
    letter-spacing: 0.05em;
    z-index: 1;
  }
</style>
