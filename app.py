import streamlit as st
import random
import google.generativeai as ai

# Set up page layout to be compact
st.set_page_config(page_title="AI Tic-Tac-Toe", layout="centered")

st.title("❌ AI-Powered Tic-Tac-Toe ⭕")
st.write("Play against a Gemini-powered AI opponent!")

# --- SIDEBAR FOR CONFIGURATION ---
with st.sidebar:
    st.header("⚙️ Game Settings")
    api_key = st.text_input("Enter your Gemini API Key", type="password")
    ai_vibe = st.selectbox(
        "Choose the AI's personality:",
        ["Sassy Trash-Talker", "Friendly Coach", "Evil Robot", "Confused Genius"]
    )
    if st.button("Reset Game"):
        st.session_state.board = [" "] * 9
        st.session_state.current_turn = "X"
        st.session_state.game_over = False

# --- INITIALIZE GAME STATE ---
if "board" not in st.session_state:
    st.session_state.board = [" "] * 9
    st.session_state.current_turn = "X"
    st.session_state.game_over = False
    st.session_state.ai_comment = "Your move, human!"

# --- HELPER FUNCTIONS ---
def check_winner(b):
    lines = [[0,1,2], [3,4,5], [6,7,8], [0,3,6], [1,4,7], [2,5,8], [0,4,8], [2,4,6]]
    for line in lines:
        if b[line[0]] == b[line[1]] == b[line[2]] != " ":
            return b[line[0]]
    if " " not in b:
        return "Tie"
    return None

def get_ai_move(board_string):
    # Fallback to random move if no API key
    if not api_key:
        empty_cells = [i for i, val in enumerate(st.session_state.board) if val == " "]
        return random.choice(empty_cells) if empty_cells else None, "My brain glitched, but I still made a move!"
    
    try:
        ai.configure(api_key=api_key)
        model = ai.GenerativeModel("gemini-1.5-flash")
        
        prompt = f"""
        You are playing a game of Tic-Tac-Toe as 'O'. The current board state is represented by a list of 9 elements where indices 0-8 represent the board grid from top-left to bottom-right:
        Current Board: {board_string}
        
        Your personality trait for this game is: '{ai_vibe}'.
        
        Analyze the board and find the best strategic index (0 to 8) that is currently empty (" ").
        Respond EXACTLY in this format with no extra text or markdown:
        INDEX: <number>
        COMMENT: <a short, one-sentence trash-talk or friendly remark matching your personality>
        """
        response = model.generate_content(prompt).text
        
        # Parse response safely
        idx = 0
        comment = "Your turn!"
        for line in response.split('\n'):
            if "INDEX:" in line:
                idx = int(line.split(":")[1].strip())
            if "COMMENT:" in line:
                comment = line.split(":")[1].strip()
        return idx, comment
    except:
        empty_cells = [i for i, val in enumerate(st.session_state.board) if val == " "]
        return random.choice(empty_cells) if empty_cells else None, "I'm moving purely on instinct right now!"

# --- HANDLING PLAYER MOVE ---
def make_move(idx):
    if st.session_state.board[idx] == " " and not st.session_state.game_over and st.session_state.current_turn == "X":
        # Human Move
        st.session_state.board[idx] = "X"
        
        winner = check_winner(st.session_state.board)
        if winner:
            st.session_state.game_over = True
            return
            
        # AI Turn
        st.session_state.current_turn = "O"
        with st.spinner("AI is thinking..."):
            ai_idx, comment = get_ai_move(str(st.session_state.board))
            if ai_idx is not None and st.session_state.board[ai_idx] == " ":
                st.session_state.board[ai_idx] = "O"
                st.session_state.ai_comment = comment
            else:
                # Emergency random fallback if AI picks taken slot
                empty_cells = [i for i, val in enumerate(st.session_state.board) if val == " "]
                if empty_cells:
                    st.session_state.board[random.choice(empty_cells)] = "O"
        
        winner = check_winner(st.session_state.board)
        if winner:
            st.session_state.game_over = True
        else:
            st.session_state.current_turn = "X"

# --- RENDER THE $3 \times 3$ SQUARE BLOCK GRID ---
st.subheader(f"Current Turn: {st.session_state.current_turn}")
st.info(f"🤖 AI says: {st.session_state.ai_comment}")

# Custom CSS to make buttons look big and square
st.markdown("""
    <style>
    div.stButton > button {
        width: 100% !important;
        height: 80px !important;
        font-size: 24px !important;
        font-weight: bold !important;
    }
    </style>
""", unsafe_allow_html=True)

# Create the rows and columns for the square block
for row in range(3):
    cols = st.columns(3)  # This creates 3 side-by-side columns
    for col in range(3):
        idx = row * 3 + col
        cell_value = st.session_state.board[idx]
        
        # Display X, O, or blank button
        with cols[col]:
            st.button(
                label=cell_value if cell_value != " " else "  ", 
                key=f"cell_{idx}", 
                on_click=make_move, 
                args=(idx,),
                disabled=st.session_state.game_over or cell_value != " "
            )

# --- GAME OVER MESSAGES ---
winner = check_winner(st.session_state.board)
if winner:
    st.session_state.game_over = True
    if winner == "Tie":
        st.success("🤝 It's a draw/tie!")
    elif winner == "X":
        st.balloons()
        st.success("🎉 Incredible! You beat the AI!")
    else:
        st.error("💀 The AI won! Better luck next time.")

