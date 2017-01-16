# Stato

DFS projection aggregation and lineup optimiser for FanDuel. 


## Install
 ```bash
git clone https://github.com/scottcorbett/stato.git
cd stato
python setup.py install
```

## Commands

Commands take a mixture of SPORT and NAME arguments. SPORT is either NFL or NBA and NAME is 
the name of a contest added to the database. 

### add
Adds a new contest to the database.

```
Usage: stato add SPORT NAME FILENAME
```

* FILENAME: path to player export from edit entry screen

### list
Lists contests for a sport

```
Usage: stato list SPORT
```

### optimise
Create optimised lineup for a contest 

```
Usage: stato optimise [OPTIONS] SPORT NAME

Options:
  -xs, --exclude_source TEXT  Exclude a projection source
  -xp, --exclude_player TEXT  Exclude a player
  -fp, --force_player TEXT    Force a player
  -rnd, --random              Include a random projection for each player
```

### update
Update player projections  

```
Usage: stato update [OPTIONS] SPORT NAME

Options:
  -s, --source TEXT           Update a specific source
  -xs, --exclude_source TEXT  Ignore a source while updating
  -c, --use_cache             Use cached http responses
```
 
### view
View player projections  

```
Usage: stato view [OPTIONS] SPORT NAME

Options:
  -s, --source TEXT    Filter by source
  -p, --position TEXT  Filter by position
  -t, --team TEXT      Filter by team code
  -fp FLOAT            Filter by minimum Fantasy Points
  -fppk FLOAT          Filter by minimum Fantasy Points Per $1000
```