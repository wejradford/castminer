# Castminer

This is the code release for the work in [Tracking onscreen gender and role bias over time](http://www.webscience-journal.net/webscience/article/view/23) in the [Journal of Web Science](http://www.webscience-journal.net/webscience), currently in pre-print.

The code is split into two parts:
1. **Data processing** Preprocess an IMDb plain text data release into an `sqlite` database.
2. **Analysis** Run extraction and plotting scripts.

This is very much **research code**, but we've happy to help troubleshoot and extend analyses. Feel free to create issues if you see a bug or are interested in new features.

[Will Radford](http://wejradford.github.io/) and [Matthias Gallé](http://www.xrce.xerox.com/About-XRCE/People/Matthias-Galle).

## Installation

The code is tested to have worked with `python2.7` inside a `virtualenv` on a Macbook running El Capitan. It makes heavy use of command-line tools and can installed using the commands below.

It also assumes that you have the following system packages installed (using (homebrew)[http://brew.sh/]):
* `sqlite`

Depending on your setup, you may or may not need the steps below:
```bash
cd /path/to/checked-out-code
virtualenv ve
source ve/bin/activate
pip install --upgrade pip
# Sometimes numpy and scipy are happier installed in separate steps...
pip install `grep numpy requirements.txt`
pip install `grep scipy requirements.txt`
pip install -r requirements.txt
```

## 1: Data processing

**Important: downloading plain text IMDb data**

These can be found [here](http://www.imdb.com/interfaces), but **please respect the copyright/licence information on their site.**.
The code assumes the data release is extracted to `~/data/gender/imdb`, but you can edit the `Makefile` to use a different location.

```bash
# With the ve above active.
cd data_processing
make
```

This took an hour on a 2015 Macbook Pro, so you might need to get a cup of tea.

## 2: Analysis

```bash
cd ../stats
make
```

This creates output in two places:
* [stats/tbl](stats/tbl) - Text file tables
* [stats/figs](stats/figs) - PDF figures
