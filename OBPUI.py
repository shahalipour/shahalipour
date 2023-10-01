import tkinter as tk
from tkinter import ttk
from tkinter import filedialog
from tkinter import messagebox
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
from scipy.optimize import curve_fit

# Initialize global variables for depth and density data
depth = []
density = []

# Constants
Gravity = 9.81  # Acceleration due to gravity in m/s^2

# Function to fit the density trend using a quadratic polynomial
def density_trend_quadratic(depth, a, b, c):
    return a * depth**2 + b * depth + c

# Function to calculate a moving average for the density log
def moving_average(data, window_size):
    return np.convolve(data, np.ones(window_size)/window_size, mode='same')

# Function to calculate overburden pressure (OBP) at a given depth
def calculate_obp(depth, density, gravity):
    obp = np.trapz(density * gravity, depth) / 1e6  # Convert to MPa
    return obp

# Function to update the chart with new data
def update_chart():
    try:
        # Extract the selected points
        x1 = float(entry_x1.get())
        y1 = float(entry_y1.get())
        x2 = float(entry_x2.get())
        y2 = float(entry_y2.get())
        x3 = float(entry_x3.get())
        y3 = float(entry_y3.get())
        
        # Fit a quadratic curve to the selected points
        params, _ = curve_fit(density_trend_quadratic, [x1, x2, x3], [y1, y2, y3])
        
        a, b, c = params
        
        # Get the selected smoothing window size from the combo box
        smoothing_window = int(smoothing_combobox.get())
        
        # Calculate the fitted density trend
        fitted_density = density_trend_quadratic(depth, a, b, c)
        
        # Calculate the moving average of the density log
        smoothed_density = moving_average(density, smoothing_window)
        
        # Calculate overburden pressure (OBP) and overburden stress
        obp_values = []
        obp_stress_values = []
        for d in depth:
            obp = calculate_obp(depth[:depth.searchsorted(d) + 1], density[:depth.searchsorted(d) + 1], Gravity)
            obp_values.append(obp)
            obp_stress_values.append(obp / d)
        
        # Clear the previous plots
        ax.clear()
        ax2.clear()
        ax3.clear()
        ax4.clear()
        
        # Plot the density log and the fitted curve
        ax.plot(density, depth, label='Density Log (Density vs. Depth)', color='b', alpha=0.5)
        ax.plot(fitted_density, depth, label='Quadratic Fit', color='g', linestyle='--')
        ax.set_xlabel('Density (g/cm^3)')
        ax.set_ylabel('Depth (m)')
        ax.invert_yaxis()
        ax.legend()
        ax.set_title('Density Log with Quadratic Fit')
        ax.grid(True)
        
        # Plot the smoothed density log
        ax2.plot(smoothed_density, depth, label=f'Smoothed (Window Size {smoothing_window})', color='y', alpha=0.7)
        ax2.set_xlabel('Density (g/cm^3)')
        ax2.set_ylabel('Depth (m)')
        ax2.invert_yaxis()
        ax2.legend()
        ax2.grid(True)
        
        # Plot the calculated overburden pressure
        ax3.plot(obp_values, depth, label='Overburden Pressure (MPa)', color='c')
        ax3.set_xlabel('Overburden Pressure (MPa)')
        ax3.set_ylabel('Depth (m)')
        ax3.invert_yaxis()
        ax3.legend()
        ax3.grid(True)
        
        # Plot the calculated overburden stress
        ax4.plot(obp_stress_values, depth, label='Overburden Stress (MPa/m)', color='m')
        ax4.set_xlabel('Overburden Stress (MPa/m)')
        ax4.set_ylabel('Depth (m)')
        ax4.invert_yaxis()
        ax4.legend()
        ax4.grid(True)
        
        # Draw the updated plots on the canvas
        canvas.draw()
        
    except Exception as e:
        result_label.config(text=f'Error: {str(e)}')

# Function to import data from a CSV file
def import_data():
    try:
        file_path = filedialog.askopenfilename(filetypes=[("CSV Files", "*.csv")])
        if file_path:
            df = pd.read_csv(file_path)
            # Update the depth and density arrays with the imported data
            global depth, density
            depth = df['Depth'].values
            density = df['Density'].values
            result_label.config(text="Data imported successfully.")
            update_chart()  # Update the chart with the imported data
    except Exception as e:
        result_label.config(text=f'Error: {str(e)}')

