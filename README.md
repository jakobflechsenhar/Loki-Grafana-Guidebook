# -------------------------------------------------------- #
# ReadMe: Loki + Grafana Guidebook
# -------------------------------------------------------- #


--------------------------------------------------------
# 💡 The Big Picture
A centralized logging system that collects, stores, and visualizes logs from multiple sources - eliminating the need to SSH into individual servers to check log files.
--------------------------------------------------------


--------------------------------------------------------
# 🏗️ The Architecture
1. Python Log Generator Script:
Purpose: Simulates real applications generating logs
Why: In production, you'd have actual apps (web servers, databases, microservices) generating logs
What it does: Creates realistic time-stamped logs with different severity levels (INFO, WARNING, ERROR)

2. Promtail:
Purpose: Log collector/shipper
What it does:
    - Watches the log files using a glob pattern (/work/logs/*.log)
    - Adds metadata (labels) like job="pythonapps" and filename="/work/logs/app1.log"
    - Ships logs to Loki in real-time

3. Loki:
Purpose: Log aggregation and storage system (like Prometheus, but for logs)
Why: Stores logs more efficiently than Prometheus by avoiding full-text indexing
What it does:
    - Receives logs from Promtail
    - Indexes them by labels (not full-text indexing)
    - Stores compressed log data
    - Provides a query API

4. Grafana:
Purpose: Visualization and query interface
What it does:
    - Connects to Loki as a data source
    - Lets you write LogQL queries (Loki's query language)
    - Can create dashboards, visualizations, and alerts
--------------------------------------------------------


--------------------------------------------------------
# 🏃 Run the Stack

1. Create isolated network for containers to communicate:
docker network create loki-network

2. Start Loki:
docker run -d --name loki-container \     # create and start a new container in detached mode
  --network loki-network \     # network in which the container is placed
  -p 3100:3100 \     # maps port 3100 from container to port 3100 on your computer/localhost
  -v $(pwd)/loki-config.yml:/etc/loki/local-config.yml \     # volume mounting the main config file 
  grafana/loki:latest      # base image
        This command creates a new container called 'loki-container' from the base Grafana Loki image. It mounts my local configuration file (loki-config.yml from the current directory) into the container at /etc/loki/local-config.yaml, replacing the default configuration. The container then runs Loki using this custom configuration.

3. Generate logs:
python3 -u log-generator-script.py > generated-logs.log &
        python3 log-generator-script.py - runs the python script that generates logs
        > generated-logs.log - redirects all output into a file called generated-logs.log
        & - runs the command in the background

4. Start Promtail:
docker run -d --name promtail-container \
--network loki-network \
-v $(pwd)/promtail-config.yml:/etc/promtail/config.yml \
-v $(pwd)/generated-logs.log:/logs/app.log \
grafana/promtail:latest

5. Start Grafana:
docker run -d --name grafana-container \
--network loki-network \
-p 3000:3000 \
grafana/grafana:latest

6. Configure Grafana:
a. Access Grafana: http://localhost:3000 (login: admin/admin)
b. Add Loki Data Source: Data Sources → Add data source → Choose "Loki" → URL: http://loki-container:3100 → Click "Save & Test"
c. Query Logs: Go to Explore, try these queries:
     {job="myapp"} # All logs
     {job="myapp"} |= "ERROR" # Only errors
     count_over_time({job="myapp"} |= "ERROR" [1m]) # Count errors per minute

7. Cleanup:
docker stop promtail-container loki-container grafana-container
docker rm promtail-container loki-container grafana-container
docker network rm loki-network
kill %1 # Stops the background log generator process
rm generated-logs.log
--------------------------------------------------------
