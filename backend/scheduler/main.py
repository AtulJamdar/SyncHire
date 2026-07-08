import time
import sys

def main():
    print("Job Finder AI Scheduler starting up...", flush=True)
    try:
        while True:
            print("Scheduler heartbeat...", flush=True)
            time.sleep(10)
    except KeyboardInterrupt:
        print("Scheduler shutting down...", flush=True)
        sys.exit(0)

if __name__ == "__main__":
    main()
