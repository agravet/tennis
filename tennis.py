        # -*- coding: utf-8 -*-
import copy
import random
import sys
import time
import os


def read_value(str,key):
    key_start = str.find(key)
    if key_start == -1:
        return "",-1
    key_end = key_start+len(key)
    val_start=key_end+1
    val_end=val_start+str[val_start:].find('\n')
    ret=str[val_start:val_end]
    return ret,val_end


def handle_comment_lines(str):
    while(True):
        key_start = str.find("#")
        if key_start < 0:
            return str
        key_end=key_start+str[key_start:].find('\n')+1
        if key_end <= key_start:
            return str
        str=str.replace(str[key_start:key_end],"",len(str))



def read_pair(str,key):
    key_start = str.find(key)
    if key_start == -1:
        return "",-1
    key_end = key_start+len(key)
    val_start=key_end+1
    val_end=len(str)
    ret=str[val_start:val_end]
    return ret,val_end


def check_next_key(str,key):
        key_start = str.find(key)
        if key_start > 5 or key_start == -1:
            return False
        return True


def pre_read_config():
    global weeks
    global raw
    global group_nr
    global players_nr
    global players
    global base_week
    global groups
    global timeslots
    global starting_week
    global ending_week
    global year
    players_nr=0
    fh = open("local/tennis.conf", "r")
    raw = fh.read()
    raw=raw.replace('\r\n','\n',1000)
    raw=handle_comment_lines(raw)
    raw=raw.replace(' ','',1000)
    raw=raw.replace("/\n","//",1000)
    raw=raw.replace("\n\n","\n",1000)
    year_t,t_pos=read_value(raw,"year")
    if (year_t):
        year=int(year_t)
    starting_week,t_pos=read_value(raw,"starting_week")
    ending_week,t_pos=read_value(raw,"ending_week")

    if starting_week and ending_week:
        weeks=int(ending_week)-int(starting_week)+1
        if (weeks<0):
            weeks += 52
        base_week = int(starting_week)
    pos = 0
    group_nr=0
    while (True):
        x,t_pos=read_value(raw[pos:],"ranking_group")
        if t_pos==-1:
            break
        group_nr+=1
        pos+=t_pos

    pos = 0
    players_nr=0
    while (True):
        x,t_pos=read_value(raw[pos:],"name")
        if t_pos==-1:
            break
        players_nr+=1
        pos+=t_pos
    pos = 0
    timeslots=0
    x,t_pos=read_value(raw[pos:],"rule")
    if t_pos==-1:
        return
    timeslots=len(x)


def read_ics_template_header():
    fh = open("template_header", "r")
    header = fh.read()
    #print header
    return header


def read_ics_template_body():
    fh = open("template_body", "r")
    body = fh.read()
    #print body
    return body


def read_ics_template_footer():
    fh = open("template_footer", "r")
    footer = fh.read()
    #print body
    return footer


def convertDate(day,week_no, hour, min):
    global year
    import datetime
    if day == 'Sun': day='-0'
    if day == 'Mon': day='-1'
    if day == 'Tue': day='-2'
    if day == 'Wed': day='-3'
    if day == 'Thu': day='-4'
    if day == 'Fri': day='-5'
    if day == 'Sat': day='-6'
    if (int(week_no)>52):
        res = int(week_no)%52
        week_no = str(res)
        t = datetime.datetime.strptime(str(year+1)+"-W"+ week_no + day, "%Y-W%W-%w") + datetime.timedelta(hours=int(hour), minutes=int(min))
    else:
        t = datetime.datetime.strptime(str(year)+"-W"+ week_no + day, "%Y-W%W-%w") + datetime.timedelta(hours=int(hour), minutes=int(min))
    return t.__format__("%Y%m%dT%H%M%S")


def convertDatePrint(day,week_no, hour, min):
    global year
    import datetime
    if day == 'Sun': day='-0'
    if day == 'Mon': day='-1'
    if day == 'Tue': day='-2'
    if day == 'Wed': day='-3'
    if day == 'Thu': day='-4'
    if day == 'Fri': day='-5'
    if day == 'Sat': day='-6'
    if (int(week_no)>52):
        res = int(week_no)%52
        week_no = str(res)
        t = datetime.datetime.strptime(str(year+1)+"-W"+ week_no + day, "%Y-W%W-%w") + datetime.timedelta(hours=int(hour), minutes=int(min))
    else:
        t = datetime.datetime.strptime(str(year)+"-W"+ week_no + day, "%Y-W%W-%w") + datetime.timedelta(hours=int(hour), minutes=int(min))
    return t.__format__("%b %d")



