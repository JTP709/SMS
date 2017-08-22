import psycopg2
from config import config

# Add dates to incidents, audits. Rebuild Audit Tables.

# Injury Case 1
injury_act_1 = ('1','2017-01-16 15:36:38','Injury','Unsafe Act', 'TRUE', 'FALSE', 'While lifting a 50 lb item from the floor onto their wokrstation, the employee felt a sharp pain in their lower back.','The employee ran out of room on their workstation because the takeaway conveyor was inoperable')

actions_injury_1 = ('Provide mobile carts employees can use to stage product if/when the conveyor is inoperable.')

# Injury Case 2
injury_act_2 = ('2',"2017-03-28 5:01:2",'Injury','Unsafe Behavior', 'TRUE', 'FALSE', 'Employee was cutting open a box and cut their forearm.','The employee was cutting towards themself and not wearing cut resistant sleeves.')

actions_injury_2 = ('Coach employees at morning stand-up meeting on proper box opening techniques. Perform additional behavior audits on decant stations.')

# Injury Case 3
injury_act_3 = ('3',"2017-03-30 12:00:5",'Injury','Unsafe Condition', 'TRUE', 'FALSE', 'Employee tripped over product protruding into the walkway from a stow location.',"The item was improperly stowed in a bin location too small to accomodate it's length.")

actions_injury_3 = ('Supervisors will walk bin locations and perform bin audits when a discrepency is found. QA will perform additional bin audits per shift.')

# Injury Case 4
injury_act_4 = ('4',"2017-04-01 01:41:29",'PIT Incident','Unsafe Act', 'FALSE', 'TRUE', "PIT Operator struck pallet racking while turning into an aisle.","The PIT Operator was looking over their shoulder and talking to another employee while moving in the opposite direction and not paying attention to where they were moving.")

actions_injury_4 = ("Hold a safety stand-down with all PIT Operators. Perform additonal behavior audits on PIT Operators for one week. Operator at fault will be held accountable in accordance with disciplinary policy.")

# Injury Case 5
injury_act_5 = ('5',"2017-05-12 19:39:18",'Injury','Unsafe Act', 'TRUE', 'TRUE', "Employee was pulling a pallet with a pallet jack under through the entryway when the top item hit the door frame and fell off, landing on another employee. The item was damaged beyond repair.","The employee pulling the pallet jack stacked the pallet to 7 feet tall, higher than the 5 foot stacking limit.")

actions_injury_5 = ("Coach all employees at start of shift stand-up meeting on the pallet heigh limits. Perform additional area organization audits with a focus on pallet stacking height.")

# Injury Case 6
injury_act_6 = ('6',"2017-05-29 21:30:08",'Injury','Unsafe Act', 'TRUE', 'FALSE', "Employee was loading a truck with outbound product when they felt a sharp pain in their shoulder.","Employee was lifitng a heavy item (estimated 40 to 50 lbs) above their head to stack on the top of the stack of items, approximately 7 foot high. The employee was not using a stool to ensure they don't have to lift outside of their 'power zone.'")

actions_injury_6 = ("Supervisor will perform an area organization audit on the dock to ensure the step stools are available. If not, supervisor will place an order for more stalls with procurement.")

# Injury Case 7
injury_act_7 = ('7',"2017-06-01 16:30:41",'Injury','Unsafe Behavior', 'TRUE', 'FALSE', "Employee was placing an item on their workstation when they dropped the item and it struck their left foot.","Employee was rushing to process the items quickly because they were worried about making rate.")

actions_injury_7 = ("Supervisor will spend an hour working one on one with the employee to help them develop skills to work efficiently without sacrificing safety or quality. Department Manager will audit supervisor engagements to ensure they are not placing undue pressure on employees.")

# Injury Case 8
injury_act_8 = ('8',"2017-06-07 11:15:48",'Near Miss','Unsafe Condition', 'FALSE', 'FALSE', "Pallets were left in main walkway.","Employees at end of shift were in a rush to get home and left pallets in the walkway rather than place them in the correct location.")

actions_injury_8 = ("Supervisor and Managers will walk the work areas at the end of shift to ensure everything is properly set up for the next shift.")

# Injury Case 9
injury_act_9 = ('9','2017-07-24 10:51:13','PIT Incident','Unsafe Act', 'FALSE', 'TRUE', "PIT truck hit guard rail while backing up. The guard rail was not anchored properly, allowing the PIT to strick the pallet racking strut and damaging it.","Guardrail was not properly anchored, allowing the PIT to damage the pallet racking.")

actions_injury_9 = ("Replace guard rail that was damaged. Facilities will inspect all guardraile in the building to ensure it is properly anchored.")

# Injury Case 10
injury_act_10 = ('10','2017-08-01 02:11:19','HAZMAT','Unsafe Act', 'FALSE', 'TRUE', "Hazardous waste barrel was rusted through, leaking material in to the secondary containment.","Hazardous waste was placed in the wrong container, resulting in erosion of the metal barrel.")

actions_injury_10 = ("Safety will retrain HAZWASTE processing employees and audit the process daily for two weeks, then twice a week afterwards.")

# Audit 1
audit_1 = ('1','2017-01-01 05:13:20','Behavior','Was the employee wearing their PPE?','Was the employee using proper lifting techniques?',"Was the employee's work area clean?",'FALSE','TRUE','TRUE')

