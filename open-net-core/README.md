# OpenNet project

## The context of the project

This project aims to enable different service providers to operate a same network to provide connection to their customers on a wholesale network. This is done using vlans and pseudo-wires through different network equipments. What we want with this project is to automate links creation using NSO and so to automatically configure different equipments to build connection between customers, using service providers informations.

## This repository

This repository contains the main NSO service that provides the core algorithm of the project. This service takes as inputs references to the inventory and compute differnet variables that we will push to bottom services, that directly configure devices. This services aims to merge all different informations coming from the user and from the inventory to automaticaly build expected links.

## More information

Project wiki: https://wiki.cisco.com/display/ADT/OpenNet+Access

Project inventory: https://wwwin-github.cisco.com/spa-ie/open-net-access
