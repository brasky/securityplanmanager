# Security Plan Manager
## Overview
Security Plan Manager (SPM) is a django app for automating tasks associated FedRAMP documentation. It was created with the idea that the system security plan (SSP) is the source of truth for most organizations and that most edits are done manually due to the cumbersome nature of FedRAMP's templates and word document automation in general. 


## Features
Currently the backend logic behind importing/exporting is the focus of development, so the UI is extremely lacking, although most everything is at least exposed in the UI.
Features available today are:
- Importing a FedRAMP SSP word document (strict formatting requirements below)
- Exporting FedRAMP SSP word document
- Exporting a Customer Implementation Summary (CIS) excel workbook
- In UI editing of CIS details or implementation details


## Setup

1. Install Django and start a new project
2. Run `python manage.py migrate`
3. Clone this repo into the project folder
4. Edit yourproject/settings.py:
   - Add the following to INSTALLED_APPS:
     - securityplanmanager.apps.SecurityPlanManagerConfig
     - django.contrib.humanize
   - You can also configure your database selection here
   - Do not commit this file to source control
   - Do not run in production with Debug on.
5. Edit yourproject/urls.py:
   - Add the following import:
     - `from django.urls import path, include`
   - Add the following urlpatterns:
     - `path('', include('securityplanmanager.urls'))`
6. Run `python manage.py makemigrations securityplanmanager` then `python manage.py migrate`
7. Start the server with `python manage.py runserver` and make sure you can connect on localhost:8000, then shut the server down.
8. Now run `python manage.py populate_db` to import controls, currently this imports all controls from the NIST's 800-53-controls.xml which includes withdrawn controls and controls not selected in any FedRAMP baseline. This also deletes all existing controls, it's meant for first time setup only and may take a few minutes.
9. Add an SSP with the first half filled out, but with blank control implementations into `static\fedramp_templates` and rename it `high.docx` (right now everything is assumed to be for FedRAMP High, this will be configurable eventually). This is what will be used as a template when exporting an SSP.
10. Now the server is set up and ready for an SSP to be imported.

## SSP Import and Formatting Requirements

The goal of this project was to support uploading a word document to fill out SSP data into a database, which has a lot of upside, but some tradeoffs as well. One of the major downsides is that in order to reliably upload the level of detail needed, the SSP must be formatted pretty strictly. This includes typos in FedRAMP's own templates, which are very difficult to get them to resolve. 

### Define your teams
Teams should be defined in SPM before uploading an SSP. Team names should match how they are referred to in the SSP (see implementation table example below). 

### Control Summary Information table:
#### Parameters
For most controls, you can just include your parameter in the box and it will work fine. The major exception is when there are two parameters in one control. For example, AC-2 (2) has two parameters, so in the Control Summary Information parameter boxes they must say: `Parameter AC-2 (2)-1:` and `Parameter AC-2 (2)-2:` in order for parameters to be correctly imported.

For parameters like AC-1(a)(1), where the parameter is defined as AC-1(a), a good solution has not been implemented yet, so those parameters are not uploaded.

### Implementation table:
The general flow of an implementation should look something like this example for AC-1: 

![alt text](https://puu.sh/Dxc2I/10534c1520.png "Implementation Table for AC-1(a)(1)")

Customer responsibilities are put at the top of the implementation box, but are captured for all subsequent control parts. So AC-1(a)(1) and AC-1(a)(2) will have the same customer responsibility in SPM. 

For part a, all service teams operate in the same way, so they are all included together with a single implementation beneath. In SPM in the backend this is a single Implementation object tied to a control with a many-to-many relationship with team objects.

For part b, Team C does things differently so they are put on their own line under the Part 2: header. In SPM this will show up as AC-1(b)(1) and AC-1(b)(2) as having 2 Implementation objects tied to each control. One implementation will have a many-to-many relationship with Team A and Team B, the other with just Team C. 




