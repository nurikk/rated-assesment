Here's a more readable and formatted version of your markdown:

# Log Processing and API

This project consists of two parts:

## Log Processing

Log processing is done using the [Bytewax](https://bytewax.io/) platform. Due to the nature of the auto-generated log file (log records timestamps generated in random order), the parameter `wait_for_system_duration` has to be set to `datetime.timedelta.max` in order to correctly process daily windows. This isn't the best approach due to potential memory impact. This parameter can be configured using the `WAIT_FOR_SYSTEM_DURATION` environment variable. Data is written to the database using SQLAlchemy ORM.

## API

It's a simple FastAPI application that exposes one endpoint `/customers/{customer_id}/stats` that returns statistics for a given customer. Database access is done using SQLAlchemy ORM with an async driver. While it's a bit overkill for this project, it allows using ORM and auto-generating the database schema.

The database schema is created using SQLAlchemy's `Base.metadata.create_all()` method. This isn't the best approach for production, but it's good enough for this project and less overkill than bringing in Alembic for a single table.

## Start the Project

For convenience, [Docker Compose](./docker-compose.yml) is used to start the project.

```bash
docker-compose up -d
```

After Docker Compose is up, you can access the FastAPI application at `http://localhost:8888/customers/cust_1/stats?from=2024-09-03`.

A quick test with [Siege](https://github.com/JoeDog/siege) demonstrates that the application handles 500 requests per second with a 0% failure rate, thanks to async database access.

```bash
siege --time 1m "http://localhost:8888/customers/cust_1/stats?from=2024-09-03"
```

```
Lifting the server siege...
Transactions:               29576 hits
Availability:               100.00 %
Elapsed time:               60.41 secs
Data transferred:           169.35 MB
Response time:              0.05 secs
Transaction rate:           489.59 trans/sec
Throughput:                 2.80 MB/sec
Concurrency:                24.79
Successful transactions:    29576
Failed transactions:        0
Longest transaction:        6.83
Shortest transaction:       0.00
```

# Deliverables

In a GitHub repo, please include the following:

- **Generated Log File**: [api_requests.log](./logs/api_requests.log) created using the provided generator script.
- **Log Processor**: Script to [create the database](./src/scripts/init_schema.py) schema and [populate it with log data](./src/ingest/log_parser.py).
- **API Implementation**: Source code for the [API](./src/api/routers/stats.py) with the required endpoint.
- **README**: A brief README file with instructions on how to set up and run the database script and API server.

# Technologies
- Bytewax
- FastAPI
- SQLAlchemy
- Pydantic
- Docker Compose
- Siege
