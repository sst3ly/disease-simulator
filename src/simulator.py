import random
from simulation_data import SimulationData

class Simulation:
    def __init__(self, population_size, virulence, avgDTI, avgIL, DC, debug=False):
        self.virulence = virulence
        self.avgDTI = avgDTI
        self.avgIL = avgIL
        self.DC = DC
        self.debug = debug
        self.popSize = population_size
        self.population = [Person(virulence, avgDTI, avgIL, DC, infected=True)]
        randSeed = random.randint(0, 10000000)
        random.seed(randSeed)
        self.simData = SimulationData(population_size, randSeed)
        self.day = 0

        for i in range(self.popSize-1):
            self.population.append(Person(virulence, avgDTI, avgIL, DC))
        self.sc = True
    
    def getStats(self):
        numInfected = 0
        numInfectious = 0
        numAlive = 0
        numImmune = 0
        totalPpl = len(self.population)
        for p in self.population:
            if(p.infected): numInfected += 1
            if(p.infectious): numInfectious += 1
            if(p.immune): numImmune += 1
            if(not p.dead): numAlive += 1
        if(numInfected == 0 or numAlive == 0): 
            self.sc = False
        return numInfected, numInfectious, numImmune, numAlive, totalPpl

    def dayTick(self):
        for p in self.population:
            p.dayTick(self.population)

        numInfected, numInfectious, numImmune, numAlive, totalPpl = self.getStats()
        self.simData.addDayData(numInfected, numInfectious, numImmune, numAlive)
        if(self.debug): print(f"----\nDay: {self.day}\nNumber Infected: {numInfected}\nNumber Infectious: {numInfectious}\nNumber Immune: {numImmune}\nNumber Alive: {numAlive}\nPopulation Size: {totalPpl}\n----")
        self.day+=1
    
    def shouldContinue(self):
        return self.sc

    def run(self, maxLength=-1):
        while(self.sc and self.day != maxLength):
            self.dayTick()
        return self.simData

'''
Factors which affect individual virus infection

1. sociability: affects how much an individual interacts with others  (0-1 float)
2. hygiene: affects how often an individual washes their hands  (0-1 float)
3. natural immunity: how immune an individual is naturally  (0-1 float)

After infection, two outcomes(depends on natural immunity)
1. death
2. immune
'''

class Person:
    def __init__(self, virulence, dti, il, dc, natural_immunity=random.random(), hygiene=random.random(), sociability=random.random(), infected=False):
        self.virulence = virulence
        self.dti = dti
        self.il = il
        self.dc = dc
        self.natural_immunity = natural_immunity
        self.hygiene = hygiene
        self.sociability = sociability
        self.immune = False
        self.dead = False
        self.infected = infected
        self.daysInfected = 0
        self.infectious = False

    def dayTick(self, population):
        if(self.dead): return

        if(self.infected):            # increment days infected if infected
            self.daysInfected += 1

            # death chance
            if(random.random() < (self.dc / 4) * self.natural_immunity):
                self.dead = True
                self.infectious = False
                self.infected = False

        if(self.daysInfected == self.dti): # decide if a person is infectious
            self.infectious = True
        
        if(self.daysInfected == self.il + self.dti): 
            self.immune = True
            self.infectious = False
            self.infected = False

        if(self.infectious):                           # if infectious, try to infect others 
            targets = [p for p in population if not p.dead]
            for i in range(random.randint(3, 5) + round(self.sociability * 2)):
                person = random.choice(targets)
                if(person != self):
                    person.infect()
            

    def infect(self):
        if(self.immune): return

        infectionChance = (self.virulence * ((1 - self.natural_immunity))) - (self.hygiene * 0.1)

        if(random.random() < infectionChance):
            self.infected = True