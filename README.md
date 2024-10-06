# Log processing and Api

This project consists of two parts:
# Log processing 
    Log processing is done using [bytewax](bytewax.io/) platform.
    Due to nature of auto generated log file (log records timestamps generated in random order, 
    parmaeter `wait_for_system_duration` has to be set to datetime.timedelta.max in order 
    to correctly process daily windows. This isn't a best approach, due to potential memory impact, 
    this parameter can be configured using `WAIT_FOR_SYSTEM_DURATION` environment variable.
    Data is written to database using SQLAlchemy ORM
# Api
    It's a simple FastApi application that exposes one endpoint `/customers/{customer_id}/stats`
    that returns statistics for a given customer. 
    Database access is done using SQLAlchemy ORM using asyn driver.


## Start the project
For convenience, docker-compose is used to start the project. 
```bash
docker-compose up -d
```

After docker-compose is up, you can access the FastApi application 
at `http://localhost:8888/customers/cust_1/stats?from=2024-09-03`

Quick test with [siege](https://github.com/JoeDog/siege) demonstrates that application 
handles 500 requests per second with 0% failure rate, thanks to async database access.

```bash
siege --time 1m "http://localhost:8888/customers/cust_1/stats?from=2024-09-03"
```

```
Lifting the server siege...
Transactions:		       29576 hits
Availability:		      100.00 %
Elapsed time:		       60.41 secs
Data transferred:	      169.35 MB
Response time:		        0.05 secs
Transaction rate:	      489.59 trans/sec
Throughput:		        2.80 MB/sec
Concurrency:		       24.79
Successful transactions:       29576
Failed transactions:	           0
Longest transaction:	        6.83
Shortest transaction:	        0.00
```


# Deliverables
In a GitHub repo, please include the following:

Generated Log File: api_requests.log created using the provided generator script.
Log Processor: Script to create the database schema and populate it with log data.
API Implementation: Source code for the API with the required endpoint.
README: A brief README file with instructions on how to set up and run the database script and API server.