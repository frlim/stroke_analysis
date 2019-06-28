'use strict';

var map;
var centersList;
var pointsList;
var linesList;
const BGOPACITY = 0.09;
const FULLOPACITY = 0.8;

var pointIcons = ["https://img.icons8.com/ios/20/000000/secured-by-alarm-system.png",
"https://img.icons8.com/ios/20/000000/secured-by-alarm-system-filled.png"];

var blue_icon = "https://chart.apis.google.com/chart?chst=d_map_pin_letter&chld=|7faeff";
var red_icon = "https://chart.apis.google.com/chart?chst=d_map_pin_letter&chld=|ffb3ad";
var dark_red_icon = "https://chart.apis.google.com/chart?chst=d_map_pin_letter&chld=•|fc2411";
var dark_blue_icon = "https://chart.apis.google.com/chart?chst=d_map_pin_letter&chld=•|1135ff|f9f9f9";
function getCenterIconByType(centerType){
  if (centerType != 'Primary'){
    return [blue_icon,dark_blue_icon];
  }
  else {
    return [red_icon,dark_red_icon];
  }
}

var dataDIR='./data_js/';
var centersDIR = dataDIR + 'MA_n=100_centers.json';
var pointsDIR = dataDIR + 'MA_n=100_points.json';
var linesDIR = dataDIR + 'MA_n=100_lines_RACE_0_s=20000.json';


function initialize() {
  // var newMap = typeof newMap !== 'undefined' ? newMap : true;
  var centerlatlng = new google.maps.LatLng(42.258383, -71.654742);
  var myOptions = {
    zoom: 7,
    center: centerlatlng,
    mapTypeId: google.maps.MapTypeId.ROADMAP
  };
  map = new google.maps.Map(document.getElementById("map"), myOptions);

  centersList={};
  pointsList={};
  linesList=[];

  fetch(pointsDIR).then(res => res.json()).then(data => createMarkersForPoints(data));
  fetch(centersDIR).then(res => res.json()).then(data => createMarkers(data));
  fetch(linesDIR).then(res => res.json()).then(function(data) {
    createLines(data);
    highLightLinesPoints();
    highLightLinesCenters();});

  document.addEventListener('keypress', responseRACE);
}

function responseRACE(e){
  let raceNum = e.code[e.code.length-1];
  linesDIR = dataDIR + "MA_n=100_lines_RACE_"+raceNum+"_s=20000.json";
  console.log(linesDIR);
  fetch(linesDIR).then(res => res.json()).then(function(data) {
    updateLines(data);});
  // only need to add listeners once
  // no need to call highLightLines() again (cause memory leaks)
}

function createMarkers(results){
    // Loop through the results array and place a marker for each
  // set of coordinates.
    for (var i = 0; i < results.length; i++) {
      var lat = results[i].Latitude;
      var long = results[i].Longitude;
      var latLng = new google.maps.LatLng(lat,long);
      var hKey = results[i].HOSP_KEY;
      var name = "HOSP_KEY " + hKey.toString();
      var type = results[i].CenterType;
      var icons= getCenterIconByType(results[i].CenterType);
      var marker = new google.maps.Marker({
        title: name.toString(),
        position: latLng,
        icon: icons[0],
        map: map
      });
      var centerObj = new Center(marker,type,hKey);
      centersList[hKey] = centerObj;
    }
}

function createMarkersForPoints(results){
    // Loop through the results array and place a marker for each
  // set of coordinates.
    for (var i = 0; i < results.length; i++) {
      var lat = results[i].Latitude;
      var long = results[i].Longitude;
      var latLng = new google.maps.LatLng(lat,long);
      var pKey = results[i].ID;
      var name = "ID " + pKey.toString();
      var marker = new google.maps.Marker({
        title: name.toString(),
        position: latLng,
        icon: pointIcons[0],
        map: map
      });
      var pointObj = new Point(marker,pKey);
      pointsList[pKey] = pointObj;
    }
}


