import streamlit as st
import pickle
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.ensemble import RandomForestClassifier
from sklearn.tree import DecisionTreeClassifier

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

# Helper function to display login page
def login_page():
    st.title("Login Page")
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    
    if st.button("Login"):
        if username == "admin" and password == "password":  # Replace with actual login logic
            st.session_state['logged_in'] = True
            st.session_state['page'] = 'input'
        else:
            st.error("Invalid username or password")

# Helper function to display input page
def input_page():
    st.title("Personality Prediction")
    
    # Input form
    with st.form(key='input_form'):
        user_text = st.text_area("Enter the text", height=200)
        algo_choice = st.selectbox("Choose Algorithm", ['Decision Tree', 'Random Forest'])
        
        submit_button = st.form_submit_button("Predict")

    if submit_button:
        if len(user_text.split()) < 40:
            st.error("Error: Please enter at least 40 words in the text.")
        elif user_text.isdigit():
            st.error("Error: Please enter valid text (non-numeric).")
        else:
            # Store input and chosen algorithm in session state
            st.session_state['user_text'] = user_text
            st.session_state['algorithm'] = algo_choice
            st.session_state['page'] = 'output'
    
    # Add "Go Back" button to go back to the login page
    if st.button("Go Back"):
        # Reset session state and navigate back to the login page
        st.session_state['logged_in'] = False
        st.session_state['page'] = 'login'

# Helper function to display output page
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
    st.subheader("Prediction: " + class_names[prediction[0]])

    # Button to go back to input page
    if st.button("Go Back"):
        st.session_state['page'] = 'input'

# Main function to manage pages
def main():
    # Initialize session state
    if 'page' not in st.session_state:
        st.session_state['page'] = 'login'
    
    if st.session_state['page'] == 'login':
        login_page()
    elif st.session_state['page'] == 'input':
        input_page()
    elif st.session_state['page'] == 'output':
        output_page()

if __name__ == '__main__':
    main()
