'use strict';

var map;
var centersList;
var pointsList;
var linesList;
const BGOPACITY = 0.7;
const FULLOPACITY = 1;

// var pointIcons = ["https://img.icons8.com/ios/20/000000/secured-by-alarm-system.png",
//   "https://img.icons8.com/ios/20/000000/secured-by-alarm-system-filled.png"
// ];

var pointIcons = ["https://img.icons8.com/ios/20/000000/secured-by-alarm-system-filled.png",
  "https://img.icons8.com/ios/20/000000/secured-by-alarm-system-filled.png"
];

var blue_icon = "https://chart.apis.google.com/chart?chst=d_map_pin_letter&chld=|7faeff";
var red_icon = "https://chart.apis.google.com/chart?chst=d_map_pin_letter&chld=|ffb3ad";
var dark_red_icon = "https://chart.apis.google.com/chart?chst=d_map_pin_letter&chld=•|fc2411";
var dark_blue_icon = "https://chart.apis.google.com/chart?chst=d_map_pin_letter&chld=•|1135ff|f9f9f9";

function getCenterIconByType(centerType) {
  if (centerType != 'Primary') {
    return [blue_icon, dark_blue_icon];
  } else {
    return [red_icon, dark_red_icon];
  }
}


function getCenterIconByTypeWithText(centerType, text) {
  text=""
  if (centerType != 'Primary') {
    var icon1 = "https://chart.apis.google.com/chart?chst=d_map_pin_letter&chld=" + text + "|7faeff";
    var icon2 = "https://chart.apis.google.com/chart?chst=d_map_pin_letter&chld=" + text + "|1135ff|f9f9f9";
    return [icon2, icon2];
  } else {
    var icon1 = "https://chart.apis.google.com/chart?chst=d_map_pin_letter&chld=" + text + "|ffb3ad";
    var icon2 = "https://chart.apis.google.com/chart?chst=d_map_pin_letter&chld=" + text + "|fc2411";
    return [icon2, icon2];
  }
}

var dataDIR = './data_js/';
var centersDIR = dataDIR + 'MA_n=100_centers.json';
var pointsDIR = dataDIR + 'MA_n=100_points.json';
var linesDIR = dataDIR + "times=MA_n=100_hospitals=MA_n=100_sex=male_age=75_race=0_symptom=40_nsim=auto_afAHA.json";
// { "color": "#ededed" },
var mapStyles = {
  "default": null,
  "hide": [{
      "featureType": "all",
      "stylers": [{
        "visibility": "off"
      }]
    },
    {
      "featureType": "landscape.natural",
      "stylers": [{
          "visibility": "on"
        },
        {
          "color": "#ededed"
        }
      ]
    },
    {
      "featureType": "road.highway",
      "elementType": "geometry",
      "stylers": [{
          "visibility": "on"
        },
        {
          "color": "#e1e1e1"
        }
      ]
    }
  ]
}

var latLngBounds = {
  east: -69.769533,
  north: 42.961923,
  south: 41.409692,
  west: -73.464296,
}


var ageInput = document.getElementById('age-input');
var raceInput = document.getElementById('race-input');
var symptomInput = document.getElementById('symptom-input');
var maleInput = document.getElementById('male-selector');
var femaleInput = document.getElementById('female-selector');
var locInput = document.getElementById('loc-input');
var afterInput = document.getElementById('after-selector');

