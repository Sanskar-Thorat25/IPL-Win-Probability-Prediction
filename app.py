import pickle
import streamlit as st
import pandas as pd

# Page config
st.set_page_config(page_title="IPL Win Predictor", page_icon="🏏", layout="wide")

# Custom CSS for styling
st.markdown("""
    <style>
    .main {
        background-color: #0e1117;
        color: white;
    }
    h1 {
        text-align: center;
        color: #f9c74f;
    }
    .stButton>button {
        background-color: #f94144;
        color: white;
        border-radius: 10px;
        height: 3em;
        width: 100%;
    }
    </style>
""", unsafe_allow_html=True)

teams = ['Sunrisers Hyderabad', 'Mumbai Indians', 'Royal Challengers Bangalore',
         'Chennai Super Kings', 'Rajasthan Royals', 'Delhi Capitals',
         'Kolkata Knight Riders', 'Kings XI Punjab']

cities = ['Hyderabad', 'Bangalore', 'Mumbai', 'Indore', 'Kolkata', 'Delhi',
          'Chandigarh', 'Jaipur', 'Chennai', 'Cape Town', 'Port Elizabeth',
          'Durban', 'Centurion', 'East London', 'Johannesburg', 'Kimberley',
          'Bloemfontein', 'Ahmedabad', 'Cuttack', 'Nagpur', 'Dharamsala',
          'Visakhapatnam', 'Pune', 'Raipur', 'Ranchi', 'Abu Dhabi',
          'Sharjah', 'Mohali', 'Bengaluru']

pipe = pickle.load(open('pipe.pkl', 'rb'))

# Title
st.title("🏏 IPL Match Win Predictor")

st.markdown("### Enter Match Details")

# Layout
col1, col2 = st.columns(2)

with col1:
    batting_team = st.selectbox('🏏 Batting Team', sorted(teams))
with col2:
    bowling_team = st.selectbox('🎯 Bowling Team', sorted(teams))

selected_city = st.selectbox('📍 Match Location', sorted(cities))

# Target input
target = st.number_input('🎯 Target Score', min_value=1)

st.markdown("### Match Situation")

col3, col4, col5 = st.columns(3)

with col3:
    score = st.number_input('🏃 Current Score', min_value=0)
with col4:
    overs = st.number_input('⏱ Overs Completed', min_value=0.0, max_value=20.0, step=0.1)
with col5:
    wickets = st.number_input('❌ Wickets Fallen', min_value=0, max_value=10)

# Prediction
if st.button('🔮 Predict Win Probability'):

    if overs == 0:
        st.error("Overs cannot be 0")
    else:
        runs_left = target - score
        balls_left = 120 - (overs * 6)
        wickets_left = 10 - wickets
        crr = score / overs
        rrr = (runs_left * 6) / balls_left if balls_left != 0 else 0

        input_df = pd.DataFrame({
            'batting_team': [batting_team],
            'bowling_team': [bowling_team],
            'city': [selected_city],
            'runs_left': [runs_left],
            'balls_left': [balls_left],
            'wickets_left': [wickets_left],
            'total_runs_x': [target],
            'crr': [crr],
            'rrr': [rrr]
        })

        result = pipe.predict_proba(input_df)
        loss = result[0][0]
        win = result[0][1]

        st.markdown("## 📊 Match Prediction")

        col6, col7 = st.columns(2)

        with col6:
            st.subheader(batting_team)
            st.progress(int(win * 100))
            st.success(f"{round(win * 100)}% chance of winning")

        with col7:
            st.subheader(bowling_team)
            st.progress(int(loss * 100))
            st.error(f"{round(loss * 100)}% chance of winning")