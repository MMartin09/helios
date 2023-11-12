# Helios

[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/charliermarsh/ruff/main/assets/badge/v1.json)](https://github.com/charliermarsh/ruff)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg?style=flat-square)](https://github.com/psf/black)
[![Imports: isort](https://img.shields.io/badge/%20imports-isort-%231674b1?style=flat-square&labelColor=ef8336)](https://pycqa.github.io/isort/)
[![pre-commit](https://img.shields.io/badge/pre--commit-enabled-brightgreen?logo=pre-commit)](https://github.com/pre-commit/pre-commit)

*Helios* is a photovoltaic (PV) automation and monitoring tool.
The service controls a list of consumers depending on the current PV production and grid flow.
The aim is to keep the surplus as small as possible at any time while simultaneously avoiding the grid's consumption.
Further, the service is used to monitor the entire system in an InfluxDB database.
This includes the monitoring of the production and the power flow as well as further attributes such as the consumers' state transition times.

Please note this is a hobby project that is only maintained by the repository owner.
If you are interested in the service or want to use it for your own PV automation, please feel free to contact me.

**Compatibility:**

The system uses a Fronius Symo converter and Shelly devices for the consumers.
In the design of the code, however, care was taken to implement an architecture that allows simple integration of different device types.

**Motivation and Background:**

Helios was founded out of necessity for a very customized automation service for different customers.
The particular requirements that are implemented within this service are not fulfilled by various commercial tools.
Further, most of the available tools only support a tiny set of consumers (e.g., only specific brands) or are very expensive (especially the acquisition costs).
Due to these reasons and personal interest, it was decided to implement a custom service.

**Technologies:**

The service is built as a RestAPI using the Python framework FastAPI.
It uses MariaDB to store the configuration of the service, such as the available consumers or the automation setting parameters.
Further, it uses InfluxDB for the storage of time-series data, such as the PV production rate or the changes in the consumer state.
The entire service, including the databases, is running on a Raspberry Pi.
