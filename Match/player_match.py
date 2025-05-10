from typing import List
from google import genai

from Tree import Node, NodeType
from .chatbot import infer_response
from .utils import convert_str_to_list, extract_python_code

def reorder_players(gen_game, ref_players: List[str]):
    """
    Reorder the players in `game` to match the order in `ref_players`.
    This updates the `players` list and remaps all player numbers accordingly in the game tree.
    """
    # Get the current order of players in the generated game
    gen_players = gen_game.players
    
    # Create a mapping from the old player index to the new player index
    player_mapping = {gen_players.index(player) + 1: ref_players.index(player) + 1 for player in gen_players}

    payoff_mapping = {gen_players.index(player): ref_players.index(player) for player in gen_players}
    
    print("Player mapping:", player_mapping)
    print("Payoff mapping:", payoff_mapping)
    
    # Update the game players order
    gen_game.players = ref_players
    
    def update_player_numbers(node: Node):
        if node.node_type == NodeType.PLAYER and node.player in player_mapping:
            node.player = player_mapping[node.player]
        
        for child in node.children.values():
            update_player_numbers(child)
        # Reorder payoffs for terminal nodes
        if node.node_type == NodeType.TERMINAL and node.payoffs:
            reordered = [0] * len(node.payoffs)
            for old_idx, payoff in enumerate(node.payoffs):
                new_idx = payoff_mapping[old_idx]
                reordered[new_idx] = payoff
            node.payoffs = reordered
    
    # Apply updates to the tree
    if gen_game.root:
        update_player_numbers(gen_game.root)

def match_palyer_name_llm(gen_game, ref_game, model):
    gen_players = gen_game.players
    ref_players = ref_game.players
    # Check the length of the players list
    if len(gen_players) != len(ref_players):
        raise ValueError("The number of players in the generated game does not match the number of players in the reference game.")
    
    # check_prompt = (f"Verify whether all players in {gen_players} correspond to players in {ref_players}, "
    #             f"considering possible name differences. Return ONLY 'True' or 'False'.")
    # check_response = client.models.generate_content(
    #     model="gemini-2.0-flash",
    #     contents=[check_prompt])
    # player_check = check_response.text.strip()
    # print(player_check)
    
    # f"However, if you think the name in generated game doesn't have a matched name in reference game, return Only an empty list."
    prompt_check_valid = (f"You are given two lists of players\\"
                          f"Generated Game Players: {gen_players}"
                          f"Reference Game Players: {ref_players}"
                          f"Disregard the different names and orders. Check if they represent the same set of players."
                          f"Output ONLY True if they match and False otherwise.")
    
    response_check = infer_response(prompt_check_valid, model)

    if response_check == "False":
        raise ValueError("The players in the generated game do not match the players in the reference game.")
    
    print(gen_players)
    
    prompt = (
    f"The following is a list of reference game players from a game tree: {ref_players}\n"
    f"Please update the names in this generated list of game players: {gen_players} so that they match the names in the reference list.\n"
    f"Do not change the order of items in the generated list.\n"
    f"Only return the modified list in Python list format."
    )

    response = infer_response(prompt, model)
    print(response)
    
    try:
        modified_players_name = extract_python_code(response) 
    except:
        print("Try another method to convert the response to a list.")
        modified_players_name = convert_str_to_list(response)

    gen_game.players = modified_players_name

def match_player(gen_game, ref_game, model):
    
    match_palyer_name_llm(gen_game, ref_game, model)
    reorder_players(gen_game, ref_game.players)