function createLines(results){
    // Loop through the results array and place a marker for each
  // set of coordinates.
    for (var i = 0; i < results.length; i++) {
      var pointID = results[i].Point.Location;
      var pLatLng = getPointCoordinates(pointID);
      var color = results[i].Point.Color;
      var comColor = results[i].Point.ComColor;
      var bestCenterID = results[i].Point.BestCenter;
      for (var c=0; c < results[i].Point.Centers.length;c++){
          var centerID = results[i].Point.Centers[c].Center;
          var weight = results[i].Point.Centers[c].Weight;
          var cLatLng = getCenterCoordinates(centerID);
          var PolylineCoordinates = [pLatLng,cLatLng];
          var path = new google.maps.Polyline({
          clickable: true,
          geodesic: true,
          path: PolylineCoordinates,
          strokeColor: color,
          strokeOpacity: BGOPACITY,
          strokeWeight: Math.round(weight*20),
          map:map
          });
          // console.log(comColor)
          var lineObj = new Line(path,centerID,pointID);
          if (centerID==bestCenterID){
            var lineSymbol = createDash(comColor);
            lineObj.setSymbol(lineSymbol);}
          registerCenter(centerID,lineObj);
          registerPoint(pointID,lineObj);
      }
    }
}


function createDash(comColor){
    var comColor = typeof comColor !== 'undefined' ? comColor : "#000000";
    // Define a symbol using SVG path notation, with an opacity of 1.
    var lineSymbol = {
      path: 'M 0,-1 0,1',
      strokeOpacity: 1,
      strokeColor: comColor,
      scale: 3,
    };
    return lineSymbol;
}

function updateLines(results){
  // remove old lines if ID is not in here
  for (var i = 0; i < results.length; i++) {
    var pointID = results[i].Point.Location;
    var centerIDsList = [];
    var preList = new Uint32Array(Object.keys(pointsList[pointID].lines));
    console.log("old plotted list: "+preList);
    // console.log(preList);
    var comColor = results[i].Point.ComColor;
    var bestCenterID = results[i].Point.BestCenter;
    console.log('best center is '+bestCenterID)
    for (var c=0; c < results[i].Point.Centers.length;c++){
      var centerID = results[i].Point.Centers[c].Center;
      var weight = results[i].Point.Centers[c].Weight;
      if (preList.includes(centerID)){
        console.log("Change line point:"+pointID+" center:"+centerID+" weight to "+weight)
        pointsList[pointID].lines[centerID].setWeight(weight);
        if (centerID != bestCenterID && pointsList[pointID].lines[centerID].bestLineStatus){
          console.log("previously best line but will be unset");
          pointsList[pointID].lines[centerID].unsetSymbol();
        }
        if (centerID == bestCenterID && !pointsList[pointID].lines[centerID].bestLineStatus){
          var lineSymbol=createDash(comColor);
          console.log("set to be new best line");
          pointsList[pointID].lines[centerID].setSymbol(lineSymbol);
        }
      }
      else{
        // create new obj
        console.log("Create new line point:"+pointID+" center:"+centerID+" weight of "+weight)
        var color = results[i].Point.Color;
        var pLatLng = getPointCoordinates(pointID);
        var cLatLng = getCenterCoordinates(centerID);
        var PolylineCoordinates = [pLatLng,cLatLng];
        var path = new google.maps.Polyline({
          clickable: true,
          geodesic: true,
          path: PolylineCoordinates,
          strokeColor: color,
          strokeOpacity: BGOPACITY,
          strokeWeight: Math.round(weight*20),
          map:map
        });
        var lineObj = new Line(path,centerID,pointID);
        if (centerID == bestCenterID){
          console.log("set to be new best line");
          lineSymbol=createDash(comColor);
          lineObj.setSymbol(lineSymbol);}
        registerCenter(centerID,lineObj);
        registerPoint(pointID,lineObj);
        // linesList.push(lineObj);
      }
      centerIDsList.push(centerID);
    }
    console.log("actual centerID for this race score: "+centerIDsList);
    // find which line not in updated list of points\
    centerIDsList = new Uint32Array(centerIDsList);
    for (var c=0;c<preList.length;c++){
      var centerID = preList[c];
      if (!centerIDsList.includes(centerID)){
        console.log("Delete line point:"+pointID+" center:"+centerID)
        pointsList[pointID].unmountLineFromMap(centerID);
        pointsList[pointID].deleteLineObj(centerID);
        centersList[centerID].deleteLineObj(pointID);
      }
    }
  }
  updateHighLight();
}

function updateHighLight(){
  for (var pointID in pointsList){
    var pointObj = pointsList[pointID];
    if (pointObj.highlightStatus){
      // console.log('rehighlight after update point');
      pointObj.highlightOn();}
    if (pointObj.blockHoverStatus){
      pointObj.blockHover();}
    if (!pointObj.highlightStatus){pointObj.highlightOff();}
    if (!pointObj.blockHoverStatus){
      pointObj.unblockHover();}
  }
  for (var centerID in centersList){
    var centerObj = centersList[centerID];
    if (centerObj.highlightStatus){
      // console.log('rehighlight after update center');
      centerObj.highlightOn();}
    if (centerObj.blockHoverStatus){
      centerObj.blockHover();}
    if (!centerObj.highlightStatus){centerObj.highlightOff();}
    if (!centerObj.blockHoverStatus){
      centerObj.unblockHover();}
  }
}


