import subprocess
import time
import requests

# Start the Flask server
flask = subprocess.Popen(["python3", "app.py"])
time.sleep(3)  # Give Flask time to start

# Start ngrok
ngrok = subprocess.Popen(["/snap/bin/ngrok", "http", "5050"])
print("Started ngrok... waiting for public URL.")

# Wait until the public ngrok URL is available
ngrok_url = ""
for _ in range(30):  # Retry for up to ~30 seconds
    try:
        response = requests.get("http://localhost:4040/api/tunnels", timeout=2).json()
        ngrok_url = response['tunnels'][0]['public_url']
        break
    except Exception:
        time.sleep(1)

# Write the ngrok URL to a file or report failure
if ngrok_url.startswith("http"):
    with open("/home/danielmarx/Desktop/CodeStuff/ngrok_url.txt", "w") as f:
        f.write(ngrok_url + "\n")
    print(f"Ngrok URL: {ngrok_url}")

    # Also write to GitHub index.html for global redirect
    with open("/home/danielmarx/Desktop/CodeStuff/index.html", "w") as f:
        f.write(f"""<!DOCTYPE html>
<html>
  <head>
    <meta http-equiv="refresh" content="0;url={ngrok_url}">
  </head>
</html>
""")

    # Commit and push the new index.html to GitHub
    subprocess.run(["git", "-C", "/home/danielmarx/Desktop/CodeStuff", "add", "index.html"])
    subprocess.run(["git", "-C", "/home/danielmarx/Desktop/CodeStuff", "commit", "-m", "Update index.html with new ngrok URL"])
    subprocess.run(["git", "-C", "/home/danielmarx/Desktop/CodeStuff", "push"])
else:
    print("❌ Failed to get ngrok URL after waiting.")

# Keep the service alive
try:
    while True:
        time.sleep(60)
except KeyboardInterrupt:
    flask.terminate()
    ngrok.terminate()
