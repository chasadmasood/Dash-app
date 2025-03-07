# adding important libraries for use
import numpy as np
import dash
from dash import dcc, html
from dash.dependencies import Input, Output, State
import plotly.graph_objects as go
import requests
# Firebase configuration
FIREBASE_HOST = "dash-data-da3cd-default-rtdb.asia-southeast1.firebasedatabase.app"
API_KEY = "AIzaSyComcT03iV0HMkz_F9DQ7Udc0CqlIPcC0E"  # Replace with actual API key
# Function to send relay command to Firebase.make a function to send command from dash to data base.
def send_relay_command(command):
    url = f"https://{FIREBASE_HOST}/relay.json?auth={API_KEY}"
    try:
        response = requests.put(url, json=command)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        print(f"Error sending relay command: {e}")

# Function to fetch data from Firebase with reduced timeout for faster data fetching
def fetch_data_from_firebase(path):
    url = f"https://{FIREBASE_HOST}/{path}.json?auth={API_KEY}"
    try:
        response = requests.get(url, timeout=5)  # Reduced timeout for faster fetching
        response.raise_for_status()
        data = response.json()
        return data if isinstance(data, list) else []
    except requests.exceptions.RequestException as e:
        print(f"Error fetching data from Firebase: {e}")
        return []
temp = fetch_data_from_firebase("temperature")or [0] * 100

# Function to compute FFT (Fast Fourier Transform) on a signal

def compute_fft(signal_list, sampling_rate):
    # Ensure signal has enough data points
    if len(signal_list) < 2:
        return [], []
    
    # Convert list to numpy array
    signal = np.array(signal_list)

    # Number of samples
    n = len(signal)

    # Compute the FFT using rfft for real-valued signals
    fft_result = np.fft.rfft(signal)

    # Compute corresponding frequencies
    frequencies = np.fft.rfftfreq(n, d=1/sampling_rate)

    # Compute single-sided amplitude spectrum
    magnitude = np.abs(fft_result) / n  # Normalize by number of samples
    magnitude *= 2  # Account for symmetry of FFT (except DC and Nyquist)

    # DC component and Nyquist frequency should not be doubled
    if n % 2 == 0:  # Even length signal
        magnitude[-1] /= 2

    return frequencies, magnitude

# multiple image background
background_images = [
    "url('https://images.unsplash.com/photo-1489781879256-fa824b56f24f?q=80&w=2070&auto=format&fit=crop&ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D')",
    # "url('https://img.freepik.com/free-photo/fuji-mountain-kawaguchiko-lake-morning-autumn-seasons-fuji-mountain-yamanachi-japan_335224-102.jpg?t=st=1739531056~exp=1739534656~hmac=032535cf29dd153e19aa6ee94cb7b54e15501bda1e152f3317d6b086cf34768f&w=1060')",
    # "url('https://img.freepik.com/free-photo/landscape-with-mountain-lake_71767-126.jpg?t=st=1739759758~exp=1739763358~hmac=883612f6b096235b0d27bfd3078ab2b20cbb5ad8f3b8d7184e85d0bebb08a9a6&w=826')",
    # "url('https://img.freepik.com/free-photo/mount-mont-blanc-covered-snow-reflecting-water-evening-chamonix-france_181624-33408.jpg?t=st=1739759833~exp=1739763433~hmac=beffdb14eee15ddc1e6e99d0b210fa46190bff4253984a0f05ee4530098d3b60&w=1060')",
    # "url('https://img.freepik.com/free-photo/mountains-with-snow-trees_1048-2411.jpg?t=st=1739759900~exp=1739763500~hmac=a4e6e2946f9d787618b163026a8d98c45c902a75105eecb9f6668e7fdc43e5ae&w=996')",
    # "url('https://img.freepik.com/free-photo/water-fall_335224-986.jpg?t=st=1739759985~exp=1739763585~hmac=ecc18b923b11de3bd8b0947bbbb95322755378459841927825911d2abbf0c01b&w=996')"
    
]
# Dash App Setup
app = dash.Dash(__name__,meta_tags=[{"name":"viewport","content":"width=device-width"}])
server = app.server
app.title = "Vibration Analysis"

