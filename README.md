followerr

A social network.

You will need an elasticsearch server running on port 9200 for all the functionality to work.

To start:
1. Open cmd and navigate to root directory containing "manage.py".
2. Run "pip install -r requirements.txt".
3. Run elasticsearch server on your machine.
4. Run "python manage.py search_index --rebuild".
5. Run "python manage.py runserver".
6. Go to "localhost:8000" to view the app.
