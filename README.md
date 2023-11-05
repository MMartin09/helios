# Helios


## Project structure

**automation_settings**
Domain-package the automation settings.

**consumer**
Domain-package for the consumers.

**core**
Contains the code relevant for the *core* of the API.

**current_data**
Domain-package for the current measurement data.
This includes for example the current powerflow as well as the current meter data.

**dto**
Contains *Data Transfer Objects*.

**integrations**
Contains the integrations to interact with the "hardware" components.
Each type of component (e.g., switch) is separated into a sub-package.

**services**
A collection of various service classes.

**utils**
Various helper functions.

## Contribution

Enable *pre-commit* hooks: `pre-commit install`
