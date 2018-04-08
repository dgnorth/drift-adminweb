events = [
    # audit log events
    {
        "type_id": 1001,
        "type_name": "event.player.player_create",
        "description": "New player has been initialized"
    },
    {
        "type_id": 1002,
        "type_name": "event.player.session_start",
        "description": "A game session has been started"
    },
    {
        "type_id": 1003,
        "type_name": "event.player.session_end",
        "description": "A game session has ended"
    },
    {
        "type_id": 1004,
        "type_name": "event.player.summarychanged",
        "description": "A game session has ended"
    },
    {
        "type_id": 1005,
        "type_name": "event.player.admineditbasic",
        "description": "Player information was edited by admin"
    },
    {
        "type_id": 1006,
        "type_name": "event.player.adminedithomebase",
        "description": "Home base was edited by admin"
    },
    {
        "type_id": 1007,
        "type_name": "event.player.change_name",
        "description": "Name was changed by player"
    },
    {
        "type_id": 1008,
        "type_name": "event.player.library_created",
        "description": "Library has been created for player"
    },
    {
        "type_id": 1009,
        "type_name": "event.player.deck_created",
        "description": "Deck created"
    },
    {
        "type_id": 1010,
        "type_name": "event.player.deck_name_changed",
        "description": "Deck renamed"
    },
    {
        "type_id": 1011,
        "type_name": "event.player.deck_cards_changed",
        "description": "Cards in deck has been updated"
    },
    {
        "type_id": 1012,
        "type_name": "event.player.deck_deleted",
        "description": "Deck has been deleted"
    },
    {
        "type_id": 1013,
        "type_name": "event.player.default_deck_created",
        "description": "Default deck created"
    },
    {
        "type_id": 1014,
        "type_name": "event.player.match_started",
        "description": "Match has been started"
    },
    {
        "type_id": 1015,
        "type_name": "event.player.registered_for_match",
        "description": "Player has been added to the lobby"
    },
    {
        "type_id": 1016,
        "type_name": "event.player.create_card",
        "description": "Player has created a card"
    },
    {
        "type_id": 1017,
        "type_name": "event.player.give_gold_to_player",
        "description": "Player got more gold"
    },
    {
        "type_id": 1018,
        "type_name": "event.player.give_dust_to_player",
        "description": "Player got more dust"
    },
    {
        "type_id": 1019,
        "type_name": "event.player.open_pack",
        "description": "Player opened a pack"
    },
    {
        "type_id": 1020,
        "type_name": "event.player.card_recycled",
        "description": "Player recycled a card"
    },
    {
        "type_id": 1021,
        "type_name": "event.player.remove_dust_from_player",
        "description": "Player spent some dust"
    },
    {
        "type_id": 1022,
        "type_name": "event.player.card_created",
        "description": "Player created a card"
    },
    {
        "type_id": 1023,
        "type_name": "event.player.stats.fps",
        "description": "Client told us it's FPS"
    },
    {
        "type_id": 1024,
        "type_name": "event.player.client.waitforaimatch.timeout",
        "description": "Client waited a long time for ai match to start"
    }
]


def event_type_id(event_name):
    # ! TODO: Needs caching
    for e in events:
        if e["type_name"].lower() == event_name.lower():
            return e["type_id"]
    return None


# noinspection PyShadowingNames
def event_type_name(event_type_id):
    # ! TODO: Needs caching
    for e in events:
        if e["type_id"] == event_type_id:
            return e["type_name"]
    return None
