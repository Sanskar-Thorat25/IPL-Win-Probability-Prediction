# IPL Win Probability Prediction 🏏

## Machine Learning–Powered IPL Match Analytics

The **IPL Win Probability Prediction** project is a machine learning web application that estimates the winning probabilities of two teams during the second innings of an Indian Premier League (IPL) cricket match.

The application uses a trained machine learning pipeline to analyze the current match situation and generate win probability estimates based on factors such as the batting team, bowling team, match venue, target score, current score, overs completed, and wickets fallen.

Built with **Python, Scikit-learn, Pandas, and Streamlit**, the project provides an interactive dashboard that transforms match information into easy-to-understand predictions and cricket analytics.

## Project Overview

Predicting the outcome of a cricket match is challenging because the situation changes with every run, wicket, and remaining delivery. This project uses historical match patterns and a trained machine learning model to estimate how likely each team is to win a match during a run chase.

The application provides a simple interface where users can enter the current match details, calculate the predicted winning probabilities, and explore important chase statistics.

The goal is to make cricket match analysis more interactive, accessible, and understandable through machine learning.

## Key Features

- **Machine Learning Predictions:** Uses a trained model pipeline to estimate the probability of winning for both teams.
- **Interactive Match Inputs:** Select the batting team, bowling team, venue, target score, current score, overs completed, and wickets fallen.
- **Win Probability Gauges:** Displays the estimated winning probabilities using animated semicircular speedometer-style gauges.
- **Match Analytics Dashboard:** Shows the target, current score, runs required, balls remaining, wickets remaining, current run rate, and required run rate.
- **Dynamic Team Branding:** Uses team-specific colours and team logo assets to distinguish the teams.
- **Dark and Light Modes:** Provides two visual themes for a comfortable viewing experience.
- **Stadium Backgrounds:** Uses separate stadium backgrounds for dark and light themes.
- **Responsive Interface:** Organizes the inputs and results into a dashboard designed to work across different screen sizes.
- **Prediction Results:** Highlights the team with the higher estimated probability of winning.
- **Real-Time Input Updates:** Updates the displayed match calculations when the input values change.

## How the Application Works

The prediction process follows these steps:

1. **Enter Match Details:** Select both teams, the venue, target score, current score, overs completed, and wickets fallen.
2. **Calculate Match Features:** The application derives additional statistics from the supplied match information.
3. **Prepare Model Inputs:** The calculated values and categorical inputs are assembled into a Pandas DataFrame containing the features expected by the trained pipeline.
4. **Generate Predictions:** The application calls the trained model's `predict_proba()` method to obtain the class probabilities.
5. **Display Results:** The dashboard presents the estimated win probabilities and the current chase statistics.

## Input Features

The application collects the following information from the user.

| Input | Description |
|---|---|
| Batting Team | The team currently chasing the target |
| Bowling Team | The opposing team defending the target |
| Venue | The city where the match is played |
| Target Score | The score the batting team needs to reach |
| Current Score | The runs scored by the batting team |
| Overs Completed | The overs entered for the current innings |
| Wickets Fallen | The number of wickets lost by the batting team |

## Features Calculated by the Application

The following derived features are passed to the trained machine learning pipeline:

| Feature | Description |
|---|---|
| `batting_team` | Selected batting team |
| `bowling_team` | Selected bowling team |
| `city` | Selected match venue's city value |
| `runs_left` | Target score minus current score |
| `balls_left` | Remaining balls, calculated using the application's existing formula |
| `wickets_left` | Ten minus wickets fallen |
| `total_runs_x` | Target score supplied to the model |
| `crr` | Current run rate |
| `rrr` | Required run rate |

The current implementation calculates these numerical features using the following formulas:

- **Runs Left** = Target Score − Current Score
- **Balls Left** = 120 − (Overs Completed × 6)
- **Wickets Left** = 10 − Wickets Fallen
- **Current Run Rate (CRR)** = Current Score ÷ Overs Completed
- **Required Run Rate (RRR)** = (Runs Left × 6) ÷ Balls Left