function getPointCoordinates(pointID){
  // console.log(pointsList[pointID].getCenter())
  return pointsList[pointID]["marker"].getPosition()
}

function getCenterCoordinates(centerID){
  // console.log(centersList[centerID].getPosition())
  return centersList[centerID]["marker"].getPosition()
}

function registerCenter(centerID,lineObj){
  centersList[centerID].addLine(lineObj);
}

function registerPoint(pointID,lineObj){
  pointsList[pointID].addLine(lineObj);
}


function highLightLinesCenters(){
  for (const key in centersList){
    centersList[key]["marker"].addListener("click", function(){
      console.log("clicked on Center "+centersList[key].ID);
      if (!centersList[key].blockHoverStatus){ // to prevent multi click error
        // if only not block yet, then highlight and block it
        centersList[key].highlightOn();
        centersList[key].blockHover();
      }
      }
     );
    centersList[key]["marker"].addListener("rightclick", function(){
      console.log("right-clicked on Center"+centersList[key].ID);
      if (centersList[key].blockHoverStatus){
        centersList[key].unblockHover();
        centersList[key].highlightOff();
        }
      }
    );
    centersList[key]["marker"].addListener("mouseover", function(){
      console.log("mouseover on Center "+centersList[key].ID);
      if (!centersList[key].blockHoverStatus){
          centersList[key].highlightOn();
        }
    });
    centersList[key]["marker"].addListener("mouseout", function(){
      console.log("mouseout on Center "+centersList[key].ID);
      if (!centersList[key].blockHoverStatus){
          centersList[key].highlightOff();
        }
    });
  }
}

function highLightLinesPoints(){
  for (const key in pointsList){
    pointsList[key]["marker"].addListener("click", function(){
      console.log("clicked on Point "+pointsList[key].ID);
      if (!pointsList[key].blockHoverStatus){ // to prevent multi click error
        // if only not block yet, then highlight and block it
        pointsList[key].highlightOn();
        pointsList[key].blockHover();
        }
      }
     );
    pointsList[key]["marker"].addListener("rightclick", function(){
      console.log("right-clicked on Point "+pointsList[key].ID);
      if (pointsList[key].blockHoverStatus){
        pointsList[key].unblockHover();
        pointsList[key].highlightOff();
        }
      }
    );
    pointsList[key]["marker"].addListener("mouseover", function(){
      console.log("mouseover on Point "+pointsList[key].ID);
      if (!pointsList[key].blockHoverStatus){
          pointsList[key].highlightOn();
        }
    });
    pointsList[key]["marker"].addListener("mouseout", function(){
      console.log("mouseout on Point "+pointsList[key].ID);
      if (!pointsList[key].blockHoverStatus){
          pointsList[key].highlightOff();
        }
    });
  }
}

class Center {
  constructor(marker,type,ID){
    this.marker=marker;
    this.type=type;
    this.ID = ID;
    this.lines={};
    this.highlightStatus=false;
    this.blockHoverStatus=false;
  }
  addLine(lineObj){
    this.lines[lineObj.pointID]=lineObj;
  }
  removeLines(){
    this.lines={};
  }
  highlightOn(){
    this.highlightStatus=true;
    // changeicon
    this.marker.setIcon(getCenterIconByType(this.type)[1]);
    // highlight lines;
    for (const l in this.lines){
      var line = this.lines[l];
      line.highlightOn();
    }
  }
  highlightOff(){
    this.highlightStatus=false;
    // changeicon
    this.marker.setIcon(getCenterIconByType(this.type)[0]);
    // highlight lines;
    for (const l in this.lines){
      var line = this.lines[l];
      // if there are no block then set highlight off
      if (!line.anyBlock){ line.highlightOff();}
    }
  }
  blockHover(){
    for (const l in this.lines){
      var line = this.lines[l];
      // only add if not already in block list
      if (!line.checkInCenterBlock(this.ID)){
        line.addCenterBlock(this.ID);
      }
    }
    this.blockHoverStatus=true;
  }
  unblockHover(){
    for (const l in this.lines){
      var line = this.lines[l];
      line.removeCenterBlock(this.ID);
    }
    this.blockHoverStatus=false;
  }
  unmountLineFromMap(pointID){
    this.lines[pointID].unmountFromMap();
  }
  deleteLineObj(pointID){
    delete this.lines[pointID];
  }
}

