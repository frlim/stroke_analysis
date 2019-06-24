var map;
var centersList;
var pointsList;
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


function initialize() {
  var centerlatlng = new google.maps.LatLng(42.258383, -71.654742);
  var myOptions = {
    zoom: 7,
    center: centerlatlng,
    mapTypeId: google.maps.MapTypeId.ROADMAP
  };
  map = new google.maps.Map(document.getElementById("map"), myOptions);
  // Create a <script> tag and set the JS-json script as soource
  var script = document.createElement('script');
  // Json script micmicing Google's example
  // https://developers.google.com/maps/documentation/javascript/earthquakes
  script.src = 'MA_n=100_points.js';
  document.getElementsByTagName('head')[0].appendChild(script);

  // Create a <script> tag and set the JS-json script as soource
  var script = document.createElement('script');
  // Json script micmicing Google's example
  // https://developers.google.com/maps/documentation/javascript/earthquakes
  script.src = 'MA_n=100_centers.js';
  document.getElementsByTagName('head')[0].appendChild(script);

  // Create a <script> tag and set the JS-json script as soource
  var script = document.createElement('script');
  // Json script micmicing Google's example
  // https://developers.google.com/maps/documentation/javascript/earthquakes
  script.src = 'MA_n=100_lines.js';
  document.getElementsByTagName('head')[0].appendChild(script);


  centersList={};
  pointsList={};
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
      // changeIconOld(marker,icons);
      var centerObj = {"marker":marker,"CenterType":type,"ID":hKey,"lines":[]};
      centersList[hKey] = centerObj;
    }
}


function changeIcon(markerObj,icons){
    markerObj["marker"].addListener('mouseover', function() {
      if (!markerObj["blockHover"]){
      markerObj["marker"].setIcon(icons[1]);}
   });
   markerObj['marker'].addListener('mouseout', function() {
     if (!markerObj['blockHover']){
     markerObj["marker"].setIcon(icons[0]);}
  });
}

function changeIconOld(marker,icons){
    marker.addListener('mouseover', function() {
      marker.setIcon(icons[1]);
   });
   marker.addListener('mouseout', function() {
     marker.setIcon(icons[0]);
  });
}


function createCircles(results){
    // Loop through the results array and place a marker for each
  // set of coordinates.
    for (var i = 0; i < results.length; i++) {
      var lat = results[i].Latitude;
      var long = results[i].Longitude;
      var latLng = new google.maps.LatLng(lat,long);
      var radius = 600;
      var pKey = results[i].ID;
      var name = "ID " + pKey.toString();
      var circle = new google.maps.Circle({
          title: name,
          strokeColor: '#008000',
          strokeOpacity: 1.0,
          strokeWeight: 1.0,
          fillColor: '#008000',
          fillOpacity: 0.3,
          map: map,
          center: latLng,
          radius: radius
        });
      var pointObj = {"circle":circle,"ID":pKey,"lines":[],"blockHover":false};
      pointsList[pKey] = pointObj;
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
      var pointObj = {"marker":marker,"ID":pKey,"lines":[],"blockHover":false};
      // changeIcon(pointObj,pointIcons);
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
          var Path = new google.maps.Polyline({
          clickable: true,
          geodesic: true,
          path: PolylineCoordinates,
          strokeColor: color,
          strokeOpacity: BGOPACITY,
          strokeWeight: Math.round(weight*20),
          map:map
          });
          var lineObj = {"Path":Path,"centerID":centerID,"pointID":pointID,
                      "centerBlockHover":[],
                      "pointBlockHover":[]}
          registerCenter(centerID,lineObj);
          registerPoint(pointID,lineObj);
      }
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
  centersList[centerID]["lines"].push(lineObj);
}

function registerPoint(pointID,lineObj){
  pointsList[pointID]["lines"].push(lineObj);
}

