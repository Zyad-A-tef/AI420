import random
from collections import defaultdict

class GA:
    def __init__(self, num_of_teams, num_of_venues, population_size=5, generations=5, crossover_rate=0.8,
                  mutation_rate=0.2, early_stopping=50, tournament_days=5, match_duration=2, daily_start_hr=8, daily_end_hr=22):
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

    

    def evaluate_fitness(self, schedule):
        fitness = 0
        team_schedule = defaultdict(list)
        venue_schedule = defaultdict(list)
        day_counts = defaultdict(int)

        
        for match, venue, day, start_hour in schedule:
            team1, team2 = match
            end_hour = start_hour - self.match_duration
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
            for current_day, current_start, current_end in team_schedule[team1]:
                if day == current_day and not (start_hour >= current_end and end_hour <= current_start):
                    fitness +=40

            venue_schedule[venue].append((day, start_hour, end_hour))

            #fair game time
            #check variance to make sure that games have normal distr. accross all days
            if len(day_counts) >1:
                avg_matches = len(schedule)/ len(day_counts)
                var = sum((count - avg_matches)**2 for count in day_counts.values())/ len(day_counts)
                fitness += var *10

        return fitness
        



    


    def display(self):
        for i, schedule in enumerate(self.population):
            fitness = self.evaluate_fitness(schedule)
            print(f"Schedule {i+1} (fitness: {fitness:.2f})")
            print("-"*20)
            for match, venue, day, start_hour in schedule:
                print(f"Day {day}: Match: {match[0]} vs {match[1]} at {venue} ({start_hour}:00)")
            print("-" * 20)




ga = GA(num_of_teams=2, num_of_venues=5)
ga.display()



