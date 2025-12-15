import numpy as np
import pytest
import tkinter as tk
from unittest.mock import patch
from calculatorApp import GraphingCalculatorApp


@pytest.fixture
def app():
    root = tk.Tk()
    root.withdraw()
    app_instance = GraphingCalculatorApp(root)
    yield app_instance
    root.destroy()


# --- 1. Multi-Variable Evaluation Test ---
def test_evaluate_expression_valid(app):
    app.expression_entry.delete(0, tk.END)
    app.expression_entry.insert(0, "A*cos(B)")
    app.variables_entry.delete(0, tk.END)
    app.variables_entry.insert(0, "A=10, B=0")

    with patch("tkinter.messagebox.showinfo") as mock_info, \
         patch("tkinter.messagebox.showerror") as mock_error:

        app.multi_variable_values()

    mock_info.assert_called_once()
    assert "10.0" in mock_info.call_args[0][1]
    mock_error.assert_not_called()


# --- 2. Invalid Assignment Test ---
def test_evaluate_expression_invalid(app):
    app.expression_entry.delete(0, tk.END)
    app.expression_entry.insert(0, "A*x")
    app.variables_entry.delete(0, tk.END)
    app.variables_entry.insert(0, "A:10")

    with patch("tkinter.messagebox.showerror") as mock_error:
        app.multi_variable_values()

    mock_error.assert_called_once()
    assert "Invalid assignment format" in mock_error.call_args[0][1]


# --- 3. Missing x-Value Calculation ---
def test_calc_value_valid(app):
    app.expression_entry.delete(0, tk.END)
    app.expression_entry.insert(0, "x**2")
    app.x_value_entry.delete(0, tk.END)

    with patch("tkinter.messagebox.showwarning") as mock_warning, \
         patch("tkinter.messagebox.showerror") as mock_error:

        app._on_calc_value()

    mock_warning.assert_called_once()
    mock_error.assert_not_called()


# --- 4. Variable Parsing: Valid ---
def test_calc_value_invalid_x(app):
    app.variables_entry.delete(0, tk.END)
    app.variables_entry.insert(0, "A=5.5, k=10, R=2")

    result = app._parse_variable_assignments()
    assert result == {"A": 5.5, "k": 10.0, "R": 2.0}


# --- 5. Variable Parsing: Invalid Value ---
def test_calc_value_invalid_expression(app):
    app.variables_entry.delete(0, tk.END)
    app.variables_entry.insert(0, "A=5, k=ten")

    with pytest.raises(ValueError):
        app._parse_variable_assignments()


# --- 6. Graphing Logic: Valid ---
def test_graph_calc(app):
    app.expression_entry.delete(0, tk.END)
    app.expression_entry.insert(0, "A*cos(x)")
    app.variables_entry.delete(0, tk.END)
    app.variables_entry.insert(0, "A=2")

    with patch.object(
        app.math_engine,
        "_evaluate_expression_for_graph",
        return_value=(np.array([0, 1, 2]), np.array([0, 0, 0]))
    ) as mock_eval, patch.object(app.plot_manager, "draw_graph") as mock_draw:

        app.graph_calculations()

    mock_eval.assert_called_once()
    assert mock_eval.call_args[0][0] == "2.0*cos(x)"
    mock_draw.assert_called_once()


# --- 7. Graphing Logic: No Variables ---
def test_unassigned_calcs(app):
    app.expression_entry.delete(0, tk.END)
    app.expression_entry.insert(0, "x**2")
    app.variables_entry.delete(0, tk.END)

    with patch.object(
        app.math_engine,
        "_evaluate_expression_for_graph",
        return_value=(np.array([0, 1, 2]), np.array([0, 1, 4]))
    ) as mock_eval, patch("tkinter.messagebox.showerror") as mock_error:

        app.graph_calculations()

    mock_eval.assert_called_once_with("x**2")
    mock_error.assert_not_called()


# --- 8. Empty Expression (Allowed Behavior) ---
def test_empty_expression(app):
    app.expression_entry.delete(0, tk.END)
    app.variables_entry.delete(0, tk.END)

    with patch("tkinter.messagebox.showerror") as mock_error:
        app.graph_calculations()

    mock_error.assert_not_called()


# --- 9. Missing Variable Assignment (Allowed Behavior) ---
def test_missing_variable_assignment(app):
    app.expression_entry.delete(0, tk.END)
    app.expression_entry.insert(0, "A*x")
    app.variables_entry.delete(0, tk.END)

    with patch("tkinter.messagebox.showerror") as mock_error:
        app.graph_calculations()

    mock_error.assert_not_called()