def getTimeslotData(ts):
    tts=ts
    loc=tts.find("_")
    day=tts[:loc]
    tts=tts[loc+1:]
    loc=tts.find(":")
    hour=tts[:loc]
    tts=tts[loc+1:]
    loc=tts.find("_")
    min=tts[:loc]
    tts=tts[loc+1:]
    location=tts
    return day,hour,min,location


def addToICS(info,ts,week_no, desc):
    day,hour,min,location = getTimeslotData(ts)
    start_date=convertDate(day,week_no,hour,min)
    end_date=convertDate(day,week_no,str(int(hour)+1),min)
    temp_ics=read_ics_template_body()
    temp_ics = temp_ics.replace("<START_DATE>",start_date,1)
    temp_ics = temp_ics.replace("<END_DATE>",end_date,1)
    temp_ics = temp_ics.replace("<TENNIS MATCH>",info,1)
    temp_ics = temp_ics.replace("<TENNIS LOCATION>",location,1)
    temp_ics = temp_ics.replace("<TENNIS DESC>",desc,1)
    temp_ics = temp_ics.replace("<TENNIS ALARM DESC>",desc,1)
    return temp_ics


def getTSInfo(ts,week_no):
    day,hour,min,location = getTimeslotData(ts)
    start_date=convertDatePrint(day,week_no,hour,min)
    return start_date+" "+ts


def handle_rule(str,weeks,timeslots):
    x = [0] * weeks
    for i in range(weeks):
        x[i] = [0] * timeslots
    for i in range(weeks):
        for j in range(timeslots):
            x[i][j] = ""
    ts = [0] * len(str)
    for i in range(len(str)):
        ts[i]=str[i]
    for j in range(weeks):
        x[j]=copy.deepcopy(ts)
    return x


def getException(z):
    first_start=0
    first_end = z.find(",")
    second_start=first_end+1
    second_end=len(z)
    return (z[first_start:first_end],z[second_start:second_end])


def handle_exception(slot,str,weeknr):
    global base_week
    comp = 0
    if (int(weeknr)-base_week)<0:
        comp = 52
    ts = [0] * len(str)
    for i in range(len(str)):
        if str[i]!='x':
            ts[i]=str[i]
        else:
            ts[i]=slot[int(weeknr)-base_week+comp][i]
    slot[int(weeknr)-base_week+comp]=copy.deepcopy(ts)
    return slot


def handleTimeslotDetails(str):
    global tsdata
    global timeslots
    global tsdata
    data_start=0
    data_end=0
    counter=0
    while (counter < timeslots):
        str=str[data_start:]
        data_end=str.find("//")
        if data_end == -1:
            break
        tsdata[counter]=str[:data_end]
        if len(tsdata[counter])>0:
            counter+=1
        data_start=data_end+2


def isIncluded(name, list, elem):
    for i in range(len(list)):
        if list[i] == elem:
            #print "for: "+name+" against "+elem+" in list: "+str(list)
            return True
    return False


