import tkinter as tk 
from tkinter import messagebox
import numpy as np  
import matplotlib.pyplot as plt
import matplotlib.figure as Figure 
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import SymPy as sym
class GraphingCalculator: 
    def graph_Display(self, root):
        """ 
        root: Creates a function called root, root is the bases to intialize the app 
        Title: The name of the function 
        Figure: Used to create the base frame of the calcutor to display 
        
        """
        self.root = root
        self.root.title = "Graphing Calculator" 
        self.my_Entry = tk.Entry(root, width = 40) 
        self.my_Entry.pack() 
        
        graph_Button = tk.Button
        self.fig = Figure(5,4, dpi = 100) 
        self.plot_area = self.fig.add_subplot(111) 
        self.canvas = FigureCanvasTkAgg(self.fig, master = root) 
        self.canvas_widget = self.canvas.get_tk_widget() 
        self.canvas_widget.pack() 
        
    def graph_Calculations(self): 
        expression = self.expression_entry.get() 
        try: 
            x = np.linspace(-10,10,400) 
            #entering the values and functions
            y = eval(expression,{"x": x, "np": np, "sin" : np.sin, "cos" : np.cos, "tan": np.tan, "log": np.log}, "pi", np.pi)  
            print(y)  
            plt.plot(x, y, f"f(x) = {expression}") 
            plt.title = "Graphing Calculator" 
            plt.xlabel("x") 
            plt.ylabel("f(x)") 
            plt.legend() 
            plt.grid(True) 
            plt.show()
        except ValueError: 
            print("Can't do this calculation because there is something wrong with your y variable")  
       
if __name__ == "main":   
    GraphingCalculator 
           
           
                
            
            
            