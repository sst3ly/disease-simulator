import random
from simulator import Simulation
import tkinter as tk
from tkinter.filedialog import askopenfilename, asksaveasfilename
import pickle
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
import matplotlib.pyplot as plt


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


data = ["number_infected", "number_infectious", "number_immune", "number_alive", "number_dead", "number_suceptible", "day"]

class SimulationData():
    def __init__(self, populationSize, randSeed):
        self.randSeed = randSeed
        self.popSize = populationSize
        self.days = []
        self.totalDays = 0

    def addDayData(self, numInfected, numInfectious, numImmune, numAlive):
        self.days.append({"number_infected": numInfected, "number_infectious": numInfectious, "number_immune": numImmune, "number_alive": numAlive, "number_dead": self.popSize - numAlive, "number_suceptible": numAlive - (numInfectious + numImmune), "day": self.totalDays})
        self.totalDays+=1
    
    def getDataXY(self, x_type, y_type):
        return ([day[x_type] for day in self.days], [day[y_type] for day in self.days])

    def visualizeData(self, x_type, y_type):
        plt.scatter([day[x_type] for day in self.days], [day[y_type] for day in self.days])
        plt.title(f"{x_type} by {y_type}")
        plt.xlabel(x_type)
        plt.ylabel(y_type)
        plt.show()
    
    def _printAllData(self):
        print(self.days)


class Window(tk.Tk):
    def __init__(self, *args, **kwargs):
        tk.Tk.__init__(self, *args, **kwargs)
        self.wm_title("Disease Simulator")

        container = tk.Frame(self, height=300, width=400, background="#000000")
        container.pack(side="top", fill="both", expand=True)

        container.grid(column=0, row=0)

        self.frames = {}
        for F in (HomePage, SimulationScreen):
            frame = F(container, self)
            self.frames[F] = frame
            frame.grid(row=0, column=0, sticky="nsew")
        
        self.show_frame(HomePage)

    def setSimData(self, simData):
        self.frames[SimulationScreen].setSimData(simData)
    
    def loadSimData(self):
        fn = askopenfilename(title="Select Simulation Data File", filetypes = (("Pickle Files", ".pickle .pkl"),))
        if(fn == ""): return
        with open(fn, "rb") as file:
            self.setSimData(pickle.load(file))
        self.show_frame(SimulationScreen)
    
    def show_frame(self, cont):
        frame = self.frames[cont]
        frame.tkraise()
    
