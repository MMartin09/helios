# Definitions

This page contains important definitions that are used within the service.

## Consumer-Type

Consumers are separated into two types depending on the number of components they have.

- `SCC`: _Single-Component Consumer_ is a consumer with just one component.
- `MCC`: _Multi-Component Consumer_ is a consumer with $[2, n]$ components.

## Grid Mode

The grid mode defines the direction of the powerflow and can have one of the following three states.

- `NOT_SET`: Grid mode is not set in the applicatio. During the normal operation this mode should never be active.
- `FEED_IN`: Feed energy into the grid. This mode is active if more energy is produced than directly consumed.
- `CONSUME`: Consume energy from the grid. This mode is active if more engergy is consumed from the grid then is produced.

## Consumer-Status

At any time a consumer has one of the possible status.

- `STOPPED`: The consumer is not running (for MCC this means that no component is active).
- `PARTIAL_RUNNING`: Only used for _MCC_. At least one component is running but not all.
- `RUNNING`: The consumer is running (for MCC this means all components are active).

## Consumer-Mode

- `DISABLED`: The consumer is no longer controlled by the service. A consumer marked as _disabled_ will also not be reseted to _automatic_.
- `AUTOMATIC`: The consumer is controlled using the service.
- `HAND_ON`: The consumer was turned on by hand. The service will however reset the mode to _automatic_.
- `HAND_OFF`: The consumer was turned off by hand. The service will however reset the mode to _automatic_.
