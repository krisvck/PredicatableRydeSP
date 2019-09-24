//Copyright 2015 Middle Fork Software LLC. or its affiliates. All Rights Reserved.

//Get modules.
var express = require('express');
var routes = require('./routes');
var http = require('http');
var path = require('path');
var fs = require('fs');
var openrouteservice = require("openrouteservice-js");

//MV Put all globals in this object.
MYAPP = new Object();

//MV this is now global.
uuid = require('node-uuid');
var session = require('express-session');
var app = express();

//###########################

app.set('port', process.env.PORT || 3000);
app.set('views', __dirname + '/views');
app.set('view engine', 'jade');
app.use(express.favicon());
app.use(express.logger('dev'));

//MV Modules added by MV
app.use(express.cookieParser());
app.use(express.bodyParser());
app.use(session({
  secret: '11111111-2222-3333-4444-555555555555',
  resave: false,
  saveUninitialized: true
}));

var LOGPREFIX = function(){
  var d = new Date();
  return "" + d.toLocaleString().substring(0, 24) + "-[server.js]: ";
}
app.use(app.router);
app.use(express.static(path.join(__dirname, 'public')));

//Set the config file
config = fs.readFileSync('./app_config_v1.json', 'utf8');

//Read config values from a JSON file.
config = JSON.parse(config);

//MV add to global space
exports.config = config;

//Server up files in public folder.
app.use(express.static('public'));


//Website's Marketing URLs to their route definitions.
app.get('/', routes.testPage);
app.get('/index.html', routes.testPage);
app.get('/test.html', routes.testPage);


// Create and Start the Web Server
http.createServer(app).listen(app.get('port'), function(){
  console.log(LOGPREFIX() + 'Express Web Server Started - listening on port ' + app.get('port'));
  console.log(LOGPREFIX() + 'Open a web browser to http://localhost:' + app.get('port') + "/test.html to see the dynamicly created test page.");
  console.log(LOGPREFIX() + 'Open a web browser to http://localhost:' + app.get('port') + "/map.html to see the static map html page.");
  //response.write('hello client!');
  //response.end();
});

//TO START THE WEBSERVER TYPE npm start from this directoroes command propt.
//c:\thisfolder\npm start

//https://www.npmjs.com/package/openrouteservice-js
console.log("Simple OpenRouteService.org test using openrouteservice-js nodejs libarary\n\n");

// add your api_key here
var Directions = new openrouteservice.Directions({
  api_key: "5b3ce3597851110001cf6248549f0ebeff1d4cd1b950ea52fa3216a9"
});


const csv = require('csv-parser');

var dataArray = new Array();
fs.createReadStream('data_set_50.csv')
  .pipe(csv())
  .on('data', (row) => {
    var coord = [Number(row.LON), Number(row.LAT)];
    dataArray.push(coord);
  })
  .on('end', () => {
    console.log('CSV file successfully processed');
    addData(dataArray);

    //var file = fs.createWriteStream('array.txt');
    //file.on('error', function(err) { /* error handling */ });
    //dataArray.forEach(function(v) { file.write(v.join(' ') + '\n'); });
    //file.end();


  });



function addData(data){
  Directions.calculate({
      coordinates: data,
      profile: 'driving-hgv',
      restrictions: { height: 10, weight: 5 },
      format: 'geojson'
    })
    .then(function(geojson) {
      var fs = require('fs')
      fs.writeFile('public/geojson.geojson', JSON.stringify(geojson), function(err){
          if(err){
              console.log(err);
          }
      });
      //console.log(JSON.stringify(geojson, null, "\t"));
      console.log("geojson created");
    })
    .catch(function(err) {
      var str = "An error occured: " + err;
      console.log(str);
    });

}

  console.log("End Simple OpenRouteService.org test using openrouteservice-js nodejs libarary\n\n - Did you notice this gets written before the test results?");
