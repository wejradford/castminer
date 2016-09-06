DATA=~/data/gender/imdb

parts.sqlite: parts.csv populate_db.sh
	./populate_db.sh $@ $<

parts.csv: all.txt.sorted find_distributions.py to_csv.py
	cat all.txt.sorted | ./find_distributions.py | ./to_csv.py > $@

all.txt.sorted: all.txt
	cat $< | LC_COLLATE=POSIX sort -t '	' -k3,3 -k6,6 -k8,8 -k2,2 -k1,1 > $@

all.txt: m.txt f.txt expand.py
	cat m.txt f.txt | cut -f 1-8 | ./expand.py > $@

m.txt: $(DATA)/actors.list.gz imdb_to_records.py companies.txt
	cat $< | gunzip | ./imdb_to_records.py --companies companies.txt 'M' > $@

f.txt: $(DATA)/actresses.list.gz imdb_to_records.py companies.txt
	cat $< | gunzip | ./imdb_to_records.py --companies companies.txt 'F' > $@

companies.txt: $(DATA)/production-companies.list.gz
	cat $< | gunzip | ./extract_production_companies.py > $@ 2> companies.log
	cat companies.log

clean:
	rm -rf m.txt f.txt all.txt parts.csv parts.sqlite all.txt.sorted companies.txt