# Function to export data to a CSV file
def export_data():
    try:
        file_path = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV Files", "*.csv")])
        if file_path:
            df = pd.DataFrame({'Depth': depth, 'Density': density})
            df.to_csv(file_path, index=False)
            result_label.config(text="Data exported successfully.")
    except Exception as e:
        result_label.config(text=f'Error: {str(e)}')

# Create the main application window
root = tk.Tk()
root.title("Density Log Quadratic Fit")

# Create and configure the frame
frame = ttk.Frame(root)
frame.grid(row=0, column=0, padx=10, pady=10, sticky='nsew')

# Create and place widgets
label_depth1 = ttk.Label(frame, text='Depth (m):')
label_depth1.grid(row=0, column=0, padx=(0, 5), pady=5, sticky='e')
entry_x1 = ttk.Entry(frame, width=10)
entry_x1.grid(row=0, column=1, padx=(0, 5), pady=5)
label_density1 = ttk.Label(frame, text='Density (g/cm^3):')
label_density1.grid(row=0, column=2, padx=(5, 0), pady=5, sticky='e')
entry_y1 = ttk.Entry(frame, width=10)
entry_y1.grid(row=0, column=3, padx=(0, 5), pady=5)

label_depth2 = ttk.Label(frame, text='Depth (m):')
label_depth2.grid(row=1, column=0, padx=(0, 5), pady=5, sticky='e')
entry_x2 = ttk.Entry(frame, width=10)
entry_x2.grid(row=1, column=1, padx=(0, 5), pady=5)
label_density2 = ttk.Label(frame, text='Density (g/cm^3):')
label_density2.grid(row=1, column=2, padx=(5, 0), pady=5, sticky='e')
entry_y2 = ttk.Entry(frame, width=10)
entry_y2.grid(row=1, column=3, padx=(0, 5), pady=5)

label_depth3 = ttk.Label(frame, text='Depth (m):')
label_depth3.grid(row=2, column=0, padx=(0, 5), pady=5, sticky='e')
entry_x3 = ttk.Entry(frame, width=10)
entry_x3.grid(row=2, column=1, padx=(0, 5), pady=5)
label_density3 = ttk.Label(frame, text='Density (g/cm^3):')
label_density3.grid(row=2, column=2, padx=(5, 0), pady=5, sticky='e')
entry_y3 = ttk.Entry(frame, width=10)
entry_y3.grid(row=2, column=3, padx=(0, 5), pady=5)

# Create a combo box for selecting the smoothing window size
smoothing_combobox_label = ttk.Label(frame, text='Smoothing Window Size:')
smoothing_combobox_label.grid(row=3, column=0, padx=(0, 5), pady=5, sticky='e')
smoothing_combobox = ttk.Combobox(frame, values=[str(i) for i in range(1, 101)], width=5)
smoothing_combobox.set('10')  # Set a default value
smoothing_combobox.grid(row=3, column=1, padx=(0, 5), pady=5)

# Create buttons for importing and exporting data
import_button = ttk.Button(frame, text='Import Data', command=import_data)
import_button.grid(row=4, column=0, pady=10)

export_button = ttk.Button(frame, text='Export Data', command=export_data)
export_button.grid(row=4, column=1, pady=10)

fit_button = ttk.Button(frame, text='Fit', command=update_chart)
fit_button.grid(row=4, column=2, pady=10)

result_label = ttk.Label(frame, text="")
result_label.grid(row=5, column=0, columnspan=3, pady=10)

# Create a Matplotlib figure and axes for the chart display
fig = Figure(figsize=(12, 6))
ax = fig.add_subplot(141)  # 1 row, 4 columns, subplot 1
ax2 = fig.add_subplot(142)  # 1 row, 4 columns, subplot 2
ax3 = fig.add_subplot(143)  # 1 row, 4 columns, subplot 3
ax4 = fig.add_subplot(144)  # 1 row, 4 columns, subplot 4

# Create a canvas to display the Matplotlib figure
canvas = FigureCanvasTkAgg(fig, master=frame)
canvas.get_tk_widget().grid(row=6, column=0, columnspan=3, pady=10)

# Set weights for column and row resizing
frame.columnconfigure(0, weight=1)
frame.rowconfigure(6, weight=1)

# Start the Tkinter main loop
root.mainloop()
