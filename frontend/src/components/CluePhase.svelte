<script>
  import { allCards, roomId, cluesDone, submitClue, errorMsg, cluePhaseTime } from "../stores/gameStore.js";
  import { onMount, onDestroy } from "svelte";

  let clueText = $state("");
  let currentCard = $state(null);
  let usedIndices = $state(new Set());

  // 60s overall timer
  let totalTime = $state(60);
  let timeLeft = $state(60);
  let timerInterval = null;
  let phaseOver = $state(false);

  function pickNextCard() {
    const pool = $allCards;
    if (!pool.length) return;
    // Pick a random card we haven't used yet
    let available = [];
    for (let i = 0; i < pool.length; i++) {
      if (!usedIndices.has(i)) available.push(i);
    }
    if (available.length === 0) {
      // Reset if we exhaust the pool
      usedIndices = new Set();
      available = pool.map((_, i) => i);
    }
    const idx = available[Math.floor(Math.random() * available.length)];
    usedIndices = new Set([...usedIndices, idx]);
    currentCard = pool[idx];
    clueText = "";
  }

  onMount(() => {
    totalTime = $cluePhaseTime;
    timeLeft = totalTime;
    pickNextCard();
    timerInterval = setInterval(() => {
      timeLeft = Math.max(0, timeLeft - 0.05);
      if (timeLeft <= 0) {
        phaseOver = true;
        clearInterval(timerInterval);
      }
    }, 50);
  });

  onDestroy(() => {
    if (timerInterval) clearInterval(timerInterval);
  });

  let timerFraction = $derived(totalTime > 0 ? timeLeft / totalTime : 0);

  function handleSubmit() {
    if (clueText.trim() && currentCard && !phaseOver) {
      submitClue($roomId, currentCard.word, currentCard.taboo_words, clueText.trim());
      pickNextCard();
    }
  }

  function handleSkip() {
    if (!phaseOver) {
      pickNextCard();
    }
  }

  // Auto-submit [EMPTY] for remaining cards when timer expires
  function submitEmptyForCurrentCard() {
    if (!submittedCurrent && timerExpired && currentEntry) {
      submittedCurrent = true;
      submitClue($roomId, currentEntry.card_id, "[EMPTY]");
    }
  }

  $effect(() => {
    if (timerExpired && !submittedCurrent && currentEntry) {
      submitEmptyForCurrentCard();
    }
  });

  function handleKeydown(e) {
    if (e.key === "Enter") handleSubmit();
  }
</script>

