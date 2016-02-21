# Hangman Assignment

### Description

Implement a minimal version of a hangman application using this API spec:

Method | URL | Description
------ | --- | -----------
POST  | /games  | Start a new game
GET  | /games  | Overview of all games
GET  | /games/{id}  | JSON response that should at least include:<br />__word__: representation of the word that is being guessed. Should contain dots for letters that have not been guessed yet (e.g. "aw..so..")<br />__tries_left__: the number of tries left to guess the word (starts at 11)<br />__status__: current status of the game (busy\|fail\|success)
POST  | /games/{id}  | Guessing a letter, <br />POST body: ```char=a```

Guessing a correct letter doesn’t decrement the amount of tries left.<br />
Only valid characters are a-z (lowercase).

### Notes
* URLs have no ending slashes;
* Unclear about JSON responses. For example, /games/ POST should return at least a new game-id;
* Edge case handling unclear. For example, repeating the same character in /game/{id} POST;
* Returning the 'already used characters' in a game JSON response would be very convenient.

---
# Submissions

The /data/ directory contains an english wordlist-file and can/will be used to store sqlite3-database files.

### Hangman Minimal (Python/Bottle)

#### Description
A minimal version using only Python 2.7.10 stdlib and Bottle (http://bottlepy.org/). It uses sqlite3 (no ORM) for saving game-state.


Run it with:

```bash
$ cd minimal; virtualenv minimal; source minimal/bin/activate
$ easy_install bottle
$ python main.py
```
Then take your favourite HTTP-client and go to:

Method | URL | Description
------ | --- | -----------
GET | http://127.0.0.1:8080/games | Returns JSON with a list of games.
POST | http://127.0.0.1:8080/games | Creates a new game (returns game-data JSON).
GET |  http://127.0.0.1:8080/games/{id} | Returns game-data JSON.
POST |  http://127.0.0.1:8080/games/{id} | Play the game by guessing a character.<br />Expects POST body with ```char=x``` where x is a single alphabetical character. Returns game-data JSON.

Response game-data example JSON:
```json
{
    "id": "55b6519e1f0f465fb63e36d55abea5a7",
    "status": "busy", 
    "tries_left": 9, 
    "word": ".a....."
}
```

