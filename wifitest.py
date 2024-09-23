import socket
import speedtest
import tkinter as tk
from tkinter import Toplevel
import threading
from datetime import datetime
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib import style

# Use a dark style for matplotlib
style.use('dark_background')

# List to store speed test results
speed_results = []

def check_internet_connection():
    try:
        socket.create_connection(("8.8.8.8", 53), timeout=5)
        return True
    except OSError:
        return False

def get_internet_speed():
    st = speedtest.Speedtest()
    st.get_best_server()
    
    download_speed = st.download() / 1_000_000
    upload_speed = st.upload() / 1_000_000
    ping = st.results.ping
    
    return download_speed, upload_speed, ping

def run_speed_test():
    try:
        if check_internet_connection():
            window.after(0, lambda: status_label.config(text="Internet speed test in progress...", fg="white"))
            window.after(0, lambda: results_label.config(text="", fg="white"))
            animate_text()
            
            download_speed, upload_speed, ping = get_internet_speed()
            speed_results.append((download_speed, upload_speed, ping))

            window.after(0, stop_animation)

            result_text = (f"Download Speed: {download_speed:.2f} Mbps\n"
                           f"Upload Speed: {upload_speed:.2f} Mbps\n"
                           f"Ping: {ping:.0f} ms")
            window.after(0, lambda: status_label.config(text="Internet speed test completed.", fg="white"))
            window.after(0, lambda: results_label.config(text=result_text, fg="white"))
            window.after(0, update_speed_table)

            if popup and popup.winfo_exists():
                window.after(0, popup.destroy)

            if graph_frame.winfo_ismapped():  # If graph is visible, update it
                window.after(0, update_graph)
        else:
            window.after(0, lambda: status_label.config(text="No internet connection detected.", fg="red"))
            window.after(0, lambda: results_label.config(text="Please check your connection and try again.", fg="red"))
            window.after(0, stop_animation)
            window.after(0, create_popup)
    except Exception as e:
        window.after(0, lambda: status_label.config(text="Error occurred during the test.", fg="red"))
        window.after(0, lambda: results_label.config(text=f"Error: {str(e)}", fg="red"))
        window.after(0, stop_animation)
        window.after(0, create_popup)

def create_popup():
    global popup
    if not popup or not popup.winfo_exists():
        popup = Toplevel(window)
        popup.title("No Internet Connection")
        popup.geometry("300x120")
        popup.configure(bg="#2E2E2E")  # Dark background
        popup.attributes("-topmost", True)
        
        current_time = datetime.now().strftime("%H:%M")
        
        popup_label = tk.Label(popup, text=f"No Internet Connection Detected!\nTime: {current_time}", fg="red", bg="#2E2E2E", font=("Arial", 12))
        popup_label.pack(pady=20)

def animate_text(step=0):
    dots = ['.', '..', '...']
    status_label.config(text=f"Testing internet speed, please wait{dots[step]}")
    next_step = (step + 1) % len(dots)
    if status_label.cget('text').startswith('Testing internet speed'):
        window.after(500, animate_text, next_step)

def stop_animation():
    status_label.config(text="")

def update_speed_table():
    table_label.config(state='normal')
    table_label.delete(1.0, tk.END)

    # Update the header to 'Test nr.'
    header = "Test nr. | Download (Mbps) | Upload (Mbps) | Ping (ms)\n"
    table_content = header + "-" * 50 + "\n"
    
    for i, (download, upload, ping) in enumerate(speed_results):
        table_content += (f"{i + 1:<9} | {download:<16.2f} | {upload:<14.2f} | {ping:<8.0f}\n")

    table_label.insert(tk.END, table_content)
    table_label.config(state='disabled')

def plot_graph():
    fig, ax = plt.subplots(figsize=(5, 4))

    if speed_results:
        download_speeds = [result[0] for result in speed_results]
        upload_speeds = [result[1] for result in speed_results]
        ping_times = [result[2] for result in speed_results]
        test_nums = range(1, len(speed_results) + 1)
        
        ax.plot(test_nums, download_speeds, label="Download (Mbps)", marker='o', color='cyan')
        ax.plot(test_nums, upload_speeds, label="Upload (Mbps)", marker='o', color='magenta')
        ax.set_xlabel("Test nr.", color="white")  # Update x-axis label to 'Test nr.'
        ax.set_ylabel("Speed (Mbps)", color="white")
        ax.set_title("Internet Speed Test Results", color="white")
        ax.legend(facecolor='black')

        ax.tick_params(colors='white')  # Set the tick color to white
        ax.spines['bottom'].set_color('white')
        ax.spines['left'].set_color('white')

    return fig

def update_graph():
    # Clear the old graph and redraw with the latest data
    for widget in graph_frame.winfo_children():
        widget.destroy()

    fig = plot_graph()  # Create a new figure
    canvas = FigureCanvasTkAgg(fig, master=graph_frame)
    canvas.draw()
    canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

def switch_to_table():
    graph_frame.pack_forget()  # Hide graph
    table_frame.pack(fill="both", expand=True)  # Show table

def switch_to_graph():
    table_frame.pack_forget()  # Hide table
    graph_frame.pack(fill="both", expand=True)  # Show graph
    update_graph()  # Automatically update the graph when switching to it

def threaded_speed_test():
    threading.Thread(target=run_speed_test, daemon=True).start()

def auto_run_speed_test():
    threaded_speed_test()
    window.after(30000, auto_run_speed_test)

def on_mouse_wheel(event):
    table_label.yview_scroll(int(-1*(event.delta/120)), "units")

# GUI setup
window = tk.Tk()
window.title("Internet Speed Test App")
window.geometry("700x500")
window.resizable(True, True)
window.configure(bg="#2E2E2E")

status_label = tk.Label(window, text="Starting automatic speed tests...", wraplength=300, bg="#2E2E2E", fg="white")
status_label.pack(pady=10)
results_label = tk.Label(window, text="", wraplength=300, justify="center", bg="#2E2E2E", fg="white")
results_label.pack(pady=10)

button_frame = tk.Frame(window, bg="#2E2E2E")
button_frame.pack(pady=10)

switch_table_button = tk.Button(button_frame, text="Show Table", command=switch_to_table, bg="#444444", fg="white", activebackground="#555555", activeforeground="white")
switch_table_button.grid(row=0, column=0, padx=10, pady=5)

switch_graph_button = tk.Button(button_frame, text="Show Graph", command=switch_to_graph, bg="#444444", fg="white", activebackground="#555555", activeforeground="white")
switch_graph_button.grid(row=0, column=1, padx=10, pady=5)

table_frame = tk.Frame(window, bg="#2E2E2E")
table_label = tk.Text(table_frame, width=70, height=15, font=("Courier New", 10), wrap="none", bg="#333333", fg="white", insertbackground="white")
table_label.pack(pady=10, side=tk.LEFT, fill=tk.BOTH, expand=True)
table_label.config(state='disabled')
table_scrollbar = tk.Scrollbar(table_frame, command=table_label.yview)
table_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
table_label['yscrollcommand'] = table_scrollbar.set
table_label.bind("<MouseWheel>", on_mouse_wheel)

graph_frame = tk.Frame(window, bg="#2E2E2E")
graph_frame.pack(fill="both", expand=True)

popup = None

window.after(0, auto_run_speed_test)
window.mainloop()
