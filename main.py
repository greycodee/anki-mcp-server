import httpx
from mcp.server.fastmcp import FastMCP
from typing import Any, List, Dict, Optional

# --- Configuration ---
# Define the Anki-Connect URL (default port)
ANKICONNECT_URL = "http://127.0.0.1:8765"
# --- MCP Server Initialization ---
# Give your server a descriptive name
mcp = FastMCP("AnkiMCPBridge")

# --- Helper Function for Anki-Connect API Calls ---

async def invoke_anki_connect(action: str, params: Optional[Dict[str, Any]] = None) -> Any:
    """
    Sends a request to the Anki-Connect API and returns the result.

    Args:
        action: The Anki-Connect action name.
        params: A dictionary of parameters for the action (optional).

    Returns:
        The 'result' field from the Anki-Connect response.

    Raises:
        Exception: If the Anki-Connect request fails or returns an error.
    """
    payload: Dict[str, Any] = {"action": action, "version": 6}
    if params:
        payload["params"] = params

    # Use httpx for asynchronous HTTP requests
    async with httpx.AsyncClient() as client:
        try:
            # Make the POST request to Anki-Connect
            response = await client.post(ANKICONNECT_URL, json=payload, timeout=30.0)

            # Raise an exception for bad status codes (4xx or 5xx)
            response.raise_for_status() 
            
            # Parse the JSON response
            data = response.json()
            
            # Check for Anki-Connect specific errors field
            if "error" in data and data["error"] is not None:
                raise Exception(f"Anki-Connect action '{action}' failed: {data['error']}")
            
            # Return the result field
            return data.get("result")

        # Handle specific httpx errors for better feedback    
        except httpx.RequestError as e:
            # Errors during the request (connection, DNS, etc.)
            raise Exception(f"Anki-Connect communication error: Could not connect to {e.request.url}. Is Anki running with Anki-Connect?")
        except httpx.HTTPStatusError as e:
            # Errors for non-2xx status codes
             raise Exception(f"Anki-Connect communication error: Received status {e.response.status_code} for action '{action}'")
        except Exception as e:
            # Catch other potential errors (e.g., JSON parsing, Anki-Connect internal errors)
            # Ensure the original exception type isn't lost if possible, or re-raise specific types
            raise Exception(f"Anki-Connect request failed for action '{action}': {e}")


# --- Deck Actions ---

@mcp.tool()
async def anki_deck_names() -> List[str]:
    """Gets the complete list of deck names for the current Anki user."""
    return await invoke_anki_connect("deckNames")

@mcp.tool()
async def anki_deck_names_and_ids() -> Dict[str, int]:
    """Gets the complete list of deck names and their respective IDs."""
    return await invoke_anki_connect("deckNamesAndIds")

@mcp.tool()
async def anki_create_deck(deck_name: str) -> int:
    """
    Creates a new empty Anki deck. Does not overwrite if deck already exists.

    Args:
        deck_name: The name for the new deck (e.g., 'Japanese::Tokyo').
    
    Returns:
        The ID of the created deck.
    """
    return await invoke_anki_connect("createDeck", {"deck": deck_name})

@mcp.tool()
async def anki_change_deck(card_ids: List[int], deck_name: str) -> None:
    """
    Moves cards to a different deck, creating the deck if it doesn't exist.

    Args:
        card_ids: A list of card IDs to move.
        deck_name: The target deck name.
    """
    await invoke_anki_connect("changeDeck", {"cards": card_ids, "deck": deck_name})
    return None # Explicitly return None for actions with null result

@mcp.tool()
async def anki_delete_decks(deck_names: List[str]) -> None:
    """
    Deletes decks with the given names. WARNING: This also deletes all cards within the decks.

    Args:
        deck_names: A list of deck names to delete.
    """
    # cardsToo must be true to delete decks and their cards
    await invoke_anki_connect("deleteDecks", {"decks": deck_names, "cardsToo": True})
    return None 

@mcp.tool()
async def anki_get_deck_stats(deck_names: List[str]) -> Dict[str, Dict[str, Any]]:
    """
    Gets statistics for the given decks, such as total cards and counts for new, learning, and review cards.

    Args:
        deck_names: A list of deck names to get stats for.

    Returns:
        A dictionary where keys are deck IDs (as strings) and values are objects containing deck statistics.
    """
    return await invoke_anki_connect("getDeckStats", {"decks": deck_names})

# --- Card Actions ---

@mcp.tool()
async def anki_find_cards(query: str) -> List[int]:
    """
    Finds cards based on an Anki search query.

    Args:
        query: The search query (e.g., 'deck:current', 'tag:myTag', 'nid:12345'). See Anki manual for syntax.

    Returns:
        A list of card IDs matching the query.
    """
    return await invoke_anki_connect("findCards", {"query": query})

