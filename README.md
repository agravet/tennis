Backlog:
=======

- Add year info to the weeknumbers
----------------------------------


- After injuries (or a flu) players sometimes wish “no ranking matches during the two first weeks, only training”.
------------------------------------------------------------------------------------------------------------------


- Only 1-2 training turns in addition to ranking matches. I.e very limited number of turns (with individual parameter?)
-----------------------------------------------------------------------------------------------------------------------


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

-player with fewer obtions allowed over weekly limit with 1
------------------------------------------------------------

- check if why some slot are left empty(if problem real at all)
---------------------------------------------------------------
  no need


- add timeslot price tag
------------------------
for payment calculation


- add payment report
--------------------


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
