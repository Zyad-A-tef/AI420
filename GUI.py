import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from GA_class import GA
from utilities import Save_results_to_csv

st.set_page_config(page_title="El Zozat's Tournament Scheduler", layout="centered")

st.markdown("""
    <style>
        .title {
            font-size: 30px;
            text-align: center;
            line-height: 1.5;
        }
        .tab-container {
            margin-top: 20px;
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

        # Store GA data in session state to persist across tabs
        st.session_state.schedule = schedule
        st.session_state.fitness_history = ga.fitness_history
        st.session_state.best_fitness = best_fitness
        st.session_state.generation = generation

        # save inputs into session 
        st.session_state.input = {"Tournament Days":tournament_days , "Number of teams" : num_teams , "Number of venues":num_venues , 
                                  "Selection Method":selection_method ,"Crossover Method":crossover_method , 
                                  "Mutation Method":mutation_method ,"Survivor Method":survivor_method , 
                                  "Random Seed":random_seed}

# tabs
tab1, tab2  , tab3 = st.tabs(["📅 Schedule", "📊 Graphs" , "🧐Compare between Results"])

# Tab 1: Schedule
with tab1:
    if run_ga and "schedule" in st.session_state:
        st.header("Tournament Schedule")
        st.table(st.session_state.schedule)

    if st.button("Save Results ? 🤔" , key="save_results_btn"):

        if Save_results_to_csv(st.session_state.schedule , st.session_state.input , st.session_state.fitness_history):
            st.success("Saved results successfully🥳")
            st.table(st.session_state.schedule)
        else:
            st.error("Nah Try again broski we couldn't save it", icon="🚨")
            st.table(st.session_state.schedule)

# Tab 2: Graphs
with tab2:
    if run_ga and "fitness_history" in st.session_state:
        st.header("Fitness Evolution")
        
        # Plot Fitness History
        fig, ax = plt.subplots()
        ax.plot(st.session_state.fitness_history, label="Fitness", color="blue")
        ax.axvline(st.session_state.generation, linestyle="--", color="red",
                    label=f"Best Fitness at Generation: {st.session_state.generation}")
        # Horizontal line at best fitness value
        ax.axhline(st.session_state.best_fitness, linestyle="--", color="green", 
           label=f"Best Fitness Value: {st.session_state.best_fitness:.2f}")
        ax.set_xlabel("Generation")
        ax.set_ylim(bottom= min(st.session_state.fitness_history)-50 , top=max(st.session_state.fitness_history))
        ax.set_ylabel("Fitness Score (Lower = Better)")
        ax.set_title("GA Training Progress")
        ax.legend()
        ax.grid()
        st.pyplot(fig)

# TODO : finish the rest of Tab3 to compare between the saved resuts : 
"""
    1 - read the results from the Folder called results each one saved with a unqiue name (timestamp)
    2 - show all the info with the graph of each result in the compare tab 
    3 - KYS
"""

# # Compare tab

# with tab3 : 

#     if run_ga