def read_config():
    global timeslots
    global weeks
    global raw
    global group_nr
    global players_nr
    global players
    global a
    global groups
    global tsdata
    global result
    global price_list
    tsdata = [""]*timeslots
    groups=[0]*group_nr
    player_counter=-1
    players = [0] * players_nr
    a = [0] * weeks
    for i in range(weeks):
        a[i] = [0] * timeslots
    for i in range(weeks):
        for j in range(timeslots):
            a[i][j] = ""
    fh = open("local/tennis.conf", "r")
    raw = fh.read()
    raw=handle_comment_lines(raw)
    raw=raw.replace(' ','',1000)
    raw=raw.replace("/\n","//",1000)
    raw=raw.replace("\n\n","\n",1000)
    ts,t_pos=read_value(raw,"timeslots")
    result=copy.deepcopy(a)
    handleTimeslotDetails(ts)
    pos=t_pos
    last_group_start=0
    last_group_end=0
    group_counter=0
    while(True):
        gr_name,t_pos=read_value(raw[pos:],"ranking_group")
        if t_pos<0:
            break
        last_group_start=last_group_end
        pos+=t_pos
        while(True):
            if check_next_key(raw[pos:],"ranking_group") or check_next_key(raw[pos:],"training_group"):
                groups[group_counter]=(last_group_start,last_group_end-1)
                group_counter+=1
                break
            last_group_end+=1
            name_list_str,t_pos=read_value(raw[pos:],"name")
            if (t_pos==-1):
                break
            pos+=t_pos
            player_counter+=1
            name_list=name_list_str.split(",")
            name=name_list[0]
            email=name_list[1]
            phone=name_list[2]
            rule,t_pos=read_value(raw[pos:],"rule")
            data = copy.deepcopy(handle_rule(rule,weeks,timeslots))
            players[player_counter]=(data,name,0,[],email,phone)
            tlength = len(rule)
            if timeslots == 0:
                timeslots=tlength
            else:
                if tlength != timeslots:
                    print ("timeslot length error in config, " + name)
                    exit(1)
            pos+=t_pos
            if check_next_key(raw[pos:],"exception_week_rule"):
                x,t_pos=read_value(raw[pos:],"exception_week_rule")
                while t_pos>-1:
                    wnr,ts=getException(x)
                    (data,name,t,z,e,f)=players[player_counter]
                    data=copy.deepcopy(handle_exception(data,ts,wnr))
                    players[player_counter]=(data,name,t,z,e,f)
                    pos+=t_pos
                    if not check_next_key(raw[pos:],"exception_week_rule"):
                        break
                    x,t_pos=read_value(raw[pos:],"exception_week_rule")
            if check_next_key(raw[pos:],"incompatible_with"):
                x,t_pos=read_value(raw[pos:],"incompatible_with")
                while t_pos>-1:
                    (data,name,t,z,e,f)=players[player_counter]
                    y=copy.deepcopy(z)
                    y.append(x)
                    players[player_counter] = (data,name,t,y,e,f)
                    pos+=t_pos
                    if not check_next_key(raw[pos:],"incompatible_with"):
                        break
                    x,t_pos=read_value(raw[pos:],"incompatible_with")

    while(True):
        x,t_pos=read_value(raw[pos:],"training_group")
        if t_pos<0:
            break
        pos+=t_pos
        while(True):
            name_list_str,t_pos=read_value(raw[pos:],"name")
            if (t_pos==-1):
                break
            pos+=t_pos
            player_counter+=1
            name_list=name_list_str.split(",")
            name=name_list[0]
            email=name_list[1]
            phone=name_list[2]
            rule,t_pos=read_value(raw[pos:],"rule")
            data = copy.deepcopy(handle_rule(rule,weeks,timeslots))
            players[player_counter]=(data,name,0,z,email,phone)
            pos+=t_pos
            if check_next_key(raw[pos:],"exception_week_rule"):
                x,t_pos=read_value(raw[pos:],"exception_week_rule")
                while t_pos>-1:
                    wnr,ts=getException(x)
                    (data,name,t,z,e,f)=players[player_counter]
                    data=copy.deepcopy(handle_exception(data,ts,wnr))
                    players[player_counter]=(data,name,t,z,e,f)
                    pos+=t_pos
                    if not check_next_key(raw[pos:],"exception_week_rule"):
                        break
                    x,t_pos=read_value(raw[pos:],"exception_week_rule")

            if check_next_key(raw[pos:],"incompatible_with"):
                x,t_pos=read_value(raw[pos:],"incompatible_with")
                while t_pos>-1:
                    (data,name,t,z,e,f)=players[player_counter]
                    y=copy.deepcopy(z)
                    y.append(x)
                    #print name+" "+"incomaptible_with:"+str(z)
                    players[player_counter] = (data,name,t,y,e,f)
                    pos+=t_pos
                    if not check_next_key(raw[pos:],"incompatible_with"):
                        break
                    x,t_pos=read_value(raw[pos:],"incompatible_with")
    #handle holidays
    t_pos=0
    pos=t_pos
    ts,t_pos=read_value(raw[pos:],"special_timeslots")
    pos+=t_pos
    x,t_pos=read_value(raw[pos:],"sp")
    while t_pos>-1:
        wnr,ts=getException(x)
        comp=0
        if (int(wnr)-base_week)<0:
            comp=52
        for k in range (len(ts)):
            if ts[k] == 'l':
                result[int(wnr)-base_week+comp][k]=" +++ HOLIDAY: CLOSED +++   "
            if ts[k] == 's':
                result[int(wnr)-base_week+comp][k]=" +++ HOLIDAY: AVAILABLE +++"
        for i in range(len(players)):
            (data,name,t,z,e,f)=players[i]
            data=copy.deepcopy(handle_exception(data,ts,wnr))
            players[i]=(data,name,t,z,e,f)
        pos+=t_pos
        x,t_pos=read_value(raw[pos:],"sp")
    x,t_pos=read_value(raw,"timeslot_prices")
    price_list = x.split(",")


