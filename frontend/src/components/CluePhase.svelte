<script>
  import { allCards, roomId, cluesDone, submitClue, errorMsg, cluePhaseTime } from "../stores/gameStore.js";
  import { onMount, onDestroy, tick } from "svelte";

  let clueText = $state("");
  let currentCard = $state(null);
  let usedIndices = $state(new Set());
  let cardWobble = $state(false);
  let inputEl = $state(null);
  let focusCounter = $state(0);

  // Tap-to-start gate
  let started = $state(false);

  // 60s overall timer
  let totalTime = $state(60);
  let timeLeft = $state(60);
  let timerInterval = null;
  let phaseOver = $state(false);

  // Mobile keyboard-aware height (only used on small screens)
  let isMobile = $state(false);
  let vpHeight = $state(typeof window !== "undefined" ? window.innerHeight : 800);
  const ACCESSORY_BAR_OVERLAP = 55;

  function onViewportResize() {
    const vv = window.visualViewport;
    if (vv) {
      const keyboardOpen = vv.height < window.innerHeight * 0.85;
      vpHeight = keyboardOpen ? vv.height + ACCESSORY_BAR_OVERLAP : vv.height;
      window.scrollTo(0, 0);
      document.documentElement.scrollTop = 0;
      document.body.scrollTop = 0;
    }
  }

  function preventScroll(e) {
    e.preventDefault();
  }

  // Focus input whenever it becomes available or focusCounter changes
  $effect(() => {
    const _el = inputEl;
    const _count = focusCounter;
    if (_el) {
      tick().then(() => {
        _el.focus({ preventScroll: isMobile });
        if (isMobile) {
          window.scrollTo(0, 0);
          document.documentElement.scrollTop = 0;
          document.body.scrollTop = 0;
        }
      });
    }
  });

  async function pickNextCard() {
    const pool = $allCards;
    if (!pool.length) return;
    let available = [];
    for (let i = 0; i < pool.length; i++) {
      if (!usedIndices.has(i)) available.push(i);
    }
    if (available.length === 0) {
      usedIndices = new Set();
      available = pool.map((_, i) => i);
    }
    const idx = available[Math.floor(Math.random() * available.length)];
    usedIndices = new Set([...usedIndices, idx]);
    currentCard = pool[idx];
    clueText = "";
    cardWobble = false;
    await tick();
    cardWobble = true;
    focusCounter++;
  }

  function startPhase() {
    started = true;
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
  }

  onMount(() => {
    isMobile = window.matchMedia("(max-width: 768px)").matches;
    pickNextCard();

    if (isMobile) {
      if (window.visualViewport) {
        window.visualViewport.addEventListener("resize", onViewportResize);
        window.visualViewport.addEventListener("scroll", onViewportResize);
      }
      document.body.style.overflow = "hidden";
      document.body.style.position = "fixed";
      document.body.style.width = "100%";
      document.body.style.height = "100%";
      document.addEventListener("touchmove", preventScroll, { passive: false });
    }
  });

  onDestroy(() => {
    if (timerInterval) clearInterval(timerInterval);
    if (isMobile) {
      if (window.visualViewport) {
        window.visualViewport.removeEventListener("resize", onViewportResize);
        window.visualViewport.removeEventListener("scroll", onViewportResize);
      }
      document.body.style.overflow = "";
      document.body.style.position = "";
      document.body.style.width = "";
      document.body.style.height = "";
      document.removeEventListener("touchmove", preventScroll);
    }
  });

  let timerFraction = $derived(totalTime > 0 ? timeLeft / totalTime : 0);
  let timerUrgent = $derived(timeLeft <= 15);

  function handleSubmit() {
    if (clueText.trim() && currentCard && !phaseOver) {
      submitClue($roomId, currentCard.word, currentCard.taboo_words.slice(0, 3), clueText.trim());
      pickNextCard();
    }
  }

  function handleSkip() {
    if (!phaseOver) {
      pickNextCard();
    }
  }

  function handleKeydown(e) {
    if (e.key === "Enter") handleSubmit();
  }
