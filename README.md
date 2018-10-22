Backlog:
=======

- check if why some slot are left empty(if problem real at all)
---------------------------------------------------------------

- add timeslot price tag
------------------------
for payment calculation

- add payment report
--------------------


- add email support
-------------------
  1) player email / phone nr to be added to configuration
  2) the ouput files would be re-processed and sent to each player in email
     triggered with a separate command
  3) phone number to be added to the player alarm information for making easy
     contacting the other guy when needed

- automatic result handling
---------------------------
    TBD


Completed:
=========
- generic holiday rules added
---------------------
    special_timeslots=holidays
        # rule=<week number>,<timeslot option 1>...
        # x=no restriction, s=available for special booking, l=closed
        sp=39,xxxssssssll
        sp=42,lllllllllll

- add user incompatibility: DONE for 1 user
---------------------------
    name=LAITAMAKI
        rule=ccccacnnnaa
        avoid=RAEVUORI
    name=RAEVUORI
        rule=nccncnnnnaa
