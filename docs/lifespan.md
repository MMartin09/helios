# Lifespan

## On-Start

- Load the current configuration from the database
- Check if all keys are present in the database. If there are missing keys create them with the default value.
- Synchronize the consumers with the database
    - Iterate over all available consumers and compare the true state against the state in the database. If they are not matching update the database (consumption, status, ...)