# App layout
app.layout = html.Div([
    # Title section
    dcc.Interval(id="bg-interval", interval=10000, n_intervals=0),
    html.Div([
    html.H1("Vibration Analysis of Motor IOT Based",style={"background":"black","padding": "2px", "borderRadius": "2px","color":"white"}),
    html.Button("Connect", id="connect-button", n_clicks=0, style={ "backgroundColor": "red","color": "white", "position": "absolute", "right": "20px", "top": "35px",}),
    html.Button("Refresh", id="refresh-button", n_clicks=0, style={  "backgroundColor": "blue","color": "white", "position": "absolute", "right": "100px", "top": "35px"}),
    html.Button("Run", id="run-button", n_clicks=0, style={  "backgroundColor": "red","color": "white", "position": "absolute", "right": "180px", "top": "35px"}),
    html.Button("Stop", id="stop-button", n_clicks=0, style={ "backgroundColor": "green","color": "white", "position": "absolute", "right": "260px", "top": "35px"}),
    html.Label("Sampling Rate (Hz):"),
        dcc.Input(id="sampling-rate", type="number", value=60, min=1, step=1, style={"marginRight": "10px"}),
        
    html.Label("Duration (s):"),
        dcc.Input(id="duration", type="number", value=60, min=0.1, step=0.1, style={"marginRight": "10px"}),
    html.Div([ 
            html.Label("Temperature (°C):"),
            html.Div(id="temperature-data", children=temp[-1], style={"display": "inline-block", "padding": "5px 10px", "border": "1px solid black", "borderRadius": "4px", "marginLeft": "10px", "backgroundColor": "white"})
        ], style={"display": "inline-block", "marginLeft": "20px"}),

    ],style={
        "textAlign": "left", "color": "black", "backgroundColor": "rgba(202,242,232,0.4)",
         "borderRadius": "8px"
    }),

    # Input and control section
   html.Div([
        
        # html.Button("Connect", id="connect-button", n_clicks=0, style={"backgroundColor": "red", "color": "white"}),
        # html.Button("Refresh", id="refresh-button", n_clicks=0, style={"marginLeft": "10px", "backgroundColor": "blue", "color": "white"}),
        # html.Button("Run", id="run-button", n_clicks=0, style={"marginLeft": "10px", "backgroundColor": "green", "color": "white"}),
        # html.Button("Stop", id="stop-button", n_clicks=0, style={"marginLeft": "10px", "backgroundColor": "red", "color": "white"}),

    ], style={"margin": "20px", "textAlign": "center"}),

    # Confirmation dialog
    dcc.ConfirmDialog(id='confirm-dialog', message='Successfully Connected To DataBase!'),

    # Interval for automatic updates
    dcc.Interval(id="interval", interval=500, n_intervals=0, disabled=True),  # Reduced interval for faster updates
    
    # Graph display section
    html.Div([
    html.Div([
        dcc.Tabs([
        dcc.Tab(label='Time Domain (X)', children=[
            dcc.Graph(id="time-domain-x", style={"width": "95%", "height": "300px","plot_height":"300px"}),
        ]),
        dcc.Tab(label='FFT Domain (X)', children=[
            dcc.Graph(id="fft-domain-x", style={"width": "95%", "height": "300px"}), 
        ]),
    ])
    ], style={"width": "33%","display": "inline-block"}),
    html.Div([
        dcc.Tabs([
        dcc.Tab(label='Time Domain (Y)', children=[
            dcc.Graph(id="time-domain-y", style={"width": "95%", "height": "300px"}),
        ]),
        dcc.Tab(label='FFT Domain (Y)', children=[
            dcc.Graph(id="fft-domain-y", style={"width": "95%", "height": "300px"}),
        ]),
    ])
    ], style={"width": "33%", "display": "inline-block"}),
     html.Div([
         dcc.Tabs([
        dcc.Tab(label='Time Domain (Z)', children=[
            dcc.Graph(id="time-domain-z", style={"width": "95%", "height": "300px"}),
        ]),
        dcc.Tab(label='FFT Domain (Z)', children=[
            dcc.Graph(id="fft-domain-z", style={"width": "95%", "height": "300px"}),
        ]),
    ])
    ], style={"width": "33%", "display": "inline-block"}),

], style={"display": "flex", "justifyContent": "center", "alignItems": "center"}),
html.Div([
    html.Div([
        dcc.Graph(id="misalignment-graph", style={"width": "95%", "height": "300px"}),
        ], style={"width": "33%", "display": "inline-block"}),
    html.Div([
        dcc.Graph(id="bearing-data",style={"width": "95%", "height": "300px"}),
        ], style={"width": "33%", "display": "inline-block"}),
    html.Div([
        dcc.Graph(id="axial-data",style={"width": "95%", "height": "300px"}),
  
        ], style={"width": "33%", "display": "inline-block"}),
    
    
        
], style={"display": "flex", "justifyContent": "center", "alignItems": "center",}),
],id="background-div", style={
    "backgroundImage": background_images[0],  # Start with the first image
    "backgroundSize": "500px,2000px",
    "backgroundRepeat": "no-repeat",
    "backgroundPosition": "center",
    "height": "100vh",
    "width": "100vw",
    "position": "absolute",
    "top": "0",
    "left": "0",
    "transition": "background-image 1.5s ease-in-out"  # Smooth transition effect
})
# app call back for background images
@app.callback(
    Output("background-div", "style"),
    Input("bg-interval", "n_intervals"),
    prevent_initial_call=False
)
# define function for background
def update_background(n):
    return {
        "backgroundImage": background_images[n % len(background_images)],  # Cycle through images
        "backgroundSize": "100%,100%",
        "backgroundRepeat": "no-repeat",
        "backgroundPosition": "left",
        "height": "100vh",
        "width": "98vw",
        "position": "absolute",
        "top": "0",
        "left": "0",
        "transition": "background-image 1.5s ease-in-out"
    }