actions_audits_1 = ("Fix the PPE machine so employees can be prepared at the beginning of the shift.",)

# Audit 2
audit_2 = ('2','2017-02-01 05:19:20','Behavior','Was the employee wearing their PPE?','Was the employee using proper lifting techniques?',"Was the employee's work area clean?",'FALSE','FALSE','TRUE')

actions_audits_2 = ("Coached the employee on the spot. Supervisor will work one on one to correct behaviors.",)

# Audit 3
audit_3 = ('3','2017-03-01 05:05:20','Behavior','Was the employee wearing their PPE?','Was the employee using proper lifting techniques?',"Was the employee's work area clean?",'TRUE','TRUE','FALSE')

actions_audits_3 = ("Helped the employee clean their workstation on the spot.",)

# Audit 4
audit_4 = ('4','2017-01-01 05:10:20',"Area Organization","Does the area have designated locations for all carts, tools, pallets, inventory, and non-inventory items?","Are all carts, pallets, tools, and items in a designated location?","Is the area clean and free from trip hazards?",'FALSE','TRUE','FALSE')

actions_audits_4 = ("Removed trip hazards during audit. Coached employees who did not keep their work area clean.",)

# Audit 5
audit_5 = ('5','2017-02-01 05:10:20',"Area Organization","Does the area have designated locations for all carts, tools, pallets, inventory, and non-inventory items?","Are all carts, pallets, tools, and items in a designated location?","Is the area clean and free from trip hazards?",'TRUE','TRUE','TRUE')

actions_audits_5 = ("Thank employees for keeping their work area clean.",)

# Audit 6
audit_6 = ('6','2017-03-01 05:10:20',"Area Organization","Does the area have designated locations for all carts, tools, pallets, inventory, and non-inventory items?","Are all carts, pallets, tools, and items in a designated location?","Is the area clean and free from trip hazards?",'FALSE','FALSE','FALSE')

actions_audits_6 = ("Stop production and host a stand down with employees on area organization.",)

# Audit 7
audit_7 = ('7','2017-01-01 05:10:20',"HAZWASTE","Are all barrels in good condition?","Are all barrels properly labelled?","Are the appropriate HAZWASTE items stored in the proper container?",'TRUE','TRUE','TRUE')

actions_audits_7 = ("Thank employees for maintaining HAZWASTE compliance.",)

# Audit 8
audit_8 = ('8','2017-02-01 05:10:20',"HAZWASTE","Are all barrels in good condition?","Are all barrels properly labelled?","Are the appropriate HAZWASTE items stored in the proper container?",'TRUE','FALSE','TRUE')

actions_audits_8 = ("Fixed labelling on the spot, ensured labels were stocked, coached employees on the compliance miss.",)

# Audit 9
audit_9 = ('9','2017-03-01 05:10:20',"HAZWASTE","Are all barrels in good condition?","Are all barrels properly labelled?","Are the appropriate HAZWASTE items stored in the proper container?",'TRUE','TRUE','TRUE')

actions_audits_9 = ("Thank employees for maintaining HAZWASTE compliance.",)

injuries = (injury_act_1, injury_act_2, injury_act_3, injury_act_4, injury_act_5, injury_act_6, injury_act_7, injury_act_8, injury_act_9, injury_act_10)

actions_i = (actions_injury_1, actions_injury_2, actions_injury_3, actions_injury_4, actions_injury_5, actions_injury_6, actions_injury_7, actions_injury_8, actions_injury_9, actions_injury_10)

audits = (audit_1, audit_2, audit_3, audit_4, audit_5, audit_6, audit_7, audit_8, audit_9)

actions_a = (actions_audits_1, actions_audits_2, actions_audits_3, actions_audits_4, actions_audits_5, actions_audits_6, actions_audits_7, actions_audits_8, actions_audits_9)

def populate():
	params = config()
	# connect to the PostgreSQL server
	conn = psycopg2.connect("dbname = safety")
	cur = conn.cursor()

	for i in range(len(injuries)):
		incident = (
			"""
			INSERT INTO incident (
							case_num,
							date_time,
							incident_type,
							incident_cat,
							injury,
							property_damage,
							description,
							root_cause
							)
				VALUES (%s,%s,%s,%s,%s,%s,%s,%s)""")
		
		cur.execute(incident, injuries[i])
		print("Injury case added!")

		audit_data = (str(i+1), injuries[i][5], actions_i[i])

		action_items = (
			"""
			INSERT INTO action_items (
							case_id,
							finding,
							corrective_action
							)
				VALUES (%s,%s,%s)""")
		
		cur.execute(action_items, audit_data)
		print("Action item added!")

	for j in range(len(audits)):
		audit = (
			"""
			INSERT INTO audit (
							id,
							date_time,
							type,
							que_1,
							que_2,
							que_3,
							ans_1,
							ans_2,
							ans_3
							)
				VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)""")
		
		cur.execute(audit, audits[j])
		print("Audit added!")

		action_data = (str(j+1), 'Audit deficiency', actions_a[j],)

		action_items_a = (
			"""
			INSERT INTO action_items (
							audit_id,
							finding,
							corrective_action
							)
				VALUES (%s,%s,%s)""")
		
		cur.execute(action_items_a, action_data)
		print("Action item added!")

	cur.close()
	conn.commit()

populate()
