# CMSC495 Capstone Project

Completed so far (all features!):   
-Initial Django models created  
-user login/registration  
-add/edit/delete/view Budgets, Categories, FundsAllocations, Transactions  
-Pagination on view Budgets, Categories, Transactions pages.  
-Visualize Spending Page / Functionality complete.    
-Complete code cleanup.  

**Note: Phase 4 (final) code will not run in dev environment due to settings.py being set up for live deployment. Use Phase 3 settings.py if trying to run in a dev environment.**

## Dev Environment Setup (use Phase 3 settings.py):
These commands are from the perspective of a Linux user.

First create a virtual environment:

    virtualenv cmsc495capstone
    
next, activate the virtualenvonment:
  
    source cmsc495capstone/bin/activate

Now clone the git repo:

    git clone https://gitlab.com/495_django/budgeting_tool.git

Next run:

```
    cd budgeting_tool; pip install -r requirements.txt
    python manage.py makemigrations
    python manage.py migrate
```

Next, create an admin super user to be able to utilize the admin panel at /admin:
    `python manage.py createsuperuser`

Finally, run the server:
    `python manage.py runserver`

Now, browse to the app at 127.0.0.1:8000 and you can play with creating a regular non-super user and logging in. Then play with creating/editing/deleting Budgets, Categories, FundsAllocations, and Transactions. Lastly, you can head over to 127.0.0.1:8000/admin and login with your superuser you created to check out the admin panel. Use the admin panel to create test data for viewing in the templates.

## Using the provided test database:
Phase 1 delivery comes with a test database file containing two users and some test data. To use the test database, copy the db.sqlite3 file over the existing db.sqlite3 file in the budgeting_tool directory. 

After replacing the database, you can login with the test users. superuser is a super user and has access to the admin panel at /admin.

	users:
	superuser
	user2

	password(for both):
	F@ncyP@ss!

**Note:** Provided test database is not required to be used with Phase 2 or 3 delivery now that the functionality is created for create/edit/delete/view for each of the models.