function initialize() {
  // var newMap = typeof newMap !== 'undefined' ? newMap : true;
  var centerlatlng = new google.maps.LatLng(42.258383, -71.654742);
  var myOptions = {
    zoom: 9,
    minZoom: 9,
    maxZoom: 14,
    center: centerlatlng,
    // mapTypeId: google.maps.MapTypeId.ROADMAP,
    mapTypeControl: false,
    styles: mapStyles['hide'],
    restriction: {
      latLngBounds: latLngBounds
    },
    streetViewControl: false
  };
  map = new google.maps.Map(document.getElementById("map"), myOptions);

  // Add controls to the map, allowing users to hide/show features.
  var styleControl = document.getElementById('style-selector-control');
  map.controls[google.maps.ControlPosition.TOP_LEFT].push(styleControl);

  var sexSelector = document.getElementById('sex-selector');
  map.controls[google.maps.ControlPosition.TOP_LEFT].push(sexSelector);

  var ageForm = document.getElementById('age-form');
  map.controls[google.maps.ControlPosition.TOP_LEFT].push(ageForm);

  var raceForm = document.getElementById('race-form');
  map.controls[google.maps.ControlPosition.TOP_LEFT].push(raceForm);

  var symptomForm = document.getElementById('symptom-form');
  map.controls[google.maps.ControlPosition.TOP_LEFT].push(symptomForm);

  var infoWindowSelector = document.getElementById('infowindow-selector');
  map.controls[google.maps.ControlPosition.TOP_LEFT].push(infoWindowSelector);

  var versionSelector = document.getElementById('version-selector');
  map.controls[google.maps.ControlPosition.TOP_LEFT].push(versionSelector);

  maleInput.addEventListener('click', responseChange);
  femaleInput.addEventListener('click', responseChange);
  ageInput.addEventListener('change', responseChange);
  raceInput.addEventListener('change', responseChange);
  symptomInput.addEventListener('change', responseChange);
  locInput.addEventListener('change', openInfoWindow);
  document.getElementById('before-selector').addEventListener('click', responseChange);
  document.getElementById('after-selector').addEventListener('click', responseChange);

  // for the user to choose to hide/show features
  document.getElementById('hide-poi').addEventListener('click', function() {
    map.setOptions({
      styles: mapStyles['hide']
    });
  });
  document.getElementById('show-poi').addEventListener('click', function() {
    map.setOptions({
      styles: mapStyles['default']
    });
  });
  // document.getElementById('race-input').addEventListener('change', responseRACE);
  document.getElementById('open-selector').addEventListener('click', openAllInfoWindow);
  document.getElementById('close-selector').addEventListener('click', closeAllInfoWindow);

  centersList = {};
  pointsList = {};
  linesList = [];

  fetch(pointsDIR).then(res => res.json()).then(data => createMarkersForPoints(data));
  fetch(centersDIR).then(res => res.json()).then(data => createMarkers(data));
  fetch(linesDIR).then(res => res.json()).then(function(data) {
    createLines(data);
    highLightLinesPoints();
    highLightLinesCenters();
  });
}

// var oldRaceNum = 0;
// function responseRACE(e){
//   let raceNum = e.srcElement.value;
//   // if raceNum is out of range, reject and put in previous value
//   if (raceNum > 9 || raceNum <0 ){
//     document.getElementById('race-input').value = oldRaceNum;
//     return}
//   linesDIR = dataDIR + "times=MA_n=100_hospitals=MA_n=100_sex=male_age=65_race="+raceNum+"_symptom=10_nsim=auto_afAHA.json";
//   console.log(linesDIR);
//   fetch(linesDIR).then(res => res.json()).then(function(data) {
//     updateLines(data);});
//   // only need to add listeners once
//   // no need to call highLightLines() again (cause memory leaks)
//   oldRaceNum = raceNum;
// }

function responseChange() {
  var sex;
  if (maleInput.checked) {
    sex = 'male';
  } else {
    sex = 'female';
  }
  var age = ageInput.value;
  var race = raceInput.value;
  var symptom = symptomInput.value;
  var version;
  if (afterInput.checked) {
    version = "afAHA";
  } else {
    version = "beAHA";
  }
  linesDIR = dataDIR + "times=MA_n=100_hospitals=MA_n=100_sex=" + sex + "_age=" + age + "_race=" + race + "_symptom=" + symptom + "_nsim=auto_" + version + ".json";
  console.log(linesDIR);
  fetch(linesDIR).then(res => res.json()).then(function(data) {
    updateLines(data);
  });
}

function openAllInfoWindow() {
  for (var pointID in pointsList) {
    var pointObj = pointsList[pointID];
    // console.log('open all info window');
    pointObj.infowindow.open(map, pointObj.marker);
  }
}

