Solving Tic-Tac-Toe with Dynamic Programming.

Starting from ideas contained in "Reinforcement Learning, An Introduction" by Sutton and Barto [pp 73-88] a model of an ideal opponent is created, a state-value function is built (mapping each possible state of the game to our prevision of the future earned rewards from that point on) and consequently a greedy policy is formed  selecting for each state the action leading to the state with the highest associated value.

The existence of a model for our environment in the particular case of Tic-Tac-Toe and the small number of existing states for the game (10^4 ca.) allows us to use "Policy Iteration" method to "solve" the game.

Agent is trained to win against an opponent perfectly described by an "hard-coded" known model, nonetheless it was not possible for me to beat it, if you manage to win, contact me!
