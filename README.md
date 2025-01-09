# State Machine Package

[![Build Test](https://github.com/DHBW-Smart-Rollerz/state_machine/actions/workflows/build-test.yaml/badge.svg)](https://github.com/DHBW-Smart-Rollerz/state_machine/actions/workflows/build-test.yaml)

This repository contains the state machine package for ros2 (python).

## State Machine Concept

The state machine has for each discipline a separate FSM that are all contained in one top level state machine.

### Free Drive
#### States
- Start = while being in the startbox and waiting for it to open
- Driving = while driving around the track


### Obstacle Avoidance
#### States
The different states in the obstacle avoidance more 
- Start = while being in the startbox and waiting for it to open
- Driving = while driving normally without any specific scenario
- Parking = while being in parking area
- No-Passing Zone = while being in the no-passing zone
- Expressway = while being in the expressway
- Pedestrian Crossing = when a pedestrian crossing is detected until it is passed
- Intersection = when an intersection is detected until it is passed (can be divided down into the different intersection types)
- Overtaking = when an obstacle is detected until it is fully passed


## Structure

- `config/`: All configurations (most of the time yaml files)
- `launch/`: Contains all launch files. Launch files can start multiple nodes with yaml-configurations
- `resource/`: Contains the package name (required to build with colcon)
- `state_machine`: Contains all nodes and sources for the ros package
- `test/`: Contains all tests
- `package.xml`: Contains metadata about the package
- `setup.py`: Used for Python package configuration
- `setup.cfg`: Additional configuration for the package
- `requirements.txt`: Python dependencies

## Contributing

Thank you for considering contributing to this repository! Here are a few guidelines to get you started:

1. Fork the repository and clone it locally.
2. Create a new branch for your contribution.
3. Make your changes and ensure they are properly tested.
4. Commit your changes and push them to your forked repository.
5. Submit a pull request with a clear description of your changes.

We appreciate your contributions and look forward to reviewing them!

## License

This repository is licensed under the MIT license. See [LICENSE](LICENSE) for details.
