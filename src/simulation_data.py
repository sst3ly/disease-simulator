import matplotlib.pyplot as plt
import pandas as pd

data = ["number_infected", "number_infectious", "number_immune", "number_alive", "number_dead", "number_susceptible", "day"]

class SimulationData():
    def __init__(self, populationSize, randSeed):
        self.randSeed = randSeed
        self.popSize = populationSize
        self.days = []
        self.totalDays = 0

    def addDayData(self, numInfected, numInfectious, numImmune, numAlive):
        self.days.append({"day": self.totalDays, "number_infected": numInfected, "number_infectious": numInfectious, "number_immune": numImmune, "number_alive": numAlive, "number_dead": self.popSize - numAlive, "number_susceptible": max(0, numAlive - (numInfectious + numImmune))})
        self.totalDays+=1
    
    def getDataXY(self, x_type, y_type):
        return ([day[x_type] for day in self.days], [day[y_type] for day in self.days])

    def visualizeData(self, x_type, y_type):
        plt.scatter([day[x_type] for day in self.days], [day[y_type] for day in self.days])
        plt.title(f"{x_type} by {y_type}")
        plt.xlabel(x_type)
        plt.ylabel(y_type)
        plt.show()

    def exportDataAsCSV(self, filename):
        df = pd.DataFrame(self.days)
        df.to_csv(filename, index=False)
    
    def _printAllData(self):
        print(self.days)
