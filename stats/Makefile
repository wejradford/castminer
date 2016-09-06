DB=../data_processing/parts.sqlite
FILES=figs/media.rm-5.pdf figs/nurse.rm-5.pdf figs/reporter.rm-5.pdf \
	tbl/gender_roles.txt \
	tbl/gender_roles.all.txt \
    tbl/time_roles.FILM+TV.top20.txt \
    tbl/time_roles.FILM+TV.top20.emerging.txt \
	tbl/time_roles.film.top20.emerging.txt \
	tbl/time_roles.tv.top20.emerging.txt \
	tbl/gender_profession_table.txt \
	figs/IMDbVsCensus.TV.log \
	figs/IMDbVsCensus.FILM.log \
	figs/IMDbVsCensus.FILM+TV.log \
	figs/rolling-hellinger.pdf \
	figs/gender-counts.rm-5.pdf \
	figs/census_lines.log figs/counts.rm-5.pdf \
    tbl/countries.txt
.PHONY: clean

all: $(FILES)

figs/media.rm-5.pdf: plot_media.py $(DB)
	./plot_media.py --db $(DB) --height 5 --font-size 12

figs/nurse.rm-5.pdf: plot_role.py $(DB)
	./plot_role.py --db $(DB) nurse --width 11 --height 5 --earliest-year 1970 --font-size 12

figs/reporter.rm-5.pdf: plot_role.py $(DB)
	./plot_role.py --db $(DB) reporter --width 10 --height 5 --earliest-year 1970 --font-size 12

tbl/gender_roles.txt: print_gender_role_table.py $(DB)
	./print_gender_role_table.py --limit 20 --db $(DB) --by-media > $@

tbl/gender_roles.all.txt: print_gender_role_table.py $(DB)
	./print_gender_role_table.py --limit 50 --db $(DB) > $@

## Time roles.
tbl/time_roles.FILM+TV.top20.txt: print_time_role_table.py $(DB)
	./print_time_role_table.py --db $(DB) --limit 10 --top 50 > $@

tbl/time_roles.FILM+TV.top20.emerging.txt: print_time_role_table.py $(DB)
	./print_time_role_table.py --db $(DB) --limit 10 --top 50 --emerging > $@

tbl/time_roles.film.top20.emerging.txt: print_time_role_table.py $(DB)
	./print_time_role_table.py --db $(DB) --medium FILM --limit 10 --top 50 --emerging > $@

tbl/time_roles.tv.top20.emerging.txt: print_time_role_table.py $(DB)
	./print_time_role_table.py --db $(DB) --medium TV --limit 10 --top 50 --emerging > $@

## Gender roles.
tbl/gender_profession_table.txt: print_gender_profession_table.py $(DB)
	./print_gender_profession_table.py --db $(DB) > $@

figs/IMDbVsCensus.TV.log: plot_temporal_census_comparison.py utils.py $(DB) ../data/imdbToCensus.txt tbl/uscensusRoles.csv
	./plot_temporal_census_comparison.py --db $(DB) --mapping ../data/imdbToCensus.txt --census tbl/uscensusRoles.csv --medium TV 2> $@

figs/IMDbVsCensus.FILM.log: plot_temporal_census_comparison.py utils.py $(DB) ../data/imdbToCensus.txt tbl/uscensusRoles.csv
	./plot_temporal_census_comparison.py --db $(DB) --mapping ../data/imdbToCensus.txt --census tbl/uscensusRoles.csv --medium FILM 2> $@

figs/IMDbVsCensus.FILM+TV.log: plot_temporal_census_comparison.py utils.py $(DB) ../data/imdbToCensus.txt tbl/uscensusRoles.csv
	./plot_temporal_census_comparison.py --db $(DB) --mapping ../data/imdbToCensus.txt --census tbl/uscensusRoles.csv --medium FILM+TV --font-size 18 2> $@

figs/rolling-hellinger.pdf: plot_rolling_hellinger.py $(DB)
	./plot_rolling_hellinger.py --db $(DB) --height 6 --font-size 12

figs/counts.rm-5.pdf: plot_all_roles.py $(DB)
	./plot_all_roles.py --db $(DB) --height=3 --width=10 --font-size 12

figs/gender-counts.rm-5.pdf: plot_all_gender_roles.py $(DB)
	./plot_all_gender_roles.py --db $(DB) --height=5 --width=11 --font-size 12

figs/census_lines.log: ./plot_temporal_census_comparison_line.py $(DB) ../data/imdbToCensus.txt tbl/uscensusRoles.csv
	 ./plot_temporal_census_comparison_line.py --db $(DB) --mapping ../data/imdbToCensus.txt --census tbl/uscensusRoles.csv --height 7 --width 10 --font-size 20 accountant architect artist baker bus driver butcher cashier ceo cook dentist electrician firefighter housekeeping janitor lawyer manager nurse pilot plumber programmer reporter scientist surgeon taxi teacher 'travel agent' teacher writer 2> $@

tbl/countries.txt: ./print_country_table.py $(DB)
	./print_country_table.py --db $(DB) > $@

clean:
	rm -rf $(FILES)
	rm -rf figs/IMDbVsCensus*.pdf
