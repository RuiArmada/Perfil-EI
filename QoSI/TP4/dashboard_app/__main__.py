from flask import Flask, render_template
import plotly
import plotly.graph_objs as go
from plotly.utils import PlotlyJSONEncoder
import json
import pandas as pd
import subprocess
import os
import threading
import re

app = Flask(__name__)

from flask import request

# Define the regex pattern to capture the region code just before the fixed suffix
pattern = r"-(\w+)-ubuntu-23-10-x64"

# Iterate over each string to find the region code
def region(sample_string):
    match = re.search(pattern, sample_string)
    if match:
        return match.group(1)
    else:
        return sample_string


@app.route('/')
def index():
    return render_template('index.html')

# --------------------------------------------------------------------------------------------------------
# DASHBOARD

@app.route('/dashboard')
def dashboard():
    files = (os.listdir("datasets/"))
    workers = [item for item in files if os.path.isdir(os.path.join("datasets/", item))]
    workers = list(set(workers) - set(["testing", "zephyrus"]))
    
    data = []
    for worker in workers:
        print(worker)
        df = pd.read_json(f'datasets/{worker}/channel_{worker.lower()}_date_06.05.2024_13h43.json')

        for hostname, group in df.groupby('hostname'):
            line = go.Scatter(
                    x=df['timestamp'].values,
                    y=df['latency'].values,
                    mode='lines',
                    name= hostname if hostname == "mia" else region(hostname)
                )
        
        data.append(line)
    graphJSON = json.dumps(data, cls=plotly.utils.PlotlyJSONEncoder)
    return render_template('dashboard.html', graphJSON=graphJSON)
    
@app.route('/update_graph', methods=['POST'])
def update_graph():

    print("Updating...")
    if request.method == 'POST':
        files = (os.listdir("datasets/"))
        workers = [item for item in files if os.path.isdir(os.path.join("datasets/", item))]
        workers = list(set(workers) - set(["testing", "zephyrus"]))
        
        data = []
        for worker in workers:
            print(worker)
            df = pd.read_json(f'datasets/{worker}/channel_{worker.lower()}_date_06.05.2024_13h43.json')
            for hostname, group in df.groupby('hostname'):
                line = go.Scatter(
                        x=df['timestamp'].values,
                        y=df['latency'].values,
                        mode='lines',
                        name= hostname if hostname == "mia" else region(hostname)
                    )
        
            data.append(line)
        graphJSON = json.dumps(data, cls=plotly.utils.PlotlyJSONEncoder)
        return graphJSON


# --------------------------------------------------------------------------------------------------------
# NETWORK DASHBOARD DNS


@app.route('/latency_dashboard_dns')
def latency_dashboard_dns():
    files = (os.listdir("datasets/"))
    workers = [item for item in files if os.path.isdir(os.path.join("datasets/", item))]
    workers = list(set(workers) - set(["mia", "testing", "zephyrus"]))
    
    data = []
    for worker in workers:
        print(worker)
        df = pd.read_json(f'datasets/{worker}/DNS/{worker}_date_06.05.2024.json')

# Generate hover text for each point
        hover_text = [
            f"{row['sent_at'].strftime('%b %d, %Y, %H:%M:%S')}, {row['time_it_took']/1000:.3f}s - {'TOS/DS was changed' if row['tos_changed'] else 'TOS/DS was not changed'}"
            for index, row in df.iterrows()
        ]

        line = go.Scatter(
                x=df['sent_at'],
                y=df['time_it_took']/1000,
                mode='lines',
                name= region(worker),
            text=hover_text,  # Set the hover text
                    hoverinfo='text+name'  # Display custom text and the name of the trace on hover
            )
    
        data.append(line)
    graphJSON = json.dumps(data, cls=plotly.utils.PlotlyJSONEncoder)
    
    return render_template('latency_dashboard_dns.html', graphJSON=graphJSON)

