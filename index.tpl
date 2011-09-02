<html>
<head>
<title>জাবদা</title>

<style type="text/css">

body {
	font-family:"Century Gothic";
	font-size: 9pt;
	color: #333;
	}

.pane {
	float:left;
	margin: 10px
}

.year-pane {
	font-size: 9pt;
	padding:10px;
	border-radius: 20px;
	text-align: center;
	background-color: lawngreen;
}
.year-pane input {border-radius:10px;padding-left:5px;padding-right:5px;}
.year-pane a:link {text-decoration: none; color: black;}
.year-pane a:visited {text-decoration: none; color: black;}
.year-pane a:hover {text-decoration: underline overline; color: red;}

.content-pane {
	padding:10px;
  font-family:"Century Gothic";	
	font-size: 11pt;
	margin-left:2em;
  width: 12cm;
  text-align: left;
}
.content-pane input {
	width: 100%; 
	border-radius: 10px;
	padding-left:5px;
	padding-right:5px;
}
.content-pane textarea {
	width: 100%; 
	border-radius: 10px;
	padding-left:5px;
	padding-right:5px;
}

.title {
	width: 100%;
	font-size:large;
	font-weight: bold;
	border-bottom: 1px dotted #ba0000;
}

.date {
  font-weight: normal;
	font-size: .8em;
}

.lastupdated {
	text-align:right;
  font-weight: bold;
	font-size: .6em;
}
.lastupdated a:link {color: black;}
.lastupdated a:visited {color: black;}

</style>
</head>   
<body>

%if view=='config':

<div class="pane year-pane">
<form action="/selectdb" method="POST">
<input type="submit" name="select" value="Set as new db file" style="width: 150px;">
<input type="text" name="newdbname" size="60" value="{{cfg['cfg file'].get('Basic','dbname')}}">
</form>
</div>

%else:

<div class="pane year-pane">
<form action="/search" method="GET">
<input type="text" size=15 name="searchtext" title="Search" autocomplete="on">
</form>
<table align="center">
%for yc in year_count:
<tr><td align="center"><a href="/{{yc['year']}}">{{yc['year']}}</a></td><td><font size="1px">({{yc['cnt']}})</font></td></tr>
%end
</table>
</div>

<div class="pane content-pane">

%if view=='list': #In the traditional list view we get the new entry box 
<form action="/new" method="POST">
<input type="text" name="title" class="entry" title="Entry title" autocomplete="off">
<p><textarea rows="10" wrap="virtual" name="body" class="entry" title="Text of entry"></textarea></p>
<input type="submit" name="save" value="save">
</form>
%end

%if view=='searchlist':
<h3>{{title}}</h3>
%end

%if view=='list' or view=='searchlist': #Show us the traditional list view
%for row in rows:
  <div class='date'>{{row['nicedate']}}</div>
  <div class='title'>{{row['title']}}</div>
  <p>{{!row['body']}}</p>
  <div class='lastupdated'>
  <a href="/edit/{{row['id']}}" title="click to edit">Last edited: {{row['updated_at']}}</a>
  </div>
%end

%elif view=='edit': #Allow us to edit a single entry
<h3>Editing {{entry['title']}}</h3>

  <form action="/save/{{entry['id']}}" method="POST">
   <p><input type="text" name="date" class="entry" title="Entry date" value="{{entry['date']}}"></p>  
   <p><input type="text" name="title" class="entry" title="Entry title" value="{{entry['title']}}"></p>
   <p><textarea rows="10" wrap="virtual" name="body" class="entry" title="Text of entry">{{entry['markup text']}}</textarea></p>
   <input type="submit" name="save" value="save">
  </form>

%elif view=='saved': #Show us the edited entry only
<h3>Saved {{entry['title']}}</h3>

  <div class='date'>{{entry['date']}}</div>
  <div class='title'>{{entry['title']}}</div>
  <p>{{!entry['body']}}</p>
  <div align="right"><a href="/edit/{{entry['id']}}">edit</a></div>
  <div class='lastupdated'>Last edited: {{entry['updated_at']}}</div>
%end

</div> <!-- content pane -->

<div class="pane year-pane">
<a href="/config">Config</a>
</div>

%end #if view == 'config'

</body>
</html>