import matplotlib
matplotlib.use("TkAgg")
import tkinter as tk
from tkinter import messagebox
import numpy as np
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import sympy as sym
from unittest.mock import MagicMock

# --------------------------- MATH ENGINE ---------------------------
class MathEngine:
    """Handles all math computations and evaluations."""

    def _evaluate_expression_for_graph(self, expression):
        x = sym.Symbol("x")
        expr = sym.sympify(expression.replace("^", "**"))
        f = sym.lambdify(x, expr, modules=["numpy"])
        x_vals = np.linspace(-10, 10, 400)
        y_vals = f(x_vals)
        return x_vals, y_vals

# --------------------------- PLOT MANAGER ---------------------------
class PlotManager:
    """Handles all matplotlib plotting in the Tkinter canvas."""

    def __init__(self, plot_area, canvas):
        self.plot_area = plot_area
        self.canvas = canvas

    def draw_graph(self, x_vals, y_vals, expression):
        self.plot_area.clear()
        self.plot_area.plot(x_vals, y_vals, color="#c62828", label=f"f(x) = {expression}")
        self.plot_area.set_title("Graphing Calculator")
        self.plot_area.set_xlabel("x")
        self.plot_area.set_ylabel("f(x)")
        self.plot_area.legend()
        self.plot_area.grid(True)
        # Safe canvas draw
        if hasattr(self.canvas, "draw"):
            self.canvas.draw()

