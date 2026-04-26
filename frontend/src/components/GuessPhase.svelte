<script>
  import { canvasCards, wordList, roomId, playersInfo, cardClaims, scores, wrongGuessCardId, submitCanvasGuess, errorMsg, finalScores, returnToLobby, guessPhaseTime, endGame } from "../stores/gameStore.js";
  import { onMount, onDestroy } from "svelte";

  let guessTexts = $state({});
  let showDropdowns = $state({});
  let gameEnded = $state(false);
  let waitingForFinalScores = $state(false);

  // Timer state
  let totalTime = $state(90);
  let timeLeft = $state(90);
  let timerInterval = null;

  onMount(() => {
    totalTime = $guessPhaseTime;
    timeLeft = totalTime;
    timerInterval = setInterval(() => {
      const nextTime = Math.max(0, timeLeft - 0.05);
      timeLeft = nextTime;
      if (nextTime <= 0 && !gameEnded) {
        gameEnded = true;
        waitingForFinalScores = true;
        endGame($roomId);
        clearInterval(timerInterval);
      }
    }, 50);
  });

  onDestroy(() => {
    if (timerInterval) clearInterval(timerInterval);
  });

  let timerFraction = $derived(totalTime > 0 ? timeLeft / totalTime : 0);
  let timerUrgent = $derived(timeLeft <= 15);

  // Only show cards that aren't mine
  let otherCards = $derived($canvasCards.filter((c) => !c.is_mine));

  function filteredFor(cardId) {
    const q = (guessTexts[cardId] || "").trim().toLowerCase();
    if (!q) return [];
    return $wordList.filter((w) => w.toLowerCase().includes(q)).slice(0, 8);
  }

  function handleSubmit(cardId) {
    const text = (guessTexts[cardId] || "").trim();
    if (text) {
      submitCanvasGuess($roomId, cardId, text);
      guessTexts[cardId] = "";
      showDropdowns[cardId] = false;
    }
  }

  function selectWord(cardId, word) {
    guessTexts[cardId] = word;
    showDropdowns[cardId] = false;
    submitCanvasGuess($roomId, cardId, word);
    guessTexts[cardId] = "";
  }

  function handleInput(cardId) {
    showDropdowns[cardId] = (guessTexts[cardId] || "").trim().length > 0;
  }

  function handleKeydown(cardId, e) {
    if (e.key === "Enter") handleSubmit(cardId);
  }

  function handleBlur(cardId) {
    setTimeout(() => { showDropdowns[cardId] = false; }, 150);
  }
</script>

