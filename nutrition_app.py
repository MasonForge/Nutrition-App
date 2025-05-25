import streamlit as st
import datetime
import plotly.graph_objs as go

# ----- PAGE SETUP -----
st.title("Eat4Goals — Nutrition Calculator")
st.warning("⚠️ Disclaimer: This calculator is for general informational purposes only and is not intended to provide medical, nutritional, or dietary advice. Always consult a qualified health professional before making any changes to your diet, exercise routine, or wellness plan. **Some numbers are rounded for clarity and may not reflect exact daily fluctuations.**")

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
    display_weight = weight_lbs
    weight_unit = "lbs"
else:
    weight = st.number_input("Weight (kg)", min_value=30.0, value=70.0)
    height = st.number_input("Height (cm)", min_value=100.0, value=175.0)
    display_weight = weight
    weight_unit = "kg"

activity_levels = {
    "Sedentary (little/no exercise)": 1.2,
    "Light (1–3 days/week)": 1.375,
    "Moderate (3–5 days/week)": 1.55,
    "Active (6–7 days/week)": 1.725,
    "Very active (physical job + exercise)": 1.9
}
activity = st.selectbox("Activity Level", list(activity_levels.keys()))

goal = st.radio("Goal", ["Maintain", "Lose Weight", "Gain Muscle"])
target_weight = st.number_input(f"Target Weight ({weight_unit})", min_value=30.0, value=display_weight)
override = st.checkbox("Enable User Override")

# ----- BMR & TDEE -----
if gender == "Male":
    bmr = 10 * weight + 6.25 * height - 5 * age + 5
else:
    bmr = 10 * weight + 6.25 * height - 5 * age - 161

tdee = bmr * activity_levels[activity]
default_adjustment = -500 if goal == "Lose Weight" else 500

st.subheader("📊 Results")
st.write(f"BMR: **{int(bmr)} kcal/day**")
st.write(f"TDEE (Maintenance): **{int(tdee)} kcal/day**")

# Convert target weight to kg if needed
if units == "Imperial (lbs/in)":
    target_weight_kg = target_weight / 2.20462
else:
    target_weight_kg = target_weight

# Init for graph
dates = []
projected_weights = []

# ----- OVERRIDE MODE -----
if override:
    start_date = st.date_input("Start Date", datetime.date.today())
    goal_date = st.date_input("Goal Date", start_date + datetime.timedelta(days=60))
    days_available = max((goal_date - start_date).days, 1)

    weight_diff_kg = target_weight_kg - weight
    calorie_total = weight_diff_kg * 7700
    calorie_change_per_day = calorie_total / days_available
    target_calories = tdee + calorie_change_per_day

    st.warning("⚠️ User Override Active: You are manually adjusting your calorie goal.")
    st.write(f"🎯 To reach **{target_weight:.1f} {weight_unit}** by **{goal_date.strftime('%b %d, %Y')}**, you need to eat **{int(target_calories)} kcal/day**")

    projected_weights = [weight + (calorie_change_per_day * d / 7700) for d in range(days_available + 1)]
    if units == "Imperial (lbs/in)":
        projected_weights = [w * 2.20462 for w in projected_weights]
    dates = [start_date + datetime.timedelta(days=i) for i in range(days_available + 1)]

# ----- DEFAULT MODE -----
else:
    weight_diff_kg = target_weight_kg - weight
    calorie_total = weight_diff_kg * 7700
    calorie_change_per_day = default_adjustment
    days_needed = int(abs(calorie_total / default_adjustment)) if default_adjustment != 0 else 0
    end_date = datetime.date.today() + datetime.timedelta(days=days_needed)
    target_calories = tdee + default_adjustment

    st.write(f"🎯 At **{abs(default_adjustment)} kcal/day**, you’ll reach **{target_weight:.1f} {weight_unit}** in approximately **{days_needed} days** (~{end_date.strftime('%b %d, %Y')})")

    projected_weights = [weight + (default_adjustment * d / 7700) for d in range(days_needed + 1)]
    if units == "Imperial (lbs/in)":
        projected_weights = [w * 2.20462 for w in projected_weights]
    dates = [datetime.date.today() + datetime.timedelta(days=i) for i in range(days_needed + 1)]

# ----- GRAPH -----
st.subheader("📈 Projected Weight Over Time")
fig = go.Figure()
fig.add_trace(go.Scatter(x=dates, y=projected_weights, mode='lines+markers', name='Projected Weight'))
fig.update_layout(yaxis_title=f"Weight ({weight_unit})", xaxis_title="Date", height=400)
st.plotly_chart(fig, use_container_width=True)

# ----- MACRONUTRIENT BREAKDOWN -----
st.subheader("🥦 Macronutrient Breakdown")

macro_mode = st.selectbox(
    "Select Macro Strategy",
    ["NASM (Default)", "Mentzer (60/25/15)", "High-Protein (35/35/30)", "Keto (10/20/70)", "Custom"]
)

# Set macro split by preset
if macro_mode == "NASM (Default)":
    protein_pct, carb_pct, fat_pct = 20, 50, 30
elif macro_mode == "Mentzer (60/25/15)":
    protein_pct, carb_pct, fat_pct = 25, 60, 15
elif macro_mode == "High-Protein (35/35/30)":
    protein_pct, carb_pct, fat_pct = 35, 35, 30
elif macro_mode == "Keto (10/20/70)":
    protein_pct, carb_pct, fat_pct = 20, 10, 70
else:
    st.info("Customize your macronutrient percentages below.")
    protein_pct = st.slider("Protein %", 0, 100, 25)
    carb_pct = st.slider("Carbohydrates %", 0, 100, 50)
    fat_pct = st.slider("Fats %", 0, 100, 25)

total_pct = protein_pct + carb_pct + fat_pct
if total_pct != 100:
    st.error("Macronutrient percentages must add up to 100%. Please adjust your sliders.")
else:
    protein_kcal = (protein_pct / 100) * target_calories
    carb_kcal = (carb_pct / 100) * target_calories
    fat_kcal = (fat_pct / 100) * target_calories

    protein_g = protein_kcal / 4
    carb_g = carb_kcal / 4
    fat_g = fat_kcal / 9

    st.markdown(f"""
    **Daily Targets:**
    - 🥩 Protein: **{int(protein_g)}g** ({int(protein_kcal)} kcal)
    - 🍞 Carbs: **{int(carb_g)}g** ({int(carb_kcal)} kcal)
    - 🥑 Fats: **{int(fat_g)}g** ({int(fat_kcal)} kcal)
    """)

    # ----- MEAL MACRO PLANNER -----
    st.subheader("🍽️ Generate Meal Macros Plan")
    meals_per_day = st.selectbox("How many meals per day?", [1, 2, 3, 4, 5, 6], index=2)

    meal_protein = protein_g / meals_per_day
    meal_carb = carb_g / meals_per_day
    meal_fat = fat_g / meals_per_day
    meal_calories = target_calories / meals_per_day

    st.markdown(f"""
    **Per Meal (~{meals_per_day} meals/day):**
    - 🔹 Calories: **{int(meal_calories)} kcal**
    - 🔹 Protein: **{round(meal_protein, 1)}g**
    - 🔹 Carbs: **{round(meal_carb, 1)}g**
    - 🔹 Fats: **{round(meal_fat, 1)}g**
    """)
