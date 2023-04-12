# **Scrapper Data Readme**

This scrapper is build in Flask ( Micro Framework)

Before running this application make sure you have python installed in your systems.

* create Virtual environment by command
  `python -m venv venv`

* Activate Virtual Environment
  `source venv/bin/activate`
* Install all the requirements.txt by command
  `pip install -r requirements.txt`

* To Run this Application type Below Command
  ``flask --app api run``

To go on the Swagger UI add below to the end of the URL

```
/api/docs/
Example for local host 
http://127.0.0.1:5000/api/docs/
```

when you go on the above link Swagger UI will appear that will show you available API's.

If want to add new api's into the Swagger UI here in static folder a sub folder named as JS contains **openapi.json**
file. Simple add URL and parameter. 


