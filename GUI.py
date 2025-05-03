import streamlit as st
from GA_class import GA

st.set_page_config(page_title="El Zozat's Tournament Scheduler", layout="centered")
st.markdown("""
    <style>
        .title {
            font-size: 30px;
            text-align: center;
            line-height: 1.5;
        }
        .schedule-table {
            width: 100%;
            border-collapse: collapse;
        }
        .schedule-table th, .schedule-table td {
            border: 1px solid #ddd;
            padding: 8px;
            text-align: center;
        }
        .schedule-table th {
            background-color: #f2f2f2;
        }
    </style>
    <div class="title">🚀 Welcome To El Zozat's Tournament Scheduler 👾</div>
""", unsafe_allow_html=True)

with st.sidebar:
    st.header("GA Settings 🤖")
    tournament_days = st.slider("Tournament Days", min_value=1, max_value=90, value=30)
    num_teams = st.number_input("Number of teams", min_value=1, max_value=50, value=10)
    num_venues = st.number_input("Number of venues", min_value=1, max_value=30, value=10)
    random_seed = st.number_input("Random Seed", min_value=0, max_value=10000000, value=42)
    selection_method = st.selectbox("Selection Method", ["tournament", "random"])
    crossover_method = st.selectbox("Crossover Method", ["uniform", "one_point"])
    mutation_method = st.selectbox("Mutation Method", ["swap", "reschedule"])
    survivor_method = st.selectbox("Survivor Method", ["steady-state", "generational", "elitism", "(μ + λ) selection"])
    run_ga = st.button("Run GA")

if run_ga:
    with st.spinner("Working On It 🤓!"):
        ga = GA(
            tournament_days=tournament_days,
            num_of_teams=num_teams,
            num_of_venues=num_venues,
            selection_method=selection_method,
            crossover_method=crossover_method,
            mutation_method=mutation_method,
            survivor_method=survivor_method,
            random_seed=random_seed
        )

        schedule, best_fitness, generation = ga.evolve()
        st.success(f"✅ Best fitness found in Generation {generation}")

        # --- Display Schedule as a Table ---
        st.header("📅 Tournament Schedule")
        

        # Display as a table
        st.table(schedule)