def mark_related_timeslots(slot,week,timeslot):
    #related_ts={0:[0,1,2],1:[0,1,2],2:[0,1,2],4:[4,5],5:[4,5],6:[6,7,8],7:[6,7,8],8:[6,7,8],9:[9,10],10:[9,10]}
    related_ts={0:[1,2,3],1:[0,2,3],2:[0,1,3],3:[0,1,2],4:[5,6,7,8],5:[4,6,7,8],6:[4,5,7,8],7:[4,5,6,8],8:[4,5,6,7],9:[10],10:[9]}
    if timeslot in related_ts:
        mapped_array=related_ts[timeslot]
        for j in range(len(mapped_array)):
            if slot[week][mapped_array[j]]=='c' or slot[week][mapped_array[j]]=='n':
                slot[week][mapped_array[j]] = 'b'

        if (timeslot == 0 or timeslot == 1 or timeslot == 2) and week > 0:
            if slot[week-1][9]=='c' or slot[week-1][9]=='n':
                slot[week-1][9] = 'b'
            if slot[week-1][10]=='c' or slot[week-1][10]=='n':
                slot[week-1][10] = 'b'

        if (timeslot == 9 or timeslot == 10) and week+1 < weeks:
            if slot[week+1][0]=='c' or slot[week+1][0]=='n':
                slot[week+1][0] = 'b'
            if slot[week+1][1]=='c' or slot[week+1][1]=='n':
                slot[week+1][1] = 'b'
            if slot[week+1][2]=='c' or slot[week+1][2]=='n':
                slot[week+1][2] = 'b'


    return slot


def check_week(slot, week, plays):
    global help_low_nr_games
    counter=0
    options_nr=0
    global low_slot_nr
    for i in range(timeslots):
        if slot[week][i]=="T" or slot[week][i]=="R":
            counter+=1
        if slot[week][i]=="T" or slot[week][i]=="R" or slot[week][i]=="c":
            options_nr+=1
    if (options_nr <= low_slot_nr) or (help_low_nr_games and plays < int(ending_week)-int(starting_week)):
        counter -=1
    return counter