</script>

<!-- Main bind for phase -->
<div class="clue-phase" style={isMobile ? `height: ${vpHeight}px;` : ''}>
  {#if !started}
    <div class="tap-gate" onclick={startPhase}>
      <div class="tap-content">
        <div class="tap-text">
        <h2>Guess Phase</h2>
        <p class="tap-hint">Tap to start writing clues</p>
        </div>
        <div class="tap-circle">
          <span>GO</span>
        </div>
      </div>
    </div>
  {:else if phaseOver}
    <div class="waiting">
      <div class="spinner"></div>
      <p class="status">Time's up! Waiting for others...</p>
      <p class="progress">{$cluesDone} clue{$cluesDone !== 1 ? 's' : ''} submitted</p>
    </div>
  {:else if currentCard}
    <div class="timer-bar" class:urgent={timerUrgent} style="transform: scaleX({timerFraction});"></div>

    <div class="card" class:card-enter={cardWobble}>
      <div class="target-word">{currentCard.word}</div>
      <div class="taboo-label">
        <span class="scroll-line"></span>
        <span class="taboo-text">Taboo</span>
        <span class="scroll-line"></span>
      </div>
      <ul class="taboo-words">
        {#each currentCard.taboo_words.slice(0, 3) as word}
          <li>{word}</li>
        {/each}
      </ul>
      <button class="skip-link" onmousedown={(e) => e.preventDefault()} onclick={handleSkip}>skip</button>
    </div>

    <div class="bottom-row">
      <p class="progress-label">{$cluesDone} clue{$cluesDone !== 1 ? 's' : ''} written</p>
    </div>

    <div class="input-row">
      <input
        type="text"
        bind:this={inputEl}
        bind:value={clueText}
        placeholder="Type your clue..."
        maxlength="200"
        inputmode="text"
        enterkeyhint="send"
        autocomplete="on"
        autocorrect="on"
        autocapitalize="on"
        spellcheck="false"
        onkeydown={handleKeydown}
        disabled={phaseOver}
      />
    </div>
  {/if}

  {#if $errorMsg}
    <p class="error">{$errorMsg}</p>
  {/if}
</div>

<style>
  /* Mobile: fixed, viewport-height layout */
  .clue-phase {
    position: fixed;
    top: 0;
    left: 0;
    width: 100%;
    display: flex;
    flex-direction: column;
    align-items: center;
    background: radial-gradient(ellipse 80% 90% at center, rgba(100, 10, 10, 0.95) 0%, rgba(40, 0, 0, 1) 100%);
    color: #ffffff;
    padding: 0 0.5rem;
    box-sizing: border-box;
    overflow: hidden;
    touch-action: none;
  }

  /* Desktop: centered flex layout */
  @media (min-width: 769px) {
    .clue-phase {
      position: static;
      justify-content: center;
      min-height: 100vh;
      padding: 1rem 0.5rem;
      overflow: visible;
      touch-action: auto;
    }
  }

  /* Timer bar */
  .timer-bar {
    width: 100%;
    height: 4px;
    background: #ffffff;
    transform-origin: left;
    flex-shrink: 0;
    transition: background 0.3s;
  }

  .timer-bar.urgent {
    background: #c0392b;
  }

  /* Card */
  .card {
    position: relative;
    background: rgba(255, 255, 255, 0.08);
    border: 1px solid rgba(255, 255, 255, 0.2);
    border-radius: 12px;
    padding: 1rem 1.25rem;
    width: min(280px, 85vw);
    text-align: center;
    margin-top: 0.75rem;
  }

  .card.card-enter {
    animation: card-wobble 0.4s ease;
  }

  @keyframes card-wobble {
    0% { transform: scale(0.95) rotate(-1deg); opacity: 0.7; }
    40% { transform: scale(1.02) rotate(0.5deg); }
    70% { transform: scale(0.99) rotate(-0.3deg); }
    100% { transform: scale(1) rotate(0); opacity: 1; }
  }

  .target-word {
    font-family: "Archivo Black", sans-serif;
    font-size: 1.4rem;
    font-weight: 400;
    margin-bottom: 0.5rem;
    color: #ffffff;
  }

  .taboo-label {
    display: flex;
    align-items: center;
    gap: 0.6rem;
    margin-bottom: 0.4rem;
    width: 100%;
    justify-content: center;
  }

  .taboo-text {
    font-family: "Times New Roman", "Georgia", serif;
    font-size: 0.7rem;
    font-weight: 400;
    font-style: italic;
    letter-spacing: 0.08em;
    color: rgba(255, 255, 255, 0.4);
    white-space: nowrap;
  }

  .scroll-line {
    flex: 1;
    max-width: 50px;
    height: 1px;
    background: rgba(255, 255, 255, 0.15);
  }

  .taboo-words {
    list-style: none;
    padding: 0;
    margin: 0;
    display: flex;
    flex-direction: column;
    gap: 0.3rem;
  }

  .taboo-words li {
    color: #ffffff;
    font-family: 'Archivo Black', sans-serif;
    font-size: 1.5rem;
    font-variant: small-caps;
    font-weight: 600;
  }

  /* Bottom row: progress */
  .bottom-row {
    display: flex;
    align-items: center;
    justify-content: space-between;
    width: min(280px, 85vw);
    margin-top: 0.5rem;
  }

  .progress-label {
    color: rgba(255, 255, 255, 0.4);
    font-size: 0.75rem;
    margin: 0;
    letter-spacing: 0.04em;
  }

  .skip-link {
    position: absolute;
    bottom: 0.5rem;
    right: 0.75rem;
    background: none;
    border: none;
    color: rgba(255, 255, 255, 0.45);
    font-size: 0.9rem;
    cursor: pointer;
    text-decoration: underline;
    text-underline-offset: 2px;
    padding: 0.25rem 0;
    transition: color 0.12s;
  }

  .skip-link:hover { color: rgba(255, 255, 255, 0.7); }
  .skip-link:active { color: #ffffff; }

  /* Input */
  .input-row {
    display: flex;
    width: min(280px, 85vw);
    border: 1px solid rgba(255, 255, 255, 0.3);
    border-radius: 8px;
    overflow: hidden;
    background: rgba(255, 255, 255, 0.08);
    margin-top: 0.4rem;
  }

  .input-row input {
    flex: 1;
    padding: 0.55rem 0.75rem;
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

  /* Waiting / phase over */
  .waiting {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    flex: 1;
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

  /* Tap-to-start gate */
  .tap-gate {
    display: flex;
    align-items: center;
    justify-content: center;
    flex: 1;
    width: 100%;
    cursor: pointer;
    -webkit-tap-highlight-color: transparent;
  }

  .tap-content {
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 2rem;
  }

  .tap-text {
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 0.25rem;
  }

  .tap-content h2 {
    font-family: "Archivo Black", sans-serif;
    font-weight: 300;
    font-size: 2.2rem;
    margin: 0;
    letter-spacing: 0.1em;
  }

  .tap-hint {
    font-family: 'Instrument Sans', sans-serif;
    color: rgba(255, 255, 255, 0.5);
    font-size: 0.9rem;
    margin: 0;
  }

  .tap-circle {
    width: 80px;
    height: 80px;
    border: 2px solid rgba(255, 255, 255, 0.4);
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    animation: pulse-ring 1.5s ease-in-out infinite;
  }

  .tap-circle span {
    font-family: "Archivo Black", sans-serif;
    font-size: 1.4rem;
    font-weight: 700;
    letter-spacing: 0.1em;
  }

  @keyframes pulse-ring {
    0%, 100% { transform: scale(1); border-color: rgba(255, 255, 255, 0.4); }
    50% { transform: scale(1.08); border-color: rgba(255, 255, 255, 0.7); }
  }

  .tap-time {
    color: rgba(255, 255, 255, 0.35);
    font-size: 0.8rem;
    margin: 0;
  }
</style>