@mcp.tool()
async def anki_cards_info(card_ids: List[int]) -> List[Dict[str, Any]]:
    """
    Gets detailed information about multiple cards.

    Args:
        card_ids: A list of card IDs.

    Returns:
        A list of objects, each containing detailed information for a card 
        (fields, deck, model, question/answer HTML, interval, ease, etc.).
    """
    return await invoke_anki_connect("cardsInfo", {"cards": card_ids})

@mcp.tool()
async def anki_cards_to_notes(card_ids: List[int]) -> List[int]:
    """
    Gets the note IDs corresponding to the given card IDs.

    Args:
        card_ids: A list of card IDs.

    Returns:
        An unordered list of unique note IDs.
    """
    return await invoke_anki_connect("cardsToNotes", {"cards": card_ids})

@mcp.tool()
async def anki_suspend_cards(card_ids: List[int]) -> bool:
    """
    Suspends the specified cards.

    Args:
        card_ids: A list of card IDs to suspend.

    Returns:
        True if successful (at least one card wasn't already suspended), False otherwise.
    """
    return await invoke_anki_connect("suspend", {"cards": card_ids})

@mcp.tool()
async def anki_unsuspend_cards(card_ids: List[int]) -> bool:
    """
    Unsuspends the specified cards.

    Args:
        card_ids: A list of card IDs to unsuspend.

    Returns:
        True if successful (at least one card was previously suspended), False otherwise.
    """
    return await invoke_anki_connect("unsuspend", {"cards": card_ids})

@mcp.tool()
async def anki_are_suspended(card_ids: List[int]) -> List[Optional[bool]]:
    """
    Checks if the given cards are suspended.

    Args:
        card_ids: A list of card IDs.

    Returns:
        A list of booleans (or null if card doesn't exist) indicating suspension status, in the same order as input.
    """
    return await invoke_anki_connect("areSuspended", {"cards": card_ids})

@mcp.tool()
async def anki_are_due(card_ids: List[int]) -> List[bool]:
    """
    Checks if the given cards are due for review.

    Args:
        card_ids: A list of card IDs.

    Returns:
        A list of booleans indicating due status, in the same order as input.
    """
    return await invoke_anki_connect("areDue", {"cards": card_ids})

@mcp.tool()
async def anki_forget_cards(card_ids: List[int]) -> None:
    """
    Resets the specified cards, making them 'new' again.

    Args:
        card_ids: A list of card IDs to forget.
    """
    await invoke_anki_connect("forgetCards", {"cards": card_ids})
    return None

@mcp.tool()
async def anki_relearn_cards(card_ids: List[int]) -> None:
    """
    Puts the specified cards into the 'relearning' state.

    Args:
        card_ids: A list of card IDs to relearn.
    """
    await invoke_anki_connect("relearnCards", {"cards": card_ids})
    return None

# --- Note Actions ---

@mcp.tool()
async def anki_add_note(
    deck_name: str, 
    model_name: str, 
    fields: Dict[str, str], 
    allow_duplicate: bool = False, 
    duplicate_scope: Optional[str] = None,
    tags: Optional[List[str]] = None,
    audio: Optional[List[Dict[str, Any]]] = None,
    video: Optional[List[Dict[str, Any]]] = None,
    picture: Optional[List[Dict[str, Any]]] = None
) -> int:
    """
    Creates a new Anki note.

    Args:
        deck_name: The name of the deck to add the note to.
        model_name: The name of the model (note type) to use.
        fields: A dictionary mapping field names to their content (e.g., {"Front": "Question", "Back": "Answer"}).
        allow_duplicate: Set to True to allow adding notes even if they are duplicates. Default is False.
        duplicate_scope: Scope for duplicate checking ('deck' or None/other for collection). Default is collection.
        tags: A list of tags to add to the note (optional).
        audio: List of audio file objects to attach (optional). See Anki-Connect docs for format.
        video: List of video file objects to attach (optional). See Anki-Connect docs for format.
        picture: List of picture file objects to attach (optional). See Anki-Connect docs for format.

    Returns:
        The ID of the newly created note, or raises an exception on failure (e.g., duplicate found).
    """
    note_data: Dict[str, Any] = {
        "deckName": deck_name,
        "modelName": model_name,
        "fields": fields,
        "options": {
            "allowDuplicate": allow_duplicate
        }
    }
    if duplicate_scope:
        note_data["options"]["duplicateScope"] = duplicate_scope
        # Potentially add duplicateScopeOptions here if needed based on Anki-Connect README examples
        # note_data["options"]["duplicateScopeOptions"] = {"deckName": "...", "checkChildren": False, "checkAllModels": False}
        
    if tags is not None: # Check explicitly for None as empty list is valid
        note_data["tags"] = tags
    if audio:
        note_data["audio"] = audio
    if video:
        note_data["video"] = video
    if picture:
        note_data["picture"] = picture

    return await invoke_anki_connect("addNote", {"note": note_data})