class HomePage(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        label = tk.Label(self, text="Home Page")
        label.pack(padx=50, pady=50)

        newSimButton = tk.Button(
            self, 
            text = "New Simulation",
            command = lambda: controller.show_frame(SimulationScreen)
        )
        newSimButton.pack(side="bottom", fill=tk.X, padx=20, pady=10)

        loadSimButton = tk.Button(
            self,
            text='Load Simulation',
            command = lambda: controller.loadSimData()
        )
        loadSimButton.pack(side="bottom", fill=tk.X, padx=20, pady=10)

class SimulationScreen(tk.Frame):
    def __init__(self, parent, controller):
        self.simData = None

        tk.Frame.__init__(self, parent)
        label = tk.Label(self, text="Simulation Page")
        label.pack(padx=10, pady=10)

        vicmd = (self.register(self.validateInteger), "%P")
        vncmd = (self.register(self.validateNumber), "%P")

        self.fig = None
        self.canvas = None

        self.data_frame = tk.Frame(self)
        self.data_frame.pack(pady=2,side="top")

        variables = tk.Frame(self.data_frame)
        variables.pack(padx=10,pady=10,side="left")

        psf = tk.Frame(variables)
        psf.pack()

        popSizeL = tk.Label(psf, text="Population Size: ") #population size
        popSizeL.pack(padx=10)

        self.popSize = tk.Entry(psf, validate="all", validatecommand=vicmd)
        self.popSize.insert(0, "30")
        self.popSize.pack(padx=10, pady=2, side="bottom")

        dtilf = tk.Frame(variables)
        dtilf.pack()

        DTIL = tk.Label(dtilf, text="Incubation Period: ")
        DTIL = tk.Label(dtilf, text="Avg Days till Infectious: ")
        DTIL.pack(padx=10)

        self.DTI = tk.Entry(dtilf, validate="all", validatecommand=vicmd)
        self.DTI.insert(0, "3")
        self.DTI.pack(padx=10, pady=2, side="bottom")

        illf = tk.Frame(variables)
        illf.pack()

        IL_L = tk.Label(illf, text="Infectious Period Length")
        IL_L = tk.Label(illf, text="Avg Infection Length")
        IL_L.pack(padx=10)

        self.IL = tk.Entry(illf, validate="all", validatecommand=vicmd)
        self.IL.insert(0, "20")
        self.IL.pack(padx=10, pady=2, side="bottom")

        dcf = tk.Frame(variables)
        dcf.pack()

        DC_L = tk.Label(dcf, text="Mortality: ")
        DC_L.pack(padx=10)

        self.DC = tk.Entry(dcf, validate="all", validatecommand=vncmd)
        self.DC.insert(0, "0.1")
        self.DC.pack(padx=10, pady=2, side="bottom")

        vf = tk.Frame(variables)
        vf.pack()

        virulenceL = tk.Label(vf, text="Virulence: ")
        virulenceL.pack(padx=10)

        self.virulence = tk.Entry(vf, validate="all", validatecommand=vncmd)
        self.virulence.insert(0, "0.8")
        self.virulence.pack(padx=10, pady=2, side="bottom")

        runSimButton = tk.Button(
            self,
            text="Run New Simulation",
            command=lambda: self.runNewSim()
        )
        runSimButton.pack(side="bottom", fill=tk.X, padx=20, pady=10)

        saveSimButton = tk.Button(
            self,
            text="Save Simulation",
            command=lambda: self.saveSim()
        )
        saveSimButton.pack(side="bottom", fill=tk.X, padx=20, pady=10)

        goHomeButton = tk.Button(
            self,
            text="Home",
            command=lambda: controller.show_frame(HomePage)
        )
        goHomeButton.pack(side="bottom", fill=tk.X, padx=20, pady=10)

        self.databox = tk.Label(self)
        self.databox.pack()

    def validateInteger(self, s):
        if(s == ""): return True
        try:
            if(int(s) and (not "." in s)): return True
        except: 
            return False

    def validateNumber(self, s):
        try:
            if(float(s) or s == ""): return True
        except: 
            return False
            

    def runNewSim(self):
        ps = self.popSize.get()
        v = self.virulence.get()
        dti = self.DTI.get()
        il = self.IL.get()
        dc = self.DC.get()
        if(ps == ""): self.popSize.insert(0,"30")
        if(dti == ""): self.DTI.insert(0,"3")
        if(il == ""):self.IL.insert(0,"20")
        if(v == ""): self.virulence.insert(0,"0.8")
        if(dc == ""): self.DC.insert(0,"0.1")
        ns = Simulation(int(ps), float(v), int(dti), int(il), float(dc), debug=False)
        sd = ns.run()
        print("Done running sim")
        self.setSimData(sd)

    def setSimData(self, sd):
        self.simData = sd
        self.reloadSimulation()
    
    def reloadSimulation(self):
        if(self.fig):
            self.fig = None
            self.canvas.get_tk_widget().destroy()
            self.canvas = None
        self.fig = Figure(figsize=(5, 4), dpi=100)
        ax = self.fig.add_subplot(111)
        x, y = self.simData.getDataXY("day", "number_infected")
        x2, y2 = self.simData.getDataXY("day", "number_immune")
        x3, y3 = self.simData.getDataXY("day", "number_suceptible")
        sur = ax.plot(x3, y3, "go-", linewidth=2, markersize=4, label="Suceptible")
        inf = ax.plot(x, y, "ro-", linewidth=2, markersize=4, label="Infected")
        imm = ax.plot(x2, y2, "bo-", linewidth=2, markersize=4, label="Recovered")
        ax.legend()

        ax.set_title("Number of infected/immune by day")
        ax.set_xlabel("Day")
        ax.set_ylabel("Number of inected/immune")

        self.canvas = FigureCanvasTkAgg(self.fig, self.data_frame)
        self.canvas.draw()
        self.canvas.get_tk_widget().pack(side="right")
    
    def saveSim(self):
        if(self.simData == None): 
            tk.messagebox.showinfo("Unable to save Simulation Data", "No simulation data currently exists. Please make a new simulation or load a simulation first.")
            return
        fn = asksaveasfilename(title="Select Simulation Data File", filetypes = (("Pickle Files", ".pickle .pkl"),))
        if(fn == ""): return
        pickle.dump(self.simData, open(fn, "wb"))

if __name__ == "__main__":
    obj = Window()
    obj.mainloop()