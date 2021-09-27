# wlan-laas-quali

This Repo holds the code base related to the Quali CloudShell installation.<br>
The repo should be kept up to date with what is being run within CloudShell.<br>
Each folder will contain a more detailed summary of its contents.<br><br>

* [Orchestration](Orchestration)
* [Scripts](Scripts)
* [Shells](Shells)

## Orchestration

The Orchestration contains Generic scripts including Blueprint scripts, Resource Scrips, Setup scripts and Teardown scripts.
The type of script denotes when or from where the script can be run, either automatically or manually through the UI/API.
CloudShell documentation on Orchestration Scripts can be found [here](help.quali.com/Online%20Help/0.0/Portal/Content/DevGuide/Orch-Scripts/Developing-Orch-Scripts.htm).<br><br>
Blueprint scripts will be run on the Sandbox level and will not be run automatically.<br><br>
Resource scripts will be run on the Resource level and will not be run automatically.<br><br>
Setup Scripts will be run on the Sandbox level and will be run automatically when reserving a Blueprint.<br><br>
Teardown Scripts will be run on the Sandbox level and will be run automatically when ending a resevation.<br><br>

## Scripts

The Scripts folder contains any CloudShell related scripts that need a repo to live in.<br>
These can include scripts that CloudShell will download and run from this repo or scripts to be run externally that interact with CloudShell through any of it's APIs.
Documentation on CloudShell's APIs can be found [here](help.quali.com/Online%20Help/0.0/Portal/Content/API/CS-API-Guide.htm).

## Shells

The Shells folder contains any resource Shells created and used within CloudShell. Shells contain code to create an instance within CloudShell of any physical or virtual resource to be used within a Sandbox environment.
Shells will also define and set attributes on the created resource instance to be used within the various automated processes within CloudShell.
Shells are typically created for a specific OS to keep away from any command incompatibilities. <br><br>

In depth information on Shell development can be found [here](help.quali.com/Online%20Help/0.0/Portal/Content/DevGuide/Shells/Intro-to-Shell-Dev.htm).

## Usage

All Scripts and shells are loading into CloudShell through the web UI, or shells can also be loaded through the shellfoundry cli tool.
Before loading, scripts and shells must be zipped. For shells specifically, the 'src' folder must be zipped with filename specified at the bottom of the 'shell-definition.yaml' as well.