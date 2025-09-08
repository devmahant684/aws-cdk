import requests
import threading

url = "http://65.2.40.5/"

num_requests = 900000
concurrency = 50

def worker():
    for _ in range(num_requests // concurrency):
        try:
            requests.get(url)
        except Exception as e:
            pass

threads = []
for i in range(concurrency):
    t = threading.Thread(target=worker)
    t.start()
    threads.append(t)

for t in threads:
    t.join()

print("Load test finished ✅")