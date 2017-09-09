
# Safety Management System Project for Udacity Full-Stack Nanodegree Program

### Author: Jonathan Prell
### v1.0 - 9/9/2017
_________________________________________________________________

## About:

The Simple Safety Manager accomplishes the requirements of the Item Catalogue project and more. I decided to build this application in substitution of the original project to demonstrate my ability to build a corporate grade solution for a real world problem.

The application allows a user to capture incident investigation details and compliance audit reports. The user may also track action items developed from the incident cases or audit reports and tie them to those submissions or input an action item independantly.

All of the data can be read by anybody, but a user must log in to submit new information. A user may only edit or delete information they created.

Authentication is managed by a third party OAuth through Google.

The application takes advantage of a simple and free open weather API from [Open Weather Map](https://openweathermap.org/api) to provide the user current weather information. The weather currently provides local information for my location in Cincinnati, OH.
_________________________________________________________________

## How to Use:

Any user may review the Incidents, Audits, or Action Items in the database.

To submit a case or report, the user must login.

Once the user is logged in, they may submit an Incident, Audit, or Action Item. These options will be available on the sidebar menu. All fields must be completed before the report can be submitted.

Action Items are automatically submitted and attached to an Incident Case or Audit. Individual Action Items related to safety may be submitted independantly. Once an Action Item has been completed, a logged in user may close the item.

Users may only edit Incidents, Audits, or Action Items they have submitted themselves.
_________________________________________________________________

## API Endpoints:

API endpoints are available to provide JSON formatted data from the database.
* /incidents/json
	* provides all items in the incidents database.
* /incidents/json/<id>
	* provides a specific item in the incidents database by id number.
* /audits/json
	* provides all items in the audits database.
* /audits/json<id>
	* provides a specific item in the audits database by id number.
* /actions/json
	* provides all items in the actions database.
* /actions/json<id>
	* provides a specific item in the actions database by id number.
* /users/json
	* provides all items in the users database.
* /users/json<id>
	* provides a specific item in the users database by id number.
_________________________________________________________________

## Installation:

Prerequisite Programs:
* [Python 3](https://www.python.org/)
* [PostgreSQL](https://www.postgresql.org/)
* [psycopg](http://initd.org/psycopg/)
* [Flask](http://flask.pocoo.org/)
* [OAuth 2.0](https://oauth.net/2/)
* [Advanced Python Scheduler](https://apscheduler.readthedocs.io/en/latest/)
* [SQL Alchemy](https://www.sqlalchemy.org/)

Please run the following programs to set up the application on a vagrant virtual machine:
* Follow these instructions to set up the vagrant VM:
	* https://www.udacity.com/wiki/ud088/vagrant

### Installing the database:
Open postgres and run the following command:
```
CREATE DATABASE safety
```
Note: you may change the name of the database if necessary.

Open the connect.py file and update the username, password, and database name fields.
```
# Update the user and password for your database
user = 'yourusername'
password ='yourpassword'
database = 'safety'
```

In your vagrant VM please run the following command:
```
python database.py
```

### Populating the database:
In your vagrant VM please run the following command:
```
python database_populator.py
```

### Running the Safety Management System:
In your vagrant VM please run the following command:
```
python3 simple_safety.py
```
note: must run using python 3
_________________________________________________________________

## Free online images used:

* [Incident clip art](http://www.clker.com/clipart-warning-exclamation-triangle.html)
* [Audit clip art](http://www.clipartpanda.com/clipart_images/downloads-2959318)
* [Action Item clip art](https://www.1001freedownloads.com/free-clipart/checkbox-checked-3)
* [User clip art](http://www.freeiconspng.com/img/909)
