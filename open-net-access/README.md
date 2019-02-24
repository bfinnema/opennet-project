# OpenNet project

## The context of the project

This project aims to enable different service providers to operate a same network to provide connection to their customers on a wholesale network. This is done using vlans and pseudo-wires through different network equipments. What we want with this project is to automate links creation using NSO and so to automatically configure different equipments to build connection between customers, using service providers informations.

## This repository

This repository contains the basic yang model for the project inventory. The goal of the inventory is to provide us a database that we will use to compute variables values in order to instanciate services and so to configure devices. 
This inventory contains 6 main parts:
* Service provider informations that contains all the SPs information 
* PoI areas that define different interconnection zones
* PE areas that defines PE nodes
* Access area that define access nodes
* Services list that describes different services (ie links between customers) informations
* Customers list that contains the list of the customers 

## More information

Project wiki: https://wiki.cisco.com/display/ADT/OpenNet+Access

Project core service: https://wwwin-github.cisco.com/spa-ie/open-net-core