def match_players(player1,player2,force,ranking,x,y):
    global timeslots
    global weeks
    global result
    comments=""
    if ranking==True:
        comments="#"
        mark='R'
    else:
        comments=" "
        mark="T"
    (slot1,name1,counter1,incomp1,e1,f1)=player1
    (slot2,name2,counter2,incomp2,e2,f2)=player2
    if name1 == name2:
        return (slot1,name1,counter1,incomp1),(slot2,name2,counter2,incomp2),False
    for j in (range(timeslots)):
        for i in range(x,weeks-y):
            if (slot1[i][j] == 'c' and slot2[i][j] == 'c'
                and result[i][j] == ""
                and not isIncluded(name1,incomp1,name2) and not isIncluded(name2,incomp2,name1)
                and check_week(slot1, i, counter1)<max_play_per_week and check_week(slot2, i, counter2)<max_play_per_week) :
                result[i][j] = '%-2s %-15s - %-15s'  % (comments, name1, name2)
                counter1 +=1
                counter2 +=1
                slot1=mark_related_timeslots(slot1,i,j)
                slot1[i][j] = mark
                slot2=mark_related_timeslots(slot2,i,j)
                slot2[i][j] = mark
                return (slot1,name1,counter1,incomp1,e1,f1),(slot2,name2,counter2,incomp2,e2,f2),True
    if force==True:
        for j in range(timeslots):
            for i in range(x,weeks-y):
                if (slot1[i][j] == 'c'
                    and slot2[i][j] != 'R' and slot2[i][j] != 'T' and slot2[i][j] != 'b' and slot2[i][j] != 'a'
                    and result[i][j] == ""
                    and not isIncluded(name1,incomp1,name2) and not isIncluded(name2,incomp2,name1)
                    and check_week(slot1, i, counter1)<max_play_per_week and check_week(slot2, i, counter2)<max_play_per_week):
                    result[i][j] = '%-2s %-15s - %-15s'  % (comments, name1, name2+"(F)")
                    counter1 +=1
                    counter2 +=1
                    slot1=mark_related_timeslots(slot1,i,j)
                    slot1[i][j] = mark
                    slot2=mark_related_timeslots(slot2,i,j)
                    slot2[i][j] = mark
                    return (slot1,name1,counter1,incomp1,e1,f1),(slot2,name2,counter2,incomp2,e2,f2),True
        for j in (range(timeslots)):
            for i in range(x,weeks-y):
                if (slot2[i][j] == 'c'
                    and slot1[i][j] != 'R' and slot1[i][j] != 'T' and slot1[i][j] != 'b' and slot1[i][j] != 'a'
                    and result[i][j] == ""
                    and not isIncluded(name1,incomp1,name2) and not isIncluded(name2,incomp2,name1)
                    and check_week(slot1, i, counter1)<max_play_per_week and check_week(slot2, i, counter2)<max_play_per_week):
                    result[i][j] = '%-2s %-15s - %-15s'  % (comments, name1+"(F)", name2)
                    counter1 +=1
                    counter2 +=1
                    slot1=mark_related_timeslots(slot1,i,j)
                    slot1[i][j] = mark
                    slot2=mark_related_timeslots(slot2,i,j)
                    slot2[i][j] = mark
                    return (slot1,name1,counter1,incomp1,e1,f1),(slot2,name2,counter2,incomp2,e2,f2),True
        for j in (range(timeslots)):
            for i in range(x,weeks-y):
                if (slot1[i][j] != 'R' and slot1[i][j] != 'T' and slot1[i][j] != 'b' and slot1[i][j] != 'a'
                    and slot2[i][j] != 'R' and slot2[i][j] != 'T' and slot2[i][j] != 'b' and slot2[i][j] != 'a'
                    and result[i][j] == ""
                    and not isIncluded(name1,incomp1,name2) and not isIncluded(name2,incomp2,name1)
                    and check_week(slot1, i, counter1)<max_play_per_week and check_week(slot2, i, counter2)<max_play_per_week):
                    result[i][j] = '%-2s %-15s - %-15s'  % (comments, name1+"(F)", name2+"(F)")
                    counter1 +=1
                    counter2 +=1
                    slot1=mark_related_timeslots(slot1,i,j)
                    slot1[i][j] = mark
                    slot2=mark_related_timeslots(slot2,i,j)
                    slot2[i][j] = mark
                    return (slot1,name1,counter1,incomp1,e1,f1),(slot2,name2,counter2,incomp2,e2,f2),True
    return (slot1,name1,counter1,incomp1,e1,f1),(slot2,name2,counter2,incomp2,e2,f2),False


def handle_group(first,last):
    global ranking_failure_counter
    global ranking_failure_report
    global weeks_before_ranking
    global weeks_after_ranking
    for i in range(first, last+1):
        for j in range(i+1, last+1):
            players[i],players[j],res = match_players(players[i],players[j],True,True,weeks_before_ranking,weeks_after_ranking)
            if res == False:
                slot1,name1,counter1,incomp1,e1,f1=players[i]
                slot2,name2,counter2,incomp2,e2,f2=players[j]
                reason=""
                if isIncluded(name1,incomp1,name2) or isIncluded(name2,incomp2,name1):
                    reason = " due to incompatibilty"
                else:
                    reason = " due to strict rules"
                ranking_failure_report += "    # Ranking failure between: "+name1+" - "+name2 + reason +"\n"
                ranking_failure_counter +=1


def handle_rankings():
    for i in range(group_nr):
        a,b=groups[i]
        handle_group(a,b)


def handle_training_by_best_effort_random(mode):
    global additional_plays
    limit=weeks+additional_plays
    for x in range(0,1000):
        i=random.randint(0, players_nr-1)
        j=random.randint(0, players_nr-1)
        if i!=j:
            slot1,name1,counter1,incomp1,e1,f1=players[i]
            if counter1 >= limit:
                continue
            slot2,name2,counter2,incomp2,e2,f2=players[j]
            if counter2 >= limit:
                continue
            players[i],players[j],res = match_players(players[i],players[j],mode,False,0,0)
    return False


def fill_slots():
    for x in range(weeks):
        for y in range(timeslots):
            if result[x][y] == "":
                min = weeks
                min_index = -1
                for i in range(players_nr):
                    slot1,name1,counter1,incomp1,e1,f1=players[i]
                    if slot1[x][y] == 'c':
                        if min > counter1:
                            min = counter1
                            min_index = i
                if (min_index != -1):
                    for j in range(players_nr):
                        if (min_index != j):
                            slot2,name2,counter2,incomp2,e2,f2=players[j]
                            if slot2[x][y] == 'c':
                                players[min_index],players[j],res = match_players(players[min_index],players[j],False,False,0,0)




