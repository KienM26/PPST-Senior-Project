# djangoproject
<h3>Django project template</h3>


**Installation instructions**
  
  <ol>
  <li>Clone this repository: <b>git clone https://github.com/grbaliga/djangostarter.git</b> </li>
  <li>Go to the djangostarter folder: <b>cd djangostarter</b></li>
  <li>Create a virtual environment (named venv): <b>python -m venv venv</b> </li>
  <li>Activate the virtual environment:  
  <ol>
  <li>Mac/Linux: <b>source venv/bin/activate</b></li>
  <li>Windows (in a git-bash shell): <b>venv/Scripts/activate</b></li>
  </ol>
  </li>
  <li>Install dependencies:  <b>pip install django</b></li>
  <li>Check for migrations:  <b>python manage.py makemigrations</b></li> 
  <li>Migrate:  <b>python manage.py migrate</b></li>
  <li>Install the fixture (test data):  <b>python manage.py shell < fixture.py</b></li>
  <li>Run the project (either from the command line using  <b>python manage.py runserver</b>) or from an IDE such as Visual Studio Code</li>
  
  </ol>
