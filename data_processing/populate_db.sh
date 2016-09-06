#!/bin/bash
DB=$1
CSV=$2
echo 'CREATE TABLE parts (year INT, name TEXT, medium VARCHAR(5), country VARCHAR(4), count INT, female REAL, male REAL);' | sqlite3 $DB
echo "Importing $CSV"
echo ".import $CSV parts" | sqlite3 --cmd '.mode csv' $DB
echo "Creating indices"
echo 'CREATE INDEX parts_year on parts(year);' | sqlite3 $DB
echo 'CREATE INDEX parts_year_name on parts(year, name);' | sqlite3 $DB
echo 'CREATE INDEX parts_name on parts(name);' | sqlite3 $DB
echo 'CREATE INDEX parts_year_medium on parts(year, medium);' | sqlite3 $DB
echo 'CREATE INDEX parts_year_medium_name on parts(year, medium, name);' | sqlite3 $DB
