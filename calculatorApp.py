import matplotlib
matplotlib.use("TkAgg")
import tkinter as tk
from tkinter import messagebox
import numpy as np
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import sympy as sym
import re
import math 
from mpl_toolkits.mplot3d import Axes3D 


# --------------------------- MATH ENGINE ---------------------------
class MathEngine:
    """Handles math computations and evaluations."""

    def _evaluate_expression_for_graph(self, expression):
        x = sym.Symbol("x")
        expr = sym.sympify(expression.replace("^", "**"))
        f = sym.lambdify(x, expr, modules=["numpy"])
        x_vals = np.linspace(-10, 10, 400)
        
        with np.errstate(divide='ignore', invalid='ignore'):
             y_vals = f(x_vals)
            
        y_vals = np.nan_to_num(y_vals, nan=np.nan, posinf=np.nan, neginf=np.nan)
        return x_vals, y_vals


# --------------------------- PLOT MANAGER ---------------------------
class PlotManager:
    """Handles matplotlib plotting."""

    def __init__(self, plot_area, canvas):
        self.plot_area = plot_area
        self.canvas = canvas

    def draw_graph(self, x_vals, y_vals, expression):
        self.plot_area.clear() 
        
        # Plot line color to a vibrant cyan for visibility on dark plot
        self.plot_area.plot(x_vals, y_vals, color="#00BCD4", label=f"f(x) = {expression}") 
        self.plot_area.set_title("Graphing Calculator")
        self.plot_area.set_xlabel("x")
        self.plot_area.set_ylabel("f(x)")
        self.plot_area.legend()
        self.plot_area.grid(True)
        self.canvas.draw()