@app.route('/update_graph_latency_dns', methods=['POST'])
def update_graph_latency_dns():
    print("Updating...")
    if request.method == 'POST':
        files = (os.listdir("datasets/"))
        workers = [item for item in files if os.path.isdir(os.path.join("datasets/", item))]
        workers = list(set(workers) - set(["mia", "testing", "zephyrus"]))
        
        data = []
        for worker in workers:
            df = pd.read_json(f'datasets/{worker}/DNS/{worker}_date_06.05.2024.json')

    # Generate hover text for each point
            hover_text = [
                f"{row['sent_at'].strftime('%b %d, %Y, %H:%M:%S')}, {row['time_it_took']/1000:.3f}s - {'TOS/DS was changed' if row['tos_changed'] else 'TOS/DS was not changed'}"
                for index, row in df.iterrows()
            ]

            line = go.Scatter(
                    x=df['sent_at'],
                    y=df['time_it_took']/1000,
                    mode='lines',
                    name= region(worker),
                    text=hover_text,  # Set the hover text
                    hoverinfo='text+name'  # Display custom text and the name of the trace on hover
                )
      
            data.append(line)
        graphJSON = json.dumps(data, cls=plotly.utils.PlotlyJSONEncoder)
        return graphJSON

# ----------------------------------------------------------------------------------------------------
@app.route('/latency_dashboard_http')
def latency_dashboard_http():
    files = (os.listdir("datasets/"))
    workers = [item for item in files if os.path.isdir(os.path.join("datasets/", item))]
    workers = list(set(workers) - set(["mia", "testing", "zephyrus"]))
    
    data = []
    for worker in workers:
        df = pd.read_json(f'datasets/{worker}/HTTP/{worker}_date_06.05.2024.json')

# Generate hover text for each point
        hover_text = [
            f"{row['sent_at'].strftime('%b %d, %Y, %H:%M:%S')}, {row['time_it_took']/1000:.3f}s - {'TOS/DS was changed' if row['tos_changed'] else 'TOS/DS was not changed'}"
            for index, row in df.iterrows()
        ]
        line = go.Scatter(
                x=df['sent_at'],
                y=df['time_it_took']/1000,
                mode='lines',
                name= region(worker),
            text=hover_text,  # Set the hover text
                    hoverinfo='text+name'  # Display custom text and the name of the trace on hover
            )
    
        data.append(line)
    graphJSON = json.dumps(data, cls=plotly.utils.PlotlyJSONEncoder)
    
    return render_template('latency_dashboard_http.html', graphJSON=graphJSON)

@app.route('/update_graph_latency_http', methods=['POST'])
def update_graph_latency_http():
    print("Updating...")
    if request.method == 'POST':
        files = (os.listdir("datasets/"))
        workers = [item for item in files if os.path.isdir(os.path.join("datasets/", item))]
        workers = list(set(workers) - set(["mia", "testing", "zephyrus"]))
        
        data = []
        for worker in workers:
            df = pd.read_json(f'datasets/{worker}/HTTP/{worker}_date_06.05.2024.json')

    # Generate hover text for each point
            hover_text = [
                f"{row['sent_at'].strftime('%b %d, %Y, %H:%M:%S')}, {row['time_it_took']/1000:.3f}s - {'TOS/DS was changed' if row['tos_changed'] else 'TOS/DS was not changed'}"
                for index, row in df.iterrows()
            ]

            line = go.Scatter(
                    x=df['sent_at'],
                    y=df['time_it_took']/1000,
                    mode='lines',
                    name= region(worker),
                    text=hover_text,  # Set the hover text
                    hoverinfo='text+name'  # Display custom text and the name of the trace on hover
                )
      
            data.append(line)
        graphJSON = json.dumps(data, cls=plotly.utils.PlotlyJSONEncoder)
        return graphJSON

# ------------------------------------------------------------------------------------------------------------
@app.route('/latency_dashboard_rtp')
def latency_dashboard_rtp():
    files = (os.listdir("datasets/"))
    workers = [item for item in files if os.path.isdir(os.path.join("datasets/", item))]
    workers = list(set(workers) - set(["mia", "testing", "zephyrus"]))
    
    data = []
    for worker in workers:
        df = pd.read_json(f'datasets/{worker}/RTP/{worker}_date_06.05.2024.json')

# Generate hover text for each point
        hover_text = [
            f"{row['sent_at'].strftime('%b %d, %Y, %H:%M:%S')}, {row['time_it_took']/1000:.3f}s - {'TOS/DS was changed' if row['tos_changed'] else 'TOS/DS was not changed'}"
            for index, row in df.iterrows()
        ]

        line = go.Scatter(
                x=df['sent_at'],
                y=df['time_it_took']/1000,
                mode='lines',
                name= region(worker),
            text=hover_text,  # Set the hover text
                    hoverinfo='text+name'  # Display custom text and the name of the trace on hover
            )
    
        data.append(line)
    graphJSON = json.dumps(data, cls=plotly.utils.PlotlyJSONEncoder)
    
    return render_template('latency_dashboard_rtp.html', graphJSON=graphJSON)

