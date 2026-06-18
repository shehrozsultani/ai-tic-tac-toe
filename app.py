import streamlit as ui
import google.generativeai as ai
import json
import random

ui.set_page_config(page_title="AI Tic-Tac-Toe", layout="centered")
ui.title("❌ AI-Powered Tic-Tac-Toe ⭕")
ui.write("Play against a Gemini-powered AI opponent. Choose its vibe before you play!")

ui.sidebar.header("Configuration")
api_key = ui.sidebar.text_input("Enter your Gemini API Key:", type="password")
ai_vibe = ui.sidebar.selectbox("AI Opponent Vibe:", ["Grandmaster (Strategic)", "Chaotic (Random/Fun)", "Sassy Trash-Talker"])

if "board" not in ui.session_state:
    ui.session_state.board = [" " ] * 9
if "turn" not in ui.session_state:
    ui.session_state.turn = "X"
if "winner" not in ui.session_state:
    ui.session_state.winner = None
if "ai_commentary" not in ui.session_state:
    ui.session_state.ai_commentary = "Your move, human!"

def check_winner(b):
    lines = [[0,1,2], [3,4,5], [6,7,8], [0,3,6], [1,4,7], [2,5,8], [0,4,8], [2,4,6]]
    for line in lines:
        if b[line[0]] == b[line[1]] == b[line[2]] and b[line[0]] != " ":
            return b[line[0]]
    if " " not in b:
        return "Tie"
    return None

def reset_game():
    ui.session_state.board = [" "] * 9
    ui.session_state.turn = "X"
    ui.session_state.winner = None
    ui.session_state.ai_commentary = "Fresh game! Let's see what you've got."

def make_move(index):
    if ui.session_state.board[index] == " " and ui.session_state.winner is None and ui.session_state.turn == "X":
        ui.session_state.board[index] = "X"
        ui.session_state.winner = check_winner(ui.session_state.board)
        if ui.session_state.winner is None:
            ui.session_state.turn = "O"

def make_ai_move():
    if not api_key:
        empty_indices = [i for i, val in enumerate(ui.session_state.board) if val == " "]
        if empty_indices:
            move = random.choice(empty_indices)
            ui.session_state.board[move] = "O"
        ui.session_state.turn = "X"
        ui.session_state.winner = check_winner(ui.session_state.board)
        return

    system_instruction = (
        f"You are playing a game of Tic-Tac-Toe as 'O'. The current board state is represented as a list of 9 elements, "
        f"indexed 0 to 8. Empty spots are ' '. You must analyze the board and pick the absolute best available index to win or block 'X'. "
        f"Your vibe is currently set to: {ai_vibe}. "
        f"CRITICAL: Respond ONLY with a valid JSON object containing two keys: 'move' (the integer index from 0 to 8) and "
        f"'comment' (a short, 1-sentence reactive quote matching your vibe)."
    )

    try:
        ai.configure(api_key=api_key)
        model = ai.GenerativeModel(model_name="gemini-1.5-flash", system_instruction=system_instruction)
        prompt = f"Current board list: {str(ui.session_state.board)}. Available indices: {[i for i, v in enumerate(ui.session_state.board) if v == ' ']}"
        response = model.generate_content(prompt)
        clean_text = response.text.strip().replace("```json", "").replace("```", "")
        data = json.loads(clean_text)
        ai_move = int(data.get("move"))
        ui.session_state.ai_commentary = data.get("comment", "Hmm...")
        if ui.session_state.board[ai_move] == " ":
            ui.session_state.board[ai_move] = "O"
        else:
            empty_indices = [i for i, val in enumerate(ui.session_state.board) if val == " "]
            ui.session_state.board[random.choice(empty_indices)] = "O"
    except Exception as e:
        empty_indices = [i for i, val in enumerate(ui.session_state.board) if val == " "]
        if empty_indices:
            ui.session_state.board[random.choice(empty_indices)] = "O"
        ui.session_state.ai_commentary = "My brain glitched, but I still made a move!"

    ui.session_state.winner = check_winner(ui.session_state.board)
    ui.session_state.turn = "X"

if ui.session_state.turn == "O" and ui.session_state.winner is None:
    with ui.spinner("AI is thinking..."):
        make_ai_move()

if ui.session_state.winner:
    if ui.session_state.winner == "Tie":
        ui.info("🤝 It's a Tie!")
    elif ui.session_state.winner == "X":
        ui.success("🏆 You won!")
    else:
        ui.error("🤖 The AI wins!")
else:
    ui.subheader(f"Current Turn: {ui.session_state.turn}")

ui.markdown(f"> **AI says:** *\"{ui.session_state.ai_commentary}\"*")

board = ui.session_state.board
cols = ui.columns(3)

for i in range(9):
    with cols[i % 3]:
        cell_val = board[i]
        button_label = cell_val if cell_val != " " else "  "
        is_disabled = (cell_val != " " or ui.session_state.winner is not None or ui.session_state.turn == "O")
        if ui.button(button_label, key=f"cell_{i}", use_container_width=True, disabled=is_disabled):
            make_move(i)
            ui.rerun()

ui.write("")
if ui.button("Reset Game Grid", type="primary"):
    reset_game()
    ui.rerun()
