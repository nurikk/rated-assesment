import pathlib

from bytewax import operators as op
from bytewax.connectors.files import DirSource
from bytewax.dataflow import Dataflow

logs_input = DirSource(dir_path=pathlib.Path("/Users/ainur.timerbaev/code/rated-assesment/logs/"),
                       glob_pat="*.log")
flow = Dataflow("api_requests")

