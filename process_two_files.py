from Match import switch_order, match_player, build_global_action_mappings
from Tree import EFGParser

# gen_efg_path = "No_Observation/gen.efg"
# ref_path = "No_Observation/ref.efg"
# gen_efg_path = "ref.efg"
# ref_path = "test.efg"
gen_efg_path = "kuhn_2.efg"
ref_path = "kuhn.efg"
# gen_efg_path = "Nim/0.efg"
# ref_path = "Nim/1.efg"

with open("kuhn.txt", "r") as file:
    content = file.read()

model = "gpt"
output_path = "match.efg"

parser_gen = EFGParser()
parser_ref = EFGParser()

gen_game = parser_gen.parse_file(gen_efg_path)
ref_game = parser_ref.parse_file(ref_path)

match_player(gen_game, ref_game, model)

ref_total = ref_game.get_total_unique_actions()
gen_total = gen_game.get_total_unique_actions()

mappings = build_global_action_mappings(ref_total, gen_total, model, content)

switch_order(ref_game.root, gen_game.root, model, mappings, content)

parser_gen.save_to_efg(output_path)
print(f"Saved to {output_path}")