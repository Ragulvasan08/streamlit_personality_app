import streamlit as st
import pickle
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.ensemble import RandomForestClassifier
from sklearn.tree import DecisionTreeClassifier
import streamlit.components.v1 as components
import time
import sqlite3
import hashlib
import base64

# Set page config at the very beginning
st.set_page_config(page_title="Personality Prediction App", page_icon="🧠", layout="centered")
def get_base64(bin_file):
    with open(bin_file, 'rb') as f:
        data = f.read()
    return base64.b64encode(data).decode()

def get_base64(file_path):
    with open(file_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')

def set_background(png_file):
    bin_str = get_base64(png_file)
    page_bg_img = f"""
    <style>
    .stApp {{
        background-image: url("data:image/png;base64,{bin_str}");
        background-size: cover;
        background-position: center;
        background-repeat: no-repeat;
        background-attachment: fixed;
    }}
    section.main {{
        background-color: transparent;
    }}
    .stApp > header {{
        background-color: transparent;
    }}
    </style>
    """
    st.markdown(page_bg_img, unsafe_allow_html=True)

# Usage
set_background(r"C:/Users/ragzv/OneDrive/Personality_app/01.jpg")

# Load the saved models and vectorizer
with open('tfidf_vectorizer.pkl', 'rb') as f:
    tfidf_vectorizer = pickle.load(f)
with open('random_forest_model.pkl', 'rb') as f:
    random_forest_model = pickle.load(f)
with open('decision_tree_model.pkl', 'rb') as f:
    decision_tree_model = pickle.load(f)

class_names = [
    'INFP personality No borderline_personality_disorder',
    'INFJ with borderline_personality_disorder',
    'INTP No borderline_personality_disorder',
    'INTJ No borderline_personality_disorder',
    'ENTP With borderline_personality_disorder'
]

# Custom CSS (updated)
st.markdown("""
<style>
    /* General text styles */
    body {
        color: #ffffff;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.5);
    }

    /* Button styles */
    .stButton > button {
        color: #ffffff;
        background-color: rgba(76, 175, 80, 0.8);
        border-radius: 5px;
        border: none;
        padding: 10px 24px;
        transition: all 0.3s ease 0s;
        font-size: 18px;
        font-weight: bold;
        text-shadow: 1px 1px 2px rgba(0,0,0,0.5);
    }
    .stButton > button:hover {
        background-color: rgba(69, 160, 73, 0.9);
    }

    /* Input field styles */
    .stTextInput > div > div > input, .stTextArea textarea {
        border-radius: 5px;
        font-size: 18px;
        font-weight: bold;
        color: #ffffff;
        background-color: rgba(0, 0, 0, 0.6);
        border: 1px solid rgba(255, 255, 255, 0.5);
        padding: 10px;
    }

    /* Label styles */
    .stTextInput > label, .stTextArea > label, .stSelectbox > label {
        color: #ffffff;
        font-weight: bold;
        font-size: 24px;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.7);
    }

    /* Alert styles */
    .stAlert {
        background-color: rgba(244, 67, 54, 0.8);
        color: #ffffff;
        padding: 10px;
        border-radius: 5px;
        font-size: 18px;
        font-weight: bold;
        text-shadow: 1px 1px 2px rgba(0,0,0,0.5);
    }

    /* Title and markdown text styles */
    .stTitle, .stMarkdown {
        font-size: 24px;
        font-weight: bold;
        color: #ffffff;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.7);
    }
    .stMarkdown h1, .stMarkdown h2, .stMarkdown h3 {
        font-size: 28px;
        color: #ffffff;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.7);
    }

    /* Selectbox styles */
    .stSelectbox > div > div > div {
        background-color: rgba(0, 0, 0, 0.6);
        color: #ffffff;
        font-size: 18px;
    }

    /* Specific styles for login and signup pages */
    .login-signup-label {
        font-size: 28px !important;
        margin-bottom: 10px;
    }

    /* Add a semi-transparent overlay to improve text readability */
    .stApp::before {
        content: "";
        position: absolute;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        background-color: rgba(0, 0, 0, 0.3);
        z-index: -1;
    }
    </style>
    """, unsafe_allow_html=True)

# Database functions
def init_db():
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS users
                 (username TEXT PRIMARY KEY, password TEXT)''')
    conn.commit()
    conn.close()

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def add_user(username, password):
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    hashed_password = hash_password(password)
    try:
        c.execute("INSERT INTO users VALUES (?, ?)", (username, hashed_password))
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False
    finally:
        conn.close()

def check_user(username, password):
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    hashed_password = hash_password(password)
    c.execute("SELECT * FROM users WHERE username=? AND password=?", (username, hashed_password))
    result = c.fetchone()
    conn.close()
    return result is not None
# Initialize the database
init_db()

# Helper function to display signup page
def signup_page():
    st.title("Sign Up")
    st.markdown("Create a new account")
    
    username = st.text_input("Username", key="signup_username")
    password = st.text_input("Password", type="password", key="signup_password")
    confirm_password = st.text_input("Confirm Password", type="password", key="signup_confirm_password")
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("Sign Up") or (password and confirm_password and st.session_state.signup_confirm_password != st.session_state.signup_confirm_password_prev):
            if password != confirm_password:
                st.error("Passwords do not match")
            elif len(password) < 6:
                st.error("Password must be at least 6 characters long")
            else:
                if add_user(username, password):
                    st.success("Account created successfully! Please log in.")
                    st.session_state['page'] = 'login'
                    st.rerun()
                else:
                    st.error("Username already exists")
    with col2:
        if st.button("Already have an account? Log In"):
            st.session_state['page'] = 'login'
            st.rerun()
    
    # Store the current confirm password value
    st.session_state.signup_confirm_password_prev = st.session_state.signup_confirm_password

# Helper function to display login page
def login_page():
    st.title("Personality Prediction App - Login")
    st.markdown('<p class="login-signup-label">Welcome to the Personality Prediction App. Please log in to continue.</p>', unsafe_allow_html=True)
    
    username = st.text_input("Username", key="login_username")
    password = st.text_input("Password", type="password", key="login_password")
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("Login") or (password and st.session_state.login_password != st.session_state.login_password_prev):
            if check_user(username, password):
                with st.spinner('Logging in...'):
                    time.sleep(1)  # Simulating login process
                st.success("Login successful!")
                st.session_state['logged_in'] = True
                st.session_state['username'] = username
                st.session_state['page'] = 'input'
                st.rerun()
            else:
                st.error("Invalid username or password")
    with col2:
        if st.button("Create an account"):
            st.session_state['page'] = 'signup'
            st.rerun()
    
    # Store the current password value
    st.session_state.login_password_prev = st.session_state.login_password


# Helper function to display input page (updated)
def input_page():
    st.title("Personality Prediction App")
    
    # New introduction section
    st.markdown("""
    <div style="font-size: 22px; font-weight: bold; color: #f0f0f0;">
        Welcome to the Personality Prediction App!<br><br>
        This application uses advanced machine learning algorithms to predict personality types 
        and assess the likelihood of borderline personality disorder based on text input.<br><br>
        <strong>How it works:</strong><br>
        Enter a text sample (minimum 40 words) in the text area below.<br>
        Choose between Decision Tree and Random Forest algorithms for prediction.<br>
        Click 'Predict' to see the results.<br><br>
        <strong>What we predict:</strong><br>
        MBTI Personality Types (INFP, INFJ, INTP, INTJ, ENTP)<br>
        Presence or absence of borderline personality disorder traits<br><br>
        Please note that this tool is for educational purposes only and should not be used as a substitute for professional medical advice or diagnosis.
    </div>
    """, unsafe_allow_html=True)
    st.text("")
    
    st.markdown(f"<div style='font-size: 25px; color: #F39C12;'>Welcome, {st.session_state['username']}! Enter your text below and choose an algorithm for personality prediction.</div>", unsafe_allow_html=True)
    
    user_text = st.text_area("Enter the text (minimum 40 words)", height=200,)
    algo_choice = st.selectbox("Choose Algorithm", ['Decision Tree', 'Random Forest'])
    
    
    col1, col2 = st.columns(2)
    with col1:
        predict_button = st.button("Predict", key="predict")
    with col2:
        go_back_button = st.button("Go Back", key="go_back")
    
    if predict_button:
        if len(user_text.split()) < 40:
            st.error("Error: Please enter at least 40 words in the text.")
        elif user_text.isdigit():
            st.error("Error: Please enter valid text (non-numeric).")
        else:
            with st.spinner('Analyzing...'):
                time.sleep(2)  # Simulating processing time
                st.session_state['user_text'] = user_text
                st.session_state['algorithm'] = algo_choice
                st.session_state['page'] = 'output'
                st.rerun()
    
    if go_back_button:
        st.session_state['page'] = 'login'
        st.rerun()

# Helper function to display output page (unchanged)
def output_page():
    st.title("Prediction Result")
    
    user_text = st.session_state['user_text']
    algorithm = st.session_state['algorithm']
    
    # Transform input text
    text_tfidf = tfidf_vectorizer.transform([user_text])
    
    # Predict based on chosen algorithm
    if algorithm == 'Random Forest':
        prediction = random_forest_model.predict(text_tfidf)
    else:
        prediction = decision_tree_model.predict(text_tfidf)
    
    # Display the result
    st.subheader("Prediction:")
    st.info(class_names[prediction[0]])
    
    st.subheader("Input Text:")
    st.text_area("", user_text, height=150, disabled=True)
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("Make Another Prediction", key="another_prediction"):
            st.session_state['page'] = 'input'
            st.rerun()
    with col2:
        if st.button("Logout", key="logout"):
            st.session_state['logged_in'] = False
            st.session_state['username'] = None
            st.session_state['page'] = 'login'
            st.rerun()

# Main function to manage pages
def main():
    # Initialize session state
    if 'page' not in st.session_state:
        st.session_state['page'] = 'login'
    if 'logged_in' not in st.session_state:
        st.session_state['logged_in'] = False
    if 'username' not in st.session_state:
        st.session_state['username'] = None
    
    if st.session_state['page'] == 'login':
        login_page()
    elif st.session_state['page'] == 'signup':
        signup_page()
    elif st.session_state['page'] == 'input' and st.session_state['logged_in']:
        input_page()
    elif st.session_state['page'] == 'output' and st.session_state['logged_in']:
        output_page()
    else:
        st.session_state['page'] = 'login'
        st.rerun()

if __name__ == '__main__':
    main()
