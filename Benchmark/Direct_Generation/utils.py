import os
from openai import OpenAI

def _build_client_and_model():
    model = os.getenv("BENCHMARK_MODEL", "qwen/qwen3.5-35b-a3b")

    if model in {"deepseek", "deepseek-chat"}:
        return (
            OpenAI(
                api_key=os.getenv("DEEPSEEK_API_KEY"),
                base_url="https://api.deepseek.com",
            ),
            "deepseek-chat",
        )

    if "/" in model:
        return (
            OpenAI(
                base_url="https://openrouter.ai/api/v1",
                api_key=os.getenv("OPENROUTER_API_KEY"),
            ),
            model,
        )

    return (
        OpenAI(api_key=os.getenv("OPENAI_API_KEY")),
        model,
    )

def get_response(prompt):
    client, model = _build_client_and_model()

    response = client.chat.completions.create(
        model=model,
        messages=prompt,
        temperature=1.0,
        extra_headers=(
            {
                "HTTP-Referer": os.getenv("OPENROUTER_SITE_URL", "http://localhost"),
                "X-OpenRouter-Title": os.getenv("OPENROUTER_SITE_NAME", "GameBenchmark"),
            }
            if "/" in model and model not in {"deepseek", "deepseek-chat"}
            else None
        ),
    )
    return response.choices[0].message.content or ""



