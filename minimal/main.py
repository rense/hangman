#!/usr/bin/env python
import os
import json
import uuid
import random
import sqlite3

from httplib import CREATED, NOT_FOUND, BAD_REQUEST, FORBIDDEN
from bottle import get, post, request, response, run

STATUS_BUSY = 0
STATUS_FAIL = 1
STATUS_SUCCESS = 2

base_dir = os.path.dirname(os.path.abspath(__file__))
WORD_LIST = list(open(os.path.join(base_dir, '..', 'data', 'wordlist.txt')))
DB_FILE = os.path.join(base_dir, '..', 'data', 'minimal.sqlite3')


@get('/games')
def game_list():
    """ Return list of games """
    result = _db_query(
        "SELECT key, word_to_guess, used_characters, tries_left, "
        "status FROM games"
    )
    games = [_output(game) for game in result]
    return json.dumps(games)


@get('/games/<key:re:[a-z0-9]+>')
def game_detail(key):
    """ Return game-detail """
    game = _db_get_game(key)
    if not game:
        response.status = NOT_FOUND
        return
    return json.dumps(_output(game))


@post('/games')
def game_start():
    """ Start/create a new game """
    key = uuid.uuid4().hex
    _db_query(
        "INSERT INTO games (key, word_to_guess, used_characters, "
        "tries_left, status) VALUES (?, ?, '', 11, 0)",
        key, random.choice(WORD_LIST).strip()
    )
    game = _db_get_game(key)
    response.status = CREATED
    return json.dumps(_output(game))


@post('/games/<key:re:[a-z0-9]+>')
def game_play(key):
    """ Play game """
    if not request.params.get('char'):
        response.status = BAD_REQUEST
        return
    character = request.params.get('char').lower()
    if len(character) > 1 or not character.isalpha():
        response.status = BAD_REQUEST
        return

    game = _db_get_game(key)
    if not game:
        response.status = NOT_FOUND
        return

    status = game['status']
    if status != STATUS_BUSY:
        response.status = FORBIDDEN
        return

    if character in game['used_characters']:
        # Requirements unclear here, do nothing...
        return json.dumps(_output(_db_get_game(key)))
    used_characters = game['used_characters'] + character

    tries_left = game['tries_left']
    if character not in game['word_to_guess']:
        # Decrement tries_left
        tries_left -= 1

    word = _dottify(game['word_to_guess'], used_characters)
    if word == game['word_to_guess']:
        # Player guessed the word!
        status = STATUS_SUCCESS
    elif tries_left <= 0:
        # Player failed to guess the word
        status = STATUS_FAIL

    # Update game-state
    _db_query(
        "UPDATE games SET used_characters=?, tries_left=?, status=? "
        "WHERE key=?", used_characters, tries_left, status, key
    )
    return json.dumps(_output(_db_get_game(key)))


def _dottify(word_to_guess, used_characters):
    """ Replace not yet guessed characters with dots """
    word = word_to_guess
    for character in word_to_guess:
        if character not in used_characters:
            word = word.replace(character, '.')
    return word


def _output(data):
    """ Format game-data for client-response """
    game = {
        'id': data['key'],
        'tries_left': data['tries_left'],
        'status': ['busy', 'fail', 'succes'][data['status']],
    }
    if data['status'] != STATUS_BUSY:
        # This game has ended, show the word
        game['word'] = data['word_to_guess']
    else:
        game['word'] = _dottify(data['word_to_guess'], data['used_characters'])
    return game


def _db_query(query, *args):
    """ Handle database-connection, do queries, return results
    """
    if not os.path.exists(DB_FILE):
        # Create our database/table, because it's missing
        conn = sqlite3.connect(DB_FILE)
        conn.execute("""
            CREATE TABLE games(
            id INTEGER PRIMARY KEY, key char(40) NOT NULL DEFAULT '',
            word_to_guess char(22) NOT NULL DEFAULT '',
            used_characters char(26) DEFAULT NULL,
            tries_left int(2) DEFAULT 11, status int(1) DEFAULT 0)
        """)
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    _cursor = conn.cursor()
    _cursor.execute(query, args)
    conn.commit()
    result = _cursor.fetchall()
    _cursor.close()
    return result


def _db_get_game(key):
    """ Convenience function for getting a single game by key """
    return _db_query(
        "SELECT key, word_to_guess, used_characters, tries_left, status "
        "FROM games WHERE key = ?", key
    )[0]


run(reloader=True)
