# Monkey's Paw Party Game

A small, no-account multiplayer web game for Python 3.10+. One player creates a room, friends join with its five-character code, and players take turns making wishes that the paw twists.

## Run locally

```bash
python -m pip install -r requirements.txt
python paw_webapp.py
```

Open <http://localhost:5000>. To play with people on the same network, share the computer's local network address and port 5000.

## Deploy on Replit

1. Create a Python Repl and add these project files.
2. Replit installs Flask from `requirements.txt`; run `paw_webapp.py`.
3. Share the published app URL. Players open it, enter nicknames, and use the room code.
4. For a stable session-signing key, add a Replit Secret named `SECRET_KEY` with a long random value.

The app uses Python and Flask on the server, with its HTML and CSS kept inside the Python file. It does not use JavaScript or a database. Room pages refresh themselves every three seconds; the page pauses automatic refresh while you have a wish or catch form open so your typing is not interrupted. Room data is held in memory, so it lasts only while the app process stays running; a restart or a host that sleeps will clear rooms. Use a single running instance for a game.

## How to play

- Create a room and share the displayed code.
- At least two players need to join before wishes can be made.
- The player whose turn it is submits one wish.
- Every other player adds one catch. Catches stay hidden while the round is in progress.
- Once everyone has submitted, the wish and all catches are revealed together in the shared ledger.
- The next player's turn begins automatically.