function highLightLinesCenters(){
  for (const key in centersList){
    centersList[key]["marker"].addListener("click", function(){
      console.log("rightclicked on Center "+centersList[key].ID);
      centersList[key]["blockHover"]=true;
      var centerIcons= getCenterIconByType(centersList[key].CenterType);
      pSetHighLight(centersList[key],centerIcons,true,{"turnOnBlockHover":"centerBlockHover"});
      }
     );
    centersList[key]["marker"].addListener("rightclick", function(){
      console.log("normalclick on Center"+centersList[key].ID);
      centersList[key]["blockHover"]=false;
      var centerIcons= getCenterIconByType(centersList[key].CenterType);
      pSetHighLight(centersList[key],centerIcons,false,{"releaseBlockHover":"centerBlockHover"});
      }
    );
    centersList[key]["marker"].addListener("mouseover", function(){
      console.log("mouseover on Center "+centersList[key].ID);
      var centerIcons= getCenterIconByType(centersList[key].CenterType);
      if (!centersList[key]["blockHover"]){
          pSetHighLight(centersList[key],centerIcons,true,{"checkHover":true});}
    });
    centersList[key]["marker"].addListener("mouseout", function(){
      console.log("mouseout on Center "+centersList[key].ID);
      var centerIcons= getCenterIconByType(centersList[key].CenterType);
      if (!centersList[key]["blockHover"]){
      pSetHighLight(centersList[key],centerIcons,false,{"checkHover":true});}
    });
  }
}

function highLightLinesPoints(){
  for (const key in pointsList){
    pointsList[key]["marker"].addListener("click", function(){
      console.log("rightclicked")
      // pointsList[key]["marker"].setIcon(pointIcons[1]);
      pointsList[key]["blockHover"]=true;
      pSetHighLight(pointsList[key],pointIcons,true,{"turnOnBlockHover":"pointBlockHover"});
      }
     );
    pointsList[key]["marker"].addListener("rightclick", function(){
      console.log("normalclick")
      // pointsList[key]["marker"].setIcon(pointIcons[0]);
      pointsList[key]["blockHover"]=false;
      pSetHighLight(pointsList[key],pointIcons,false,{"releaseBlockHover":"pointBlockHover"});
      }
    );
    pointsList[key]["marker"].addListener("mouseover", function(){
      console.log("mouseover")
        if (!pointsList[key]["blockHover"]){
          pSetHighLight(pointsList[key],pointIcons,true,{"checkHover":true});}
    });
    pointsList[key]["marker"].addListener("mouseout", function(){
      console.log("mouseout");
      if (!pointsList[key]["blockHover"]){
      pSetHighLight(pointsList[key],pointIcons,false,{"checkHover":true});}
    });
  }
}

function pSetHighLight(pointObj,icons,toogleHighlight,options){
  // default optional parameters in JS
  var checkHover = options.checkHover || false;
  var releaseBlockHover = options.releaseBlockHover || 'none';
  var turnOnBlockHover = options.turnOnBlockHover || 'none';

  //checkHover must equal false to activate the 2 final feature
  if (checkHover){
    releaseBlockHover='none';
    turnOnBlockHover='none';
  }
  console.log('releaseBlockHover is ' + releaseBlockHover);
  console.log('turnOnBlockHover is ' + turnOnBlockHover);
  if (releaseBlockHover!='none' && turnOnBlockHover!='none'){
    throw 'Either releaseBlockHover or turnOnBlockHover (or both) needs to be none ';
  }

  if (toogleHighlight){
    icon = icons[1];
    strokeOpacity = FULLOPACITY;
  } else{
    icon = icons[0];
    strokeOpacity = BGOPACITY;
  }
  pointObj["marker"].setIcon(icon);
  for (var l=0; l < pointObj["lines"].length; l++){
      var lineObj = pointObj["lines"][l];
      if (releaseBlockHover !='none') {
        pointObj["lines"][l][releaseBlockHover].splice(pointObj["lines"][l][releaseBlockHover].indexOf(pointObj.ID),1);}
      if (turnOnBlockHover !='none') {
        // if id already exist then dont add again
        if (pointObj["lines"][l][turnOnBlockHover].indexOf(pointObj.ID) <=-1){
        pointObj["lines"][l][turnOnBlockHover].push(pointObj.ID);}
      }
      var changeOpacity = lineObj["centerBlockHover"].length==0 && lineObj["pointBlockHover"].length==0;

      // if (checkHover){
      //   changeOpacity = lineObj["centerBlockHover"].length==0 && lineObj["pointBlockHover"].length==0;
      console.log("info below -- line for point:" + lineObj["pointID"] + " center:"+lineObj["centerID"]);

      console.log("centerBlockHover is "+lineObj["centerBlockHover"]);
      console.log("pointBlockHover is "+lineObj["pointBlockHover"]);
      //   console.log("should change?" +changeOpacity)
      // }

      if (changeOpacity){
        lineObj["Path"].setOptions({
          strokeOpacity:strokeOpacity});
      }
    }
}
