# Taboo with Sentence Embeddings.
This application will build a real-time networked application similar to the card game 'Taboo'. It will support rooms, and allow the person who created a room to start a room. The person who created a room is also the leader, and can start the game.
- It will allow up to 50 people to join a room at a time.
Stack. Use Flask with Svelte, and flask networks.

### Taboo Implementation
Each player will be presented with a target word, and five words which they cannot use to describe the target. In general, please load the cards from data/taboo_cards.csv. However, to begin with just load the following card:

Orange,Color ; Fruit ; Juicy ; Citrus ; Red

The regular goal of taboo is to allow one player to guess a target word by a clue. However, in this first version, we are only interested in the responses to the card, and how users cluster based on their answers. Here are the screens in order of presentation:

1. Landing screen. (there should be a make lobby button, which makes the current connected player the leader and takes them to a /<ID> page. There should also be a join lobby input for other players to join the respective lobby). Players should be assigned unique ids, which can be numbers for now. Once the leader starts the game, we will show all users the game screen.

2. Game screen. Each user will now be shown the card and the taboo words, and have the chance to input a response. Once a user submits their response, they will be taken to the waiting screen.

3. Waiting screen. In the waiting screen, each player should be shown the number of players who have submitted their answer. Once all players have submitted their answers, the app should compute a visualization, and display a loading icon. Once the visualization is complete, each player should be taken to view it.