# --------------------------- MAIN APP ---------------------------
class GraphingCalculatorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Graphing Calculator 2D & 3D")

        # ---------- BACKGROUND ----------
        self._setup_background()
        
        # --- STRUCTURED LAYOUT FOR WIDGETS ---
        # bg="#1A237E" (Dark Indigo Blue)
        self.control_frame = tk.Frame(root, bg="#1A237E") 
        self.control_frame.pack(side=tk.LEFT, fill=tk.Y, padx=10)

        # ---------- INPUTS ----------
        self._create_expression_entry(self.control_frame)
        self._create_variables_entry(self.control_frame) 
        self._create_x_value_entry(self.control_frame)
        
        # ---------- BUTTONS ----------
        self._create_buttons(self.control_frame)

        # ---------- PLOT AREA (Right Side) ----------
        # bg="#000000" (Black)
        self.graph_frame = tk.Frame(root, bg="#000000")
        self.graph_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=10, pady=10)
        self._create_graph_area(self.graph_frame)


        # ---------- ENGINE & PLOT ----------
        self.math_engine = MathEngine()
        self.plot_manager = PlotManager(self.plot_area, self.canvas)

        # ---------- ANIMATION FLAG ----------
        self.animating = False
        self._surface = None 
        self.ax3d = None 

        # ---------- BIND RESIZE ----------
        self.root.bind("<Configure>", self._redraw_gradient)
        self.root.after(200, self._lower_background)

    # ------------------- BACKGROUND & GRADIENT -------------------
    def _setup_background(self):
        width, height = 900, 700
        self.root.geometry(f"{width}x{height}")
        self.gradient = tk.Canvas(self.root, width=width, height=height, highlightthickness=0, bd=0)
        self.gradient.place(x=0, y=0, relwidth=1, relheight=1)
        self._draw_gradient(width, height) 
        
    def app_Tutorial(self): 
        # Tutorial Window remains dark for optimal text readability
        tutorial_window = tk.Toplevel(self.root) 
        tutorial_window.title("Graphing Calculator Tutorial") 
        tutorial_window.geometry("500x350")  
        tutorial_window.configure(bg = "#333333") 
        tutorial_window.unbind("<Configure>") 
        
        frame = tk.Frame(tutorial_window, bd = 5, relief = tk.RAISED, bg = "#424242") 
        frame.pack(padx = 10, pady = 10, fill = tk.BOTH, expand = True) 
        
        # Title accent to light blue/cyan
        tk.Label(frame, text = "App Guide", font = ("Arial", 14, "bold"), 
                 fg = "#00BCD4", bg = "#424242").pack(pady = 10) 
        
        tutorial_text = """
                Using the Calculator 
                
                1. 2D Graphing:  
                    - Enter an expression using 'x' 
                    - Click 'Graph'  
                    
                2. 3D Rendering 
                    - Enter an expression using 'x' and 'y' (e.g., sin(x)*cos(y)) 
                    - Or an implicit equation (e.g., x^2+y^2+z^2 = R^2) 
                    - Unassigned constants (like R) will default to 1.0. 
                    - Click '3D Render'
                
                3. 3D Animation 
                    - Enter expression using 'x' and 'y' 
                    - Click 3D Animate to rotate viewpoint  
                
                4 Calculation 
                    - Enter expression in top box 
                    - Enter numerical value in the 'x value' box 
                    - Click 'Calculate' 
                
                Reminder: Use '**' or '^' when doing calculations regarding raising expression to a power 
            """ 
            
        tutorial_widget = tk.Text(frame, wrap = tk.WORD, font = ('Arial', 10), 
                                      bg = "#555555", fg = "white", bd = 0, padx= 10, pady= 10) 
        tutorial_widget.insert(tk.END, tutorial_text)  
        tutorial_widget.configure(state = tk.DISABLED) 
        tutorial_widget.pack(fill = tk.BOTH, expand = True) 
        
        # Close button to light blue/cyan
        tk.Button(tutorial_window, text = "Close", command = tutorial_window.destroy, 
                  bg = "#00BCD4", fg = "black", font = ("Arial", 10, "bold")).pack(pady = 5)
    
           
    def _draw_gradient(self, width, height):
        self.gradient.delete("all")
        
        # DEEP NIGHT COLORS: Dark Indigo Blue to Black
        r1, g1, b1 = (26, 35, 126)   # #1A237E (Dark Indigo Blue)
        r2, g2, b2 = (0, 0, 0)       # #000000 (Black)
        
        if height <= 0:
            height = 1 
            
        for i in range(height):
            # Calculate interpolation factor (0.0 at top, 1.0 at bottom)
            factor = i / height

            # Linearly interpolate between the two colors for each RGB component
            r = int(r1 + (r2 - r1) * factor)
            g = int(g1 + (g2 - g1) * factor)
            b = int(b1 + (b2 - b1) * factor)
            
            # Clamp values to ensure they are within 0-255 range (safety measure)
            r = max(0, min(255, r))
            g = max(0, min(255, g))
            b = max(0, min(255, b))
            
            # Format as a hex color string
            color = f"#{r:02x}{g:02x}{b:02x}"
            
            # Draw a 1-pixel high line across the entire width
            self.gradient.create_line(0, i, width, i, fill=color)

    def _redraw_gradient(self, event):
        """Re-draws the gradient when the window size changes."""
        width = self.root.winfo_width()
        height = self.root.winfo_height()
        
        if hasattr(self, "_resize_job"):
            self.root.after_cancel(self._resize_job)
            
        # Debounce the redrawing
        self._resize_job = self.root.after(150, lambda: self._draw_gradient(width, height))
        
        self._lower_background() 
    
    def _lower_background(self):
        """Ensures the gradient Canvas is below all other widgets."""
        try:
             self.gradient.lower() 
        except:
             pass

    # ------------------- INPUTS -------------------
    def _create_expression_entry(self, root):
        # Label bg to indigo, fg to light blue-gray
        tk.Label(root, text="Expression f(x or z(x,y,t)):", bg="#1A237E", fg="#B0BEC5",
                 font=("Arial", 11, "bold")).pack(pady=(10, 2))
        # Entry bg to dark slate, fg to white
        self.expression_entry = tk.Entry(root, width=40, font=("Arial", 11),
                                         bg="#263238", fg="white", insertbackground="white")
        self.expression_entry.pack(pady=4) 

    def _create_variables_entry(self, root):
        # Label bg to indigo, fg to light blue-gray
        tk.Label(root, text="Multi-Var Assignment (e.g., a=5, R=2):", bg="#1A237E", fg="#B0BEC5",
                 font=("Arial", 11, "bold")).pack(pady=(10, 2))
        # Entry bg to dark slate, fg to white
        self.variables_entry = tk.Entry(root, width=40, font=("Arial", 11),
                                         bg="#263238", fg="white", insertbackground="white")
        self.variables_entry.pack(pady=4) 

    def _create_x_value_entry(self, root):
        # Label bg to indigo, fg to light blue-gray
        tk.Label(root, text="x value (for single-var calculation):", bg="#1A237E", fg="#B0BEC5",
                 font=("Arial", 11, "bold")).pack(pady=(10, 2))
        # Entry bg to dark slate, fg to white
        self.x_value_entry = tk.Entry(root, width=10, font=("Arial", 11),
                                      bg="#263238", fg="white", insertbackground="white")
        self.x_value_entry.pack(pady=4)

    # ------------------- BUTTONS -------------------
    def _create_buttons(self, root):
        # Button frame bg to Very Dark Indigo for separation
        button_frame = tk.Frame(root, bg="#0D113B", bd=2, relief="raised")
        button_frame.pack(pady=10)
        self._create_numeric_and_operator_buttons(button_frame)
        self._create_function_buttons(button_frame)

    def _create_numeric_and_operator_buttons(self, button_frame):
        # High-Contrast Color Definitions for the Keypad
        # FIX: Changed number background to Light Gray (#CFD8DC) 
        COLOR_NUMBER = "#CFD8DC"    # Light Gray (Will now use BLACK text)
        COLOR_OPERATOR = "#00BCD4"  # Cyan/Aqua (MUST use BLACK text)
        COLOR_EQUALS = "#FFC107"    # Vibrant Yellow/Amber (MUST use BLACK text)

        buttons_layout = [
            ("7", 1, 0, COLOR_NUMBER), ("8", 1, 1, COLOR_NUMBER), ("9", 1, 2, COLOR_NUMBER), ("/", 1, 3, COLOR_OPERATOR),
            ("4", 2, 0, COLOR_NUMBER), ("5", 2, 1, COLOR_NUMBER), ("6", 2, 2, COLOR_NUMBER), ("*", 2, 3, COLOR_OPERATOR),
            ("1", 3, 0, COLOR_NUMBER), ("2", 3, 1, COLOR_NUMBER), ("3", 3, 2, COLOR_NUMBER), ("-", 3, 3, COLOR_OPERATOR),
            ("0", 4, 0, COLOR_NUMBER), (".", 4, 1, COLOR_NUMBER), ("(", 4, 2, COLOR_OPERATOR), (")", 4, 3, COLOR_OPERATOR),
            ("+", 5, 3, COLOR_OPERATOR), ("=", 5, 2, COLOR_EQUALS),
            ("sin", 6, 0, COLOR_NUMBER), ("cos", 6, 1, COLOR_NUMBER), ("tan", 6, 2, COLOR_NUMBER),
            ("pi", 7, 0, COLOR_NUMBER), ("e", 7, 1, COLOR_NUMBER), ("^", 7, 2, COLOR_OPERATOR),
        ]
        
        for (text, row, col, bg_color) in buttons_layout:
            # Logic to assign text color based on background color:
            # If the background is light (Cyan, Yellow, OR Light Gray), use black text.
            is_light_bg = bg_color in (COLOR_OPERATOR, COLOR_EQUALS, COLOR_NUMBER)
            fg_color = "black" if is_light_bg else "white" 

            tk.Button(
                button_frame, text=text, width=5, height=1, font=("Arial", 10, "bold"),
                bg=bg_color, 
                fg=fg_color, 
                # Maintaining active state colors to prevent visual glitches:
                activebackground=bg_color, 
                activeforeground=fg_color, 
                command=lambda val=text: self._on_button_click(val) 
            ).grid(row=row, column=col, padx=2, pady=2)
    def _create_function_buttons(self, button_frame):
        
        # Graph (2D) -> Cyan (#00BCD4), Text is BLACK
        tk.Button(button_frame, text="Graph (2D)", command=self.graph_calculations,
              bg="#00BCD4", fg="black", font=("Arial", 10, "bold"),
              width=12, height=2).grid(row=8, column=0, pady=5, padx=4)

        # Calculate (x) -> Red/Orange (#F44336), Text is WHITE
        tk.Button(button_frame, text="Calculate (x)", command=self._on_calc_value,
              bg="#F44336", fg="white", font=("Arial", 10, "bold"),
              width=12, height=2).grid(row=8, column=1, pady=5, padx=4)
        
        # Calculate (Multi-Var) -> Red/Orange (#F44336), Text is WHITE
        tk.Button(button_frame, text="Calculate (Multi-Var)", command=self.multi_variable_values,
              bg="#F44336", fg="black", font=("Arial", 10, "bold"),
              width=18, height=2).grid(row=8, column=2, columnspan=2, pady=5, padx=4)

        
        # 3D Render -> Cyan (#00BCD4), Text is BLACK
        tk.Button(button_frame, text="3D Render", command=self._3D_Render_Callback,
              bg="#00BCD4", fg="black", font=("Arial", 10, "bold"),
              width=12, height=2).grid(row=9, column=0, pady=5, padx=4)
    
        # 3D Animate -> Red/Orange (#F44336), Text is WHITE
        tk.Button(button_frame, text="3D Animate", command=self.three_dim_animate,
              bg="#F44336", fg="black", font=("Arial", 10, "bold"),
              width=12, height=2).grid(row=9, column=1, pady=5, padx=4)
    
        # Tutorial -> Muted Navy Blue (#557088), Text is WHITE
        tk.Button(button_frame, text="Tutorial", command=self.app_Tutorial, 
              bg="#557088", fg="black", font=("Arial", 10, "bold"),
              width=12, height=2).grid(row=10, column=0, columnspan=2, pady=5, padx=4)

    # ------------------- GRAPH AREA -------------------
    def _create_graph_area(self, root):
        # Set Figure background to dark charcoal (#1C1C1C)
        fig = Figure(figsize=(6, 4), dpi=100, facecolor="#1C1C1C") 
        # Set subplot background to dark black (#000000)
        self.plot_area = fig.add_subplot(111, facecolor="#000000") 

        # Set colors for the grid, ticks, and spines to light gray for dark plot
        self.plot_area.tick_params(colors='gray')
        self.plot_area.spines['left'].set_color('#B0BEC5')
        self.plot_area.spines['bottom'].set_color('#B0BEC5')
        self.plot_area.spines['right'].set_color('#B0BEC5')
        self.plot_area.spines['top'].set_color('#B0BEC5')
        
        # Set label and title colors to light blue-gray
        self.plot_area.xaxis.label.set_color('#B0BEC5')
        self.plot_area.yaxis.label.set_color('#B0BEC5')
        self.plot_area.title.set_color('#B0BEC5') 
        
        self.canvas = FigureCanvasTkAgg(fig, master=root)
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True, padx=6, pady=6)


    # ------------------- UTILITY METHODS (FIXES APPLIED) -------------------

    def _on_button_click(self, value):
        if value == "=":
            self._on_calc_value() 
        else:
            current = self.expression_entry.get()
            
            if value in ("sin", "cos", "tan"):
                 value += "("
                 
            self.expression_entry.delete(0, tk.END)
            self.expression_entry.insert(tk.END, current + value)

    def _stop_all_animation(self):
        self.animating = False

    def _clear_plot(self):
        self._stop_all_animation()
        try:
            # Clear the entire figure and then add a default 2D subplot back
            self.plot_area.figure.clf() 
        except:
            pass
        
        # Ensure plot area is recreated as a default 2D subplot
        self.plot_area = self.canvas.figure.add_subplot(111, facecolor="#000000") 
        
        if hasattr(self, 'ax3d'):
             del self.ax3d
             self.ax3d = None
             
        self._surface = None
        self.canvas.draw_idle()

    def _reset_before_new_graph(self):
        self._stop_all_animation()
        self._clear_plot()

    def _parse_variable_assignments(self):
        variable_input_str = self.variables_entry.get().strip()
        if not variable_input_str:
            return {} 

        variable_vals = {}
        assignments = [item.strip() for item in variable_input_str.split(',')]
        
        for item in assignments: 
            if "=" in item: 
                var, val_str = item.split("=", 1)
                var = var.strip()
                val_str = val_str.strip()
                
                if var.isalpha() and len(var) >= 1: 
                    try:
                        variable_vals[var] = float(val_str)
                    except ValueError:
                        raise ValueError(f"Value for variable '{var}' is not a valid number: '{val_str}'")
                else: 
                    raise ValueError(f"Invalid variable name: '{var}'. Name must be one or more letters.")  
            
            else: 
                raise ValueError(f"Invalid assignment format: '{item}'. Must contain '='.") 

        return variable_vals

    def _solve_implicit_equation(self, expression, target_var_str='z'):
        if '=' not in expression:
            return expression 

        lhs_str, rhs_str = expression.split('=', 1)
        
        target_var = sym.Symbol(target_var_str)
        
        try:
            lhs = sym.sympify(self._preprocess_expression(lhs_str))
            rhs = sym.sympify(self._preprocess_expression(rhs_str))
            equation = lhs - rhs
        except Exception as e:
            raise ValueError(f"Could not parse equation terms: {e}")
        
        solutions = sym.solve(equation, target_var)
        
        if not solutions:
            raise ValueError(f"Could not solve the equation for {target_var_str}. It might be too complex or not contain {target_var_str}.")
        
        return str(solutions[0])

    def graph_calculations(self):
        expression = self.expression_entry.get()
        if not expression.strip():
            messagebox.showwarning("Warning", "Enter an expression first.")
            return
        try:
            self._reset_before_new_graph()
            
            variable_vals = self._parse_variable_assignments()
            pre = self._preprocess_expression(expression)
            
            for var, value in variable_vals.items():
                pattern = r'\b' + re.escape(var) + r'\b'
                pre = re.sub(pattern, str(value), pre)

            x_vals, y_vals = self.math_engine._evaluate_expression_for_graph(pre)
            self.plot_manager.draw_graph(x_vals, y_vals, expression)
            
        except ValueError as e:
            messagebox.showerror("Variable Error", str(e))
        except Exception as e:
            messagebox.showerror("Error", f"Invalid expression or plotting issue: {e}")

    def multi_variable_values(self): 
        expression = self.expression_entry.get() 
        
        if not expression: 
            messagebox.showerror("Input Error", "Enter an expression.") 
            return  
            
        try:
            variable_vals = self._parse_variable_assignments()
        except ValueError as e:
            messagebox.showerror("Variable Error", str(e))
            return
        
        if not variable_vals and re.search(r'[a-zA-Z]', expression):
            messagebox.showwarning("Input Missing", "Expression contains variables but no assignments were provided.")
            return

        processed_expression = self._preprocess_expression(expression)
        
        for var, value in variable_vals.items():
            pattern = r'\b' + re.escape(var) + r'\b'
            processed_expression = re.sub(pattern, str(value), processed_expression)

        safe_globals = {
            '__builtins__': None,  
            'sin': math.sin, 'cos': math.cos, 'tan': math.tan,
            'sqrt': math.sqrt, 'pi': math.pi, 'e': math.e,
        }
        
        try:
            result = eval(processed_expression, safe_globals) 
            
            display_vars = ', '.join([f'{k}={v}' for k, v in variable_vals.items()])
            messagebox.showinfo("Result", f"f({display_vars}) = {result}")

        except (SyntaxError, TypeError, NameError) as e:
            messagebox.showerror("Invalid Expression", f"Invalid Expression or missing variable: {e}")
        except Exception as e:
            messagebox.showerror("Calculation Error", f"An unexpected calculation error occurred: {e}")


    def _on_calc_value(self):
        expr = self.expression_entry.get()
        x_val_str = self.x_value_entry.get()

        if not expr.strip() or not x_val_str.strip():
            messagebox.showwarning("Warning", "Enter expression and x value.")
            return

        try:
            x = sym.Symbol("x")
            expr_proc = self._preprocess_expression(expr)
            expr_sym = sym.sympify(expr_proc)
            f = sym.lambdify(x, expr_sym, modules=["numpy"])
            result = f(float(x_val_str))
            messagebox.showinfo("Result", f"f({x_val_str}) = {result}")
        except Exception as e:
            messagebox.showerror("Error", f"Cannot compute value:\n{e}")

    def _3D_Render_Callback(self):
        expression = self.expression_entry.get().strip()
        if not expression:
            messagebox.showwarning("Warning", "Enter expression first.")
            return
        
        try:
            preprocessed_expression = self._preprocess_expression(expression)
            
            if '=' in preprocessed_expression:
                explicit_expression = self._solve_implicit_equation(preprocessed_expression, 'z')
                messagebox.showinfo("Auto-Solved", f"Implicit equation solved for z.\nPlotting: z = {explicit_expression}")
            else:
                explicit_expression = preprocessed_expression

            self._reset_before_new_graph()
            self.three_dimension_Render(explicit_expression)
            
        except ValueError as e:
            messagebox.showerror("Solve Error", str(e))
        except Exception as e:
            messagebox.showerror("3D Render Error", f"An unexpected error occurred: {e}")


    def three_dimension_Render(self, expression):
        x, y = sym.symbols("x y")
        
        try:
            expr = sym.sympify(expression.replace("^", "**"))
        except Exception as e:
            messagebox.showerror("3D Render Error", f"Invalid expression: {e}")
            return

        all_symbols = expr.free_symbols
        constant_symbols = [s for s in all_symbols if str(s) not in ('x', 'y', 'z')]
        
        default_substitutions = {s: 1.0 for s in constant_symbols}
        
        if default_substitutions:
             const_info = ', '.join([f'{str(s)}=1.0' for s in default_substitutions])
             messagebox.showinfo("Variable Defaults", f"Assigning default value of 1.0 to: {const_info} for rendering.")
        
        expr_with_constants = expr.subs(default_substitutions)
        f = sym.lambdify((x, y), expr_with_constants, modules=["numpy"])
        
        X, Y = np.meshgrid(np.linspace(-5, 5, 150), np.linspace(-5, 5, 150))
        
        with np.errstate(divide='ignore', invalid='ignore'):
             Z = f(X, Y)
             
        if Z.ndim == 0:
            Z = np.full_like(X, Z.item())
        elif Z.ndim == 1 and X.shape[0] * X.shape[1] == Z.shape[0]:
            Z = Z.reshape(X.shape)
            
        Z = np.nan_to_num(Z, nan=0.0, posinf=0.0, neginf=0.0)
        Z_CLAMP_LIMIT = 50.0 
        Z = np.clip(Z, -Z_CLAMP_LIMIT, Z_CLAMP_LIMIT)

        # FIX: Remove any existing 2D plot before adding 3D
        self.plot_area.figure.clf() 
        # FIX: Explicitly create 3D axes object
        self.ax3d = self.plot_area.figure.add_subplot(111, projection="3d", facecolor="#000000")
        
        # cmap to 'cool' for blue/purple tones on a dark background
        self._surface = self.ax3d.plot_surface(X, Y, Z, cmap="cool", edgecolor="none") 

        try:
            zmin, zmax = np.nanmin(Z), np.nanmax(Z)
            if not np.isfinite(zmin) or not np.isfinite(zmax) or zmin == zmax:
                zmin, zmax = -5, 5
        except:
            zmin, zmax = -5, 5
            
        # Set axis/label colors for dark theme
        self.ax3d.set_zlim(zmin, zmax)
        self.ax3d.set_xlabel("x", color="#B0BEC5")
        self.ax3d.set_ylabel("y", color="#B0BEC5")
        self.ax3d.set_zlabel("z", color="#B0BEC5")
        self.ax3d.tick_params(axis='x', colors='#B0BEC5')
        self.ax3d.tick_params(axis='y', colors='#B0BEC5')
        self.ax3d.tick_params(axis='z', colors='#B0BEC5')
        # FIX: Set the title here explicitly
        self.ax3d.set_title(f"3D Render: {expression}", color="#B0BEC5")
        self.canvas.draw_idle()

    def three_dim_animate(self):
        expr_str = self.expression_entry.get().strip()
        if not expr_str.strip():
            messagebox.showwarning("Warning", "Enter 3D expression (f(x, y)) first.")
            return
        
        if '=' in expr_str:
            messagebox.showwarning("Invalid Input", "3D Animation does not support implicit equations.")
            return
        
        self._reset_before_new_graph()

        x, y = sym.symbols("x y")
        try:
            expr = sym.sympify(expr_str.replace("^", "**"))
        except Exception as e:
            messagebox.showerror("Error", f"Invalid expression: {e}")
            return

        all_symbols = expr.free_symbols
        constant_symbols = [s for s in all_symbols if str(s) not in ('x', 'y', 'z')]
        default_substitutions = {s: 1.0 for s in constant_symbols}
        
        if default_substitutions:
             const_info = ', '.join([f'{str(s)}=1.0' for s in default_substitutions])
             messagebox.showinfo("Variable Defaults", f"Assigning default value of 1.0 to: {const_info} for animation.")
        
        expr_with_constants = expr.subs(default_substitutions)
        f = sym.lambdify((x, y), expr_with_constants, modules=["numpy"])
        
        X, Y = np.meshgrid(np.linspace(-5, 5, 100), np.linspace(-5, 5, 100))
        
        with np.errstate(divide='ignore', invalid='ignore'):
             Z = f(X, Y)
        
        if Z.ndim == 0:
            Z = np.full_like(X, Z.item())
        elif Z.ndim == 1 and X.shape[0] * X.shape[1] == Z.shape[0]:
            Z = Z.reshape(X.shape)
            
        Z = np.nan_to_num(Z, nan=0.0, posinf=0.0, neginf=0.0)
        Z_CLAMP_LIMIT = 50.0 
        Z = np.clip(Z, -Z_CLAMP_LIMIT, Z_CLAMP_LIMIT)

        try:
            zmin, zmax = np.nanmin(Z), np.nanmax(Z)
            if not np.isfinite(zmin) or not np.isfinite(zmax) or zmin == zmax:
                zmin, zmax = -5, 5
        except:
            zmin, zmax = -5, 5

        # FIX: Remove any existing 2D plot before adding 3D
        self.plot_area.figure.clf() 
        # FIX: Explicitly create 3D axes object
        self.ax3d = self.plot_area.figure.add_subplot(111, projection="3d", facecolor="#000000")
        
        self._surface = self.ax3d.plot_surface(X, Y, Z, cmap="cool", edgecolor="none")
        self.ax3d.set_zlim(zmin, zmax)
        self.ax3d.set_xlabel("x", color="#B0BEC5")
        self.ax3d.set_ylabel("y", color="#B0BEC5")
        self.ax3d.set_zlabel("z", color="#B0BEC5")
        self.ax3d.tick_params(axis='x', colors='#B0BEC5')
        self.ax3d.tick_params(axis='y', colors='#B0BEC5')
        self.ax3d.tick_params(axis='z', colors='#B0BEC5')
        self.ax3d.set_title(f"3D Rotation: {expr_str}", color="#B0BEC5")

        self.animating = True
        angle = 0
        
        def update_frame():
            nonlocal angle
            if not self.animating:
                return

            self.ax3d.view_init(elev=30, azim=angle) 
            angle = (angle + 3) % 360 
            
            self.canvas.draw_idle()

            self.root.after(33, update_frame)

        update_frame()
        
    def _preprocess_expression(self, expr: str) -> str:
        expr = expr.strip().replace("^", "**")
        
        expr = re.sub(r"(?<=\d|\))(?=[a-zA-Z\(])", "*", expr) 
        expr = re.sub(r"(?<=[a-zA-Z\)])(?=\d)", "*", expr)     
        expr = re.sub(r"(?<=[a-zA-Z0-9\)])(?=[a-zA-Z\(])", "*", expr) 

        return expr


# ------------------- RUN APP -------------------
if __name__ == "__main__":
    root = tk.Tk()
    app = GraphingCalculatorApp(root)
    root.mainloop()
