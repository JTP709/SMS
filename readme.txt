
Safety Management System Project for Udacity Full-Stack Nanodegree Program

Author: Jonathan Prell
v1.0	9/1/2017
_________________________________________________________________

About:

The Simple Safety Manager accomplishes the requirements of the Item Catalogue project and more. I decided to build this application in substitution of the original project to demonstrate my ability to build a corporate grade solution for a real world problem.

The application allows a user to capture incident investigation details and compliance audit reports. The user may also track action items developed from the incident cases or audit reports and tie them to those submissions or input an action item independantly.

All of the data can be read by anybody, but a user must log in to submit new information. A user may only edit or delete information they created.

Authentication is managed by a third party OAuth through Google.

The application takes advantage of a simple and free open weather API from https://openweathermap.org/api to provide the user current weather information. The weather currently provides local information for my location in Cincinnati, OH.
_________________________________________________________________

API Endpoints:

API endpoints are available to provide JSON formatted data from the database.
	/incidents/json 		- provides all items in the incidents database.
	/incidents/json/*id* 	- provides a specific item in the incidents database by id number.
	/audits/json 			- provides all items in the audits database.
	/audits/json*id* 		- provides a specific item in the audits database by id number.
	/actions/json 			- provides all items in the actions database.
	/actions/json*id* 		- provides a specific item in the actions database by id number.
	/users/json 			- provides all items in the users database.
	/users/json*id* 		- provides a specific item in the users database by id number.
_________________________________________________________________

Installation:

Prerequisite Programs:
Python 3-					https://www.python.org/
PostgreSQL - 				https://www.postgresql.org/
psycopg -					http://initd.org/psycopg/
Flask -						http://flask.pocoo.org/
OAuth 2.0 -					https://oauth.net/2/
Advanced Python Scheudler -	https://apscheduler.readthedocs.io/en/latest/

Please run the following programs to set up the application on a vagrant virtual machine:
	* Please following these instructions for setting up the vagrant VM:
	https://www.udacity.com/wiki/ud088/vagrant

Installing the database:
	python database.py

Populating the database:
	python database_populator.py

Running the Safety Management System:
	python3 simple_safety.py
		*note: must run using python 3
_________________________________________________________________

Free online images used:

Incident clip art: http://www.clker.com/clipart-warning-exclamation-triangle.html
Audit clip art: http://www.clipartpanda.com/clipart_images/downloads-2959318
Action Item clip art: https://www.1001freedownloads.com/free-clipart/checkbox-checked-3
User clip art: http://www.freeiconspng.com/img/909
