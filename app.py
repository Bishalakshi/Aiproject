from groq import Groq
import random
import streamlit as st

API_KEY = os.environ.get("API_KEY")
client = Groq(api_key=API_KEY)

class UnoGame:

    def __init__(self):
        self.colors = ["Red", "Blue", "Green", "Yellow"]
        self.target_score = 500
        self.start_match()

    def start_match(self):
        self.player_score = 0
        self.system_score = 0
        self.start_round()

    def start_round(self):

        self.create_deck()

        self.player_hand = [self.draw_card() for _ in range(7)]
        self.system_hand = [self.draw_card() for _ in range(7)]

        self.discard = []
        self.round_over = False
        self.winner = None
        self.wild_color = None

        card = self.draw_card()

        while card.startswith("Wild_Draw_4"):
            self.deck.append(card)
            random.shuffle(self.deck)
            card = self.draw_card()

        self.current_card = card

        if card.startswith("Wild"):
            self.current_color = random.choice(self.colors)
        else:
            self.current_color = card.split("_")[0]

        self.turn = "player"
        self.message = ""
        self.uno_called = False

    def create_deck(self):
        self.deck = []

        for color in self.colors:
            for i in range(10):
                self.deck.append(f"{color}_{i}.jpg")

            self.deck.append(f"{color}_Skip.jpg")
            self.deck.append(f"{color}_Reverse.jpg")
            self.deck.append(f"{color}_Draw_2.jpg")

        for _ in range(4):
            self.deck.append("Wild.jpg")
            self.deck.append("Wild_Draw_4.jpg")

        random.shuffle(self.deck)

    def draw_card(self):
        if not self.deck:
            return None
        return self.deck.pop()

    def playable(self, card):

        if card.startswith("Wild"):
            return True

        color = card.split("_")[0]
        value = card.replace(".jpg", "").split("_")[-1]
        top_value = self.current_card.replace(".jpg", "").split("_")[-1]

        return color == self.current_color or value == top_value

    def player_play(self, card, chosen_color):

        if self.round_over:
            return False

        if card not in self.player_hand or not self.playable(card):
            return False

        self.player_hand.remove(card)
        self.discard.append(self.current_card)
        self.current_card = card
        self.wild_color = None

        if card.startswith("Wild"):
            self.current_color = chosen_color
        else:
            self.current_color = card.split("_")[0]

        extra_turn = self.apply_action(card, "system")

        if len(self.player_hand) == 1:
            self.uno_called = False

        if len(self.player_hand) == 0:
            self.finish_round("player")
            return True

        self.update_live_score()

        if not extra_turn:
            self.system_turn()

        return True

    def system_turn(self):

        if self.round_over:
            return

        playable_cards = [c for c in self.system_hand if self.playable(c)]

        if playable_cards:

            card = playable_cards[0]
            self.system_hand.remove(card)

            self.discard.append(self.current_card)
            self.current_card = card

            if card.startswith("Wild"):
                color = random.choice(self.colors)
                self.current_color = color
                self.wild_color = color
                self.message = f"System played Wild"
            else:
                self.current_color = card.split("_")[0]
                self.message = f"System played {card}"

            extra_turn = self.apply_action(card, "player")

            if len(self.system_hand) == 0:
                self.finish_round("system")
                return

            self.update_live_score()

            if extra_turn:
                self.system_turn()
            else:
                self.turn = "player"

        else:
            new = self.draw_card()
            if new:
                self.system_hand.append(new)
                self.message = "System draws a card"

            self.turn = "player"

    def apply_action(self, card, target):

        hand = self.player_hand if target == "player" else self.system_hand

        if "Skip" in card or "Reverse" in card:
            self.message = f"{target} skipped"
            return True

        if "Draw_2" in card:
            for _ in range(2):
                hand.append(self.draw_card())
            self.message = f"{target} draws 2 cards"
            return True

        if "Wild_Draw_4" in card:
            for _ in range(4):
                hand.append(self.draw_card())
            self.message = f"{target} draws 4 cards"
            return True

        return False

    def call_uno(self):
        if len(self.player_hand) == 1:
            self.uno_called = True
            return True
        return False

    def update_live_score(self):
        self.player_score = self.calculate_hand_score(self.system_hand)
        self.system_score = self.calculate_hand_score(self.player_hand)

    def calculate_hand_score(self, hand):
        total = 0
        for c in hand:
            name = c.replace(".jpg", "")
            if "Wild" in name:
                total += 50
            elif any(x in name for x in ["Skip", "Reverse", "Draw_2"]):
                total += 20
            else:
                total += int(name.split("_")[-1])
        return total

    def finish_round(self, winner):
        self.round_over = True
        self.winner = winner
        self.update_live_score()

    def ai_hint(self):

        playable_cards = [c for c in self.player_hand if self.playable(c)]

        if not playable_cards:
            return "Draw"

        return playable_cards[0]


if "game" not in st.session_state:
    st.session_state.game = UnoGame()

game = st.session_state.game

st.title("🃏 UNO Game")

if st.button("New Match"):
    game.start_match()

if st.button("Next Round"):
    game.start_round()

st.write(f"**Current Card:** {game.current_card}")
st.write(f"**Current Color:** {game.current_color}")
st.write(f"**Your Score:** {game.player_score} | **System Score:** {game.system_score}")
st.write(f"**Message:** {game.message}")

if game.round_over:
    st.success(f"Round Over! Winner: {game.winner}")
else:
    st.write("### Your Hand:")
    for card in game.player_hand:
        if st.button(f"Play {card}", key=card):
            chosen_color = game.current_color
            if card.startswith("Wild"):
                chosen_color = st.selectbox("Choose color", game.colors)
            game.player_play(card, chosen_color)

    if st.button("Draw Card"):
        c = game.draw_card()
        if c:
            game.player_hand.append(c)
        game.update_live_score()
        game.system_turn()

    if st.button("Call UNO"):
        result = game.call_uno()
        st.write("UNO called!" if result else "You don't have UNO yet!")

    if st.button("Get Hint"):
        st.write(f"Hint: {game.ai_hint()}")

st.write(f"**System has {len(game.system_hand)} cards**")











