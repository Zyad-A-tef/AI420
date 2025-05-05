import pandas as pd
import matplotlib.pyplot as plt
import datetime
import os
import streamlit as st

def Save_results_to_csv(schedule , inputs , fitness_history ):

    # save the results to a pandas df 1st 
    df = pd.DataFrame(schedule)

    df2 = pd.DataFrame(fitness_history)

    df3 = pd.DataFrame([inputs])

    

    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")

    # save to csv

    try:
        # create the dir if it doesn't exist
        os.makedirs("Results", exist_ok=True)

        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        save_dir = os.path.join("Results", timestamp)
        
        # create the sub dir
        os.makedirs(save_dir, exist_ok=True)

        df.to_csv(f"Results/{timestamp}/schedule.csv" , index=False)
        df2.to_csv(f"Results/{timestamp}/fitness_history.csv" , header=['fitness_history'] , index=False)
        df3.to_csv(f"Results/{timestamp}/inputs.csv" , index=False)
        return True
    
    except Exception as e:
        print("Weak ass shit, couldn't save please Try Again !")
        st.error(f"Save failed: {str(e)}", icon="🚨")
        return False
    


# TODO : the fitness history Graph function (ana matet walahy hkml bokra) ----> COMPLETED

def Fitness_history_plot(fitness_history , best_fitness , gene):

    # Plot Fitness History
        fig, ax = plt.subplots()
        ax.plot(fitness_history, label="Fitness", color="blue")
        ax.axvline(gene, linestyle="--", color="red",
                    label=f"Best Fitness at Generation: {gene}")
        # Horizontal line at best fitness value
        ax.axhline(best_fitness, linestyle="--", color="green", 
           label=f"Best Fitness Value: {best_fitness:.2f}")
        ax.set_xlabel("Generation")
        ax.set_ylim(bottom= min(fitness_history)-50 , top=max(fitness_history))
        ax.set_ylabel("Fitness Score (Lower = Better)")
        ax.set_title("GA Training Progress")
        ax.legend()
        ax.grid()
        st.pyplot(fig)



def load_data_from_csv():
    # Get all saved results
    saved_runs = []
    if os.path.exists("Results"):
        saved_runs = sorted([d for d in os.listdir("Results") if os.path.isdir(os.path.join("Results", d))], reverse=True)
    
    if len(saved_runs) < 2:
        st.warning("No saved runs found or not enough runs to compare. Run and save at least 2 schedules.")
        return None, None
    
    # Let user select which runs to compare
    cols = st.columns(2)
    with cols[0]:
        run1_id = st.selectbox("Select first run", saved_runs, key="select_run1")
    with cols[1]:
        run2_id = st.selectbox("Select second run", [r for r in saved_runs if r != run1_id], key="select_run2")

    if st.button("Compare selected Runs"):
        st.session_state.compared_run1 = load_run(run1_id)
        st.session_state.compared_run2 = load_run(run2_id)
        st.session_state.show_comparison = True
    
    if "show_comparison" in st.session_state and st.session_state.show_comparison:
        return st.session_state.compared_run1, st.session_state.compared_run2
    
    return None, None


def load_run(run_id):
    base_path = os.path.join("Results", run_id)

    run = {
        "schedule" : pd.read_csv(os.path.join(base_path, "schedule.csv")),
        "inputs"   : pd.read_csv(os.path.join(base_path, "inputs.csv")).iloc[0].to_dict(),
        "fitness"  : pd.read_csv(os.path.join(base_path, "fitness_history.csv"))
    }


    return run




### testing 


# run = load_run("20250505_043057")


# print(run['inputs'])