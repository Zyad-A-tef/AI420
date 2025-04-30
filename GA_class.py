import random
from collections import defaultdict

class GA:
    def __init__(self, num_of_teams, num_of_venues, population_size=5, generations=5, crossover_rate=0.8,
                  mutation_rate=0.2, early_stopping=50, tournament_days=5, match_duration=2, daily_start_hr=8, daily_end_hr=23,
                  max_matches_per_day=4,venue_rest=1):
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
        self.teams = []
        self.venues = []
        self.population = []
        self.fitness_history= []
        self.best_schedule = None
        self.best_fitness = float('inf')
        self.create_teams_and_venues()
        self.initialize_population()

    # 1 2 3 4 
    # 1 2, 1 3, 1 4

    def create_teams_and_venues(self):
        # if self.num_of_teams % 2 != 0:
        #     self.num_of_teams +=1
        
        self.teams = [i for i in range(self.num_of_teams)]
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

    

    def evaluate_fitness(self, schedule):
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
                    fitness +=100

            # fair rest 
            for team in [team1,team2]:
                for prev_day, prev_start_hr, prev_end_hr in team_schedule[team]:
                    rest_days = abs(day - prev_day)
                    if rest_days < 3:
                        fitness += (2 - rest_days) *30


            team_schedule[team1].append ((day, start_hour, end_hour))
            team_schedule[team2].append ((day, start_hour, end_hour))


            # venue double booking
            for current_day, current_start, current_end in venue_schedule[venue]:
                if day == current_day and not (start_hour >= current_end and end_hour <= current_start):
                    fitness +=40
            ## [edit] correct venue_schedule[venue] from Team_scheduleas

            venue_schedule[venue].append((day, start_hour, end_hour))

            #fair game time
            #check variance to make sure that games have normal distr. accross all days
            if len(day_counts) >1:
                avg_matches = len(schedule)/ len(day_counts)
                var = sum((count - avg_matches)**2 for count in day_counts.values())/ len(day_counts)
                fitness += var *10

        return fitness
        

    ## selection of Parents

    def tournament_selection(self, population, k=3):

        selected = random.sample(population, k)
        best = min(selected, key=lambda ind: self.evaluate_fitness(ind)) 

        return best

    def roulette_wheel_selection(self, population):

        fitnesses = [1 / (self.evaluate_fitness(ind) + 1e-6) for ind in population]
        total = sum(fitnesses)
        probability = [f / total for f in fitnesses]

        return random.choices(population, weights=probability, k=1)[0]


    ## Crossover

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

    def evolve(self):
        for generation in range(self.generations):
            new_population = []


            # Elitism
            fitness_values = [self.evaluate_fitness(ind) for ind in self.population]
            best_idx = min(range(len(fitness_values)), key=lambda i:fitness_values[i])
            self.best_schedule = self.population[best_idx]
            self.best_fitness = fitness_values[best_idx]
            new_population.append(self.population[best_idx])
            self.fitness_history.append(self.best_fitness)

            #early stopping
            if len(self.fitness_history) > self.early_stopping:
                current_fitness = min(self.fitness_history[-self.early_stopping:])
                if current_fitness >= self.best_fitness:
                    print(f"Early stopping at generation {generation}. - due to no improvement")
                    break





        return  self.best_schedule


    def display(self):
        for i, schedule in enumerate(self.population):
            fitness = self.evaluate_fitness(schedule)
            print(f"Schedule {i+1} (fitness: {fitness:.2f})")
            print("-"*20)
            for match, venue, day, start_hour in schedule:
                print(f"Day {day}: Match: {match[0]} vs {match[1]} at {venue} ({start_hour}:00)")
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






ga = GA(num_of_teams=4, num_of_venues=2)
best_schedule = ga.evolve()
print(best_schedule)
ga.display()
# ga.test_selection_methods()
# ga.test_crossover()




