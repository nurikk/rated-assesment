import datetime
import random
import sys


# Function to generate random timestamp
def generate_timestamp():
    start_date = datetime.datetime.now() - datetime.timedelta(days=30)
    random_seconds = random.randint(0, 30 * 24 * 60 * 60)
    return start_date + datetime.timedelta(seconds=random_seconds)


if __name__ == "__main__":
    # Parameters
    log_file = sys.argv[1] or "api_requests.log"
    num_entries = int(sys.argv[2]) or 10000

    random.seed(42)  # Set seed before generating durations

    # Possible values for log fields
    customer_ids = [f"cust_{i}" for i in range(1, 51)]
    request_paths = ["/api/v1/resource1", "/api/v1/resource2", "/api/v1/resource3", "/api/v1/resource4"]
    status_codes = [200, 201, 400, 401, 403, 404, 500]
    durations = [random.uniform(0.1, 2.0) for _ in range(num_entries)]

    # Generate log entries
    with open(log_file, "w") as f:
        for _ in range(num_entries):
            timestamp = generate_timestamp().strftime("%Y-%m-%d %H:%M:%S")
            customer_id = random.choice(customer_ids)
            request_path = random.choice(request_paths)
            status_code = random.choice(status_codes)
            duration = f"{random.choice(durations):.3f}"
            f.write(f"{timestamp} {customer_id} {request_path} {status_code} {duration}\n")

    print(f"Log file '{log_file}' generated with {num_entries} entries.")
