var tag = document.createElement('script');
tag.src = "https://maps.googleapis.com/maps/api/js?key="+config.apiKey+"&callback=initialize";
tag.defer = true;
tag.async = true;
var body = document.getElementsByTagName("body")[0];
body.appendChild(tag);
