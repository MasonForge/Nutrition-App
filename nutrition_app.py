import streamlit as st

st.title("Nutrition Calculator (BMR, TDEE, TEF, PDCAAS)")

# Basic input
gender = st.selectbox("Gender", ["Male", "Female"])
age = st.number_input("Age", min_value=10, max_value=100, value=30)
weight = st.number_input("Weight (kg)", min_value=30.0, value=70.0)
height = st.number_input("Height (cm)", min_value=100.0, value=175.0)

activity_levels = {
    "Sedentary (little/no exercise)": 1.2,
    "Light (1–3 days/week)": 1.375,
    "Moderate (3–5 days/week)": 1.55,
    "Active (6–7 days/week)": 1.725,
    "Very active (physical job + exercise)": 1.9
}
activity = st.selectbox("Activity Level", list(activity_levels.keys()))
goal = st.radio("Goal", ["Maintain", "Lose Weight", "Gain Muscle"])

# Calculate BMR
if gender == "Male":
    bmr = 10 * weight + 6.25 * height - 5 * age + 5
else:
    bmr = 10 * weight + 6.25 * height - 5 * age - 161

tdee = bmr * activity_levels[activity]
if goal == "Lose Weight":
    goal_cals = tdee - 500
elif goal == "Gain Muscle":
    goal_cals = tdee + 500
else:
    goal_cals = tdee

st.subheader("📊 Results")
st.write(f"BMR: **{int(bmr)} kcal/day**")
st.write(f"TDEE: **{int(tdee)} kcal/day**")
st.write(f"Target Calories for Goal: **{int(goal_cals)} kcal/day**")
