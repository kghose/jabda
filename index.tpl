<html>
<head>
<title>Diary</title>

<style type="text/css">

body {
	font-family:"Century Gothic";
	font-size: 12pt;
  background-color: #fff; 
	color: #333;
	text-align:center;
	}

.year {
	text-align: center;
  font-size: 6em;
	font-weight: bold;
	font-family:"Century Gothic";
	color: black;
}

.year-pane {
	position:absolute;
	top:10px;
	left:10%;
	border:solid;
	padding:5px;
	-moz-border-radius: 1em;
	text-align: center;
}

.year-pane a:link {text-decoration: none; color: black;}
.year-pane a:visited {text-decoration: none; color: black;}
.year-pane a:hover {text-decoration: underline overline; color: red;}


.entry {
  width: 100%; /*dynamic with div size*/
}

.content {
  font-family:"Century Gothic";	
	font-size: 11pt;
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

<div style="position:fixed;top:3;right:5;">
<a href="/quit" title="Quit the diary application">X</a>
</div>

<div style="position:fixed;top:3;left:5;">
<a href="/help" title="Get help">?</a>
<a href="/config" title="Advanced configuration">C</a>
</div>

<div class="year-pane">
<form action="/search" method="GET">
<input type="text" size=20 name="searchtext" title="Search" autocomplete="on">
</form>
<table align="center">
%for yc in year_count:
<tr><td align="center"><a href="/{{yc['year']}}">{{yc['year']}}</a></td><td><font size="1px">({{yc['cnt']}})</font></td></tr>
%end
</table>
</div>

%if view=='list': #In the traditional list view we get the new entry box 
<div class='content'>
<form action="/new" method="POST">
<p><input type="text" name="title" class="entry" title="Entry title" autocomplete="off"></p>
<p><textarea rows="10" wrap="virtual" name="body" class="entry" title="Text of entry"></textarea></p>
<input type="submit" name="save" value="save">
</form>
</div>
%end

%if view=='searchlist':
<div class="content">
<b>{{title}}</b>
</div>
%end

%if view=='list' or view=='searchlist': #Show us the traditional list view
%for row in rows:
<div class="content">
  <div class='date'>{{row['nicedate']}}</div>
  <div class='title'>{{row['title']}}</div>
  <p>{{!row['body']}}</p>
  <div class='lastupdated'>
  <a href="/edit/{{row['id']}}" title="click to edit">Last edited: {{row['updated_at']}}</a>
  </div>
</div>
%end

%elif view=='edit': #Allow us to edit a single entry
<div class="content">
Editing <b>{{entry['title']}}</b>
</div>
<div class="content">
  <form action="/save/{{entry['id']}}" method="POST">
   <p><input type="text" name="date" class="entry" title="Entry date" value="{{entry['date']}}"></p>  
   <p><input type="text" name="title" class="entry" title="Entry title" value="{{entry['title']}}"></p>
   <p><textarea rows="10" wrap="virtual" name="body" class="entry" title="Text of entry">{{entry['markup text']}}</textarea></p>
   <input type="submit" name="save" value="save">
  </form>
</div>
%elif view=='saved': #Show us the edited entry only
<div class="content">
Saved <b>{{entry['title']}}</b>
</div>
<div class="content">
  <div class='date'>{{entry['date']}}</div>
  <div class='title'>{{entry['title']}}</div>
  <p>{{!entry['body']}}</p>
  <div align="right"><a href="/edit/{{entry['id']}}">edit</a></div>
  <div class='lastupdated'>Last edited: {{entry['updated_at']}}</div>
</div>
%end
</body>
</html>