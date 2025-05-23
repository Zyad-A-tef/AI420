import json
import random
from collections import defaultdict

class GA:
    def __init__(self, num_of_teams, num_of_venues,tournament_days, match_duration,  max_matches_per_day, venue_rest,
                 population_size=100, generations=300, crossover_rate=0.8,
                  mutation_rate=0.3, early_stopping=50, daily_start_hr=8, daily_end_hr=23,
                  selection_method="tournament", 
                  crossover_method="uniform", 
                  mutation_method="swap",
                  survivor_method="steady-state",
                  random_seed = None,
                  game_name = "champions_league",
                  initialization_approach = "random"):
        
        self.num_islands = 4
        self.migration_rate = 0.4  # 40% of population migrates
        self.migration_interval = 20  # every N generations

        ## added a random seed to ensure reproducible results every time
        if random_seed is not None:
            random.seed(random_seed)

        self.game_name = game_name

        self.num_of_teams = num_of_teams
        self.num_of_venues = num_of_venues
        self.num_of_rounds = (num_of_teams * (num_of_teams-1)) /2 
        self.tournament_days = tournament_days

        self.match_duration = match_duration
        self.max_matches_per_day = max_matches_per_day
        self.venue_rest = venue_rest

        self.daily_start = daily_start_hr
        self.daily_end = daily_end_hr
        
        self.match_duration = match_duration
        self.available_hours_per_day = daily_end_hr - daily_start_hr

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

        self.initialization_approach = initialization_approach

        self.create_teams_and_venues()
        self.initialize_population()

        self.prepare_teams_data()
        self.prepare_venues_data()

    
    # Function to prepare teams data from teams saved data
    def prepare_teams_data(self):

        if not self.game_name:
            raise ValueError(f"You have to choose game first")
        
        game_folder = "schedules_data/" + self.game_name + "/"

        with open(game_folder + "teams" + ".json", 'r') as f:
            all_teams = json.load(f)
        
        # Convert values to a list (ignore IDs)
        team_names = list(all_teams.values())

        # Validate input
        if self.num_of_teams > len(all_teams):
            raise ValueError(f"Maximum teams available is {len(all_teams)}")
        
        self.teams_data = random.sample(team_names, self.num_of_teams)


    # Function to prepare venues data from venues saved data
    def prepare_venues_data(self):
        
        if not self.game_name:
            raise ValueError(f"You have to choose game first")
        
        game_folder = "schedules_data/" + self.game_name + "/"


        with open(game_folder + "venues_full" + ".json", 'r') as f:
            all_venues = json.load(f)
        
        venue_names = list(all_venues.values())  # Full dictionaries
        venue_names = [venue["name"] for venue in all_venues.values()]  # Just names


        # Validate input
        if self.num_of_venues > len(all_venues):
            raise ValueError(f"Maximum venues available is {len(all_venues)}")
        
        self.venues_data = random.sample(venue_names, self.num_of_venues)


    # Create Team and Venues Number
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
    

    # initialize of Population
    def initialize_population(self):
        if self.initialization_approach == "random":
            self.random_initialize_population()

        elif self.initialization_approach == "greedy":
            self.greedy_initialize_population()

        else:
            self.random_initialize_population()
    
    
    def random_initialize_population(self):
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

    def greedy_initialize_population(self):
        self.population = []
        base_fixtures = self.generate_round_robin_fixtures()
        
        for _ in range(self.population_size):
            schedule = []
            # Initialize data structures to track usage
            day_usage = {day: {'matches': 0, 'hours': set()} for day in range(1, self.tournament_days+1)}
            venue_usage = {venue: {'last_day': 0, 'rest_days': self.venue_rest} for venue in self.venues}
            
            # Flatten all matches
            all_matches = [match for round_matches in base_fixtures for match in round_matches]
            
            # Sort matches by some heuristic (e.g., team popularity, rivalry, etc.)
            # Here we'll just shuffle to get different greedy solutions
            random.shuffle(all_matches)
            
            for match in all_matches:
                # Find best day and venue
                best_day = None
                best_venue = None
                best_start = None
                best_score = float('inf')
                
                # Try each day
                for day in range(1, self.tournament_days+1):
                    # Check day constraints
                    if day_usage[day]['matches'] >= self.max_matches_per_day:
                        continue
                        
                    # Try each venue
                    for venue in self.venues:
                        # Check venue rest period
                        if venue_usage[venue]['last_day'] > 0 and \
                        day - venue_usage[venue]['last_day'] < venue_usage[venue]['rest_days']:
                            continue
                            
                        # Try possible start times
                        for start_hour in range(self.daily_start, self.daily_end - self.match_duration + 1):
                            # Check if time slot is available
                            time_slot_conflict = False
                            for hour in range(start_hour, start_hour + self.match_duration):
                                if hour in day_usage[day]['hours']:
                                    time_slot_conflict = True
                                    break
                            if time_slot_conflict:
                                continue
                                
                            # Calculate a greedy score (lower is better)
                            score = 0
                            # Penalize days with many matches already
                            score += day_usage[day]['matches'] * 2
                            # Penalize venues that have been used recently
                            if venue_usage[venue]['last_day'] > 0:
                                score += max(0, 5 - (day - venue_usage[venue]['last_day']))
                                
                            if score < best_score:
                                best_score = score
                                best_day = day
                                best_venue = venue
                                best_start = start_hour
                
                if best_day is None:  # Couldn't find a valid slot - use random as fallback
                    best_day = random.randint(1, self.tournament_days)
                    best_venue = random.choice(self.venues)
                    best_start = random.randint(self.daily_start, self.daily_end - self.match_duration)
                    
                # Add the match to schedule
                schedule.append((match, best_venue, best_day, best_start))
                
                # Update usage trackers
                day_usage[best_day]['matches'] += 1
                for hour in range(best_start, best_start + self.match_duration):
                    day_usage[best_day]['hours'].add(hour)
                venue_usage[best_venue]['last_day'] = best_day
                
            self.population.append(schedule)


    # Diversity Technqies (island split)        
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
            

    # fitness Evaltuion
    def fitness_function(self, schedule):
        fitness = 0
        team_schedule = defaultdict(list)
        venue_schedule = defaultdict(list)
        day_counts = defaultdict(int)


        for match, venue, day, start_hour in schedule:
            team1, team2 = match
            end_hour = start_hour + self.match_duration + self.venue_rest
            day_counts[day] += 1


            # same team cant play more than one match/day
            for team in [team1, team2]:
                if any(prev_day == day for prev_day, _, _ in team_schedule[team]):
                    fitness +=20

            # fair rest
            for team in [team1,team2]:
                for prev_day, prev_start_hr, prev_end_hr in team_schedule[team]:
                    rest_days = abs(day - prev_day)
                    if rest_days < 3:
                        fitness += (2 - rest_days) *10


            team_schedule[team1].append ((day, start_hour, end_hour))
            team_schedule[team2].append ((day, start_hour, end_hour))


            # venue double booking
            for current_day, current_start, current_end in venue_schedule[venue]:
                if day == current_day and not (end_hour < current_start or start_hour >= current_end):
                    fitness +=10

            venue_schedule[venue].append((day, start_hour, end_hour))

            #fair game time
            #check variance to make sure that games have normal distr. accross all days
        if len(day_counts) >1:
            avg_matches = len(schedule)/ len(day_counts)
            var = sum((count - avg_matches)**2 for count in day_counts.values())/ len(day_counts)
            fitness += var *2

        return fitness


    # selection of Parents
    def tournament_selection(self, population, k=3):

        selected = random.sample(population, k)
        best = min(selected, key=lambda ind: self.fitness_function(ind))

        return best

    def roulette_wheel_selection(self, population):

        fitnesses = [1 / (self.fitness_function(ind) + 1e-6) for ind in population]
        total = sum(fitnesses)
        probability = [f / total for f in fitnesses]

        return random.choices(population, weights=probability, k=1)[0]


    # Crossover
    def one_point_crossover(self, parent1, parent2):

        point = random.randint(1, len(parent1) - 2)
        child = parent1[:point] + parent2[point:]

        return child

    def uniform_crossover(self, parent1, parent2):
        child = []
        for gene1, gene2 in zip(parent1, parent2):

            match = gene1[0]
            venue = random.choice([gene1[1], gene2[1]])
            day = random.choice([gene1[2], gene2[2]])
            start_hour = random.choice([gene1[3], gene2[3]])
            child.append((match, venue, day, start_hour))

        return child


    # Mutation
    def swap_mutation(self, individual):
        i, j = random.sample(range(len(individual)), 2)
        individual[i], individual[j] = individual[j], individual[i]

    def reschedule_mutation(self, individual):
        index = random.randint(0, len(individual) - 1)
        match, _, _, _ = individual[index]

        new_venue = random.choice(self.venues)
        new_day = random.randint(1, self.tournament_days)
        new_start_hour = random.randint(self.daily_start, self.daily_end - self.match_duration)

        individual[index] = (match, new_venue, new_day, new_start_hour)


    # Selection of Offspring
    def survivor_selection(self, population, offspring):
        
        combined = population + offspring
        
        if self.survivor_method == "elitism":
            # Preserve top N elite individuals from current population
            num_elites = max(1, int(0.1 * self.population_size))  # 10% elitism, at least 1

            # Sort current population by fitness (assumes lower is better)
            population.sort(key=lambda ind: self.fitness_function(ind))
            elites = population[:num_elites]

            # Sort offspring by fitness and take the best to fill the rest
            offspring.sort(key=lambda ind: self.fitness_function(ind))
            survivors = elites + offspring[:self.population_size - num_elites]

            return survivors
            
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
        

    # Decoding the schedule back into names
    def DecodeToNames(self,schedule) : 

        decoded_schedule = []

        for match in schedule:
            
            game = dict()
            teams , venue_id , day , hour = match

            game['Team 1'] = self.get_team_name(teams[0])
            game['Team 2'] = self.get_team_name(teams[1])
            game['Venue'] = self.get_venue_name(venue_id)
            game['Day']   = day
            game['Hour']  = hour

            decoded_schedule.append(game)
        
        sorted_schedule = sorted(decoded_schedule, key=lambda x: (x['Day'], x['Hour']))

        return sorted_schedule


    #Evolve Function
    def evolve(self):
        if not self.population:
            raise ValueError("Population failed to initialize")

        islands = self.split_into_islands(self.population)
        best_fitness = float('inf')
        best_schedule = None
        generation_found = 0
        no_improv_counter = 0

        for generation in range(1, self.generations + 1):
            new_islands = []

            for island in islands:
                new_population = []

                while len(new_population) < len(island):
                    # Selection
                    select = self.tournament_selection if self.selection_method == "tournament" else self.roulette_wheel_selection
                    parent1 = select(island)
                    parent2 = select(island)

                    # Crossover
                    if random.random() < self.crossover_rate:
                        if self.crossover_method == "one-point":
                            child = self.one_point_crossover(parent1, parent2)
                        else:  # uniform
                            child = self.uniform_crossover(parent1, parent2)
                    else:
                        child = parent1.copy()

                    # Mutation
                    if random.random() < self.mutation_rate:
                        if self.mutation_method == "swap":
                            self.swap_mutation(child)
                        else:  # reschedule
                            self.reschedule_mutation(child)

                    new_population.append(child)

                # Survivor selection
                island = self.survivor_selection(island, new_population)
                new_islands.append(island)

            islands = new_islands

            # Migration
            if generation % self.migration_interval == 0:
                self.migrate_islands(islands)

            # Evaluate best across all islands
            flat_population = [ind for island in islands for ind in island]
            fitness_values = [self.fitness_function(ind) for ind in flat_population]
            best_idx = min(range(len(fitness_values)), key=lambda i: fitness_values[i])
            current_best_schedule = flat_population[best_idx]
            current_best_fitness = fitness_values[best_idx]

            if current_best_fitness < best_fitness:
                best_fitness = current_best_fitness
                best_schedule = current_best_schedule.copy()
                generation_found = generation
                no_improv_counter = 0
            else:
                no_improv_counter += 1

            self.fitness_history.append(best_fitness)
            print(f"Generation {generation}: Best Fitness = {best_fitness:.2f}")

            if no_improv_counter >= self.early_stopping:
                print(f"Early stopping at generation {generation} (no improvement)")
                break

        print(f"\nBest solution found at generation {generation_found} with fitness {best_fitness:.2f}")
        decoded_schedule = self.DecodeToNames(best_schedule)

        return decoded_schedule, best_fitness, generation_found


    # def display_with_names(self):
    #     for i, schedule in enumerate(self.population):
    #         fitness = self.fitness_function(schedule)
    #         print(f"Schedule {i+1} (fitness: {fitness:.2f})")
    #         print("-"*20)
    #         for match, venue, day, start_hour in schedule:
    #             print(f"Day {day}: Match: {self.get_team_name(match[0])} vs {self.get_team_name(match[1])} at {self.get_venue_name(venue)} ({start_hour}:00)")
    #         print("-" * 20)
                    
    # Function to get the name of a team by it's ID
    def get_team_name(self, team_id):
        return self.teams_data[team_id]
    
    # Function to get the name of a venue by it's ID
    def get_venue_name(self, venue_id = 0):
        return self.venues_data[venue_id]


