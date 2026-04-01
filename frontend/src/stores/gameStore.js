import { writable } from "svelte/store";
import { io } from "socket.io-client";

// --- Stores ---
export const screen = writable("landing");
export const roomId = writable(null);
export const playerId = writable(null);
export const playerName = writable(null);
export const isLeader = writable(false);
export const players = writable([]);
export const errorMsg = writable(null);

// Clue phase
export const cards = writable([]);
export const wordList = writable([]);
export const currentCardIndex = writable(0);
export const cluesDone = writable(0);
export const clueProgress = writable({ players_done: 0, total: 0 });

// Canvas/guess phase
export const canvasCards = writable([]);
export const playersInfo = writable([]);   // [{sid, name, color}] ordered for circle
export const playerColors = writable({});  // {sid: color}
export const cardClaims = writable({});    // {card_id: {claimer_sid, claimer_color}}
export const scores = writable({});        // {sid: correct_count}
export const wrongGuessCardId = writable(null); // briefly set on wrong guess

// Finish screen
export const finalScores = writable([]);  // [{sid, name, color, score}]

// --- Socket connection ---
const socket = io({ path: "/socket.io" });

socket.on("connect", () => {
  console.log("Connected:", socket.id);
});

socket.on("error", (data) => {
  errorMsg.set(data.message);
  setTimeout(() => errorMsg.set(null), 4000);
});

// Room creation
socket.on("room_created", (data) => {
  roomId.set(data.room_id);
  playerId.set(data.player_id);
  playerName.set(data.player_name);
  isLeader.set(data.is_leader);
  players.set(data.players);
  screen.set("lobby");
});

// Room join
socket.on("room_joined", (data) => {
  roomId.set(data.room_id);
  playerId.set(data.player_id);
  playerName.set(data.player_name);
  isLeader.set(data.is_leader);
  players.set(data.players);
  screen.set("lobby");
});

// Name updated
socket.on("name_updated", (data) => {
  playerName.set(data.name);
});

// Player updates
socket.on("player_joined", (data) => {
  players.set(data.players);
});

socket.on("player_left", (data) => {
  players.set(data.players);
});

// Game started — clue phase begins
socket.on("game_started", (data) => {
  cards.set(data.cards);
  wordList.set(data.word_list);
  currentCardIndex.set(0);
  cluesDone.set(0);
  clueProgress.set({ players_done: 0, total: 0 });
  screen.set("clue");
});

// Clue phase events
socket.on("clue_submitted", (data) => {
  cluesDone.set(data.clues_done);
  currentCardIndex.update((idx) => {
    if (data.clues_done > idx) return data.clues_done;
    return idx;
  });
});

socket.on("clue_progress", (data) => {
  clueProgress.set(data);
});

// Canvas ready — guess phase begins
socket.on("canvas_ready", (data) => {
  canvasCards.set(data.canvas);
  wordList.set(data.word_list);
  playersInfo.set(data.players_info);
  playerColors.set(data.player_colors);
  scores.set(data.scores);
  cardClaims.set({});
  screen.set("guess");
});

// A card was correctly guessed — broadcast to all players
socket.on("card_claimed", (data) => {
  cardClaims.update((c) => ({
    ...c,
    [data.card_id]: {
      claimer_sid: data.claimer_sid,
      claimer_color: data.claimer_color,
    },
  }));
  scores.set(data.scores);
});

// Wrong guess — only sent to the guesser
socket.on("guess_wrong", (data) => {
  wrongGuessCardId.set(data.card_id);
  setTimeout(() => wrongGuessCardId.set(null), 1200);
});

// Game over — stays on guess screen, modal shown via finalScores
socket.on("game_over", (data) => {
  finalScores.set(data.scores);
});

// Return to lobby
socket.on("returned_to_lobby", (data) => {
  players.set(data.players);
  finalScores.set([]);
  cardClaims.set({});
  scores.set({});
  screen.set("lobby");
});

// --- Actions ---
export function createRoom() {
  socket.emit("create_room", {});
}

export function joinRoom(id) {
  socket.emit("join_room", { room_id: id });
}

export function startGame(id) {
  socket.emit("start_game", { room_id: id });
}

export function submitClue(id, cardId, clue) {
  socket.emit("submit_clue", { room_id: id, card_id: cardId, clue });
}

export function submitCanvasGuess(id, cardId, guess) {
  socket.emit("submit_canvas_guess", { room_id: id, card_id: cardId, guess });
}

export function addBots(id, count) {
  socket.emit("add_bots", { room_id: id, count });
}

export function returnToLobby(id) {
  socket.emit("return_to_lobby", { room_id: id });
}

export function renameSelf(id, name) {
  socket.emit("rename", { room_id: id, name });
}
