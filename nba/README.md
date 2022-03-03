# POELTL

https://poeltl.dunk.town/

## Collect data 
by running the following script on 
https://en.wikipedia.org/wiki/List_of_current_NBA_team_rosters

```
$("table.toccolours").each(function() {
    team_name = $("> caption > div > b", this).contents().first().text();
    team_name = team_name.replace(/ roster/gi, "");
    
    $("> tbody > tr > td> table.sortable.jquery-tablesorter", this).each(function() {
        $("> tbody > tr", this).each(function() {
          console.log(team_name + "\t" + this.innerText);
        });
    })
})
```

## Generate data sheet
- Copy printed info into a spreadsheet
- Export as CSV
