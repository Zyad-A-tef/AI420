import json
import random
from collections import defaultdict

class GA:
    def __init__(self, num_of_teams, num_of_venues, population_size=100, generations=200, crossover_rate=0.8,
                  mutation_rate=0.3, early_stopping=50, tournament_days=30, match_duration=2, daily_start_hr=8, daily_end_hr=23,
                  max_matches_per_day=4,venue_rest=1, 
                  selection_method="tournament", 
                  crossover_method="uniform", 
                  mutation_method="swap",
                  survivor_method="steady-state",
                  random_seed = None):
        
        self.num_islands = 4
        self.migration_rate = 0.4  # 10% of population migrates
        self.migration_interval = 20  # every N generations

        ## added a random seed to ensure reproducible results every time
        if random_seed is not None:
            random.seed(random_seed)

        self.num_of_teams = num_of_teams
        self.num_of_venues = num_of_venues # if num_of_venues else max(2, num_of_teams//2)
        self.num_of_rounds = (num_of_teams * (num_of_teams-1)) /2 # if num_of_teams %2 ==0 else num_of_teams
        
        self.daily_start = daily_start_hr
        self.daily_end = daily_end_hr
        
        self.match_duration = match_duration
        self.available_hours_per_day = daily_end_hr - daily_start_hr
        self.tournament_days = tournament_days

        self.venue_rest = venue_rest
        self.max_matches_per_day = max_matches_per_day
        
        self.population_size = population_size
        self.generations = generations
        
        self.crossover_rate = crossover_rate
        self.mutation_rate = mutation_rate

        self.early_stopping = early_stopping

        self.selection_method = selection_method
        self.crossover_method = crossover_method
        self.mutation_method = mutation_method
        self.survivor_method = survivor_method

        self.teams = []
        self.venues = []
        self.population = []
        self.fitness_history = []

        self.create_teams_and_venues()
        self.initialize_population()

        self.prepare_teams_data()
        self.prepare_venues_data()

    
    # Function to prepare teams data from teams saved data
    def prepare_teams_data(self, json_file: str = 'champions_league_teams.json'):
        with open(json_file, 'r') as f:
            all_teams = json.load(f)
        
        # Convert values to a list (ignore IDs)
        team_names = list(all_teams.values())

        # Validate input
        if self.num_of_teams > len(all_teams):
            raise ValueError(f"Maximum teams available is {len(all_teams)}")
        
        self.teams_data = random.sample(team_names, self.num_of_teams)

    # Function to prepare venues data from venues saved data
    def prepare_venues_data(self, json_file: str = 'football_venues_full.json'):
        with open(json_file, 'r') as f:
            all_venues = json.load(f)
        
        venue_names = list(all_venues.values())  # Full dictionaries
        venue_names = [venue["name"] for venue in all_venues.values()]  # Just names


        # Validate input
        if self.num_of_venues > len(all_venues):
            raise ValueError(f"Maximum venues available is {len(all_venues)}")
        
        self.venues_data = random.sample(venue_names, self.num_of_venues)

    def create_teams_and_venues(self):

        self.teams  = [i for i in range(self.num_of_teams)]
        self.venues = [i for i in range(self.num_of_venues)]



    # return type list of tuple(size 2)
    def generate_round_robin_fixtures(self):
        fixtures = [] # who plays vs who and when

        for _ in range(self.num_of_teams):
            round_matches = []
            for i in range(_+1, self.num_of_teams):
                round_matches.append((self.teams[_], self.teams[i]))

            fixtures.append(round_matches)

        return fixtures



    def initialize_population(self):
        self.population = []
        base_fixtures = self.generate_round_robin_fixtures()

        for _ in range(self.population_size):
            schedule = []

            for round_matches in base_fixtures:
                for match in round_matches:
                    # add random day within duration
                    day = random.randint(1, self.tournament_days)

                    start_hour = random.randint(
                        self.daily_start,
                        self.daily_end - self.match_duration
                    )

                    venue = random.choice(self.venues)
                    schedule.append((match,venue,day,start_hour))

            self.population.append(schedule)

    ### Diversity Technqies (island split)        
    def split_into_islands(self, population):
        island_size = len(population) // self.num_islands
        return [population[i*island_size:(i+1)*island_size] for i in range(self.num_islands)]

    def migrate_islands(self, islands):
        for i in range(len(islands)):
            source = islands[i]
            target = islands[(i + 1) % len(islands)]

            num_migrants = max(1, int(len(source) * self.migration_rate))
            migrants = random.sample(source, num_migrants)

            # Replace weakest in target
            target.sort(key=lambda ind: self.fitness_function(ind), reverse=True)
            target[-num_migrants:] = migrants
            

    def fitness_function(self, schedule):
        fitness = 0
        team_schedule = defaultdict(list)
        venue_schedule = defaultdict(list)
        day_counts = defaultdict(int)


        for match, venue, day, start_hour in schedule:
            team1, team2 = match
            end_hour = start_hour + self.match_duration
            ## [edit] plus not minus in logic
            day_counts[day] += 1


            # same team cant play more than one match/day
            for team in [team1, team2]:
                if any(prev_day == day for prev_day, _, _ in team_schedule[team]):
                    fitness +=50

            # fair rest
            for team in [team1,team2]:
                for prev_day, prev_start_hr, prev_end_hr in team_schedule[team]:
                    rest_days = abs(day - prev_day)
                    if rest_days < 3:
                        fitness += (2 - rest_days) *20


            team_schedule[team1].append ((day, start_hour, end_hour))
            team_schedule[team2].append ((day, start_hour, end_hour))


            # venue double booking
            for current_day, current_start, current_end in venue_schedule[venue]:
                if day == current_day and not (end_hour <= current_start and start_hour >= current_end):
                    fitness +=40
            ## [edit] correct venue_schedule[venue] from Team_scheduleas

            venue_schedule[venue].append((day, start_hour, end_hour))

            #fair game time
            #check variance to make sure that games have normal distr. accross all days
            if len(day_counts) >1:
                avg_matches = len(schedule)/ len(day_counts)
                var = sum((count - avg_matches)**2 for count in day_counts.values())/ len(day_counts)
                fitness += var *5

        return fitness


    ######### selection of Parents

    def tournament_selection(self, population, k=3):

        selected = random.sample(population, k)
        best = min(selected, key=lambda ind: self.fitness_function(ind))

        return best

    def roulette_wheel_selection(self, population):

        fitnesses = [1 / (self.fitness_function(ind) + 1e-6) for ind in population]
        total = sum(fitnesses)
        probability = [f / total for f in fitnesses]

        return random.choices(population, weights=probability, k=1)[0]


    ######### Crossover

    # one point
    def one_point_crossover(self, parent1, parent2):

        point = random.randint(1, len(parent1) - 2)
        child = parent1[:point] + parent2[point:]

        return child


    # Uniform Cross

    # [Observe that unifrom get offspring near to parent to seach more to make more diversity]
    def uniform_crossover(self, parent1, parent2):
        child = []
        for gene1, gene2 in zip(parent1, parent2):
            # Randomly select each field from one of the parents
            match = gene1[0]
            venue = random.choice([gene1[1], gene2[1]])
            day = random.choice([gene1[2], gene2[2]])
            start_hour = random.choice([gene1[3], gene2[3]])
            child.append((match, venue, day, start_hour))

        return child



    ######### Mutation

    # Swap Mutation

    def swap_mutation(self, individual):
        i, j = random.sample(range(len(individual)), 2)
        individual[i], individual[j] = individual[j], individual[i]

    # Reschedule Mutation

    def reschedule_mutation(self, individual):
        index = random.randint(0, len(individual) - 1)
        match, _, _, _ = individual[index]

        new_venue = random.choice(self.venues)
        new_day = random.randint(1, self.tournament_days)
        new_start_hour = random.randint(self.daily_start, self.daily_end - self.match_duration)

        individual[index] = (match, new_venue, new_day, new_start_hour)

    def survivor_selection(self, population, offspring):
        
        combined = population + offspring
        
        if self.survivor_method == "elitism":
            # Keep top-N best individuals
            combined.sort(key = lambda ind: self.fitness_function(ind))
            return combined[:self.population_size]
            
        elif self.survivor_method == "generational":
            # Replace entire population with offspring
            return offspring[:self.population_size]
            
        elif self.survivor_method == "steady-state":
            # Replace worst individuals in population with best offspring
            population.sort(key = lambda ind: self.fitness_function(ind), reverse=True)
            offspring.sort(key = lambda ind: self.fitness_function(ind))
            return population[:-len(offspring)] + offspring
            
        else:  # Default to (μ + λ) selection
            combined.sort(key=lambda ind: self.fitness_function(ind))
            return combined[:self.population_size]
        


    #### Decoding the schedule back into names ####

    def DecodeToNames(self,schedule) : 

        decoded_schedule = []

        for match in schedule:
            
            game = dict()
            teams , venue_id , day , hour = match

            game['team1'] = self.get_team_name(teams[0])
            game['team2'] = self.get_team_name(teams[1])
            game['venue'] = self.get_venue_name(venue_id)
            game['day']   = day
            game['hour']  = hour

            decoded_schedule.append(game)
        
        sorted_schedule = sorted(decoded_schedule, key=lambda x: (x['day'], x['hour']))

        return sorted_schedule

    # def evolve(self):
    #     if not self.population:
    #         raise ValueError("Population failed to initialize")

    #     best_fitness = float('inf')
    #     best_schedule = None
    #     # fitness_hist = []
    #     generation_found = 0
    #     no_improv_counter = 0

    #     for generation in range(self.generations):
    #         new_population = []

    #         # Evaluation
    #         fitness_values = [self.fitness_function(ind) for ind in self.population]
    #         best_idx = min(range(len(fitness_values)), key=lambda i: fitness_values[i])
    #         current_best_schedule = self.population[best_idx]
    #         current_best_fitness = fitness_values[best_idx]

    #         # Track best solution
    #         if current_best_fitness < best_fitness:
    #             best_fitness = current_best_fitness
    #             best_schedule = current_best_schedule.copy()
    #             generation_found = generation + 1
    #             no_improv_counter = 0
    #         else:
    #             no_improv_counter += 1

    #         self.fitness_history.append(current_best_fitness)

    #         # Elitism
    #         # new_population.append(current_best_schedule)

    #         #controlled Elitism
    #         # if random.random() < 0.5:
    #         #     new_population.append(current_best_schedule)

    #         print(f"Generation {generation + 1}: Best fitness: {current_best_fitness:.2f}")

    #         # Early stopping
    #         if no_improv_counter >= self.early_stopping:
    #             print(f"Early stopping at generation {generation + 1} - no improvement")
    #             break


    #         #adaptive mutation rate
    #         # if no_improv_counter > 10:
    #         #     self.mutation_rate = min(self.mutation_rate * 1.1, 0.5)
    #         # else:
    #         #     self.mutation_rate = min(self.mutation_rate * 0.9, 0.01)


    #         while len(new_population) < self.population_size:
    #             # Selection
    #             parent1 = (self.tournament_selection if self.selection_method == "tournament"
    #                        else self.roulette_wheel_selection)(self.population)
    #             parent2 = (self.tournament_selection if self.selection_method == "tournament"
    #                        else self.roulette_wheel_selection)(self.population)

    #             # Crossover
    #             if random.random() < self.crossover_rate:
    #                 if self.crossover_method == "uniform":
    #                     child1 = self.uniform_crossover(parent1, parent2)
    #                     child2 = self.uniform_crossover(parent2, parent1)
    #                 else:
    #                     child1 = self.one_point_crossover(parent1, parent2)
    #                     child2 = self.one_point_crossover(parent2, parent1)
    #             else:
    #                 child1, child2 = parent1.copy(), parent2.copy()

    #             # Mutation
    #             for child in [child1, child2]:
    #                 if random.random() < self.mutation_rate:
    #                     (self.swap_mutation if self.mutation_method == "swap"
    #                      else self.reschedule_mutation)(child)

    #             new_population.extend([child1, child2])

    #         # Survivor selection
    #         self.population = self.survivor_selection(self.population, new_population[:self.population_size])



    #         # Sort and decode the best schedule

    #         decoded_schedule = self.DecodeToNames(best_schedule)




    #     return decoded_schedule, best_fitness, generation_found

    def evolve(self):
        if not self.population:
            raise ValueError("Population failed to initialize")

        # Split population into islands
        islands = self.split_into_islands(self.population)

        best_fitness = float('inf')
        best_schedule = None
        generation_found = 0
        no_improv_counter = 0

        for generation in range(self.generations):
            all_individuals = []
            all_fitness = []

            for island_index, island in enumerate(islands):
                new_population = []
                island_fitness = [self.fitness_function(ind) for ind in island]
                best_idx = min(range(len(island_fitness)), key=lambda i: island_fitness[i])
                current_best_schedule = island[best_idx]
                current_best_fitness = island_fitness[best_idx]

                # Track global best
                if current_best_fitness < best_fitness:
                    best_fitness = current_best_fitness
                    best_schedule = current_best_schedule.copy()
                    generation_found = generation + 1
                    no_improv_counter = 0
                else:
                    no_improv_counter += 1

                # Optional elitism
                # new_population.append(current_best_schedule.copy())

                # Optional adaptive mutation
                # if no_improv_counter > 10:
                #     self.mutation_rate = min(self.mutation_rate * 1.1, 0.5)
                # else:
                #     self.mutation_rate = max(self.mutation_rate * 0.9, 0.01)

                while len(new_population) < len(island):
                    # Selection
                    selector = self.tournament_selection if self.selection_method == "tournament" else self.roulette_wheel_selection
                    parent1 = selector(island)
                    parent2 = selector(island)

                    # Crossover
                    if random.random() < self.crossover_rate:
                        if self.crossover_method == "uniform":
                            child1 = self.uniform_crossover(parent1, parent2)
                            child2 = self.uniform_crossover(parent2, parent1)
                        else:
                            child1 = self.one_point_crossover(parent1, parent2)
                            child2 = self.one_point_crossover(parent2, parent1)
                    else:
                        child1, child2 = parent1.copy(), parent2.copy()

                    # Mutation
                    for child in [child1, child2]:
                        if random.random() < self.mutation_rate:
                            if self.mutation_method == "swap":
                                self.swap_mutation(child)
                            else:
                                self.reschedule_mutation(child)

                    new_population.extend([child1, child2])

                # Survivor selection
                islands[island_index] = self.survivor_selection(island, new_population[:len(island)])

                all_individuals.extend(islands[island_index])
                all_fitness.extend([self.fitness_function(ind) for ind in islands[island_index]])

            self.fitness_history.append(best_fitness)
            print(f"Generation {generation + 1}: Best fitness: {best_fitness:.2f}")

            # Early stopping
            if no_improv_counter >= self.early_stopping:
                print(f"Early stopping at generation {generation + 1} - no improvement")
                break

            # Migration
            if generation % self.migration_interval == 0 and len(islands) > 1:
                self.migrate_islands(islands)

        decoded_schedule = self.DecodeToNames(best_schedule)
        return decoded_schedule, best_fitness, generation_found


    def display(self):
        for i, schedule in enumerate(self.population):
            fitness = self.fitness_function(schedule)
            print(f"Schedule {i+1} (fitness: {fitness:.2f})")
            print("-"*20)
            for match, venue, day, start_hour in schedule:
                print(f"Day {day}: Match: {match[0]} vs {match[1]} at {venue} ({start_hour}:00)")
            print("-" * 20)


    def display_with_names(self):
        for i, schedule in enumerate(self.population):
            fitness = self.fitness_function(schedule)
            print(f"Schedule {i+1} (fitness: {fitness:.2f})")
            print("-"*20)
            for match, venue, day, start_hour in schedule:
                print(f"Day {day}: Match: {self.get_team_name(match[0])} vs {self.get_team_name(match[1])} at {self.get_venue_name(venue)} ({start_hour}:00)")
            print("-" * 20)


 #### TEstinggggggg Selection of parent

    def test_selection_methods(self):

        print("\nTournament Selection\n")
        selected1 = self.tournament_selection(self.population, k=3)
        for match in selected1:
            print(match)

        print("\nRoulette Wheel Selection \n")
        selected2 = self.roulette_wheel_selection(self.population)
        for match in selected2:
            print(match)


 #### TEstinggggggg Cross

    def test_crossover(self):

        parent1 = self.population[0]
        parent2 = self.population[1]

        print("\nParent 1:")
        for gene in parent1: print(gene)
        print("\nParent 2:")
        for gene in parent2: print(gene)

        print("\n Uniform Crossover \n")
        child1 = self.uniform_crossover(parent1, parent2)
        for gene in child1: print(gene)

        print("\n One-Point Crossover \n")
        child2 = self.one_point_crossover(parent1, parent2)
        for gene in child2: print(gene)


 #### TEstinggggggg Cross
    def test_mutation(self):
        print("\n🧪 Testing Mutation Methods")

        original = self.population[0].copy()
        print("\nOriginal Individual:")
        for gene in original: print(gene)

        mutated_swap = original.copy()
        self.swap_mutation(mutated_swap)
        print("\n--- After Swap Mutation ---")
        for gene in mutated_swap: print(gene)

        mutated_reschedule = original.copy()
        self.reschedule_mutation(mutated_reschedule)
        print("\n--- After Reschedule Mutation ---")
        for gene in mutated_reschedule: print(gene)

    # This function retrieves the team IDs for the two teams scheduled to play in a given match_id
    def get_match_teams(self, match_id):

        if(match_id >= self.num_of_rounds):
            raise ValueError(f"Maximum match_id is {self.num_of_rounds -1}")

        now = 0
        for i in range(self.num_of_teams):
            for j in range(i+1, self.num_of_teams):
                if(match_id == now):
                    return (i, j)
                else:
                    now = now + 1
                    
    # Function to get the name of a team by it's ID
    def get_team_name(self, team_id):
        return self.teams_data[team_id]
    
    # Function to get the name of a venue by it's ID
    def get_venue_name(self, venue_id = 0):
        return self.venues_data[venue_id]

#  TODO: solve the problem of high convergence

# ga = GA(num_of_teams=10, num_of_venues=3)
# ga.display()
# schedule, fitness, gen = ga.evolve()

# print(ga.get_team_name(ga.get_teams_from_match(10)[0]) + " VS " + ga.get_team_name(ga.get_teams_from_match(10)[1]))
# ga.test_selection_methods()
# ga.test_crossover()
# ga.test_mutation




