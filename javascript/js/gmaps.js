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

dataDIR='./data_js/';
var centersDIR = dataDIR + 'MA_n=100_centers.json';
var pointsDIR = dataDIR + 'MA_n=100_points.json';
var linesDIR = dataDIR + 'MA_n=100_lines_RACE_0.json';


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
  linesDIR = dataDIR + "MA_n=100_lines_RACE_"+raceNum+".json";
  console.log(linesDIR);
  fetch(linesDIR).then(res => res.json()).then(function(data) {
    updateLines(data);});
  // only need to add listeners once
  // no need to call highLightLines() again (cause memory leaks)
}


function updateLines(results){
  // remove old lines if ID is not in here
  for (var i = 0; i < results.length; i++) {
    var pointID = results[i].Point.Location;
    var centerIDsList = [];
    var preList = new Uint32Array(Object.keys(pointsList[pointID].lines));
    console.log("old plotted list: "+preList);
    // console.log(preList);
    for (var c=0; c < results[i].Point.Centers.length;c++){
      var centerID = results[i].Point.Centers[c].Center;
      var weight = results[i].Point.Centers[c].Weight;
      if (preList.includes(centerID)){
        console.log("Change line point:"+pointID+" center:"+centerID+" weight to "+weight)
        pointsList[pointID].lines[centerID].setWeight(weight);
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
        registerCenter(centerID,lineObj);
        registerPoint(pointID,lineObj);
        // linesList.push(lineObj);
      }
      centerIDsList.push(centerID);
    }
    // find which line not in updated list of points\
    console.log("center id list: "+centerIDsList);
    console.log("includes test: "+centerIDsList);
    centerIDsList = new Uint32Array(centerIDsList);
    for (var c=0;c<preList.length;c++){
      var centerID = preList[c];
      if (!centerIDsList.includes(centerID)){
        console.log("Delete line point:"+pointID+" center:"+centerID)
        pointsList[pointID].lines[centerID].path.setMap(null);
        delete centersList[centerID].lines[pointID];
        delete pointsList[pointID].lines[centerID];
      }
    }
  }
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
      icons= getCenterIconByType(results[i].CenterType);
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
          var lineObj = new Line(path,centerID,pointID);
          registerCenter(centerID,lineObj);
          registerPoint(pointID,lineObj);
          // linesList.push(lineObj);
      }
    }
}

function clearLinesFromMap(lineLists){
  for (var i=0;i<lineLists.length;i++){
    linesList[i].path.setMap(null);
  }
}

function clearLinesReferences(){
  linesList=[];
  // reset these referrences
  for (const key in pointsList){
    pointsList[key].removeLines();
  }
  for (const key in centersList){
    centersList[key].removeLines();
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
      console.log("clicked on Center "+pointsList[key].ID);
      if (!pointsList[key].blockHoverStatus){ // to prevent multi click error
        // if only not block yet, then highlight and block it
        pointsList[key].highlightOn();
        pointsList[key].blockHover();
        }
      }
     );
    pointsList[key]["marker"].addListener("rightclick", function(){
      console.log("right-clicked on Center"+pointsList[key].ID);
      if (pointsList[key].blockHoverStatus){
        pointsList[key].unblockHover();
        pointsList[key].highlightOff();
        }
      }
    );
    pointsList[key]["marker"].addListener("mouseover", function(){
      console.log("mouseover on Center "+pointsList[key].ID);
      if (!pointsList[key].blockHoverStatus){
          pointsList[key].highlightOn();
        }
    });
    pointsList[key]["marker"].addListener("mouseout", function(){
      console.log("mouseout on Center "+pointsList[key].ID);
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
    this.highlight=false;
    this.blockHoverStatus=false;
  }
  addLine(lineObj){
    this.lines[lineObj.pointID]=lineObj;
  }
  removeLines(){
    this.lines={};
  }
  highlightOn(){
    this.highlight=true;
    // changeicon
    this.marker.setIcon(getCenterIconByType(this.type)[1]);
    // highlight lines;
    for (const l in this.lines){
      var line = this.lines[l];
      // if not on, set on
      if (!line.highlightStatus){ line.highlightOn();}
    }
  }
  highlightOff(){
    this.highlight=false;
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
      line.addCenterBlock(this.ID);
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
  get linesStuff(){
    console.log('get lineStuff')
    return this.lines;
  }
}

class Point {
  constructor(marker,ID){
    this.marker=marker;
    this.ID = ID;
    this.lines={};
    this.highlight=false;
    this.blockHoverStatus=false;
  }
  addLine(lineObj){
    this.lines[lineObj.centerID]=lineObj;
  }
  removeLines(){
    this.lines={};
  }
  highlightOn(){
    this.highlight=true;
    // changeicon
    this.marker.setIcon(pointIcons[1]);
    // highlight lines;
    for (const l in this.lines){
      var line = this.lines[l];
      // if not on, set on
      if (!line.highlight){ line.highlightOn();}
    }
  }
  highlightOff(){
    this.highlight=false;
    // changeicon
    this.marker.setIcon(pointIcons[0]);
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
      line.addCenterBlock(this.ID);
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
  get linesStuff(){
    console.log('get lineStuff')
    return this.lines;
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
  removeCenterBlock(centerID){
    this.centerBlockHover.splice(this.centerBlockHover.indexOf(centerID),1);
  }
  highlightOn(){
    this.path.setOptions({
      "strokeOpacity":FULLOPACITY
    });
  }
  highlightOff(){
    this.path.setOptions({
      "strokeOpacity":BGOPACITY
    });
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
}
