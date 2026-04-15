<script>
  import { cards, roomId, currentCardIndex, cluesDone, clueProgress, submitClue, errorMsg } from "../stores/gameStore.js";

  let clueText = $state("");
  let allCluesDone = $derived($cluesDone >= $cards.length && $cards.length > 0);
  let currentEntry = $derived($cards[$currentCardIndex]);
  let currentCard = $derived(currentEntry?.card);
  let timeLeft = $state(60);
  let submittedCurrent = $state(false);
  let timerExpired = $state(false);

  // Only reset submitted flag when card changes (timer persists across cards)
  $effect(() => {
    $currentCardIndex; // dependency
    submittedCurrent = false;
  });

  // Timer effect - runs once for entire phase
  $effect(() => {
    if (timeLeft > 0 && !timerExpired && !allCluesDone) {
      const interval = setInterval(() => {
        timeLeft--;
        if (timeLeft === 0) {
          timerExpired = true;
          // Auto-submit [EMPTY] for current card if not yet submitted
          if (!submittedCurrent && currentEntry) {
            submittedCurrent = true;
            submitClue($roomId, currentEntry.card_id, "[EMPTY]");
          }
        }
      }, 1000);
      return () => clearInterval(interval);
    }
  });

  //submit a clue on card button.
  function handleSubmit() {
    if (clueText.trim() && currentEntry && !submittedCurrent) {
      submittedCurrent = true;
      submitClue($roomId, currentEntry.card_id, clueText.trim());
      clueText = "";
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

<div class="clue-phase">
  {#if allCluesDone}
    <div class="waiting">
      <div class="spinner"></div>
      <p class="status">Waiting for other players...</p>
      <p class="progress">{$clueProgress.players_done} / {$clueProgress.total} players done</p>
    </div>
  {:else if currentCard}
    <div class="timer" class:expired={timerExpired}>Time left: {timeLeft}s</div>

    <p class="progress-label">Card {$currentCardIndex + 1} of {$cards.length}</p>

    <div class="card">
      <div class="target-word">{currentCard.word}</div>
      <div class="taboo-label">TABOO</div>
      <ul class="taboo-words">
        {#each currentCard.taboo_words as word}
          <li>{word}</li>
        {/each}
      </ul>
    </div>

    <div class="response-area">
      <p class="prompt">Describe this word without using the taboo words:</p>
      <input
        type="text"
        bind:value={clueText}
        placeholder="Type your clue..."
        maxlength="200"
        onkeydown={handleKeydown}
        disabled={submittedCurrent || timerExpired}
      />
      <button class="btn primary" onclick={handleSubmit} disabled={!clueText.trim() || submittedCurrent || timerExpired}>
        Submit Clue
      </button>
    </div>
  {/if}

  {#if $errorMsg}
    <p class="error">{$errorMsg}</p>
  {/if}
</div>

<style>
  .clue-phase {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    min-height: 100vh;
    font-family: system-ui, sans-serif;
    background: #faf8f5;
    color: #2c2c2c;
    gap: 1.5rem;
  }

  .progress-label {
    color: #888;
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
    background: #fff;
    border: 2px solid #2c2c2c;
    border-radius: 12px;
    padding: 2rem;
    width: 280px;
    text-align: center;
  }

  .target-word {
    font-size: 2rem;
    font-weight: 700;
    margin-bottom: 1rem;
  }

  .taboo-label {
    font-size: 0.7rem;
    font-weight: 700;
    letter-spacing: 0.15em;
    color: #c0392b;
    text-transform: uppercase;
    margin-bottom: 0.5rem;
    border-bottom: 1px solid #eee;
    padding-bottom: 0.5rem;
  }

  .taboo-words {
    list-style: none;
    padding: 0;
    margin: 0;
    display: flex;
    flex-direction: column;
    gap: 0.35rem;
  }

  .taboo-words li {
    color: #c0392b;
    font-size: 1.1rem;
  }

  .response-area {
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 0.75rem;
    width: 320px;
  }

  .prompt {
    color: #666;
    font-size: 0.9rem;
    text-align: center;
    margin: 0;
  }

  input {
    width: 100%;
    padding: 0.75rem;
    border: 1px solid #ddd;
    border-radius: 8px;
    font-size: 1rem;
    box-sizing: border-box;
  }

  input:focus {
    outline: none;
    border-color: #2c2c2c;
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

  .waiting {
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 0.75rem;
  }

  .status {
    color: #666;
    font-size: 1.1rem;
    margin: 0;
  }

  .progress {
    color: #aaa;
    font-size: 0.85rem;
    margin: 0;
  }

  .spinner {
    width: 40px;
    height: 40px;
    border: 3px solid #e8e4df;
    border-top-color: #2c2c2c;
    border-radius: 50%;
    animation: spin 0.8s linear infinite;
  }

  @keyframes spin {
    to { transform: rotate(360deg); }
  }

  .error {
    color: #c0392b;
    font-size: 0.9rem;
  }
</style>