<div class="timer-bar" style="transform: scaleX({timerFraction});"></div>
<div class="clue-phase">
  {#if phaseOver}
    <div class="waiting">
      <div class="spinner"></div>
      <p class="status">Time's up! Waiting for others...</p>
      <p class="progress">{$cluesDone} clue{$cluesDone !== 1 ? 's' : ''} submitted</p>
    </div>
  {:else if currentCard}
    <p class="progress-label">{$cluesDone} clue{$cluesDone !== 1 ? 's' : ''} written</p>

    <div class="card">
      <div class="target-word">{currentCard.word}</div>
      <div class="taboo-label">TABOO</div>
      <ul class="taboo-words">
        {#each currentCard.taboo_words as word}
          <li>{word}</li>
        {/each}
      </ul>
    </div>

    <div class="input-row">
      <input
        type="text"
        bind:value={clueText}
        placeholder="Type your clue..."
        maxlength="200"
        onkeydown={handleKeydown}
        disabled={submittedCurrent || timerExpired}
      />
      <button class="submit-arrow" onclick={handleSubmit} disabled={!clueText.trim()} aria-label="Submit clue">
        &#8594;
      </button>
    </div>

    <button class="skip-btn" onclick={handleSkip}>Skip</button>
  {/if}

  {#if $errorMsg}
    <p class="error">{$errorMsg}</p>
  {/if}
</div>

<style>
  .timer-bar {
    position: fixed;
    top: 0;
    left: 0;
    width: 100%;
    height: 4px;
    background: #ffffff;
    transform-origin: left;
    z-index: 50;
  }

  .clue-phase {
    position: relative;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    min-height: 100vh;
    font-family: "Avenir Next", "Gill Sans", "Trebuchet MS", sans-serif;
    background: radial-gradient(ellipse 80% 90% at center, rgba(100, 10, 10, 0.95) 0%, rgba(40, 0, 0, 1) 100%);
    color: #ffffff;
    gap: 1.5rem;
    overflow: hidden;
  }

  .progress-label {
    color: rgba(255, 255, 255, 0.5);
    font-size: 0.85rem;
    margin: 0;
    letter-spacing: 0.05em;
  }

  .timer {
    font-size: 1.2rem;
    font-weight: 600;
    color: #2c2c2c;
    margin-bottom: 1rem;
  }

  .timer.expired {
    color: #c0392b;
  }

  .card {
    background: rgba(255, 255, 255, 0.08);
    border: 1px solid rgba(255, 255, 255, 0.2);
    border-radius: 12px;
    padding: 2rem;
    width: 280px;
    text-align: center;
  }

  .target-word {
    font-size: 1.5rem;
    font-weight: 700;
    margin-bottom: 1rem;
    color: #ffffff;
  }

  .taboo-label {
    font-size: 0.65rem;
    font-weight: 700;
    letter-spacing: 0.15em;
    color: rgba(255, 255, 255, 0.4);
    text-transform: uppercase;
    margin-bottom: 0.5rem;
    border-bottom: 1px solid rgba(255, 255, 255, 0.15);
    padding-bottom: 0.5rem;
  }

  .taboo-words {
    list-style: none;
    padding: 0;
    margin: 0;
    display: flex;
    flex-direction: column;
    gap: 0.4rem;
  }

  .taboo-words li {
    color: #ffffff;
    font-size: 1.3rem;
    font-variant: small-caps;
    font-weight: 600;
  }

  .input-row {
    display: flex;
    width: 280px;
    border: 1px solid rgba(255, 255, 255, 0.4);
    border-radius: 8px;
    overflow: hidden;
    background: rgba(255, 255, 255, 0.08);
  }

  .input-row input {
    flex: 1;
    padding: 0.75rem 1rem;
    border: none;
    border-radius: 0;
    font-size: 1rem;
    background: transparent;
    color: #ffffff;
    outline: none;
    box-sizing: border-box;
  }

  .input-row input::placeholder {
    color: rgba(255, 255, 255, 0.4);
  }

  .submit-arrow {
    display: flex;
    align-items: center;
    justify-content: center;
    width: 3rem;
    border: none;
    border-left: 1px solid rgba(255, 255, 255, 0.2);
    background: #ffffff;
    color: #000000;
    font-size: 1.25rem;
    cursor: pointer;
    transition: opacity 0.15s ease;
  }

  .submit-arrow:hover { opacity: 0.85; }
  .submit-arrow:disabled { opacity: 0.3; cursor: default; }

  .skip-btn {
    background: none;
    border: none;
    color: rgba(255, 255, 255, 0.4);
    font-size: 0.85rem;
    cursor: pointer;
    text-decoration: underline;
    transition: color 0.15s;
  }

  .skip-btn:hover { color: rgba(255, 255, 255, 0.7); }

  .waiting {
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 0.75rem;
  }

  .status {
    color: rgba(255, 255, 255, 0.7);
    font-size: 1.1rem;
    margin: 0;
  }

  .progress {
    color: rgba(255, 255, 255, 0.4);
    font-size: 0.85rem;
    margin: 0;
  }

  .spinner {
    width: 40px;
    height: 40px;
    border: 3px solid rgba(255, 255, 255, 0.15);
    border-top-color: #ffffff;
    border-radius: 50%;
    animation: spin 0.8s linear infinite;
  }

  @keyframes spin {
    to { transform: rotate(360deg); }
  }

  .error {
    color: #ffb8b0;
    font-size: 0.9rem;
  }
</style>