class Point {
  constructor(marker,ID){
    this.marker=marker;
    this.ID = ID;
    this.lines={};
    this.highlightStatus=false;
    this.blockHoverStatus=false;
  }
  addLine(lineObj){
    this.lines[lineObj.centerID]=lineObj;
  }
  removeLines(){
    this.lines={};
  }
  highlightOn(){
    this.highlightStatus=true;
    // changeicon
    this.marker.setIcon(pointIcons[1]);
    // highlight lines;
    for (const l in this.lines){
      var line = this.lines[l];
      // console.log('in point:'+this.ID + ' might highlight line center:'+l+' its highlightStatus is '+line.highlightStatus);
      line.highlightOn();
    }
  }
  highlightOff(){
    this.highlightStatus=false;
    // changeicon
    this.marker.setIcon(pointIcons[0]);
    // highlight lines;
    for (const l in this.lines){
      var line = this.lines[l];
      // console.log('in point:'+this.ID + ' might OFFhighlight line center:'+l+' its highlightStatus is '+line.highlightStatus);
      // if there are no block and currently on then set highlight off
      if (!line.anyBlock && line.highlightStatus){
        // console.log('highlight off called');
        line.highlightOff();}
    }
  }
  blockHover(){
    for (const l in this.lines){
      var line = this.lines[l];
      // only add if not already in block list
      if (!line.checkInPointBlock(this.ID)){
        line.addPointBlock(this.ID);
      }
    }
    this.blockHoverStatus=true;
  }
  unblockHover(){
    for (const l in this.lines){
      var line = this.lines[l];
      line.removePointBlock(this.ID);
    }
    this.blockHoverStatus=false;
  }
  unmountLineFromMap(centerID){
    this.lines[centerID].unmountFromMap();
  }
  deleteLineObj(centerID){
    delete this.lines[centerID];
  }
}

class Line {
  constructor(path,centerID,pointID){
    this.path = path;
    this.centerID = centerID;
    this.pointID = pointID;
    this.centerBlockHover = [];
    this.pointBlockHover = [];
    this.highlightStatus=false;
    this.bestLineStatus = false; //best line will get a dash on top
  }
  setSymbol(lineSymbol){
    this.bestLineStatus=true;
    this.lineSymbol=lineSymbol;
  }
  unsetSymbol(){
    this.bestLineStatus=false;
    delete this.lineSymbol;
    this.path.setOptions({
      "icons":[]
    });
  }
  registerCenter(center){
    this.center=center;
  }
  registerPoint(point){
    this.point=point;
  }
  addPointBlock(pointID){
    this.pointBlockHover.push(pointID);
  }
  addCenterBlock(centerID){
    this.centerBlockHover.push(centerID);
  }
  removePointBlock(pointID){
    this.pointBlockHover.splice(this.pointBlockHover.indexOf(pointID),1);
  }
  checkInPointBlock(pointID){
    return this.pointBlockHover.indexOf(pointID) > -1;
  }
  checkInCenterBlock(centerID){
    return this.centerBlockHover.indexOf(centerID) > -1;
  }
  removeCenterBlock(centerID){
    this.centerBlockHover.splice(this.centerBlockHover.indexOf(centerID),1);
  }
  highlightOn(){
    this.highlightStatus=true;
    this.path.setOptions({
      "strokeOpacity":FULLOPACITY
    });
    if (this.bestLineStatus){
      this.lineSymbol.strokeOpacity=1;
      this.path.setOptions({"icons": [{
              icon: this.lineSymbol,
              offset: '0',
              repeat: '10px'
      }]});
    }
  }
  highlightOff(){
    this.highlightStatus=false;
    this.path.setOptions({
      "strokeOpacity":BGOPACITY
    });
    if (this.bestLineStatus){
      this.lineSymbol.strokeOpacity=0;
      this.path.setOptions({"icons": [{
              icon: this.lineSymbol,
              offset: '0',
              repeat: '10px'
      }]});
    }
  }
  get anyBlock(){
    return (this.pointBlockHover.length>0) || (this.centerBlockHover.length>0);
  }
  setWeight(weight){
    var strokeWeight = Math.round(weight*20);
    this.path.setOptions({
      "strokeWeight":strokeWeight
    });
  }
  unmountFromMap(){
    this.path.setMap(null);
  }
}