The formulas above describe the current application implementation. The overs calculation assumes decimal overs, so the model's training conventions should be checked before changing how overs are entered or interpreted.

## Output and Analytics

After the user calculates a prediction, the application displays:

### 1. Win Probability

Two semicircular gauges display the model's estimated probabilities for the batting and bowling teams. The gauges use different team colours and animated progress arcs to make the results easy to compare.

### 2. Match Situation

The dashboard displays the current score, target, runs required, balls remaining, and wickets remaining.

### 3. Run Rate Analysis

The application calculates and displays:

- **Current Run Rate (CRR):** The batting team's current scoring rate.
- **Required Run Rate (RRR):** The scoring rate required to reach the target within the remaining balls.

These statistics help users understand the demands of the chase.

### 4. Predicted Favourite

The application highlights the team with the higher estimated winning probability. The prediction is a model-generated estimate, not a guarantee of the actual match result.

## Technology Stack

| Technology | Purpose |
|---|---|
| Python | Core programming language |
| Pandas | Preparing input data for the machine learning model |
| Scikit-learn | Machine learning pipeline and probability prediction |
| Streamlit | Interactive web application and dashboard |
| HTML and CSS | Interface styling, gauges, animations, and theme layouts |
| SVG | Semicircular gauges, icons, and vector graphics |
| Pickle | Loading the serialized trained model pipeline |

## Project Structure

```text
IPL-Win-Probability-Prediction/
│
├── app.py
│   └── Streamlit application and prediction interface
│
├── pipe.pkl
│   └── Trained machine learning pipeline
│
├── requirements.txt
│   └── Python dependencies
│
├── stadium_dark.webp
│   └── Stadium background for dark mode
│
├── stadium_light.webp
│   └── Stadium background for light mode
│
├── IPL Probability Prediction.ipynb
│   └── Model development and experimentation notebook
│
├── Procfile
│   └── Process configuration for supported deployments
│
└── README.md
    └── Project documentation
```

## Installation and Setup

### Prerequisites

- Python installed on your system
- pip package manager
- Git, if you want to clone the repository
- The trained `pipe.pkl` model file

### Step 1: Clone the repository

```bash
git clone https://github.com/Sanskar-Thorat25/IPL-Win-Probability-Prediction.git
```

### Step 2: Open the project directory

```bash
cd IPL-Win-Probability-Prediction
```

### Step 3: Install dependencies

```bash
pip install -r requirements.txt
```

### Step 4: Run the application

```bash
streamlit run app.py
```

Streamlit will start the application and display a local URL in the terminal. Open that URL in your web browser to use the prediction dashboard.

## Model and Prediction Notes

The application loads the existing trained pipeline from `pipe.pkl`. For successful predictions, the pipeline must be compatible with the model input features and the categorical values provided by the application.

The interpretation of the probability classes must match the trained model's class ordering. The application currently assumes that the second probability value corresponds to the batting team and the first corresponds to the bowling team.

The accuracy of predictions depends on the training data, feature engineering, model performance, and quality of the input values.

## Future Enhancements

Potential improvements for future versions include:

- Integrating live IPL match data through an appropriate data source.
- Expanding support for teams and historical seasons.
- Improving model evaluation and probability calibration.
- Adding match history and prediction comparison.
- Visualizing changes in win probability over the course of an innings.
- Deploying the application for public access.

These are possible future improvements and are not necessarily implemented in the current version.

## Limitations

- Predictions depend on the trained model and its training data.
- The application currently focuses on second-innings chase scenarios.
- Live match information is not automatically fetched by the current input-based workflow.
- Incorrect or unrealistic inputs may produce misleading estimates.
- The model's output should not be interpreted as a guaranteed match outcome.

## Author

**Sanskar Thorat**

GitHub: [Sanskar-Thorat25](https://github.com/Sanskar-Thorat25)

## Disclaimer

This project is developed for educational purposes and machine learning experimentation. The predicted probabilities represent model estimates and should not be treated as guaranteed results or professional betting advice.

---

**IPL Win Probability Prediction — Bringing machine learning and cricket analytics together.**