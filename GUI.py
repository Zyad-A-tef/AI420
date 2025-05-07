import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from GA_class import GA
from Utilities import *

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
    
    game_name = st.selectbox("Game Name", ["champions_league", "NBA"])
    
    match_duration = st.number_input("Match Duration", min_value=1, max_value=10, value=2)
    rest = st.number_input("Venue Maintenance", min_value=1, max_value=20, value=1)
    max_matches_per_day = st.number_input("Max Matches/Day", min_value=1, max_value=20, value=4)
    
    num_teams = st.number_input("Number Of Teams", min_value=1, max_value=50, value=10)
    num_venues = st.number_input("Number Of Venues", min_value=1, max_value=30, value=3)
    random_seed = st.number_input("Random Seed", min_value=0, max_value=10000000, value=42)

    selection_method = st.selectbox("Selection Method", ["tournament", "random"])
    crossover_method = st.selectbox("Crossover Method", ["uniform", "one_point"])
    mutation_method = st.selectbox("Mutation Method", ["swap", "reschedule"])
    survivor_method = st.selectbox("Survivor Method", ["steady-state", "generational", "elitism", "(μ + λ) selection"])
    
    run_ga = st.button("Run GA")


if run_ga:
    with st.spinner("Working On It 🤓!"):
        ga = GA(
            tournament_days      = tournament_days,
 
            num_of_teams         = num_teams,
            num_of_venues        = num_venues,
             
            match_duration       = match_duration,
            venue_rest           = rest,
            max_matches_per_day  = max_matches_per_day,
             
            selection_method     = selection_method,
            crossover_method     = crossover_method,
            mutation_method      = mutation_method,
            survivor_method      = survivor_method,
            random_seed          = random_seed,
             
            game_name            =  game_name
        )

        schedule, best_fitness, generation = ga.evolve()
        st.success(f"✅ Best fitness found in Generation {generation}")

        # Store GA data in session state to persist across tabs
        st.session_state.schedule = schedule
        st.session_state.fitness_history = ga.fitness_history
        st.session_state.best_fitness = best_fitness
        st.session_state.generation = generation

        # save inputs into session 
        st.session_state.input = {"Game Name": game_name, "Tournament Days":tournament_days , "Number of teams" : num_teams , "Number of venues":num_venues , 
                                  "Selection Method":selection_method ,"Crossover Method":crossover_method , 
                                  "Mutation Method":mutation_method ,"Survivor Method":survivor_method , 
                                  "Random Seed":random_seed , "Max number of matches per day" : max_matches_per_day,
                                  "Venue Rest Period" : rest , "Match Duration" : match_duration}

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

        Fitness_history_plot(st.session_state.fitness_history , st.session_state.best_fitness , st.session_state.generation)



with tab3:
    st.header("🧐 Compare Results")
    
    # Initialize variables
    run1 = None
    run2 = None
    
    # Only try to load if we have runs to compare
    run1, run2 = load_data_from_csv()


    if run1 is not None and run2 is not None:
        # Display comparison only if we have valid data
        st.subheader("Side-by-Side Comparison")

        best_fitness1 = float(run1['fitness'].min())  # Force single float
        gene1 = int(run1['fitness'].idxmin()) + 1                 # Convert to 1-based as integer

        best_fitness2 = float(run2['fitness'].min())  # Force single float
        gene2 = int(run2['fitness'].idxmin()) + 1 
        # meta data 

        st.write("### Configuration")
        meta_cols = st.columns(2)
        with meta_cols[0]:
            st.json(run1["inputs"])
        with meta_cols[1]:
            st.json(run2["inputs"]) 
    
        # Schedule comparison
        st.write("### Schedules")
        sched_cols = st.columns(2)
        with sched_cols[0]:
            st.write("**Run 1**")
            st.table(run1['schedule'])
            # Plot
            plot_fitness_history(
                fitness_data=run1['fitness'], 
                best_fitness=best_fitness1,
                best_gene=gene1,
                title="Run 1 Fitness Evolution"
            )
        with sched_cols[1]:
            st.write("**Run 2**")
            st.table(run2['schedule'])
            # Plot
            plot_fitness_history(
                fitness_data=run2['fitness'], 
                best_fitness=best_fitness2,
                best_gene=gene2,
                title="Run 2 Fitness Evolution"
            )
        
        # Add a button to clear the comparison
        if st.button("Clear Comparison"):
            if "compared_run1" in st.session_state:
                del st.session_state.compared_run1
            if "compared_run2" in st.session_state:
                del st.session_state.compared_run2
            st.session_state.show_comparison = False
            st.experimental_rerun()