@mcp.tool()
async def anki_update_note_fields(
    note_id: int, 
    fields: Dict[str, str], 
    audio: Optional[List[Dict[str, Any]]] = None, 
    video: Optional[List[Dict[str, Any]]] = None, 
    picture: Optional[List[Dict[str, Any]]] = None
) -> None:
    """
    Modifies the fields of an existing note. Can also add media.

    Args:
        note_id: The ID of the note to update.
        fields: A dictionary mapping field names to their new content. Only specified fields are updated.
        audio: Optional list of audio file objects to add/update.
        video: Optional list of video file objects to add/update.
        picture: Optional list of picture file objects to add/update.
    """
    note_data: Dict[str, Any] = {"id": note_id, "fields": fields}
    if audio:
        note_data["audio"] = audio
    if video:
        note_data["video"] = video
    if picture:
        note_data["picture"] = picture
    
    await invoke_anki_connect("updateNoteFields", {"note": note_data})
    return None

@mcp.tool()
async def anki_find_notes(query: str) -> List[int]:
    """
    Finds notes based on an Anki search query.

    Args:
        query: The search query (e.g., 'deck:current', 'tag:myTag'). See Anki manual for syntax.

    Returns:
        A list of note IDs matching the query.
    """
    return await invoke_anki_connect("findNotes", {"query": query})

@mcp.tool()
async def anki_notes_info(note_ids: List[int]) -> List[Dict[str, Any]]:
    """
    Gets detailed information about multiple notes.

    Args:
        note_ids: A list of note IDs.

    Returns:
        A list of objects, each containing detailed information for a note 
        (fields, tags, modelName, cards list, modification time, etc.).
    """
    return await invoke_anki_connect("notesInfo", {"notes": note_ids})

@mcp.tool()
async def anki_get_note_tags(note_id: int) -> List[str]:
    """
    Gets the tags for a specific note.

    Args:
        note_id: The ID of the note.

    Returns:
        A list of tags associated with the note.
    """
    return await invoke_anki_connect("getNoteTags", {"note": note_id})

@mcp.tool()
async def anki_add_tags(note_ids: List[int], tags: str) -> None:
    """
    Adds one or more tags to the specified notes. Tags are space-separated.

    Args:
        note_ids: A list of note IDs to add tags to.
        tags: A space-separated string of tags to add (e.g., "tag1 tag2").
    """
    await invoke_anki_connect("addTags", {"notes": note_ids, "tags": tags})
    return None

@mcp.tool()
async def anki_remove_tags(note_ids: List[int], tags: str) -> None:
    """
    Removes one or more tags from the specified notes. Tags are space-separated.

    Args:
        note_ids: A list of note IDs to remove tags from.
        tags: A space-separated string of tags to remove.
    """
    await invoke_anki_connect("removeTags", {"notes": note_ids, "tags": tags})
    return None

@mcp.tool()
async def anki_update_note_tags(note_id: int, tags: List[str]) -> None:
    """
    Sets the tags for a specific note, removing any old tags first.

    Args:
        note_id: The ID of the note to update.
        tags: A list of the new tags for the note.
    """
    await invoke_anki_connect("updateNoteTags", {"note": note_id, "tags": tags})
    return None
    
@mcp.tool()
async def anki_delete_notes(note_ids: List[int]) -> None:
    """
    Deletes the specified notes and all their associated cards.

    Args:
        note_ids: A list of note IDs to delete.
    """
    await invoke_anki_connect("deleteNotes", {"notes": note_ids})
    return None

# --- Miscellaneous Actions ---

@mcp.tool()
async def anki_request_permission() -> Dict[str, Any]:
    """
    Requests permission to use the Anki-Connect API. 
    Displays a popup in Anki if the origin is not trusted. This should be the first call.

    Returns:
        A dictionary containing permission status ('granted' or 'denied'), 
        whether an API key is required ('requireApiKey'), and the Anki-Connect version ('version').
    """
    return await invoke_anki_connect("requestPermission")

@mcp.tool()
async def anki_version() -> int:
    """Gets the version of the Anki-Connect API."""
    return await invoke_anki_connect("version")

@mcp.tool()
async def anki_sync() -> None:
    """Synchronizes the local Anki collection with AnkiWeb."""
    await invoke_anki_connect("sync")
    return None

# --- Model Actions (Examples) ---

@mcp.tool()
async def anki_model_names() -> List[str]:
    """Gets the list of model (note type) names."""
    return await invoke_anki_connect("modelNames")

@mcp.tool()
async def anki_model_field_names(model_name: str) -> List[str]:
    """Gets the list of field names for a given model."""
    return await invoke_anki_connect("modelFieldNames", {"modelName": model_name})

# --- Main Execution Block ---

if __name__ == "__main__":
    print("Starting Anki MCP Bridge Server...")
    print(f"Ensure Anki is running with Anki-Connect add-on enabled at {ANKICONNECT_URL}")
    # Run the MCP server using stdio transport when script is executed directly
    # Other transports like 'sse' are available if needed for web integration.
    # See MCP Python SDK docs for details.
    mcp.run(transport='stdio')