##################################################################
def infer_code(game):
    init_message = "You will be given a game description. The task is to generate a Gambit EFG representation of the game."
    rules = """
    Structure of the prologue
    The extensive gamefile consists of two parts: the prologue, or header, and the list of nodes, or body. In the example file, the prologue is the first line. (Again, this is just a consequence of the formatting we have chosen and is not a requirement of the file structure itself.)
    The prologue is constructed as follows. The file begins with the token EFG , identifying it as an extensive gamefile. Next is the digit 2 ; this digit is a version number. Since only version 2 files have been supported for more than a decade, all files have a 2 in this position. Next comes the letter R . The letter R used to distinguish files which had rational numbers for numerical data; this distinction is obsolete, so all new files should have R in this position.
    The prologue continues with the title of the game. Following the title is a list of the names of the players defined in the game. This list follows the convention found elsewhere in the file of being surrounded by curly braces and delimited by whitespace (but not commas, semicolons, or any other character). The order of the players is significant; the first entry in the list will be numbered as player 1, the second entry as player 2, and so forth. At the end of the prologue is an optional text comment field.

    Structure of the body (list of nodes)
    The body of the file lists the nodes which comprise the game tree. These nodes are listed in the prefix traversal of the tree. The prefix traversal for a subtree is defined as being the root node of the subtree, followed by the prefix traversal of the subtree rooted by each child, in order from first to last. Thus, for the whole tree, the root node appears first, followed by the prefix traversals of its child subtrees. For convenience, the game above follows the convention of one line per node.
    Each node entry begins with an unquoted character indicating the type of the node. There are three node types:
    1. c for a chance node
    2. p for a personal player node
    3. t for a terminal node
    Each node type will be discussed individually below. There are three numbering conventions which are used to identify the information structure of the tree. Wherever a player number is called for, the integer specified corresponds to the index of the player in the player list from the prologue. The first player in the list is numbered 1, the second 2, and so on. Information sets are identified by an arbitrary positive integer which is unique within the player. Gambit generates these numbers as 1, 2, etc. as they appear first in the file, but there are no requirements other than uniqueness. The same integer may be used to specify information sets for different players; this is not ambiguous since the player number appears as well. Finally, outcomes are also arbitrarily numbered in the file format in the same way in which information sets are, except for the special number 0 which indicates the null outcome.
    Information sets and outcomes may (and frequently will) appear multiple times within a game. By convention, the second and subsequent times an information set or outcome appears, the file may omit the descriptive information for that information set or outcome. Alternatively, the file may specify the descriptive information again; however, it must precisely match the original declaration of the information set or outcome. If any part of the description is omitted, the whole description must be omitted.
    Outcomes may appear at nonterminal nodes. In these cases, payoffs are interepreted as incremental payoffs; the payoff to a player for a given path through the tree is interpreted as the sum of the payoffs at the outcomes encountered on that path (including at the terminal node). This is ideal for the representation of games with well- defined”stages”; see, for example, the file bayes2a.efg in the Gambit distribution for a two-stage example of the Bayesian game represented previously.
    In the following lists, fields which are omittable according to the above rules are indicated by the label (optional).
    
    Format of chance (nature) nodes. Entries for chance nodes begin with the character c . Following this, in order, are
    a text string, giving the name of the node
    a positive integer specifying the information set number
    (optional) the name of the information set
    (optional) a list of actions at the information set with their corresponding probabilities
    a nonnegative integer specifying the outcome
    (optional)the payoffs to each player for the outcome
    
    Format of personal (player) nodes. Entries for personal player decision nodes begin with the character p . Following this, in order, are:
    a text string, giving the name of the node
    a positive integer specifying the player who owns the node
    a positive integer specifying the information set
    (optional) the name of the information set
    (optional) a list of action names for the information set
    a nonnegative integer specifying the outcome
    (optional) the name of the outcome
    the payoffs to each player for the outcome
    
    Format of terminal nodes. Entries for terminal nodes begin with the character t . Following this, in order, are:
    a text string, giving the name of the node
    a nonnegative integer specifying the outcome
    (optional) the name of the outcome
    the payoffs to each player for the outcome
    There is no explicit end-of-file delimiter for the file.

    Below are some examples given the game description and its corresponding EFG representation.
    Game Description:
    There are two players, a Buyer and a Seller. The Buyer moves first and has two actions, Trust or Not trust. If the Buyer chooses Not trust, then the game ends, and both players receive payoffs of 0. If the Buyer chooses Trust, then the Seller has a choice with two actions, Honor or Abuse. If the Seller chooses Honor, both players receive payoffs of 1; if the Seller chooses Abuse, the Buyer receives a payoff of -1 and the Seller receives a payoff of 2.
    EFG:
    EFG 2 R "One-shot trust game, after Kreps (1990)" { "Buyer" "Seller" }
    p "" 1 1 "" { "Trust" "Not trust" } 0
    p "" 2 1 "" { "Honor" "Abuse" } 0
    t "" 1 "Trustworthy" { 1, 1 }
    t "" 2 "Untrustworthy" { -1, 2 }
    t "" 3 "Opt-out" { 0, 0 }

    Game description:
    There are two players, Alice and Bob. There is a deck of cards, with equal numbers of King and Queen cards. The game begins with each player putting $1 in the pot. One card is dealt at random to Alice; Alice observes her card but Bob does not. After Alice observes her card, she can choose either to Raise or to Fold. If she chooses to Fold, Bob wins the pot and the game ends. If she chooses to Raise, she adds another $1 to the pot. Bob then chooses either to Meet or Pass. If he chooses to Pass, Alice wins the pot and the game ends. If he chooses to Meet, he adds another $1 to the pot. There is then a showdown, in which Alice reveals her card. If she has a King, then she wins the pot; if she has a Queen, then Bob wins the pot.
    EFG:
    EFG 2 R "One card poker game, after Myerson (1991)" { "Alice" "Bob" }
    c "" 1 "" { "King" 1/2 "Queen" 1/2 } 0
    p "" 1 1 "" { "Raise" "Fold" } 0
    p "" 2 1 "" { "Meet" "Pass" } 0
    t "" 1 "Alice wins big" { 2, -2 }
    t "" 2 "Alice wins" { 1, -1 }
    t "" 4 "Bob wins" { -1, 1 }
    p "" 1 2 "" { "Raise" "Fold" } 0
    p "" 2 1 "" { "Meet" "Pass" } 0
    t "" 3 "Bob wins big" { -2, 2 }
    t "" 2 "Alice wins" { 1, -1 }
    t "" 4 "Bob wins" { -1, 1 }

    If a chance move assigns probability 0 to an action, do not include that action or its branch in the game tree.
    """

    message_pool = []
    init_message = {"role": "system", "content": init_message + rules}
    message_pool.append(init_message)

    # question = """Game Description:
    # A new manufacturer is planning to enter the market, and its strength, determined by a chance node, can be either strong (S, 80%) or weak (W, 20%). Then the new manufacturer will give a signal either strong (S) or weak (W). The current manufacturer is unaware of the new manufacturer's strength but observes a signal indicating whether it is strong (S) or weak (W). Based on this signal, the existing manufacturer must choose between competing aggressively (F) or adapting to the new competitor's presence (A).
    # If the new manufacturer is strong and the existing manufacturer chooses to compete aggressively, the new manufacturer will have a higher payoff under the strong signal and an equal payoff under the weak signal. If the existing manufacturer decides to adapt, the new manufacturer will still have a higher payoff (even more so with a strong signal), but the existing manufacturer will receive a higher payoff than if they chose to fight.
    # If the new manufacturer is weak and the existing manufacturer decides to fight, the existing manufacturer will have a higher payoff, with the new manufacturer having a higher payoff under the weak signal compared to the strong signal. If the existing manufacturer decides to adapt, the new manufacturer will have a higher payoff, with an even higher payoff under the weak signal.

    # Could you generate an EFG representation of the game described above?
    # """

    final_message = "Game Description:\n" + game + "\nCould you generate an EFG representation of the game described above? Only provide the EFG representation (no comments), nothing else."
    qa_message = {"role": "user", "content": final_message}

    message_pool.append(qa_message)
    response = get_response(message_pool)
    print(response)

    return response
