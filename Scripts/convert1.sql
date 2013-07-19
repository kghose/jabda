drop table if exists entries;
CREATE TABLE entries
(
  id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
  entry_date DATETIME,
  entry TEXT
);
attach 'olddb.sqlite3' as olddb;
insert into entries(entry_date, entry) select date, ifnull(title,'') || x'0A' || ifnull(body,'') from olddb.entries;