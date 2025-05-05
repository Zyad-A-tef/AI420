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
    


# TODO : the fitness history Graph function (ana matet walahy hkml bokra)
        