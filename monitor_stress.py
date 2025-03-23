import psutil
import time
import subprocess
import requests
import shutil

# Constants
THRESHOLD = 75  # CPU usage percentage
STRESS_DURATION = 45  #Duration for stress test
STRESS_CORES = 4  # Number of CPU cores to stress
GCP_TRIGGER_URL = "https://scale-up-instance-xk4lfjdp7a-em.a.run.app"  

# GCP Instance Group Details
PROJECT = "m23csa520-vcc-sem3"  # Update with your actual project ID
ZONE = "asia-south2-a"  # Update with your actual zone
INSTANCE_GROUP = "vcc-auto-scale-group"  # Update with your actual instance group
NEW_SIZE = 2  # Target size after scaling up

def start_stress():
    """Start a CPU stress test using 'stress-ng' and wait for CPU to rise."""
    print("Low CPU detected! Running stress test...")

    if not shutil.which("stress-ng"):
        print("Error: 'stress-ng' not found. Installing it...")
        subprocess.run(["sudo", "apt", "update"], check=True)
        subprocess.run(["sudo", "apt", "install", "-y", "stress-ng"], check=True)

    # Start stress-ng in background
    process = subprocess.Popen([
        "stress-ng", "--cpu", str(STRESS_CORES),
        "--cpu-method", "matrixprod", "--cpu-load", "80",
        "--timeout", str(STRESS_DURATION)
    ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    print("Waiting for CPU load to increase...")

    # **Wait until CPU load crosses THRESHOLD before returning**
    while True:
        time.sleep(5)  # Give some time for stress to take effect
        cpu_usage = psutil.cpu_percent(interval=1)
        print(f"Current CPU usage: {cpu_usage}%")

        if cpu_usage >= THRESHOLD:
            print("CPU load has increased successfully! Triggering cloud deployment...")
            trigger_gcp_scaling()
            break  # Stop waiting and return

def trigger_gcp_scaling():
    """Trigger GCP function to scale up instances."""
    payload = {
        "project": PROJECT,
        "zone": ZONE,
        "instance_group": INSTANCE_GROUP,
        "size": NEW_SIZE
    }
    
    headers = {"Content-Type": "application/json"}
    
    try:
        response = requests.post(GCP_TRIGGER_URL, json=payload, headers=headers)
        print(f"Cloud response: {response.status_code} - {response.text}")
        
        if response.status_code != 200:
            print("Check GCP function logs for errors!")
    
    except requests.RequestException as e:
        print(f"Failed to reach cloud function: {e}")

def check_resources():
    """Monitor CPU usage and trigger stress test if needed."""
    while True:
        cpu_usage = psutil.cpu_percent(interval=5)
        memory_usage = psutil.virtual_memory().percent
        print(f"CPU: {cpu_usage}%, Memory: {memory_usage}%")

        if cpu_usage < THRESHOLD:  # Start stress if CPU is low
            start_stress()

        time.sleep(2)  # Check every 2 seconds

if __name__ == "__main__":
    check_resources()