@app.route('/update_graph_latency_rtp', methods=['POST'])
def update_graph_latency_rtp():
    print("Updating...")
    if request.method == 'POST':
        files = (os.listdir("datasets/"))
        workers = [item for item in files if os.path.isdir(os.path.join("datasets/", item))]
        workers = list(set(workers) - set(["mia", "testing", "zephyrus"]))
        
        data = []
        for worker in workers:
            df = pd.read_json(f'datasets/{worker}/RTP/{worker}_date_06.05.2024.json')

    # Generate hover text for each point
            hover_text = [
                f"{row['sent_at'].strftime('%b %d, %Y, %H:%M:%S')}, {row['time_it_took']/1000:.3f}s - {'TOS/DS was changed' if row['tos_changed'] else 'TOS/DS was not changed'}"
                for index, row in df.iterrows()
            ]

            line = go.Scatter(
                    x=df['sent_at'],
                    y=df['time_it_took']/1000,
                    mode='lines',
                    name= region(worker),
                    text=hover_text,  # Set the hover text
                    hoverinfo='text+name'  # Display custom text and the name of the trace on hover
                )
      
            data.append(line)
        graphJSON = json.dumps(data, cls=plotly.utils.PlotlyJSONEncoder)
        return graphJSON


# ------------------------------------------------------------------------------------------------------------
@app.route('/latency_dashboard_sip')
def latency_dashboard_sip():
    files = (os.listdir("datasets/"))
    workers = [item for item in files if os.path.isdir(os.path.join("datasets/", item))]
    workers = list(set(workers) - set(["mia", "testing", "zephyrus"]))

    data = []
    for worker in workers:
        df = pd.read_json(f'datasets/{worker}/SIP/{worker}_date_06.05.2024.json')

# Generate hover text for each point
        hover_text = [
            f"{row['sent_at'].strftime('%b %d, %Y, %H:%M:%S')}, {row['time_it_took']/1000:.3f}s - {'TOS/DS was changed' if row['tos_changed'] else 'TOS/DS was not changed'}"
            for index, row in df.iterrows()
        ]
        
        line = go.Scatter(
                x=df['sent_at'],
                y=df['time_it_took']/1000,
                mode='lines',
                name= region(worker),
            text=hover_text,  # Set the hover text
                    hoverinfo='text+name'  # Display custom text and the name of the trace on hover
            )
    
        data.append(line)
    graphJSON = json.dumps(data, cls=plotly.utils.PlotlyJSONEncoder)
    
    return render_template('latency_dashboard_sip.html', graphJSON=graphJSON)

@app.route('/update_graph_latency_sip', methods=['POST'])
def update_graph_latency_sip():
    print("Updating...")
    if request.method == 'POST':
        files = (os.listdir("datasets/"))
        workers = [item for item in files if os.path.isdir(os.path.join("datasets/", item))]
        workers = list(set(workers) - set(["mia", "testing", "zephyrus"]))
        
        data = []
        for worker in workers:
            df = pd.read_json(f'datasets/{worker}/SIP/{worker}_date_06.05.2024.json')

    # Generate hover text for each point
            hover_text = [
                f"{row['sent_at'].strftime('%b %d, %Y, %H:%M:%S')}, {row['time_it_took']/1000:.3f}s - {'TOS/DS was changed' if row['tos_changed'] else 'TOS/DS was not changed'}"
                for index, row in df.iterrows()
            ]

            line = go.Scatter(
                    x=df['sent_at'],
                    y=df['time_it_took']/1000,
                    mode='lines',
                    name= region(worker),
                    text=hover_text,  # Set the hover text
                    hoverinfo='text+name'  # Display custom text and the name of the trace on hover
                )
      
            data.append(line)
        graphJSON = json.dumps(data, cls=plotly.utils.PlotlyJSONEncoder)
        return graphJSON



if __name__ == '__main__':
    app.run(debug=True,host="0.0.0.0")