def count_unused_timeslots():
    global result
    counter=0
    for i in range(weeks):
        for j in range(timeslots):
            if result[i][j] == "" :
                counter += 1
    return counter


def analyze():
    global result
    min=1000
    max=0
    for i in range(0,players_nr):
        slot,name,counter,incomp,e,f=players[i]
        if min >  counter:
            min = counter
        if max <  counter:
            max = counter
    return max,min


def readInput(text):
    print text
    # raw_input returns the empty string for "enter"
    yes = {'yes','y', 'ye', ''}
    no = {'no','n'}
    choice = raw_input().lower()
    if choice in yes:
        return True
    elif choice in no:
        return False
    else:
        sys.stdout.write("Please respond with 'yes' or 'no'")


def sendEmail(to):
    import smtplib
    server = smtplib.SMTP('smtp.gmail.com', 587)
    server.starttls()
    server.login("levente.varga@gmail", "xxxxx")
    msg = "YOUR MESSAGE!"
    server.sendmail("levente.varga@gmail", to, msg)
    server.quit()


import time
from threading import Thread


def thread_func(i):
    global stop
    while 1:
        print 'Press <ENTER> to if result is good enough'
        raw_input("")
        stop=True
        return

def thread_start():
    t = Thread(target=thread_func, args=(0,))
    t.start()


#####################################################################################
#####################################################################################