function openInfoWindow() {
  var loc = locInput.value;
  var pointObj = pointsList[loc];
  pointObj.infowindow.open(map, pointObj.marker);
  pointObj.highlightOn();
  pointObj.blockHover();
}


function closeAllInfoWindow() {
  for (var pointID in pointsList) {
    var pointObj = pointsList[pointID];
    pointObj.infowindow.close();
  }
}


function createMarkers(results) {
  // Loop through the results array and place a marker for each
  // set of coordinates.
  for (var i = 0; i < results.length; i++) {
    var lat = results[i].Latitude;
    var long = results[i].Longitude;
    var latLng = new google.maps.LatLng(lat, long);
    var hKey = results[i].HOSP_KEY;
    var name = hKey.toString();
    var type = results[i].CenterType;
    var icons = getCenterIconByTypeWithText(results[i].CenterType, hKey.toString());
    var marker = new google.maps.Marker({
      // title: name.toString(),
      position: latLng,
      icon: icons[0],
      map: map
    });
    var centerObj = new Center(marker, type, hKey);
    centersList[hKey] = centerObj;
  }
}

function createMarkersForPoints(results) {
  // Loop through the results array and place a marker for each
  // set of coordinates.
  var keys = Object.keys(results);
  for (var i = 0; i < keys.length; i++) {
    var key = keys[i];
    var lat = results[key].Latitude;
    var long = results[key].Longitude;
    var latLng = new google.maps.LatLng(lat, long);
    var pKey = key;
    var name = pKey.toString();
    var marker = new google.maps.Marker({
      // title: name.toString(),
      position: latLng,
      icon: pointIcons[0],
      map: map
    });
    var pointObj = new Point(marker, pKey);
    pointsList[pKey] = pointObj;
  }
}


function createLines(results) {
  // Loop through the results array and place a marker for each
  // set of coordinates.
  for (var i = 0; i < results.length; i++) {
    var pointID = results[i].Point.Location;
    var pLatLng = getPointCoordinates(pointID);
    var color = results[i].Point.Color;
    var comColor = results[i].Point.ComColor;
    var bestCenterID = results[i].Point.BestCenter;
    for (var c = 0; c < results[i].Point.Centers.length; c++) {
      var centerID = results[i].Point.Centers[c].Center;
      var weight = results[i].Point.Centers[c].Weight;
      var cLatLng = getCenterCoordinates(centerID);
      var PolylineCoordinates = [pLatLng, cLatLng];
      var path = new google.maps.Polyline({
        clickable: true,
        geodesic: true,
        path: PolylineCoordinates,
        strokeColor: color,
        strokeOpacity: BGOPACITY,
        strokeWeight: Math.round(weight * 20),
        map: map
      });
      // console.log(comColor)
      var lineObj = new Line(path, centerID, pointID);
      if (centerID == bestCenterID) {
        var lineSymbol = createDash(comColor);
        lineObj.setSymbol(lineSymbol);
      }
      registerCenter(centerID, lineObj);
      registerPoint(pointID, lineObj);
    }
  }
}


function createDash(comColor) {
  var comColor = typeof comColor !== 'undefined' ? comColor : "#000000";
  // Define a symbol using SVG path notation, with an opacity of 1.
  var lineSymbol = {
    path: 'M 0,-1 0,1',
    strokeOpacity: 1,
    strokeColor: comColor,
    scale: 2,
  };
  return lineSymbol;
}

