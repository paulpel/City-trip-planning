
# CityTripPlanner

Web aplication to solve multi-criteria problem of trip planning.


## Installation

Install python

Install virtualenv, create virtual environment

```bash
  pip install virtualenv
  virtualenv venv
```
Clone the project

```bash
  git clone https://github.com/paulpel/City-trip-planning.git
```

Go to the project directory

```bash
  cd city-trip-planning
```

Activate virtual environment

```bash
  venv/Scripts/activate
```
Install requirements

```bash
  pip install -r requirements.txt
```
Add your API key for openrouteservice in config/config.cfg. You can generate your token here: https://openrouteservice.org/
```bash
  [ORS]
  api_key = your_api_key
```

Donwload js file used to export HTML tables to excel from https://github.com/rusty1s/table2excel/tree/master/dist and place it in app/static folder

## Run Locally

Go to the project app directory

```bash
  cd city-trip-planning/app

```

Run the app

```bash
  python app.py

```

Go to localhost