<div class="timer-bar" class:urgent={timerUrgent} style="transform: scaleX({timerFraction});"></div>
<div class="guess-phase">
  <div class="scoreboard">
    {#each $playersInfo as player}
      <div class="score-chip">
        <span class="color-dot" style="background: {player.color}"></span>
        <span class="chip-name">{player.name}</span>
        <span class="chip-score">{$scores[player.sid] || 0}</span>
      </div>
    {/each}
  </div>

  <div class="card-grid">
    {#each otherCards as card}
      {@const claim = $cardClaims[card.card_id]}
      {@const isClaimed = !!claim}
      {@const isWrong = $wrongGuessCardId === card.card_id}

      <div
        class="card-tile"
        class:claimed={isClaimed}
        class:wrong-shake={isWrong}
        style={isClaimed ? `border-color: ${claim.claimer_color}; background: ${claim.claimer_color}18;` : ''}
      >
        <div class="card-owner">{card.owner_name}</div>
        <div class="card-clue">"{card.clue}"</div>

        {#if isClaimed}
          <div class="card-label claimed-label" style="color: {claim.claimer_color}">Claimed</div>
        {:else}
          <div class="inline-input">
            {#if isWrong}
              <div class="wrong-msg">Wrong!</div>
            {/if}
            <div class="autocomplete-wrapper">
              <input
                type="text"
                bind:value={guessTexts[card.card_id]}
                placeholder="guess..."
                maxlength="100"
                oninput={() => handleInput(card.card_id)}
                onkeydown={(e) => handleKeydown(card.card_id, e)}
                onblur={() => handleBlur(card.card_id)}
                onfocus={() => handleInput(card.card_id)}
              />
              {#if showDropdowns[card.card_id] && filteredFor(card.card_id).length > 0}
                <ul class="dropdown">
                  {#each filteredFor(card.card_id) as word}
                    <li>
                      <button type="button" onmousedown={() => selectWord(card.card_id, word)}>{word}</button>
                    </li>
                  {/each}
                </ul>
              {/if}
            </div>
          </div>
        {/if}
      </div>
    {/each}
  </div>

  {#if $errorMsg}
    <p class="error">{$errorMsg}</p>
  {/if}

  {#if $finalScores.length > 0 || waitingForFinalScores}
    <div class="modal-overlay">
      <div class="modal">
        <h3>Game Over</h3>

        {#if $finalScores.length > 0}
          <div class="modal-scores">
            {#each $finalScores as entry, i}
              <div class="score-row" class:winner={i === 0}>
                <span class="rank">{i + 1}</span>
                <span class="color-dot" style="background: {entry.color}"></span>
                <span class="modal-name">{entry.name}</span>
                <span class="modal-score">{entry.score}</span>
              </div>
            {/each}
          </div>
        {:else}
          <p class="loading">Waiting for final scores...</p>
        {/if}

        <button class="btn primary" onclick={() => returnToLobby($roomId)}>
          Back to Lobby
        </button>
      </div>
    </div>
  {/if}
</div>

<style>
  .timer-bar {
    position: fixed;
    top: 0;
    left: 0;
    width: 100%;
    height: 8px;
    background: #ffffff;
    transform-origin: left;
    z-index: 50;
    transition: background 0.3s;
  }

  .timer-bar.urgent {
    background: #c0392b;
  }

  .guess-phase {
    position: relative;
    display: flex;
    flex-direction: column;
    align-items: center;
    min-height: 100vh;
    font-family: system-ui, sans-serif;
    background: radial-gradient(ellipse 80% 90% at center, rgba(100, 10, 10, 0.95) 0%, rgba(0, 0, 0, 1) 100%);
    color: #2c2c2c;
    padding: 3.5rem 1rem 1.5rem;
  }


  .scoreboard {
    position: fixed;
    top: 8px;
    left: 0;
    right: 0;
    display: flex;
    gap: 0.5rem;
    flex-wrap: wrap;
    justify-content: center;
    padding: 0.5rem 1rem;
    z-index: 40;
  }

  .score-chip {
    display: flex;
    align-items: center;
    gap: 0.5rem;
    background: #fff;
    border: 1px solid #eee;
    border-radius: 20px;
    padding: 0.4rem 1rem;
  }

  .color-dot {
    width: 12px;
    height: 12px;
    border-radius: 50%;
    flex-shrink: 0;
  }

  .chip-name {
    font-size: 0.9rem;
    font-weight: 500;
  }

  .chip-score {
    font-size: 1rem;
    font-weight: 700;
  }

  .card-grid {
    display: flex;
    flex-direction: column;
    gap: 1rem;
    width: 100%;
    max-width: 500px;
  }

  .card-tile {
    background: #fff;
    border: 2px solid #2c2c2c;
    border-radius: 12px;
    padding: 1rem;
    display: flex;
    flex-direction: column;
    gap: 0.5rem;
    transition: opacity 0.2s, border-color 0.3s, background 0.3s;
  }

  .card-tile.claimed {
    opacity: 0.6;
    pointer-events: none;
  }

  .card-tile.wrong-shake {
    animation: shake 0.4s ease;
  }

  @keyframes shake {
    0%, 100% { transform: translateX(0); }
    20% { transform: translateX(-6px); }
    40% { transform: translateX(6px); }
    60% { transform: translateX(-4px); }
    80% { transform: translateX(4px); }
  }

  .card-owner {
    font-size: 0.7rem;
    color: #888;
    text-transform: uppercase;
    letter-spacing: 0.08em;
  }

  .card-clue {
    font-size: 0.95rem;
    font-style: italic;
    line-height: 1.3;
    flex: 1;
  }

  .card-label {
    font-size: 0.75rem;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.05em;
    text-align: center;
    padding: 0.3rem;
    border-radius: 6px;
  }

  .card-label.claimed-label {
    font-weight: 700;
  }

  .inline-input {
    display: flex;
    flex-direction: column;
    gap: 0.4rem;
  }

  .wrong-msg {
    color: #c0392b;
    font-size: 0.8rem;
    font-weight: 600;
    text-align: center;
  }

  .autocomplete-wrapper {
    position: relative;
    width: 100%;
  }

  input {
    width: 100%;
    padding: 0.5rem;
    border: 1px solid #ddd;
    border-radius: 6px;
    font-size: 0.85rem;
    box-sizing: border-box;
  }

  input:focus {
    outline: none;
    border-color: #2c2c2c;
  }

  .dropdown {
    position: absolute;
    top: 100%;
    left: 0;
    right: 0;
    background: #fff;
    border: 1px solid #ddd;
    border-top: none;
    border-radius: 0 0 6px 6px;
    list-style: none;
    padding: 0;
    margin: 0;
    max-height: 150px;
    overflow-y: auto;
    z-index: 20;
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
  }

  .dropdown li button {
    width: 100%;
    padding: 0.4rem 0.5rem;
    border: none;
    background: none;
    text-align: left;
    font-size: 0.8rem;
    cursor: pointer;
    color: #2c2c2c;
    transition: transform 0.1s ease;
  }

  .dropdown li button:hover {
    background: #f0ede8;
  }

  .dropdown li button:active {
    transform: scale(0.97);
  }

  .error {
    color: #c0392b;
    font-size: 0.9rem;
    margin-top: 1rem;
  }

  .modal-overlay {
    position: fixed;
    inset: 0;
    background: rgba(0, 0, 0, 0.4);
    display: flex;
    align-items: center;
    justify-content: center;
    z-index: 100;
  }

  .modal {
    background: #faf8f5;
    border-radius: 16px;
    padding: 2rem;
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 1.25rem;
    min-width: 280px;
    box-shadow: 0 8px 30px rgba(0, 0, 0, 0.15);
  }

  .modal h3 {
    margin: 0;
    font-size: 1.4rem;
  }

  .modal-scores {
    display: flex;
    flex-direction: column;
    gap: 0.4rem;
    width: 100%;
  }

  .score-row {
    display: flex;
    align-items: center;
    gap: 0.6rem;
    padding: 0.5rem 0.75rem;
    background: #fff;
    border: 1px solid #eee;
    border-radius: 8px;
  }

  .score-row.winner {
    border-color: #f39c12;
    background: #fffdf5;
  }

  .rank {
    font-weight: 700;
    color: #aaa;
    width: 1.2rem;
    text-align: center;
    font-size: 0.95rem;
  }

  .winner .rank {
    color: #f39c12;
  }

  .modal-name {
    flex: 1;
    font-size: 0.95rem;
    font-weight: 500;
  }

  .modal-score {
    font-size: 1.1rem;
    font-weight: 700;
  }

  .btn {
    padding: 0.6rem 1.5rem;
    border: none;
    border-radius: 8px;
    font-size: 0.95rem;
    cursor: pointer;
    transition: opacity 0.15s, transform 0.15s ease;
  }

  .btn:hover { opacity: 0.85; }
  .btn:active { transform: scale(0.95); }

  .primary {
    background: #2c2c2c;
    color: #fff;
  }
</style>