function updateLines(results) {
  // remove old lines if ID is not in here
  for (var i = 0; i < results.length; i++) {
    var pointID = results[i].Point.Location;
    var centerIDsList = [];
    var preList = Object.keys(pointsList[pointID].lines);
    console.log("old plotted list: " + preList);
    // console.log(preList);
    var comColor = results[i].Point.ComColor;
    var bestCenterID = results[i].Point.BestCenter;
    console.log('best center is ' + bestCenterID)
    for (var c = 0; c < results[i].Point.Centers.length; c++) {
      var centerID = results[i].Point.Centers[c].Center;
      var weight = results[i].Point.Centers[c].Weight;
      if (preList.includes(centerID)) {
        console.log("Change line point:" + pointID + " center:" + centerID + " weight to " + weight)
        pointsList[pointID].lines[centerID].setWeight(weight);
        if (centerID != bestCenterID && pointsList[pointID].lines[centerID].bestLineStatus) {
          console.log("previously best line but will be unset");
          pointsList[pointID].lines[centerID].unsetSymbol();
        }
        if (centerID == bestCenterID && !pointsList[pointID].lines[centerID].bestLineStatus) {
          var lineSymbol = createDash(comColor);
          console.log("set to be new best line");
          pointsList[pointID].lines[centerID].setSymbol(lineSymbol);
        }
      } else {
        // create new obj
        console.log("Create new line point:" + pointID + " center:" + centerID + " weight of " + weight)
        var color = results[i].Point.Color;
        var pLatLng = getPointCoordinates(pointID);
        var cLatLng = getCenterCoordinates(centerID);
        var PolylineCoordinates = [pLatLng, cLatLng];
        var path = new google.maps.Polyline({
          clickable: true,
          geodesic: true,
          path: PolylineCoordinates,
          strokeColor: color,
          strokeOpacity: BGOPACITY,
          strokeWeight: Math.round(weight * 20),
          map: map
        });
        var lineObj = new Line(path, centerID, pointID);
        if (centerID == bestCenterID) {
          console.log("set to be new best line");
          lineSymbol = createDash(comColor);
          lineObj.setSymbol(lineSymbol);
        }
        registerCenter(centerID, lineObj);
        registerPoint(pointID, lineObj);
        // linesList.push(lineObj);
      }
      centerIDsList.push(centerID);
    }
    console.log("actual centerID for this race score: " + centerIDsList);
    // find which line not in updated list of points\
    centerIDsList = centerIDsList;
    for (var c = 0; c < preList.length; c++) {
      var centerID = preList[c];
      if (!centerIDsList.includes(centerID)) {
        console.log("Delete line point:" + pointID + " center:" + centerID)
        pointsList[pointID].unmountLineFromMap(centerID);
        pointsList[pointID].deleteLineObj(centerID);
        centersList[centerID].deleteLineObj(pointID);
      }
    }
  }
  updateHighLight();
}

function updateHighLight() {
  for (var pointID in pointsList) {
    var pointObj = pointsList[pointID];
    if (pointObj.highlightStatus) {
      // console.log('rehighlight after update point');
      pointObj.highlightOn();
    }
    if (pointObj.blockHoverStatus) {
      pointObj.blockHover();
    }
    if (!pointObj.highlightStatus) {
      pointObj.highlightOff();
    }
    if (!pointObj.blockHoverStatus) {
      pointObj.unblockHover();
    }
  }
  for (var centerID in centersList) {
    var centerObj = centersList[centerID];
    if (centerObj.highlightStatus) {
      // console.log('rehighlight after update center');
      centerObj.highlightOn();
    }
    if (centerObj.blockHoverStatus) {
      centerObj.blockHover();
    }
    if (!centerObj.highlightStatus) {
      centerObj.highlightOff();
    }
    if (!centerObj.blockHoverStatus) {
      centerObj.unblockHover();
    }
  }
}


function getPointCoordinates(pointID) {
  // console.log(pointsList[pointID].getCenter())
  return pointsList[pointID]["marker"].getPosition()
}

function getCenterCoordinates(centerID) {
  // console.log(centersList[centerID].getPosition())
  return centersList[centerID]["marker"].getPosition()
}

function registerCenter(centerID, lineObj) {
  centersList[centerID].addLine(lineObj);
}

function registerPoint(pointID, lineObj) {
  pointsList[pointID].addLine(lineObj);
}


