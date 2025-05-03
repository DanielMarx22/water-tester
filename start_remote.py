import subprocess
import time
import requests
import os

# Start the Flask server
flask = subprocess.Popen(["python3", "app.py"])
time.sleep(3)  # Give Flask time to start

# Start ngrok
ngrok = subprocess.Popen(["/snap/bin/ngrok", "http", "5050"])
print("Started ngrok... waiting for public URL.")

# Wait until the public ngrok URL is available
ngrok_url = ""
for _ in range(30):
    try:
        response = requests.get("http://localhost:4040/api/tunnels", timeout=2).json()
        ngrok_url = response['tunnels'][0]['public_url']
        break
    except Exception:
        time.sleep(1)

# If we got a valid URL, update local files and push to GitHub
if ngrok_url.startswith("http"):
    # Write to local file
    with open("ngrok_url.txt", "w") as f:
        f.write(ngrok_url + "\n")

    # Update GitHub index.html for redirect
    with open("index.html", "w") as f:
        f.write(f"""<!DOCTYPE html>
<html>
  <head>
    <meta http-equiv="refresh" content="0;url={ngrok_url}">
  </head>
</html>
""")
    # Git add, commit, and push
    subprocess.run(["git", "add", "ngrok_url.txt", "index.html"])
    subprocess.run(["git", "commit", "-m", "Update index.html with new ngrok URL"])
    subprocess.run(["git", "push"])
    print(f"✅ Ngrok URL updated and pushed: {ngrok_url}")
else:
    print("❌ Failed to retrieve ngrok URL.")

# Keep the service alive
try:
    while True:
        time.sleep(60)
except KeyboardInterrupt:
    flask.terminate()
    ngrok.terminate()
