# Anki MCP Server

[![Python Version][python-badge]][python-url]
[![MCP Specification][spec-badge]][spec-url]

[python-badge]: https://img.shields.io/pypi/pyversions/mcp.svg
[python-url]: https://www.python.org/downloads/
[spec-badge]: https://img.shields.io/badge/spec-spec.modelcontextprotocol.io-blue.svg
[spec-url]: https://spec.modelcontextprotocol.io

## Overview

This project provides a Model Context Protocol (MCP) server that acts as a bridge to the [Anki](https://apps.ankiweb.net/) spaced repetition software via the [Anki-Connect](https://ankiweb.net/shared/info/2055492159) add-on. It allows MCP-compatible clients (like AI assistants or other applications) to interact with your Anki collection, managing decks, cards, and notes.

## Features

*   Exposes a comprehensive set of Anki actions as MCP tools.
*   Manages communication with the local Anki-Connect instance.
*   Provides tools for:
    *   Deck Management (list, create, delete, move cards, get stats)
    *   Card Management (find, get info, suspend, unsuspend, check status, forget, relearn)
    *   Note Management (add, update, find, get info, manage tags, delete)
    *   Model Management (list names, list fields)
    *   Miscellaneous Actions (request permission, get version, sync)

## Prerequisites

1.  **Anki:** You must have Anki installed and running on your system.
2.  **Anki-Connect Add-on:** The Anki-Connect add-on must be installed in Anki and running. By default, it listens on `http://127.0.0.1:8765`.
3.  **Python:** A compatible Python version (see `pyproject.toml`).
4.  **uv:** Recommended for managing Python environments and dependencies ([uv installation](https://docs.astral.sh/uv/install/)).

## Installation

1.  **Clone the repository:**
    ```bash
    git clone <repository-url> # Replace with the actual URL if applicable
    cd anki-mcp-server
    ```
2.  **Install dependencies:**
    ```bash
    uv sync
    ```

## Running the Server

Ensure Anki is running with the Anki-Connect add-on enabled before starting the server.

You can run the server in several ways:

1.  **Direct Execution (using uv):**
    ```bash
    uv run python main.py
    ```
    This will start the server using the stdio transport, suitable for direct integration or testing.

2.  **Development Mode (using MCP Inspector):**
    ```bash
    uv run mcp dev main.py
    ```
    This starts the server and opens the MCP Inspector tool, allowing you to interactively test the available tools and resources.

3.  **Install for Claude Desktop:**
    ```bash
    uv run mcp install main.py --name "Anki Bridge"
    ```
    This installs the server into Claude Desktop (if available), making the Anki tools accessible within the assistant.

## Usage

Once the server is running and connected to an MCP client (like Claude Desktop via `mcp install` or another application using the MCP protocol):

1.  **Request Permission:** The first action should typically be `anki_request_permission`. If the client's origin isn't trusted by Anki-Connect, a confirmation popup will appear in Anki.
2.  **Use Tools:** Call the available tools (listed below) to interact with your Anki collection.

## Configuration

*   **Anki-Connect URL:** The server connects to Anki-Connect using the URL defined by the `ANKICONNECT_URL` constant in `main.py` (default: `http://127.0.0.1:8765`). Modify this if your Anki-Connect setup uses a different address or port.

## Available Tools

The server exposes the following tools, mirroring the Anki-Connect API actions:

### Deck Actions

*   `anki_deck_names`: Gets the complete list of deck names.
*   `anki_deck_names_and_ids`: Gets deck names and their IDs.
*   `anki_create_deck(deck_name: str)`: Creates a new empty deck.
*   `anki_change_deck(card_ids: List[int], deck_name: str)`: Moves cards to a different deck.
*   `anki_delete_decks(deck_names: List[str])`: Deletes specified decks and their cards.
*   `anki_get_deck_stats(deck_names: List[str])`: Gets statistics for specified decks.

### Card Actions

*   `anki_find_cards(query: str)`: Finds cards using an Anki search query.
*   `anki_cards_info(card_ids: List[int])`: Gets detailed information about multiple cards.
*   `anki_cards_to_notes(card_ids: List[int])`: Gets the note IDs for given card IDs.
*   `anki_suspend_cards(card_ids: List[int])`: Suspends specified cards.
*   `anki_unsuspend_cards(card_ids: List[int])`: Unsuspends specified cards.
*   `anki_are_suspended(card_ids: List[int])`: Checks if cards are suspended.
*   `anki_are_due(card_ids: List[int])`: Checks if cards are due for review.
*   `anki_forget_cards(card_ids: List[int])`: Resets specified cards to new.
*   `anki_relearn_cards(card_ids: List[int])`: Puts specified cards into the relearning state.

### Note Actions

*   `anki_add_note(...)`: Creates a new Anki note with specified deck, model, fields, options, tags, and media.
*   `anki_update_note_fields(...)`: Modifies the fields and media of an existing note.
*   `anki_find_notes(query: str)`: Finds notes using an Anki search query.
*   `anki_notes_info(note_ids: List[int])`: Gets detailed information about multiple notes.
*   `anki_get_note_tags(note_id: int)`: Gets the tags for a specific note.
*   `anki_add_tags(note_ids: List[int], tags: str)`: Adds space-separated tags to notes.
*   `anki_remove_tags(note_ids: List[int], tags: str)`: Removes space-separated tags from notes.
*   `anki_update_note_tags(note_id: int, tags: List[str])`: Sets the tags for a note, replacing old ones.
*   `anki_delete_notes(note_ids: List[int])`: Deletes specified notes and their cards.

### Model Actions

*   `anki_model_names()`: Gets the list of model (note type) names.
*   `anki_model_field_names(model_name: str)`: Gets the list of field names for a given model.

### Miscellaneous Actions

*   `anki_request_permission()`: Requests permission to use the Anki-Connect API. Should be called first.
*   `anki_version()`: Gets the version of the Anki-Connect API.
*   `anki_sync()`: Synchronizes the local Anki collection with AnkiWeb.

## Contributing

Contributions are welcome! Please refer to the project's contribution guidelines (if available).

## License

Specify the license under which this project is distributed (e.g., MIT License).
