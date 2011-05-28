%#template to generate a HTML table from a list of tuples (or list of lists, or tuple of tuples or ...)
<html>
<head>
<title>PyLog: {{year}}</title>

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
	align: center;
  width: 100%;
}

.year-pane a:link {text-decoration: none}
.year-pane a:hover {text-decoration: underline overline; color: red;}


.entry {
  width: 100%; /*dynamic with div size*/
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
  width: 12cm;
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

<div style="float:right;">
<a href="/quit" title="Quit the diary application">X</a>
</div>

<div style="float:left;">
<a href="/help" title="Get help">?</a>
<a href="/config" title="Advanced configuration">?</a>
</div>

<div class='year-pane'>
%size = 10/1.5**9
%for this_year in range(int(year)-10,int(year)):
<a href="/{{this_year}}"><font size="{{size}}px">{{this_year}}</font></a> 
%size *= 1.5
%end

<span class='year'>{{year}}</span> 

%size = 10
%for this_year in range(int(year)+1,int(year)+11):
<a href="/{{this_year}}"><font size="{{size}}px">{{this_year}}</font></a> 
%size /= 1.5
%end

</div>

%if not edit:
<div class='content'>
<form action="/new" method="POST">
<p><input type="text" name="title" class="entry" title="Entry title" autocomplete="off"></p>
<p><textarea rows="10" wrap="virtual" name="body" class="entry" title="Text of entry"></textarea></p>
<input type="submit" name="save" value="save">
</form>
</div>
%end

%for row in rows:
<div class="content">
<a name="entry{{row['id']}}">
%if edit==True and int(id)==int(row['id']):
<div class='date'>{{row['date']}}</div>
<form action="/save/{{year}}/{{id}}#entry{{id}}" method="POST">
<p><input type="text" name="title" class="entry" title="Entry title" autocomplete="off" value="{{row['title']}}"></p>
<p><textarea rows="10" wrap="virtual" name="body" class="entry" title="Text of entry">
{{row['markup text']}}
</textarea></p>
<input type="submit" name="save" value="save">
</form>
%else:
  	<div class='date'>{{row['date']}}</div>
  	<div class='title'>{{row['title']}}</div>
  	<p>{{!row['body']}}</p>
  	<div align="right"><a href="/edit/{{year}}/{{row['id']}}#entry{{row['id']}}">edit</a></div>
%end
</div>
%end
</body>
</html>