# --------------------------- MAIN APP ---------------------------
class GraphingCalculatorApp:
    def __init__(self, root):
        """Initialize the app window"""
        self.root = root
        self.testing = isinstance(root, MagicMock)

        if not self.testing:
            self.ibiza_sunset()

        self._create_expression_entry(root)
        self._create_x_value_entry(root)
        self._create_graph_area(root)
        self._create_buttons(root)

        self.math_engine = MathEngine()
        self.plot_manager = PlotManager(self.plot_area, self.canvas)

        if not self.testing:
            self.root.bind("<Configure>", self._redraw_gradient)
            self.root.after(200, self._lower_background)

    # ------------------- BACKGROUND -------------------
    def ibiza_sunset(self):
        """Creates the gradient background"""
        width, height = 600, 600
        self.root.geometry(f"{width}x{height}")
        self.gradient = tk.Canvas(self.root, width=width, height=height, highlightthickness=0, bd=0)
        self.gradient.place(x=0, y=0, relwidth=1, relheight=1)
        self._draw_gradient(width, height)

    def _draw_gradient(self, width, height):
        self.gradient.delete("all")
        r1, g1, b1 = (238, 9, 121)
        r2, g2, b2 = (255, 106, 0)
        for i in range(height):
            r = int(r1 + (r2 - r1) * i / height)
            g = int(g1 + (g2 - g1) * i / height)
            b = int(b1 + (b2 - b1) * i / height)
            color = f"#{r:02x}{g:02x}{b:02x}"
            self.gradient.create_line(0, i, width, i, fill=color)

    def _redraw_gradient(self, event):
        if hasattr(self, "_resize_job"):
            self.root.after_cancel(self._resize_job)
        self._resize_job = self.root.after(150, lambda: self._draw_gradient(event.width, event.height))
        self._lower_background()

    def _lower_background(self):
        if not self.testing:
            self.gradient.lower("all")

    # ------------------- INPUTS -------------------
    def _create_expression_entry(self, root):
        tk.Label(root, text="Expression f(x):", bg="#ffe6eb", font=("Arial", 11, "bold")).pack()
        self.expression_entry = tk.Entry(root, width=30, font=("Arial", 11))
        self.expression_entry.pack(pady=5)

    def _create_x_value_entry(self, root):
        tk.Label(root, text="x value (for calculation):", bg="#ffe6eb", font=("Arial", 11, "bold")).pack()
        self.x_value_entry = tk.Entry(root, width=10, font=("Arial", 11))
        self.x_value_entry.pack(pady=5)

    # ------------------- BUTTONS -------------------
    def _create_buttons(self, root):
        button_frame = tk.Frame(root, bg="#fff5f5", bd=2, relief="ridge")
        button_frame.pack(pady=10)
        self._create_numeric_and_operator_buttons(button_frame)
        self._create_function_buttons(button_frame)

    def _create_numeric_and_operator_buttons(self, button_frame):
        buttons = [
            ("7", 1, 0), ("8", 1, 1), ("9", 1, 2), ("/", 1, 3),
            ("4", 2, 0), ("5", 2, 1), ("6", 2, 2), ("*", 2, 3),
            ("1", 3, 0), ("2", 3, 1), ("3", 3, 2), ("-", 3, 3),
            ("0", 4, 0), (".", 4, 1), ("(", 4, 2), (")", 4, 3),
            ("+", 5, 3), ("=", 5, 2)
        ]
        for (text, row, col) in buttons:
            tk.Button(
                button_frame,
                text=text,
                width=5,
                height=1,
                font=("Arial", 10, "bold"),
                bg="#fff",
                fg="#333",
                command=lambda val=text: self._on_button_click(val),
            ).grid(row=row, column=col, padx=2, pady=2)

    def _create_function_buttons(self, button_frame):
        tk.Button(button_frame, text="Graph", command=self.graph_calculations,
                  bg="#b71c1c", fg="white", font=("Arial", 10, "bold"),
                  width=12, height=2).grid(row=6, column=0, pady=5)

        tk.Button(button_frame, text="Calculate", command=self._on_calc_value,
                  bg="#880e4f", fg="white", font=("Arial", 10, "bold"),
                  width=12, height=2).grid(row=6, column=1, pady=5)

        tk.Button(button_frame, text="3D Render",
                  command=self._3D_Render_Callback,
                  bg="#ad1457", fg="white", font=("Arial", 10, "bold"),
                  width=12, height=2).grid(row=7, column=1, pady=5)

        tk.Button(button_frame, text="3D Animate",
                  command=self.three_dim_animate,
                  bg="#ff9800", fg="white",
                  font=("Arial", 10, "bold"),
                  width=12, height=2).grid(row=7, column=2, pady=5)

    # ------------------- GRAPHING -------------------
    def _create_graph_area(self, root):
        fig = Figure(figsize=(5, 4), dpi=100)
        self.plot_area = fig.add_subplot(111)
        if not self.testing:
            self.canvas = FigureCanvasTkAgg(fig, master=root)
            self.canvas.get_tk_widget().pack()
        else:
            self.canvas = MagicMock()  # Safe for tests

    def _on_button_click(self, value):
        if value == "=":
            self._on_calc_value()
        else:
            current = self.expression_entry.get()
            self.expression_entry.delete(0, tk.END)
            self.expression_entry.insert(tk.END, current + value)

    def graph_calculations(self):
        expression = self.expression_entry.get()
        try:
            x_vals, y_vals = self.math_engine._evaluate_expression_for_graph(expression)
            self.plot_manager.draw_graph(x_vals, y_vals, expression)
        except Exception as e:
            messagebox.showerror("Error", f"Invalid expression: {e}")

    def _on_calc_value(self):
        expr = self.expression_entry.get()
        x_val_str = self.x_value_entry.get()
        if not expr.strip():
            messagebox.showwarning("Warning", "Please enter an expression first.")
            return
        if not x_val_str.strip():
            messagebox.showwarning("Warning", "Please enter an x value.")
            return
        try:
            x = sym.Symbol("x")
            expr = sym.sympify(expr.replace("^", "**"))
            f = sym.lambdify(x, expr, modules=["numpy"])
            result = f(float(x_val_str))
            messagebox.showinfo("Result", f"f({x_val_str}) = {result}")
        except Exception as e:
            messagebox.showerror("Error", f"Invalid expression or input:\n\n{e}")

    # ------------------- 3D RENDER -------------------
    def _3D_Render_Callback(self):
        expression = self.expression_entry.get()
        if not expression.strip():
            messagebox.showwarning("Warning", "Please enter an expression before rendering.")
            return
        try:
            expression = expression.replace("^", "**")
            self.three_dimension_Render(expression)
        except Exception as e:
            messagebox.showerror("3D Render Error", f"Could not render the 3D image:\n\n{e}")

    def three_dimension_Render(self, expression):
        if "x" not in expression or "y" not in expression:
            messagebox.showwarning(
                "Invalid Expression",
                "3D Render requires both variables 'x' and 'y'.\nExample: x**2 + y**2",
            )
            return
        try:
            x, y = sym.symbols("x y")
            expr = sym.sympify(expression)
            f = sym.lambdify((x, y), expr, modules=["numpy"])

            x_vals = np.linspace(-5, 5, 100)
            y_vals = np.linspace(-5, 5, 100)
            X, Y = np.meshgrid(x_vals, y_vals)
            Z = f(X, Y)

            self.plot_area.figure.clf()
            ax = self.plot_area.figure.add_subplot(111, projection="3d")
            self.plot_area = ax

            ax.plot_surface(X, Y, Z, cmap="plasma", edgecolor="none")
            ax.set_title(f"3D Render: z = {expression}")
            ax.set_xlabel("x")
            ax.set_ylabel("y")
            ax.set_zlabel("z")

            if hasattr(self.canvas, "draw"):
                self.canvas.draw()
        except Exception as e:
            messagebox.showerror("3D Render Error", f"Could not render 3D surface:\n\n{e}")

    def three_dim_animate(self):
        from matplotlib.animation import FuncAnimation
        from mpl_toolkits.mplot3d import Axes3D  # noqa: F401

        self.plot_area.figure.clf()
        ax = self.plot_area.figure.add_subplot(111, projection="3d")
        self.plot_area = ax

        x = np.linspace(-5, 5, 100)
        y = np.linspace(-5, 5, 100)
        X, Y = np.meshgrid(x, y)

        def update(frame):
            ax.clear()
            Z = np.sin(np.sqrt(X**2 + Y**2) - frame / 10.0)
            surf = ax.plot_surface(X, Y, Z, cmap="viridis", edgecolor="none")
            ax.set_zlim(-1, 1)
            ax.set_title(f"3D animation frame {frame}")
            return surf,

        if hasattr(self, 'ani'):
            self.ani.event_source.stop()

        self.ani = FuncAnimation(self.plot_area.figure, update, frames=100, interval=50, blit=False)
        if hasattr(self.canvas, "draw"):
            self.canvas.draw()


# ------------------- RUN APP -------------------
if __name__ == "__main__":
    root = tk.Tk()
    myApp = GraphingCalculatorApp(root)
    root.mainloop()