function highLightLinesCenters() {
  for (const key in centersList) {
    centersList[key]["marker"].addListener("click", function() {
      console.log("clicked on Center " + centersList[key].ID);
      if (!centersList[key].blockHoverStatus) { // to prevent multi click error
        // if only not block yet, then highlight and block it
        centersList[key].highlightOn();
        centersList[key].blockHover();
      }
    });
    centersList[key]["marker"].addListener("rightclick", function() {
      console.log("right-clicked on Center" + centersList[key].ID);
      if (centersList[key].blockHoverStatus) {
        centersList[key].unblockHover();
        centersList[key].highlightOff();
      }
    });
    centersList[key]["marker"].addListener("mouseover", function() {
      console.log("mouseover on Center " + centersList[key].ID);
      if (!centersList[key].blockHoverStatus) {
        centersList[key].highlightOn();
      }
    });
    centersList[key]["marker"].addListener("mouseout", function() {
      console.log("mouseout on Center " + centersList[key].ID);
      if (!centersList[key].blockHoverStatus) {
        centersList[key].highlightOff();
      }
    });
  }
}

function highLightLinesPoints() {
  for (const key in pointsList) {
    pointsList[key]["marker"].addListener("click", function() {
      console.log("clicked on Point " + pointsList[key].ID);
      if (!pointsList[key].blockHoverStatus) { // to prevent multi click error
        // if only not block yet, then highlight and block it
        pointsList[key].highlightOn();
        pointsList[key].blockHover();
      }
    });
    pointsList[key]["marker"].addListener("rightclick", function() {
      console.log("right-clicked on Point " + pointsList[key].ID);
      if (pointsList[key].blockHoverStatus) {
        pointsList[key].unblockHover();
        pointsList[key].highlightOff();
      }
    });
    pointsList[key]["marker"].addListener("mouseover", function() {
      console.log("mouseover on Point " + pointsList[key].ID);
      if (!pointsList[key].blockHoverStatus) {
        pointsList[key].highlightOn();
      }
    });
    pointsList[key]["marker"].addListener("mouseout", function() {
      console.log("mouseout on Point " + pointsList[key].ID);
      if (!pointsList[key].blockHoverStatus) {
        pointsList[key].highlightOff();
      }
    });
  }
}

class Center {
  constructor(marker, type, ID) {
    this.marker = marker;
    this.type = type;
    this.ID = ID;
    this.lines = {};
    this.highlightStatus = false;
    this.blockHoverStatus = false;
  }
  addLine(lineObj) {
    this.lines[lineObj.pointID] = lineObj;
  }
  removeLines() {
    this.lines = {};
  }
  highlightOn() {
    this.highlightStatus = true;
    // changeicon
    this.marker.setIcon(getCenterIconByTypeWithText(this.type, this.ID.toString())[1]);
    // highlight lines;
    for (const l in this.lines) {
      var line = this.lines[l];
      line.highlightOn();
    }
  }
  highlightOff() {
    this.highlightStatus = false;
    // changeicon
    this.marker.setIcon(getCenterIconByTypeWithText(this.type, this.ID.toString())[0]);
    // highlight lines;
    for (const l in this.lines) {
      var line = this.lines[l];
      // if there are no block then set highlight off
      if (!line.anyBlock) {
        line.highlightOff();
      }
    }
  }
  blockHover() {
    for (const l in this.lines) {
      var line = this.lines[l];
      // only add if not already in block list
      if (!line.checkInCenterBlock(this.ID)) {
        line.addCenterBlock(this.ID);
      }
    }
    this.blockHoverStatus = true;
  }
  unblockHover() {
    for (const l in this.lines) {
      var line = this.lines[l];
      line.removeCenterBlock(this.ID);
    }
    this.blockHoverStatus = false;
  }
  unmountLineFromMap(pointID) {
    this.lines[pointID].unmountFromMap();
  }
  deleteLineObj(pointID) {
    delete this.lines[pointID];
  }
}

