from Match import switch_order, match_player, match_names_then_update_tree
from Tree import EFGParser


gen_efg_path = "No_Observation/gen.efg"
ref_path = "No_Observation/ref.efg"
# gen_efg_path = "game2.efg"
# ref_path = "game1.efg"
# gen_efg_path = "Nim/0.efg"
# ref_path = "Nim/1.efg"

model = "gpt"
output_path = "match.efg"

parser_gen = EFGParser()
parser_ref = EFGParser()

gen_game = parser_gen.parse_file(gen_efg_path)
ref_game = parser_ref.parse_file(ref_path)

match_player(gen_game, ref_game, model)
match_names_then_update_tree(ref_game, gen_game, "gpt")
switch_order(ref_game.root, gen_game.root, model)

parser_gen.save_to_efg(output_path)
print(f"Saved to {output_path}")