def main():
    global max_play_per_week
    global max_slots_left
    global max_diff_between_most_and_least_plays
    global max_cycles
    global low_slot_nr
    global additional_plays
    global weeks_before_ranking
    global weeks_after_ranking
    global help_low_nr_games
    global stop
    stop = False
    #default settings
    max_play_per_week = 2
    max_slots_left = 0
    max_diff_between_most_and_least_plays=2
    max_cycles=10000
    low_slot_nr=5
    additional_plays=1
    weeks_before_ranking=2
    weeks_after_ranking=1
    if len(sys.argv) > 1 and (sys.argv[1]=="help" or sys.argv[1]=="-h" or sys.argv[1]=="--help"):
            print ("Usage:")
            print ("python "+sys.argv[0]+" max_cycles=1000 max_plays_per_week=1 low_slot_nr=5 additional_plays=1 weeks_before_ranking=1 weeks_after_ranking=1")
            exit(0)
    print ("max_cycles = "+str(max_cycles))
    print ("max_plays_per_week = "+str(max_play_per_week))
    print ("low_slot_nr = "+str(low_slot_nr))
    print ("additional_plays = "+str(additional_plays))
    print ("weeks_before_ranking = "+str(weeks_before_ranking))
    print ("weeks_after_ranking = "+str(weeks_after_ranking))
    print ('-----------------')

    #read command line parameters
    for i in range(len(sys.argv)):
        val,t_pos =read_pair(sys.argv[i], "max_cycles")
        if val:
            max_cycles = int(val)
            print ("override max_cycles = "+str(max_cycles))
            continue

        val,t_pos =read_pair(sys.argv[i], "max_plays_per_week")
        if val:
            max_play_per_week = int(val)
            print ("override max_plays_per_week = "+str(max_play_per_week))
            continue

        val,t_pos =read_pair(sys.argv[i], "low_slot_nr")
        if val:
            low_slot_nr = int(val)
            print ("override low_slot_nr = "+str(low_slot_nr))
            continue

        val,t_pos =read_pair(sys.argv[i], "additional_plays")
        if val:
            additional_plays = int(val)
            print ("override additional_plays = "+str(additional_plays))
            continue

        val,t_pos =read_pair(sys.argv[i], "weeks_before_ranking")
        if val:
            weeks_before_ranking = int(val)
            print ("override weeks_before_ranking = "+str(weeks_before_ranking))
            continue

        val,t_pos =read_pair(sys.argv[i], "weeks_after_ranking")
        if val:
            weeks_after_ranking = int(val)
            print ("override weeks_after_ranking = "+str(weeks_after_ranking))
            continue

    global timeslots
    global weeks
    global raw
    global group_nr
    global players_nr
    global players
    global a
    global groups
    global tsdata
    global result
    global unused_slots
    global diff_most_least
    global ranking_failure_counter
    global ranking_failure_report
    global cycles_used
    global stored_result
    global stored_analyze
    global stored_players
    global price_list
    global starting_week
    global ending_week
    global help_low_nr_games
    sys.stdout.write("\nStarted:")
    sys.stdout.flush()
    cycles_used=0
    best = 10000
    best_index = 0
    best_cycle = 0
    counter=0

    thread_start()
    while(cycles_used < max_cycles):
        timeslots = 0
        weeks = 0
        raw=""
        group_nr=0
        ranking_failure_counter = 0
        ranking_failure_report =""
        help_low_nr_games=0
        #read configuration
        pre_read_config()
        read_config()
        players_orig=copy.deepcopy(players)
        #handle ranking matches
        handle_rankings()
        #handle training matches, respecting player options

        orig_low_slot_nr = low_slot_nr
        low_slot_nr = 0
        handle_training_by_best_effort_random(False)
        help_low_nr_games=1
        handle_training_by_best_effort_random(False)
        low_slot_nr = orig_low_slot_nr
        handle_training_by_best_effort_random(False)

        fill_slots()

        #collect statitistical data
        unused_slots = count_unused_timeslots()
        max,min=analyze()
        diff_most_least = max-min
        #store best result so far
        equiv = (diff_most_least*1 + unused_slots*5 + (weeks-min)* + 10*ranking_failure_counter)
        if best > equiv:
            best = equiv
            stored_result=copy.deepcopy(result)
            stored_players=copy.deepcopy(players)
            stored_analyze = max, min, unused_slots, cycles_used
            sys.stdout.write("("+str(diff_most_least)+"/"+str(unused_slots)+"/"+str(min)+"/"+str(ranking_failure_counter)+")")
        else:
            counter = counter + 1
            '''
            perc = "["+str("%  d" % (int(100*counter/max_cycles)))+'%]'
            sys.stdout.write(perc)
            for i in range(len(perc)):
                sys.stdout.write('\b')
            sys.stdout.flush()
            '''
            perc = '['
            for i in range(10):
                if i < int(10*counter/max_cycles)+1:
                    perc +='*'
                else:
                    perc +=' '
            perc +=']'
            sys.stdout.write(perc)
            for i in range(len(perc)):
                sys.stdout.write('\b')
            sys.stdout.flush()

        cycles_used = cycles_used + 1
        if stop:
            break
    print ""
    #after loop, prepare results
    result= copy.deepcopy(stored_result)
    players=copy.deepcopy(stored_players)
    max, min, unused_slots, best_cycle = stored_analyze
    #prezent the results
    to_print = ''
    common_part_print=''
    common_part_print = common_part_print +  ("\n\n\n\n\n\n\n\n")
    common_part_print = common_part_print +  ("--------------------------------------------------------------------------------------------------------") + "\n"
    for i in range(group_nr):
        a,b=groups[i]
        common_part_print = common_part_print +  ("========= ranking group: "+str(i+1)+"  ===============================================================") + "\n"
        for j in range(a,b+1):
            slot,name,counter,incomp,e,f=players[j]
            common_part_print = common_part_print +  ('%-20s  %-50s  %-20s' % (name,e,f)) + "\n"
    common_part_print = common_part_print +  ("========= training group: =================================================================") + "\n"
    for i in range(b+1,players_nr):
        slot,name,counter,incomp,e,f=players[i]
        common_part_print = common_part_print +  ('%-20s  %-50s  %-20s' % (name,e,f)) + "\n"
    common_part_print = common_part_print +  ("===========================================================================================") + "\n"
    common_part_print = common_part_print +  ("\n\n\n") + "\n"
    for i in range(weeks):
        common_part_print = common_part_print + ("========= week: "+str((i+base_week)%52)+"  ===============================================================") + "\n"
        for j in range(timeslots):
            if result[i][j]:
                text=result[i][j]
            else:
                text=" +++ UNUSED : AVAILABLE +++"
            common_part_print = common_part_print +  ('%-36s  %-40s' % (text, getTSInfo(tsdata[j], str(i+base_week)) )) + "\n"
    common_part_print = common_part_print + ("=======================================================================================================") + "\n"
    to_print = to_print + common_part_print
    os.system("rm -rf out")
    for i in range(players_nr):
        own_schedule_print=''
        price = 0
        slot,name,counter,incomp,e,f=players[i]
        ics=read_ics_template_header()
        own_schedule_print = own_schedule_print + ("\n")
        own_schedule_print = own_schedule_print + ('=======  %s  plays %d times =============================================================' % (name, counter)) + "\n"
        for x in range(weeks):
            own_schedule_print = own_schedule_print + ('w%d:' % ((x+base_week)%52)) + "\n"
            for y in range(timeslots):
                if slot[x][y]=='R' or slot[x][y]=='T':
                    own_schedule_print = own_schedule_print + ('%-36s  %-40s' % (result[x][y], getTSInfo(tsdata[y], str(x+base_week)) )) + "\n" 
                    if slot[x][y]=='R':
                        ics+=addToICS(result[x][y], tsdata[y], str(x+base_week), "Ranking Match")
                    else:
                        ics+=addToICS(result[x][y], tsdata[y], str(x+base_week), "Training Match")
                    #price += float(price_list[y])
        ics+=read_ics_template_footer()
        ics=ics.replace(' ','',1000)
        if not os.path.exists("out"):
            os.makedirs("out")
        f=open('./out/'+name+".ics", 'w+')
        f.write(ics)
        f.close()
        #print ics
        own_schedule_print = own_schedule_print +('\n-Payments:---------------------------------------------------') + "\n"
        for x in range(weeks):
            #print ('%0d:' % (x+base_week))
            own_schedule_print = own_schedule_print +('w'+str((x+base_week))+': ')
            for y in range(timeslots):
                if slot[x][y]=='R' or slot[x][y]=='T':
                    own_schedule_print = own_schedule_print +(price_list[y])
                    price += float(price_list[y])
                else:
                    own_schedule_print = own_schedule_print +(' -- ')
                own_schedule_print = own_schedule_print +(' ')
            own_schedule_print = own_schedule_print +('\n')
        if name.find('*')>=0:
            new_price = price*2
            own_schedule_print = own_schedule_print + ('   total pay:'+str(price)+ ' x 2 = '+str(new_price)+' Euros') + "\n"
        else:
            own_schedule_print = own_schedule_print + ('   total pay:'+str(price)+ ' Euros') + "\n"
        to_print = to_print + own_schedule_print
        f=open('./out/'+name+".txt", 'w+')
        f.write( own_schedule_print + common_part_print + ("\n\n\n © Levente Varga 2018"))
        f.close()
    to_print = to_print + ('\n=========================================================================================') + "\n"

    report_to_print=''
    report_to_print = report_to_print + ("Report: ") + '\n'
    report_to_print = report_to_print +  ("   ranking failures: "+str(ranking_failure_counter)) + '\n'
    report_to_print = report_to_print +  (ranking_failure_report) + '\n'
    report_to_print = report_to_print +  ("   unused slots:     "+str(unused_slots)) + '\n'
    report_to_print = report_to_print +  ("   diff most/least:  "+str(max - min)) + '\n'
    report_to_print = report_to_print +  ("   max plays:        "+str(max)) + '\n'
    report_to_print = report_to_print +  ("   min plays:        "+str(min)) + '\n'
    report_to_print = report_to_print +  ("   cycles used:      "+str(cycles_used)) + '\n'
    report_to_print = report_to_print +  '\n'
    report_to_print = report_to_print +  (" © Levente Varga 2018") + '\n'

    print report_to_print

    to_print = to_print + report_to_print

    f=open('./out/'+"common"+".txt", 'w+')
    f.write(to_print)
    f.close()

    
    if readInput('Are you satisfied with the results? [Y/n] '):
        
        if readInput('Do you want to store the results? [Y/n] '):
            '''
            #send email
            print "Sending results by e-mail"
            sendEmail("levente.l.varga@ericsson.com")
            '''
            out_folder="out_"+starting_week+"-"+ending_week
            out_folder_pub=out_folder+"_pub"
            os.system("cp -rf out "+out_folder_pub)
            os.system("cp local/tennis.conf out/")
            os.system("cp -rf out "+out_folder)
            os.system("rm  -rf "+out_folder+".zip "+out_folder_pub+".zip")
            os.system("zip -rq "+out_folder_pub+".zip "+out_folder_pub)
            os.system("zip -rq "+out_folder+".zip "+out_folder)
            os.system("rm  -rf "+out_folder+" "+out_folder_pub)
        else:
            print "Results not stored, but they still can be found in folder \'out\'"
    else:
        print "Please modify parameters and re-run the program"



main()