class Point {
  constructor(marker, ID) {
    this.marker = marker;
    this.ID = ID;
    this.lines = {};
    this.highlightStatus = false;
    this.blockHoverStatus = false;
    this.infowindow = new google.maps.InfoWindow({
      content: this.ID.toString()
    });
  }
  addLine(lineObj) {
    this.lines[lineObj.centerID] = lineObj;
  }
  removeLines() {
    this.lines = {};
  }
  highlightOn() {
    this.highlightStatus = true;
    // changeicon
    this.marker.setIcon(pointIcons[1]);
    // open info window
    this.infowindow.open(map, this.marker);
    // highlight lines;
    for (const l in this.lines) {
      var line = this.lines[l];
      // console.log('in point:'+this.ID + ' might highlight line center:'+l+' its highlightStatus is '+line.highlightStatus);
      line.highlightOn();
    }
  }
  highlightOff() {
    this.highlightStatus = false;
    // changeicon
    this.marker.setIcon(pointIcons[0]);
    // close info window
    this.infowindow.close();
    // highlight lines;
    for (const l in this.lines) {
      var line = this.lines[l];
      // console.log('in point:'+this.ID + ' might OFFhighlight line center:'+l+' its highlightStatus is '+line.highlightStatus);
      // if there are no block and currently on then set highlight off
      if (!line.anyBlock && line.highlightStatus) {
        // console.log('highlight off called');
        line.highlightOff();
      }
    }
  }
  blockHover() {
    for (const l in this.lines) {
      var line = this.lines[l];
      // only add if not already in block list
      if (!line.checkInPointBlock(this.ID)) {
        line.addPointBlock(this.ID);
      }
    }
    this.blockHoverStatus = true;
  }
  unblockHover() {
    for (const l in this.lines) {
      var line = this.lines[l];
      line.removePointBlock(this.ID);
    }
    this.blockHoverStatus = false;
  }
  unmountLineFromMap(centerID) {
    this.lines[centerID].unmountFromMap();
  }
  deleteLineObj(centerID) {
    delete this.lines[centerID];
  }
}

class Line {
  constructor(path, centerID, pointID) {
    this.path = path;
    this.centerID = centerID;
    this.pointID = pointID;
    this.centerBlockHover = [];
    this.pointBlockHover = [];
    this.highlightStatus = false;
    this.bestLineStatus = false; //best line will get a dash on top
  }
  setSymbol(lineSymbol) {
    this.bestLineStatus = true;
    this.lineSymbol = lineSymbol;
  }
  unsetSymbol() {
    this.bestLineStatus = false;
    delete this.lineSymbol;
    this.path.setOptions({
      "icons": []
    });
  }
  registerCenter(center) {
    this.center = center;
  }
  registerPoint(point) {
    this.point = point;
  }
  addPointBlock(pointID) {
    this.pointBlockHover.push(pointID);
  }
  addCenterBlock(centerID) {
    this.centerBlockHover.push(centerID);
  }
  removePointBlock(pointID) {
    this.pointBlockHover.splice(this.pointBlockHover.indexOf(pointID), 1);
  }
  checkInPointBlock(pointID) {
    return this.pointBlockHover.indexOf(pointID) > -1;
  }
  checkInCenterBlock(centerID) {
    return this.centerBlockHover.indexOf(centerID) > -1;
  }
  removeCenterBlock(centerID) {
    this.centerBlockHover.splice(this.centerBlockHover.indexOf(centerID), 1);
  }
  highlightOn() {
    this.highlightStatus = true;
    this.path.setOptions({
      "strokeOpacity": FULLOPACITY
    });
    if (this.bestLineStatus) {
      this.lineSymbol.strokeOpacity = 1;
      this.path.setOptions({
        "icons": [{
          icon: this.lineSymbol,
          offset: '0',
          repeat: '12px'
        }]
      });
    }
  }
  highlightOff() {
    this.highlightStatus = false;
    this.path.setOptions({
      "strokeOpacity": BGOPACITY
    });
    if (this.bestLineStatus) {
      this.lineSymbol.strokeOpacity = 0;
      this.path.setOptions({
        "icons": [{
          icon: this.lineSymbol,
          offset: '0',
          repeat: '12px'
        }]
      });
    }
  }
  get anyBlock() {
    return (this.pointBlockHover.length > 0) || (this.centerBlockHover.length > 0);
  }
  setWeight(weight) {
    var strokeWeight = Math.round(weight * 20);
    this.path.setOptions({
      "strokeWeight": strokeWeight
    });
  }
  unmountFromMap() {
    this.path.setMap(null);
  }
}
