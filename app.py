import streamlit as st
import random
import google.generativeai as ai

# Set up page layout and force a dark theme wrapper vibe
st.set_page_config(page_title="Neon AI Tic-Tac-Toe", layout="centered")

# --- CUSTOM FIXED 3x3 BLOCK CSS ---
st.markdown("""
    <style>
    /* Dark space background */
    .stApp {
        background-color: #0c0817 !important;
    }
    
    /* Center and style the heading elements */
    h1, h3, p, label, .stMarkdown {
        color: #fff !important;
        text-shadow: 0 0 8px #bc13fe !important;
        font-family: 'Courier New', Courier, monospace;
        text-align: center;
    }
    
    /* Outer glowing rectangular box holding the game grid */
    #tic_tac_toe_grid {
        border: 4px solid #bc13fe !important;
        border-radius: 16px !important;
        padding: 12px !important;
        background-color: #120e24 !important;
        max-width: 350px;
        margin: 0 auto;
        box-shadow: 0 0 20px rgba(188, 19, 254, 0.4) !important;
    }

    /* FORCES all 3 columns to stay side-by-side on mobile without dropping down */
    [data-testid="stHorizontalBlock"] {
        display: flex !important;
        flex-direction: row !important;
        flex-wrap: nowrap !important;
        gap: 8px !important;
        justify-content: center !important;
        width: 100% !important;
        margin: 0 auto !important;
    }
    
    /* Ensures each of the 3 columns takes exactly one-third of the screen width */
    [data-testid="column"] {
        width: 33.33% !important;
        flex: 1 1 33.33% !important;
        min-width: 0 !important;
    }

    /* Style the 9 game buttons to look like perfect square blocks */
    div.stButton > button {
        background-color: #1a1530 !important;
        border: 2px solid #5a3b8c !important; 
        border-radius: 12px !important;
        width: 100% !important;
        height: 90px !important; /* Perfect square-ish block height for phone screens */
        font-size: 38px !important; 
        font-weight: bold !important;
        font-family: 'Arial Black', sans-serif !important;
        transition: all 0.15s ease-in-out !important;
        padding: 0 !important;
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
    }

    /* Hover effect over the blocks */
    div.stButton > button:hover {
        border-color: #bc13fe !important;
        box-shadow: 0 0 12px #bc13fe !important;
    }

    /* Keep buttons clear when selected or disabled */
    div.stButton > button:disabled {
        background-color: #151026 !important;
        opacity: 1 !important;
    }
    </style>
""", unsafe_allow_html=True)

st.title("NEON MATRIX")
st.write("3x3 Game Board Active")

# --- SIDEBAR CONFIGURATION ---
with st.sidebar:
    st.header("⚙️ CONFIG")
    api_key = st.text_input("Enter your Gemini API Key", type="password")
    ai_vibe = st.selectbox(
        "AI Personality:",
        ["Sassy Trash-Talker", "Friendly Coach", "Evil Robot", "Confused Genius"]
    )
    if st.button("RESET GAME"):
        st.session_state.board = [" "] * 9
        st.session_state.current_turn = "X"
        st.session_state.game_over = False

# --- INITIALIZE GAME STATE ---
if "board" not in st.session_state:
    st.session_state.board = [" "] * 9
    st.session_state.current_turn = "X"
    st.session_state.game_over = False
    st.session_state.ai_comment = "Your move, human!"

def check_winner(b):
    lines = [[0,1,2], [3,4,5], [6,7,8], [0,3,6], [1,4,7], [2,5,8], [0,4,8], [2,4,6]]
    for line in lines:
        if b[line[0]] == b[line[1]] == b[line[2]] != " ":
            return b[line[0]]
    if " " not in b:
        return "Tie"
    return None

def get_ai_move(board_string):
    if not api_key:
        empty_cells = [i for i, val in enumerate(st.session_state.board) if val == " "]
        return random.choice(empty_cells) if empty_cells else None, "Offline mode active!"
    
    try:
        ai.configure(api_key=api_key)
        model = ai.GenerativeModel("gemini-1.5-flash")
        prompt = f"Tic-Tac-Toe 'O'. Board: {board_string}. Reply index only."
        response = model.generate_content(prompt).text
        return int(response.strip()), "Analyzed your move."
    except:
        empty_cells = [i for i, val in enumerate(st.session_state.board) if val == " "]
        return random.choice(empty_cells) if empty_cells else None, "Override protocol engaged!"

def make_move(idx):
    if st.session_state.board[idx] == " " and not st.session_state.game_over and st.session_state.current_turn == "X":
        st.session_state.board[idx] = "X"
        winner = check_winner(st.session_state.board)
        if winner:
            st.session_state.game_over = True
            return
            
        st.session_state.current_turn = "O"
        ai_idx, comment = get_ai_move(str(st.session_state.board))
        if ai_idx is not None and st.session_state.board[ai_idx] == " ":
            st.session_state.board[ai_idx] = "O"
            st.session_state.ai_comment = comment
        else:
            empty_cells = [i for i, val in enumerate(st.session_state.board) if val == " "]
            if empty_cells:
                st.session_state.board[random.choice(empty_cells)] = "O"
        
        winner = check_winner(st.session_state.board)
        if winner:
            st.session_state.game_over = True
        else:
            st.session_state.current_turn = "X"

# --- DISPLAY INTERFACE ---
st.subheader(f"TURN: {st.session_state.current_turn}")

# Outer rectangular bounding frame
st.markdown('<div id="tic_tac_toe_grid">', unsafe_allow_html=True)

# Build the 3x3 layout matrix
for row in range(3):
    cols = st.columns(3)
    for col in range(3):
        idx = row * 3 + col
        cell_value = st.session_state.board[idx]
        
        display_label = cell_value if cell_value != " " else " "
        
        with cols[col]:
            # Colors individual buttons when X or O is clicked to inject neon glowing text styles
            if cell_value == "X":
                st.markdown(f'<style>button[key="cell_{idx}"] div p {{ color: #00ffff !important; text-shadow: 0 0 15px #00ffff !important; }} button[key="cell_{idx}"] {{ border-color: #00ffff !important; box-shadow: 0 0 10px rgba(0,255,255,0.3) !important; }}</style>', unsafe_allow_html=True)
            elif cell_value == "O":
                st.markdown(f'<style>button[key="cell_{idx}"] div p {{ color: #ff007f !important; text-shadow: 0 0 15px #ff007f !important; }} button[key="cell_{idx}"] {{ border-color: #ff007f !important; box-shadow: 0 0 10px rgba(255,0,127,0.3) !important; }}</style>', unsafe_allow_html=True)
                
            st.button(
                label=display_label, 
                key=f"cell_{idx}", 
                on_click=make_move, 
                args=(idx,),
                disabled=st.session_state.game_over or cell_value != " "
            )

st.markdown('</div>', unsafe_allow_html=True)

# --- STATUS ALERTS ---
winner = check_winner(st.session_state.board)
if winner:
    st.session_state.game_over = True
    if winner == "Tie":
        st.info("DRAW MATCH")
    elif winner == "X":
        st.balloons()
        st.success("YOU WIN!")
    else:
        st.error("AI WINS!")

