%#template to generate a HTML table from a list of tuples (or list of lists, or tuple of tuples or ...)
<html>
<head>
<style type="text/css">

body {
	font-family:"Century Gothic";
	font-size: 12pt;
  background-color: #fff; 
	color: #333;
	text-align:center;
	}

.year {
//	float:left;
	text-align: center;
//	display:block;
  font-size: 6em;
	font-weight: bold;
	font-family:"Century Gothic";
	color: black;
//  -moz-transform: rotate(-90deg);
//	left:1cm;
}

.year-pane {
  width: 100%;
  overflow: auto;	
}

.content {
  font-family:"Century Gothic";	
	font-size: 12pt;
	background-color:#5ff;
	border:thin;
	border-style:solid;
	-moz-border-radius: 1em;
	padding-left:2em;
	padding-right:2em;
	padding-top:.1em;
	padding-bottom:.1em;
	margin: 1em auto;	
  width: 15cm;
  text-align: left;
	}

.title {
	width: 100%;
	font-size:large;
	font-weight: bold;
}

.date {
  font-weight: normal;
	font-size: .8em;
}
		   
</style>
</head>   
<body>

<div class='year-pane'>
%for this_year in range(int(year)-10,int(year)):
<a href="/{{this_year}}">{{this_year}}</a>,
%end

<span class='year'>{{year}}</span> 

%for this_year in range(int(year)+1,int(year)+11):
<a href="/{{this_year}}">{{this_year}}</a>,
%end

</div>


%for row in rows:
<div class='content'>  	
  	<div class='date'>{{row['date']}}</div>
  	<div class='title'>{{row['title']}}</div>
  	<p>{{!row['body']}}</p>
</div>
%end
</body>
</html>