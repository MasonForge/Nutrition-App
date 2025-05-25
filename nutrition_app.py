import streamlit as st
import datetime
import math
import plotly.graph_objs as go

# ----- PAGE SETUP -----
st.title("Eat4Goals — Nutrition Calculator")
st.warning("⚠️ Disclaimer: This calculator is for general informational purposes only and is not intended to provide medical, nutritional, or dietary advice. Always consult a qualified health professional before making any changes to your diet, exercise routine, or wellness plan.")

# ----- UNIT SELECTION -----
units = st.radio("Units", ["Metric (kg/cm)", "Imperial (lbs/in)"])

# ----- INPUT FIELDS -----
gender = st.selectbox("Gender", ["Male", "Female"])
age = st.number_input("Age", min_value=10, max_value=100, value=30)

if units == "Imperial (lbs/in)":
    weight_lbs = st.number_input("Weight (lbs)", min_value=66.0, value=154.0)
    height_in = st.number_input("Height (inches)", min_value=48.0, value=68.0)
    weight = weight_lbs / 2.20462
    height = height_in * 2.54
else:
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

# ----- GOAL TIMING AND TARGET -----
start_date = st.date_input("Start Date", datetime.date.today())
end_date = st.date_input("Goal Date", datetime.date.today() + datetime.timedelta(days=60))
target_weight = st.number_input("Target Weight", min_value=30.0, value=weight, help="Use the same units as your original weight.")

# ----- CALCULATIONS -----
if gender == "Male":
    bmr = 10 * weight + 6.25 * height - 5 * age + 5
else:
    bmr = 10 * weight + 6.25 * height - 5 * age - 161

tdee = bmr * activity_levels[activity]
default_adjustment = 500  # kcal/day

# Calculate required calorie shift
weight_diff_kg = weight - target_weight
calorie_total = weight_diff_kg * 7700  # 7700 kcal per kg of fat
days_available = max((end_date - start_date).days, 1)
calorie_change_per_day = calorie_total / days_available
recommended_adjustment = -default_adjustment if goal == "Lose Weight" else default_adjustment

st.subheader("📊 Results")
st.write(f"BMR: **{int(bmr)} kcal/day**")
st.write(f"TDEE (Maintenance): **{int(tdee)} kcal/day**")

# ----- USER OVERRIDE -----
override = st.checkbox("Enable User Override")

if override:
    custom_adjust = st.number_input("Custom Calorie Adjustment per Day", value=int(calorie_change_per_day))
    st.warning("⚠️ User Override Active: You are manually adjusting your calorie goal. Please consult a qualified health professional before making any changes to your diet or nutrition plan.")
    final_target = tdee + custom_adjust
else:
    final_target = tdee + calorie_change_per_day

st.write(f"🎯 Target Daily Calories: **{int(final_target)} kcal/day**")

# ----- GRAPH: PROJECTED WEIGHT CHANGE -----
projected_weights = [weight - (calorie_change_per_day * d / 7700) for d in range(days_available + 1)]
dates = [start_date + datetime.timedelta(days=i) for i in range(days_available + 1)]

st.subheader("📈 Projected Weight Over Time")
fig = go.Figure()
fig.add_trace(go.Scatter(x=dates, y=projected_weights, mode='lines+markers', name='Projected Weight'))
fig.update_layout(yaxis_title="Weight (kg)", xaxis_title="Date", height=400)
st.plotly_chart(fig, use_container_width=True)
