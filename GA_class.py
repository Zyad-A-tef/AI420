import random
from collections import defaultdict

class GA:
    def __init__(self, num_of_teams, num_of_venues=None, population_size=5, generations=5, crossover_rate=0.8, mutation_rate=0.2, early_stopping=50):
        self.num_of_teams = num_of_teams
        self.num_of_venues = num_of_venues if num_of_venues else max(2, num_of_teams//2)
        self.num_of_rounds = num_of_teams-1 if num_of_teams %2 ==0 else num_of_teams
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



    def create_teams_and_venues(self):
        if self.num_of_teams % 2 != 0:
            self.num_of_teams +=1
        
        self.teams = [f"Team {chr(65+i)}" for i in range(self.num_of_teams)]

        self.venues = [f"Venue{i+1}" for i in range(self.num_of_venues)]



    def generate_round_robin_fixtures(self):
        fixtures = [] # who plays vs who and when
        teams = self.teams.copy()
        if len(self.teams) %2:
            self.teams.append("dummy")
        
        for _ in range(len(self.teams)-1):
            round_matches = []
            for i in range(len(self.teams)//2):
                round_matches.append((self.teams[i], self.teams[len(self.teams)-1-i]))
            fixtures.append(round_matches)
            self.teams.insert(1, self.teams.pop()) 

        return fixtures
        

    
    def initialize_population(self):
        self.population = []
        base_fixtures = self.generate_round_robin_fixtures()
        
        for _ in range(self.population_size):
            schedule = []
            for round_matches in base_fixtures:
                for match in round_matches:
                    venue = random.choice(self.venues)
                    time_slot = random.randint(1, self.num_of_rounds *2) # *2 to provides more time slots and reduce double booking
                    schedule.append((match,venue,time_slot))
            self.population.append(schedule)

    

    # def evaluate_fitness(self, schedule):
    #     fitness = 0
    #     team_matches = defaultdict(list)
    #     venue_schedule = defaultdict(list)

    #     # fair rest
    #     for i, (match, venue, time) in enumerate(schedule):
    #         team1, team2 = match
    #         team_matches[team1].append((time,i))
    #         team_matches[team2].append((time,i))
    #         venue_schedule[venue].append((time,i))

    #     for team, matches in team_matches.items():
    #         matches.sort()
    #         for i in range(1,len(matches)):
    #             time_diff = matches[i][0] - matches[i-1][0]
    #             if time_diff < 2:
    #                 fitness += (2- time_diff) *10 # apply penalty

    



    
    def display(self):
        for i, schedule in enumerate(self.population):
            print(f"Schedule {i+1}\n")
            for match, venue, time in schedule:
                print(f"Match: {match[0]} vs {match[1]} || Venue : {venue} || Time Slot {time}")
            print("_" * 10)




ga = GA(num_of_teams=4, population_size=6)
ga.display()

