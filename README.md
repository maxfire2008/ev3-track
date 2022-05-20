# ev3-track
Random stuff with ev3

Download inputs from me at maxfire2008/inputs

### Connection to EV3
`ssh robot@192.168.137.3 -R 127.0.0.1:5000:127.0.0.1:5000`

### Start server
```powershell
$env:FLASK_APP="control_server:app"
$env:FLASK_ENV="development"
py -m flask run
```