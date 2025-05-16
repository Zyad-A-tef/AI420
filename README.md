# El Zowzat's Tournament Scheduler 👾

##  Project Overview

El Zowzat's Tournament Scheduler is a powerful and flexible tool designed to generate optimized tournament schedules using a sophisticated Genetic Algorithm (GA). It is built using Streamlit for an intuitive user interface and offers a wide range of customization options for the Genetic Algorithm settings.

##  Evalutions Steps

* **Flexible Genetic Algorithm Customization:**

  * Initialization Methods:

    * **Random Initialization:** Generates schedules randomly for diverse solutions.
    * **Greedy Initialization:** Prioritizes efficient schedule creation by considering day, venue, and time constraints.
  * Selection Methods:

    * **Tournament Selection:** Competes randomly chosen schedules, selecting the best for reproduction.
    * **Roulette Wheel Selection:** Probabilistic selection based on fitness values.
  * Crossover Methods:

    * **Uniform Crossover:** Randomly selects genes from parents.
    * **One-Point Crossover:** Splits parents at a single point for child creation.
  * Mutation Methods:

    * **Swap Mutation:** Swaps two matches in the schedule.
    * **Reschedule Mutation:** Changes the day, venue, or time of a match.
  * Survivor Selection Strategies:

    * **Steady-State:** Replaces worst solutions with new ones.
    * **Generational:** Replaces entire population.
    * **Elitism:** Preserves the best solutions.
    * **(μ + λ) Selection:** Combines parents and offspring for selection.
* **Island Model for Population Diversity:** Population is split into islands with periodic migration to ensure diverse solutions.
* **Interactive GUI:** Built with Streamlit for easy configuration and visualization.
* **Visualized Fitness Evolution:** Monitors how the schedule quality improves over generations.
* **Result Comparison:** Save, load, and compare different runs easily.

## 📁 Project Structure

```
├── GA_class.py           # Core Genetic Algorithm implementation.
├── GUI.py                # Streamlit GUI for user interaction.
├── Utilities.py          # Helper functions (e.g., save/load, plotting).
├── schedules_data/       # JSON data files for teams and venues.
└── README.md             # Project documentation.
```

##  Usage

1. Run the application using Streamlit:

```bash
streamlit run GUI.py
```

2. Customize your Genetic Algorithm settings from the sidebar.
3. Click "Run GA" to generate the tournament schedule.
4. View, save, and compare schedules and monitor fitness evolution.

##  How It Works

* **Genetic Algorithm:**

  * Population of schedules is initialized (Random or Greedy).
  * Parent schedules are selected (Tournament or Roulette Wheel).
  * New schedules are generated using crossover and mutation.
  * Fitness is evaluated based on criteria like fair rest, venue usage, and match distribution.
  * The best schedules survive to the next generation.
* **Island Model:** The population is divided into islands with periodic migration for diversity.
* **Fitness Evaluation:** Evaluates schedules for fairness, efficient use of venues, and balanced match distribution.

## 📊 Visualization

* Monitor Fitness Evolution over generations using a graph.
* Compare different runs side by side to identify the best configuration.