# Callback to start fetching data when "Connect" button is clicked
@app.callback(
    [Output("interval", "disabled"),
     Output("connect-button", "style"),
     Output("confirm-dialog", "displayed")],
    Input("connect-button", "n_clicks"),
    prevent_initial_call=True
)
def start_fetching(n_clicks):
    return False, { "backgroundColor": "green","color": "white", "position": "absolute", "right": "20px", "top": "35px"}, True

# Callback to manually refresh graphs
@app.callback(
    Output("interval", "n_intervals"),
    Input("refresh-button", "n_clicks"),
    prevent_initial_call=True
)
def refresh_graph(n_clicks):
    return 0  # Resets the interval count to trigger an update
@app.callback(
    Output("run-button", "style"),
    Input("run-button", "n_clicks"),
    prevent_initial_call=True
)
def run_motor(n_clicks):
    send_relay_command("Run")
    return {"backgroundColor": "green","color": "white", "position": "absolute", "right": "180px", "top": "35px"}

@app.callback(
    Output("stop-button", "style"),
    Input("stop-button", "n_clicks"),
    prevent_initial_call=True
)
def stop_motor(n_clicks):
    send_relay_command("Stop")
    return {"backgroundColor": "red","color": "white", "position": "absolute", "right": "260px", "top": "35px"}

# Callback to update graphs periodically
@app.callback(
    [Output("time-domain-x", "figure"), Output("fft-domain-x", "figure"),
     Output("time-domain-y", "figure"), Output("fft-domain-y", "figure"),
     Output("time-domain-z", "figure"), Output("fft-domain-z", "figure"),
     Output("misalignment-graph", "figure"),
     Output("bearing-data", "figure"),
     Output("axial-data", "figure")],
     
    Input("interval", "n_intervals"),
    [State("sampling-rate", "value"), State("duration", "value")]
)
def update_graphs(n_intervals, sampling_rate, duration):
    if n_intervals == 0:
        empty_fig = go.Figure()
        empty_fig.update_layout(paper_bgcolor="rgba(242,242,242,0.5)", plot_bgcolor="black")
        return [empty_fig] * 9

    # Fetch data from Firebase

    # accel_x = [(value - 1) for value in (fetch_data_from_firebase("accelx") or [0] * 100)]
    accel_x = fetch_data_from_firebase("accely") or [2] * 100
    accel_y = fetch_data_from_firebase("accely") or [0] * 100
    accel_z = fetch_data_from_firebase("accelz") or [0] * 100
    misalignment = fetch_data_from_firebase("misalignment") or [0] * 100
    bearing_data = fetch_data_from_firebase("bearing_fault")or [0] * 100
    axial_data = fetch_data_from_firebase("axial_fault")or [0] * 100

    num_samples = min(len(accel_x), int(duration * sampling_rate))
    time_vals = np.linspace(0, duration, num_samples, endpoint=False)

    # Compute FFT for each axis
    freqs_x, fft_x = compute_fft(accel_x, sampling_rate)
    freqs_y, fft_y = compute_fft(accel_y, sampling_rate)
    freqs_z, fft_z = compute_fft(accel_z, sampling_rate)
    print(freqs_x,fft_x)
    def create_graph(x_vals, y_vals, title, x_label, y_label, line_color):
        fig = go.Figure(go.Scatter(x=x_vals, y=y_vals, mode="lines", line=dict(color=line_color)))
        fig.update_layout(
            title=title, xaxis_title=x_label, yaxis_title=y_label,
            paper_bgcolor="black",
            plot_bgcolor="rgba(52, 50, 50, 0.5)", 
            font=dict(color="White"),
            margin=dict(l=50, r=50, t=50, b=50)
        )
        return fig

    return [
        create_graph(time_vals, accel_x[:num_samples], "Acceleration X (Time Domain)", "Time (s)", "Amplitude mm", "red"),
        create_graph(freqs_x, fft_x, "Acceleration X (FFT)", "Frequency (Hz)", "Magnitude", "red"),
        create_graph(time_vals, accel_y[:num_samples], "Acceleration Y (Time Domain)", "Time (s)", "Amplitude", "green"),
        create_graph(freqs_y, fft_y, "Acceleration Y (FFT)", "Frequency (Hz)", "Magnitude", "green"),
        create_graph(time_vals, accel_z[:num_samples], "Acceleration Z (Time Domain)", "Time (s)", "Amplitude", "blue"),
        create_graph(freqs_z, fft_z, "Acceleration Z (FFT)", "Frequency (Hz)", "Magnitude", "blue"),
        create_graph(time_vals, misalignment[:num_samples], "Misalignment Data", "Time (s)", "Amplitude", "yellow"),
        create_graph(time_vals, bearing_data[:num_samples], "Bearing Fault Data", "Time (s)", "Amplitude", "purple"),
        create_graph(time_vals, axial_data[:num_samples], "Axial Fault Data", "Time (s)", "Amplitude", "orange")
        
  ]

if __name__ == "__main__":
    app.run_server(debug=True)
