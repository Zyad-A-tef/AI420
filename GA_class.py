import random
from collections import defaultdict

class GA:
    def __init__(self, num_of_teams, num_of_venues, population_size=5, generations=5, crossover_rate=0.8,
                  mutation_rate=0.2, early_stopping=50, tournament_days=30, match_duration=2, daily_start_hr=8, daily_end_hr=22):
        self.num_of_teams = num_of_teams
        self.num_of_venues = num_of_venues if num_of_venues else max(2, num_of_teams//2)
        self.num_of_rounds = num_of_teams-1 if num_of_teams %2 ==0 else num_of_teams
        self.daily_start = daily_start_hr
        self.daily_end = daily_end_hr
        self.match_duration = match_duration
        self.available_hours_per_day = daily_end_hr - daily_start_hr
        self.tournament_days = tournament_days
        self.max_matches_per_day = self.available_hours_per_day//match_duration
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
        if len(teams) %2:
            teams.append("dummy")
        
        for _ in range(len(teams)-1):
            round_matches = []
            for i in range(len(teams)//2):
                round_matches.append((teams[i], teams[len(teams)-1-i]))
            fixtures.append(round_matches)
            teams.insert(1, teams.pop()) 

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

    #     # double booking penalty
    #     for venue, bookings in venue_schedule.items():
    #         bookings.sort()
    #         for i in range(1, len(bookings)):
    #             if bookings[i][0] == bookings[i-1][0]:
    #                 fitness +=20
                    

    


    def display(self):
        for i, schedule in enumerate(self.population):
            print(f"Schedule {i+1}\n")
            for match, venue, day, start_hour in schedule:
                print(f"Day {day}: Match: {match[0]} vs {match[1]} || Venue : {venue} || Start Time: {start_hour}:00")
            print("_" * 10)




ga = GA(num_of_teams=4, num_of_venues=5)
ga.display()



