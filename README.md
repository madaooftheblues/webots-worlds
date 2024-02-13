# Simulating Industry 4.0 for the Study of Human-Robot Collaboration
A heterogeneous environment where robots of different types collaborate with humans is simulated using Webots.
Through the simulation of the industrial environment, productive ways can be deduced for deployment of intelligent robots in the local industry. 
The scope includes sensors and perception, actuators and actions, maintaining team and task states.
The project incorporates an easy-to-setup, cost-effective and convenient simulation of human-robot collaboration on the industrial floor, which can later be deployed on-field. 

> Check out the frontend interface of the simulation [here](https://github.com/madaooftheblues/simulation_interface).

![A broad shot of the simulation](./assets/images/simulation_view.png)

## Scenario Tested
Suppose a heterogeneous environment, where humans and robots are working together.
The human operator is in need of a tool and asks the robots to fetch it.
The robots then collaborate to deliver the requested object to the human. 

![A closeup shot of the simulation](./assets/images/simulation_closeup.png)


> The requested object is first identified, and if it present, it is picked up by a UR5e manipulator/arm robot. The arm which is closer to the identified object picks it up.

![A ur5e manipulator robot picking up the requested object](./assets/images/ur5e_pick_place.png)



> The UR5e that has picked the object then waits for the Pioneer 3-DX mobile robot to to arrive at the appropriate catching location.

![A Pioneer 3-DX mobile robot at a suitable location to catch the object from UR5e arm robot](./assets/images/pioneer_fetch.png)



> As the mobile robot reaches the location, the arm robot drops the object onto a basket embedded on the mobile robot.

![The mobile robot catches the requested object](./assets/images/pioneer_catch.png)



> The mobile robot then delivers the caught object to the human's location

![A mobile robot delivering an object to the human's location](./assets/images/pioneer_delivery.png)

## Summary
The purpose of this study was to simulate an industrial setup to experiment with human-robot interaction and collaborative scenarios, where the number of incoming jobs is higher than the number of robots available; task execution is based on first-come-first-serve principle. The simulaion has established a baseline for the study of preemptive task scheduling in robots, to manage the ‘task vs resource’ availability dilemma.
