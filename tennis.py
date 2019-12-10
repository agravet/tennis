        # -*- coding: utf-8 -*-
import copy
import random
import sys
import time
import os

OPTION_NONE             = '0'
OPTION_NO_PLAY          = '1'
OPTION_NO_TRAINING      = '3'
OPTION_NO_RANKING       = '5'
OPTION_NO_BOTH          = '7'
OPTION_TRAINING         = '2'
OPTION_RANKING          = '4'
OPTION_BOTH             = '6'
SCHEDULE_REST           = 'b'
SCHEDULE_TRAINING       = 'T'
SCHEDULE_RANKING        = 'R'

#####################################################################################



def executeCommand(cmd):
    return os.popen(cmd).read()



#####################################################################################



def killOtherInstances():
    res = executeCommand("ps -elf | grep tennis.py | grep -v grep | awk '{ print $4 }'")
    res_list = res.split()
    actual_pid = max(res_list)
    res_list.remove(actual_pid)
    for x in res_list:
        command = "kill -9 " + str(x)
        res = executeCommand(command);
        print (command +" ->"+res)



#####################################################################################



def get_slot_data(str):
    sep_start = str.find("-")
    if sep_start == -1:
        return "",""
    val1 = str[:sep_start]
    val2 = str[sep_start+1:]
    #print (val1)
    return val1,val2



#####################################################################################



def read_value(str,key):
    key_start = str.find(key)
    if key_start == -1:
        return "",-1
    key_end = key_start+len(key)
    val_start=key_end+1
    val_end=val_start+str[val_start:].find('\n')
    ret=str[val_start:val_end]
    return ret,val_end



#####################################################################################



def handle_comment_lines(str):
    while(True):
        key_start = str.find("#")
        if key_start < 0:
            return str
        key_end=key_start+str[key_start:].find('\n')+1
        if key_end <= key_start:
            return str
        str=str.replace(str[key_start:key_end],"",len(str))



#####################################################################################



def read_pair(str,key):
    key_start = str.find(key)
    if key_start == -1:
        return "",-1
    key_end = key_start+len(key)
    val_start=key_end+1
    val_end=len(str)
    ret=str[val_start:val_end]
    return ret,val_end



#####################################################################################



def check_next_key(str,key):
        key_start = str.find(key)
        if key_start > 5 or key_start == -1:
            return False
        return True



#####################################################################################



def pre_read_config():
    global weeks
    global raw
    global group_nr
    global players_nr
    global players
    global groups
    global timeslots
    global starting_week
    global ending_week
    global year
    players_nr=0
    fh = open("tennis.conf", "r")
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
    mxp,tsl = get_slot_data(x)
    timeslots=len(tsl)



#####################################################################################



def read_ics_template_header():
    fh = open("template_header", "r")
    header = fh.read()
    #print header
    return header



#####################################################################################



def read_ics_template_body():
    fh = open("template_body", "r")
    body = fh.read()
    #print body
    return body



#####################################################################################



def read_ics_template_footer():
    fh = open("template_footer", "r")
    footer = fh.read()
    #print body
    return footer



#####################################################################################



def covertWeekNumberToIndex(w_no,st_w,end_w):
    if (int(st_w) <= int(w_no)):
        return int(w_no)-int(st_w)
    else:
        return 52 - int(st_w) + int(w_no)



#####################################################################################



def convertIndexToWeekNumber(w_ind,st_w,end_w):
    toret = (int(st_w)-1+int(w_ind))%52+1
    #print "w_ind: %d st_w:%s end_w:%s   - > %d" % (w_ind,st_w,end_w,toret)
    return toret



#####################################################################################



def convertIndexToWeekNumberMachine(w_ind,st_w,end_w):
    #52-5, 0-> 52 + 1->0 2->1
    toret = (int(st_w)+int(w_ind))%53
    #print "w_ind: %d st_w:%s end_w:%s   - > %d" % (w_ind,st_w,end_w,toret)
    return toret



#####################################################################################



def getYear(w_nos,st_w,end_w,start_year):
    w_no =int(w_nos)+1
    if int(w_no) < int(st_w):
        toret = int(start_year)+1
    else:
        toret = int(start_year)
    #print "w_no:%d,st_w:%d,end_w:%d,start_year:%d -> toret:%d" % (int(w_no),int(st_w),int(end_w),int(start_year),toret)
    return toret



#####################################################################################



def convertDate(day,week_no, hour, min):
    global year
    global starting_week
    global ending_week
    import datetime
    if day == 'Sun': day='-0'
    if day == 'Mon': day='-1'
    if day == 'Tue': day='-2'
    if day == 'Wed': day='-3'
    if day == 'Thu': day='-4'
    if day == 'Fri': day='-5'
    if day == 'Sat': day='-6'
    t = datetime.datetime.strptime(str(getYear(week_no,starting_week,ending_week,year))+"-W"+ str(int(week_no)-1) + day, "%Y-W%W-%w") + datetime.timedelta(hours=int(hour)-2, minutes=int(min))
    #print "yyy(day:%s,week_no:%s, hour:%s, min:%s -> %s)" % (day,week_no, hour, min, t.__format__("%Y %b %d"))
    return t.__format__("%Y%m%dT%H%M%S")



#####################################################################################



def convertDatePrint(day,week_no, hour, min):
    global year
    global starting_week
    global ending_week
    import datetime
    if day == 'Sun': day='-0'
    if day == 'Mon': day='-1'
    if day == 'Tue': day='-2'
    if day == 'Wed': day='-3'
    if day == 'Thu': day='-4'
    if day == 'Fri': day='-5'
    if day == 'Sat': day='-6'
    t = datetime.datetime.strptime(str(getYear(week_no,starting_week,ending_week,year))+"-W"+ str(int(week_no)-1) + day, "%Y-W%W-%w") + datetime.timedelta(hours=int(hour), minutes=int(min))
    #print "xxx(day:%s,week_no:%s, hour:%s, min:%s -> %s)" % (day,week_no, hour, min, t.__format__("%Y %b %d"))
    return t.__format__("%d/%b/%y")



#####################################################################################



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



#####################################################################################



def addToICS(info,ts,week_no, desc):
    day,hour,min,location = getTimeslotData(ts)
    start_date=convertDate(day,week_no,str(int(hour)),min)
    end_date=convertDate(day,week_no,str(int(hour)+1),min)
    temp_ics=read_ics_template_body()
    temp_ics = temp_ics.replace("<START_DATE>",start_date + "Z",1)
    temp_ics = temp_ics.replace("<END_DATE>",end_date + "Z",1)
    temp_ics = temp_ics.replace("<TENNIS MATCH>",info,1)
    temp_ics = temp_ics.replace("<TENNIS LOCATION>",location,1)
    temp_ics = temp_ics.replace("<TENNIS DESC>",desc,1)
    temp_ics = temp_ics.replace("<TENNIS ALARM DESC>",desc,1)
    return temp_ics



#####################################################################################



def getTSInfo(ts,week_no):
    day,hour,min,location = getTimeslotData(ts)
    start_date=convertDatePrint(day,week_no,hour,min)
    return start_date+" "+ts



#####################################################################################



def handle_rule(str,weeks,timeslots, max):
    mx = [0] * weeks
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
        mx[j]=max
    return x, mx



#####################################################################################



def getException(z):
    first_start=0
    first_end = z.find(",")
    second_start=first_end+1
    second_end=len(z)
    return (z[first_start:first_end],z[second_start:second_end])



#####################################################################################



def handle_exception(slot,str,weeknr, mxp, mx):
    global starting_week
    global ending_week
    ts = [0] * len(str)
    for i in range(len(str)):
        if str[i]!=OPTION_NONE:
            ts[i]=str[i]
        else:
            ts[i]=slot[covertWeekNumberToIndex(weeknr,starting_week,ending_week)][i]
    slot[covertWeekNumberToIndex(weeknr,starting_week,ending_week)]=copy.deepcopy(ts)
    mx[covertWeekNumberToIndex(weeknr,starting_week,ending_week)] = mxp
    return slot, mx



#####################################################################################



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



#####################################################################################



def isIncluded(name, list, elem):
    for i in range(len(list)):
        if list[i] == elem:
            #print "for: "+name+" against "+elem+" in list: "+str(list)
            return True
    return False



#####################################################################################



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
    fh = open("tennis.conf", "r")
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
            rulel,t_pos=read_value(raw[pos:],"rule")
            mxp,rule = get_slot_data(rulel)
            data, mx = copy.deepcopy(handle_rule(rule,weeks,timeslots,mxp))
            players[player_counter]=(data,name,0,[],email,phone, mx)
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
                    mxp,tsl = get_slot_data(x)
                    wnr,ts=getException(tsl)
                    (data,name,t,z,e,f,  mx)=players[player_counter]
                    data, mx2=copy.deepcopy(handle_exception(data,ts,wnr,mxp, mx))
                    players[player_counter]=(data,name,t,z,e,f, mx)
                    pos+=t_pos
                    if not check_next_key(raw[pos:],"exception_week_rule"):
                        break
                    x,t_pos=read_value(raw[pos:],"exception_week_rule")
            if check_next_key(raw[pos:],"incompatible_with"):
                x,t_pos=read_value(raw[pos:],"incompatible_with")
                while t_pos>-1:
                    (data,name,t,z,e,f,mx)=players[player_counter]
                    y=copy.deepcopy(z)
                    y.append(x)
                    players[player_counter] = (data,name,t,y,e,f,mx)
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
            rulel,t_pos=read_value(raw[pos:],"rule")
            mxp,rule = get_slot_data(rulel)
            data, mx = copy.deepcopy(handle_rule(rule,weeks,timeslots, mxp))
            players[player_counter]=(data,name,0,z,email,phone, mx)
            pos+=t_pos
            if check_next_key(raw[pos:],"exception_week_rule"):
                x,t_pos=read_value(raw[pos:],"exception_week_rule")
                while t_pos>-1:
                    mxp,tsl = get_slot_data(x)
                    wnr,ts=getException(tsl)
                    (data,name,t,z,e,f, mx)=players[player_counter]
                    data, mx=copy.deepcopy(handle_exception(data,ts,wnr,mxp, mx))
                    players[player_counter]=(data,name,t,z,e,f, mx)
                    pos+=t_pos
                    if not check_next_key(raw[pos:],"exception_week_rule"):
                        break
                    x,t_pos=read_value(raw[pos:],"exception_week_rule")

            if check_next_key(raw[pos:],"incompatible_with"):
                x,t_pos=read_value(raw[pos:],"incompatible_with")
                while t_pos>-1:
                    (data,name,t,z,e,f,mx)=players[player_counter]
                    y=copy.deepcopy(z)
                    y.append(x)
                    #print name+" "+"incomaptible_with:"+str(z)
                    players[player_counter] = (data,name,t,y,e,f,mx)
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
        #print ts
        wnr,ts=getException(x)
        #print "-------------------------------------------"
        #print wnr
        #print ts
        for k in range (len(ts)):
            if ts[k] == 'l':
                result[covertWeekNumberToIndex(wnr,starting_week,ending_week)][k]=" +++ HOLIDAY: CLOSED +++   "
                #print "weeknr:"+str(covertWeekNumberToIndex(wnr,starting_week,ending_week))+"read:"+wnr+" closed\n"
            if ts[k] == 's':
                result[covertWeekNumberToIndex(wnr,starting_week,ending_week)][k]=" +++ HOLIDAY: AVAILABLE +++"
                #print "weeknr:"+str(covertWeekNumberToIndex(wnr,starting_week,ending_week))+"read:"+wnr+" available\n"
        """
        for i in range(len(players)):
            (data,name,t,z,e,f,mx)=players[i]
            data, mx=copy.deepcopy(handle_exception(data,ts,wnr,"3",mx))
            players[i]=(data,name,t,z,e,f,mx)
        """
        pos+=t_pos
        x,t_pos=read_value(raw[pos:],"sp")
    x,t_pos=read_value(raw,"timeslot_prices")
    price_list = x.split(",")



#####################################################################################



def mark_related_timeslots(slot,week,timeslot):
    #related_ts={0:[0,1,2],1:[0,1,2],2:[0,1,2],4:[4,5],5:[4,5],6:[6,7,8],7:[6,7,8],8:[6,7,8],9:[9,10],10:[9,10]}
    #related_ts={0:[1,2,3],1:[0,2,3],2:[0,1,3],3:[0,1,2],4:[5,6,7,8],5:[4,6,7,8],6:[4,5,7,8],7:[4,5,6,8],8:[4,5,6,7],9:[10],10:[9]}
    related_ts={0:[1,2,3],1:[0,2,3],2:[0,1,3],3:[0,1,2],4:[5,6,7,8,9],5:[4,6,7,8,9],6:[4,5,7,8,9],7:[4,5,6,8,9],8:[4,5,6,7,9],9:[4,5,6,7,8],10:[11],11:[10]}
    if timeslot in related_ts:
        mapped_array=related_ts[timeslot]
        for j in range(len(mapped_array)):
            if slot[week][mapped_array[j]] == OPTION_TRAINING or slot[week][mapped_array[j]] == OPTION_RANKING or slot[week][mapped_array[j]] == OPTION_BOTH:
                slot[week][mapped_array[j]] = SCHEDULE_REST

        if (timeslot == 0 or timeslot == 1 or timeslot == 2) and week > 0:
            if slot[week-1][10] == OPTION_TRAINING or slot[week-1][10] == OPTION_RANKING or slot[week-1][10] == OPTION_BOTH:
                slot[week-1][10] = SCHEDULE_REST
            if slot[week-1][11] == OPTION_TRAINING or slot[week-1][11] == OPTION_RANKING or slot[week-1][11] == OPTION_BOTH:
                slot[week-1][11] = SCHEDULE_REST

        if (timeslot == 10 or timeslot == 11) and week+1 < weeks:
            if slot[week+1][0] == OPTION_TRAINING or slot[week+1][0] == OPTION_RANKING or slot[week+1][0] == OPTION_TRAINING:
                slot[week+1][0] = SCHEDULE_REST
            if slot[week+1][1] == OPTION_TRAINING or slot[week+1][1] == OPTION_RANKING or slot[week+1][1] == OPTION_BOTH:
                slot[week+1][1] = SCHEDULE_REST
            if slot[week+1][2] == OPTION_TRAINING or slot[week+1][2] == OPTION_RANKING or slot[week+1][2] == OPTION_BOTH:
                slot[week+1][2] = SCHEDULE_REST
    return slot



#####################################################################################



def check_week(slot, week, plays):
    global help_low_nr_games
    counter=0
    options_nr=0
    global low_slot_nr
    for i in range(timeslots):
        if slot[week][i]=="T" or slot[week][i]=="R":
            counter+=1
        if slot[week][i]=="T" or slot[week][i]=="R" or slot[week][i]=="2" or slot[week][i]=="4" or slot[week][i]=="6":
            options_nr+=1
    #if (options_nr <= low_slot_nr) or (help_low_nr_games and plays < int(ending_week)-int(starting_week)):
    #    counter -=1
    #print counter
    return counter



#####################################################################################



def match_players(player1,player2,force,ranking,x,y):
    global timeslots
    global weeks
    global result
    comments=""
    if ranking==True:
        comments="#"
        mark=SCHEDULE_RANKING
    else:
        comments=" "
        mark="T"
    (slot1,name1,counter1,incomp1,e1,f1, mx1)=player1
    (slot2,name2,counter2,incomp2,e2,f2, mx2)=player2
    if name1 == name2:
        return (slot1,name1,counter1,incomp1,e1,f1,mx1),(slot2,name2,counter2,incomp2,e1,f2,mx2),False
    if (ranking == False):
        for j in (range(timeslots)):
            for i in range(x,weeks-y):
                if ((slot1[i][j] == OPTION_TRAINING or slot1[i][j] == OPTION_BOTH) and (slot2[i][j] == OPTION_TRAINING or slot2[i][j] == OPTION_BOTH)
                    and result[i][j] == ""
                    and not isIncluded(name1,incomp1,name2) and not isIncluded(name2,incomp2,name1)
                    and check_week(slot1, i, counter1)<int(mx1[i]) and check_week(slot2, i, counter2)<int(mx2[i])) :
                    result[i][j] = '%-2s %-15s - %-15s'  % (comments, name1, name2)
                    counter1 +=1
                    counter2 +=1
                    slot1=mark_related_timeslots(slot1,i,j)
                    slot1[i][j] = mark
                    slot2=mark_related_timeslots(slot2,i,j)
                    slot2[i][j] = mark
                    return (slot1,name1,counter1,incomp1,e1,f1,mx1),(slot2,name2,counter2,incomp2,e2,f2,mx2),True

    if (ranking == True):
        for j in (range(timeslots)):
            for i in range(x,weeks-y):
                if ((slot1[i][j] == OPTION_RANKING or slot1[i][j] == OPTION_BOTH) and (slot2[i][j] == OPTION_RANKING or slot2[i][j] == OPTION_BOTH)
                    and result[i][j] == ""
                    and not isIncluded(name1,incomp1,name2) and not isIncluded(name2,incomp2,name1)
                    and check_week(slot1, i, counter1)<int(mx1[i]) and check_week(slot2, i, counter2)<int(mx2[i])) :
                    result[i][j] = '%-2s %-15s - %-15s'  % (comments, name1, name2)
                    counter1 +=1
                    counter2 +=1
                    slot1=mark_related_timeslots(slot1,i,j)
                    slot1[i][j] = mark
                    slot2=mark_related_timeslots(slot2,i,j)
                    slot2[i][j] = mark
                    return (slot1,name1,counter1,incomp1,e1,f1,mx1),(slot2,name2,counter2,incomp2,e2,f2,mx2),True
        if (force == True):
            for j in (range(timeslots)):
                for i in range(x,weeks-y):
                    if ((slot1[i][j] == OPTION_RANKING or slot1[i][j] == OPTION_BOTH) and (slot2[i][j] == OPTION_TRAINING)
                        and result[i][j] == ""
                        and not isIncluded(name1,incomp1,name2) and not isIncluded(name2,incomp2,name1)
                        and check_week(slot1, i, counter1)<int(mx1[i]) and check_week(slot2, i, counter2)<int(mx2[i])) :
                        result[i][j] = '%-2s %-15s - %-15s'  % (comments, name1, name2)
                        counter1 +=1
                        counter2 +=1
                        slot1=mark_related_timeslots(slot1,i,j)
                        slot1[i][j] = mark
                        slot2=mark_related_timeslots(slot2,i,j)
                        slot2[i][j] = mark
                        return (slot1,name1,counter1,incomp1,e1,f1,mx1),(slot2,name2,counter2,incomp2,e2,f2,mx2),True

    return (slot1,name1,counter1,incomp1,e1,f1,mx1),(slot2,name2,counter2,incomp2,e2,f2,mx2),False



#####################################################################################



def match_players_rand(player1,player2,force,ranking,x,y):
    global timeslots
    global weeks
    global result
    comments=""
    if ranking==True:
        comments="#"
        mark = SCHEDULE_RANKING
    else:
        comments=" "
        mark=SCHEDULE_TRAINING
    (slot1,name1,counter1,incomp1,e1,f1, mx1)=player1
    (slot2,name2,counter2,incomp2,e2,f2, mx2)=player2
    #print(">>>")
    #print (mx1)
    #print (mx2)
    if name1 == name2:
        return (slot1,name1,counter1,incomp1),(slot2,name2,counter2,incomp2),False
    if (ranking == False):
        for q in range(0,200):
            j=random.randint(0, timeslots-1)
            i=random.randint(0+x, weeks-1-y)
            if i!=j:
                if ((slot1[i][j] == OPTION_TRAINING or slot1[i][j] == OPTION_BOTH) and (slot2[i][j] == OPTION_TRAINING or slot2[i][j] == OPTION_BOTH)
                    and result[i][j] == ""
                    and not isIncluded(name1,incomp1,name2) and not isIncluded(name2,incomp2,name1)
                    and check_week(slot1, i, counter1)<int(mx1[i]) and check_week(slot2, i, counter2)<int(mx2[i])) :
                    result[i][j] = '%-2s %-15s - %-15s'  % (comments, name1, name2)
                    counter1 +=1
                    counter2 +=1
                    slot1=mark_related_timeslots(slot1,i,j)
                    slot1[i][j] = mark
                    slot2=mark_related_timeslots(slot2,i,j)
                    slot2[i][j] = mark
                    return (slot1,name1,counter1,incomp1,e1,f1,mx1),(slot2,name2,counter2,incomp2,e2,f2,mx2),True

    if (ranking == True):
        for q in range(0,200):
            j=random.randint(0, timeslots-1)
            i=random.randint(0+x, weeks-1-y)
            if i!=j:
                if ((slot1[i][j] == OPTION_RANKING or slot1[i][j] == OPTION_BOTH) and (slot2[i][j] == OPTION_RANKING or slot2[i][j] == OPTION_BOTH)
                    and result[i][j] == ""
                    and not isIncluded(name1,incomp1,name2) and not isIncluded(name2,incomp2,name1)
                    and check_week(slot1, i, counter1)<int(mx1[i]) and check_week(slot2, i, counter2)<int(mx2[i])) :
                    result[i][j] = '%-2s %-15s - %-15s'  % (comments, name1, name2)
                    counter1 +=1
                    counter2 +=1
                    slot1=mark_related_timeslots(slot1,i,j)
                    slot1[i][j] = mark
                    slot2=mark_related_timeslots(slot2,i,j)
                    slot2[i][j] = mark
                    return (slot1,name1,counter1,incomp1,e1,f1,mx1),(slot2,name2,counter2,incomp2,e2,f2,mx2),True
        if (force == True):
            for q in range(0,200):
                j=random.randint(0, timeslots-1)
                i=random.randint(0+x, weeks-1-y)
                if i!=j:
                    if ((slot1[i][j] == OPTION_BOTH or slot1[i][j] == OPTION_RANKING) and (slot2[i][j] == OPTION_TRAINING)
                        and result[i][j] == ""
                        and not isIncluded(name1,incomp1,name2) and not isIncluded(name2,incomp2,name1)
                        and check_week(slot1, i, counter1)<int(mx1[i]) and check_week(slot2, i, counter2)<int(mx2[i])) :
                        result[i][j] = '%-2s %-15s - %-15s'  % (comments, name1, name2+'(F)')
                        counter1 +=1
                        counter2 +=1
                        slot1=mark_related_timeslots(slot1,i,j)
                        slot1[i][j] = mark
                        slot2=mark_related_timeslots(slot2,i,j)
                        slot2[i][j] = mark
                        return (slot1,name1,counter1,incomp1,e1,f1,mx1),(slot2,name2,counter2,incomp2,e2,f2,mx2),True
            for q in range(0,200):
                j=random.randint(0, timeslots-1)
                i=random.randint(0+x, weeks-1-y)
                if i!=j:
                    if ((slot1[i][j] == OPTION_TRAINING) and (slot2[i][j] == OPTION_RANKING or slot2[i][j] == OPTION_BOTH)
                        and result[i][j] == ""
                        and not isIncluded(name1,incomp1,name2) and not isIncluded(name2,incomp2,name1)
                        and check_week(slot1, i, counter1)<int(mx1[i]) and check_week(slot2, i, counter2)<int(mx2[i])) :
                        result[i][j] = '%-2s %-15s - %-15s'  % (comments, name1+'(F)', name2)
                        counter1 +=1
                        counter2 +=1
                        slot1=mark_related_timeslots(slot1,i,j)
                        slot1[i][j] = mark
                        slot2=mark_related_timeslots(slot2,i,j)
                        slot2[i][j] = mark
                        return (slot1,name1,counter1,incomp1,e1,f1,mx1),(slot2,name2,counter2,incomp2,e2,f2,mx2),True
            for q in range(0,200):
                j=random.randint(0, timeslots-1)
                i=random.randint(0+x, weeks-1-y)
                if i!=j:
                    if ((slot1[i][j] == OPTION_TRAINING) and (slot2[i][j] == OPTION_TRAINING)
                        and result[i][j] == ""
                        and not isIncluded(name1,incomp1,name2) and not isIncluded(name2,incomp2,name1)
                        and check_week(slot1, i, counter1)<int(mx1[i]) and check_week(slot2, i, counter2)<int(mx2[i])) :
                        result[i][j] = '%-2s %-15s - %-15s'  % (comments, name1+'(F)', name2+'(F)')
                        counter1 +=1
                        counter2 +=1
                        slot1=mark_related_timeslots(slot1,i,j)
                        slot1[i][j] = mark
                        slot2=mark_related_timeslots(slot2,i,j)
                        slot2[i][j] = mark
                        return (slot1,name1,counter1,incomp1,e1,f1,mx1),(slot2,name2,counter2,incomp2,e2,f2,mx2),True

    return (slot1,name1,counter1,incomp1,e1,f1,mx1),(slot2,name2,counter2,incomp2,e2,f2,mx2),False



#####################################################################################



def handle_group(first,last):
    global ranking_failure_counter
    global ranking_failure_report
    global weeks_before_ranking
    global weeks_after_ranking
    for i in  range(first, last+1):
        for j in range(i+1, last+1):
            players[i],players[j],res = match_players_rand(players[i],players[j],True,True,weeks_before_ranking,weeks_after_ranking)
            if res == False:
                slot1,name1,counter1,incomp1,e1,f1,mx1=players[i]
                slot2,name2,counter2,incomp2,e2,f2,mx2=players[j]
                if isIncluded(name1,incomp1,name2) or isIncluded(name2,incomp2,name1):
                    ranking_failure_report += "    # No ranking between: "+name1+" - "+name2 + " due to incompatibilty" +"\n"
                else:
                    ranking_failure_counter +=1
                    ranking_failure_report += "    # Ranking failure between: "+name1+" - "+name2 + " due to strict rules" +"\n"



#####################################################################################



def handle_rankings():
    for i in range(group_nr):
        a,b=groups[i]
        handle_group(a,b)



#####################################################################################



def getPlayerInGroup(group,index):
    global group_nr
    if (group < group_nr):
        a,b=groups[group]
        if (index>=a and index <= b):
            slot1,name1,counter1,incomp1,e1,f1, mx=players[index]
            return name1
    return ''



#####################################################################################



def handle_training_by_best_effort_random(mode):
    global additional_plays
    limit=weeks+additional_plays
    for x in range(0,200):
        i=random.randint(0, players_nr-1)
        j=random.randint(0, players_nr-1)
        if i!=j:
            slot1,name1,counter1,incomp1,e1,f1, mx1=players[i]
            if counter1 >= limit:
                continue
            slot2,name2,counter2,incomp2,e2,f2, mx2=players[j]
            if counter2 >= limit:
                continue
            players[i],players[j],res = match_players_rand(players[i],players[j],mode,False,0,0)
    return False



#####################################################################################



def handle_training_by_best_effort(mode):
    global additional_plays
    limit=weeks+additional_plays
    for x in range(0,200):
        i=random.randint(0, players_nr-1)
        j=random.randint(0, players_nr-1)
        if i!=j:
            slot1,name1,counter1,incomp1,e1,f1,mx1=players[i]
            if counter1 >= limit:
                continue
            slot2,name2,counter2,incomp2,e2,f2,mx2=players[j]
            if counter2 >= limit:
                continue
            players[i],players[j],res = match_players(players[i],players[j],mode,False,0,0)
    return False



#####################################################################################



def fill_slots():
    for x in range(weeks):
        for y in range(timeslots):
            if result[x][y] == "":
                min = weeks
                min_index = -1
                for i in range(players_nr):
                    slot1,name1,counter1,incomp1,e1,f1,mx1=players[i]
                    if (slot1[x][y] == OPTION_TRAINING or slot1[x][y] == OPTION_RANKING or slot1[x][y] == OPTION_BOTH):
                        if min > counter1:
                            min = counter1
                            min_index = i
                if (min_index != -1):
                    for j in range(players_nr):
                        if (min_index != j):
                            slot2,name2,counter2,incomp2,e2,f2,mx2=players[j]
                            if (slot2[x][y] == OPTION_TRAINING or slot2[x][y] == OPTION_RANKING or slot2[x][y] == OPTION_BOTH):
                                players[min_index],players[j],res = match_players_rand(players[min_index],players[j],False,False,0,0)



#####################################################################################



def getPlayerStats(opt_slot, sched_slot):
    rank_option = 0
    training_option = 0
    pure_training_option = 0
    rankings_scheduled = 0
    training_scheduled = 0
    rest_rule = 0;
    pure_training_option = 0
    ranking_when_both = 0
    for x in range(weeks):
        for y in range(timeslots):
            if (opt_slot[x][y] == OPTION_TRAINING  or opt_slot[x][y] == OPTION_BOTH):
                training_option += 1
            if (opt_slot[x][y]== OPTION_RANKING or opt_slot[x][y] == OPTION_BOTH):
                rank_option += 1
            if (sched_slot[x][y] == SCHEDULE_RANKING):
                rankings_scheduled += 1
            if (sched_slot[x][y] == SCHEDULE_TRAINING):
                training_scheduled += 1
            if (sched_slot[x][y] == SCHEDULE_REST):
                rest_rule += 1
            if (sched_slot[x][y] == SCHEDULE_RANKING and (opt_slot[x][y] == OPTION_BOTH)):
               ranking_when_both += 1
            if (sched_slot[x][y] != SCHEDULE_REST and (opt_slot[x][y] == OPTION_TRAINING  or opt_slot[x][y] == OPTION_BOTH)):
               pure_training_option += 1
    return rank_option, training_option, rankings_scheduled, training_scheduled, rest_rule, pure_training_option-ranking_when_both



#####################################################################################



def raiseLowestCoefPlayers(lowLimCoef):
    ordered = []
    for i in range(players_nr):
        sched_slot,name,counter,incomp,e,f,mx=players[i]
        opt_slot,name,counter,incomp,e,f, mx=players_orig[i]
        rank_option, training_option, rankings_scheduled, training_scheduled, rest_rule, training_option = getPlayerStats(opt_slot, sched_slot)
        if (training_option != 0):
            ordered.append( (name,float(100*(training_scheduled))/(training_option)) )
        else:
            ordered.append( (name, float(100)) )
    #print ordered

    for i in range(players_nr):
        for j in range(players_nr):
            (a_name, a_coef) = ordered[i]
            (b_name, b_coef) = ordered[j]
            if (a_coef<b_coef):
                (t_name,t_coef) = ordered[j]
                ordered[j] = ordered[i]
                ordered[i] = (t_name,t_coef)

    for i in range(players_nr):
        (t_name,t_coef)=ordered[i]
        if (t_coef>lowLimCoef):
            return
        for j in range(players_nr):
            sched_slot,name,counter,incomp,e,f,mx=players[j]
            if (t_name == name):
                 for k in range(players_nr):
                        if (j != k):
                            players[j],players[k],res = match_players(players[j],players[k],False,False,0,0)
                            if (res==True):
                                sched_slot,namek,counter,incomp,e,f,mx=players[k]
                                #print(name + str(t_coef )+ "-" + namek+"\n")



#####################################################################################



def raiseLowestSlotPlayers(lowSlotNr):
    ordered = []
    for i in range(players_nr):
        sched_slot,name,counter,incomp,e,f,mx=players[i]
        opt_slot,name,counter,incomp,e,f,mx=players_orig[i]
        rank_option, training_option, rankings_scheduled, training_scheduled, rest_rule, training_option = getPlayerStats(opt_slot, sched_slot)
        if (training_option != 0):
            ordered.append( (name, float(rank_option + training_option-rest_rule)))
        else:
            ordered.append( (name, float(100)) )


    for i in range(players_nr):
        for j in range(players_nr):
            (a_name, a_coef) = ordered[i]
            (b_name, b_coef) = ordered[j]
            if (a_coef<b_coef):
                (t_name,t_coef) = ordered[j]
                ordered[j] = ordered[i]
                ordered[i] = (t_name,t_coef)

    for i in range(players_nr):
        (t_name,t_coef)=ordered[i]
        if (t_coef>lowSlotNr):
            return
        for j in range(players_nr):
            sched_slot,name,counter,incomp,e,f,mx=players[j]
            if (t_name == name):
                 for k in range(players_nr):
                        if (j != k):
                            players[j],players[k],res = match_players(players[j],players[k],False,False,0,0)
                            #if (res==True):
                                #sched_slot,namek,counter,incomp,e,f,mx=players[k]
                                #print(name + str(t_coef )+ "-" + namek+"\n")



#####################################################################################



def getLowestPlayerNr():
    min = 100
    for i in range(players_nr):
        sched_slot,name,counter,incomp,e,f,mx=players[i]
        opt_slot,name,counter,incomp,e,f, mx=players_orig[i]
        rank_option, training_option, rankings_scheduled, training_scheduled, rest_rule, pure_training_option = getPlayerStats(opt_slot, sched_slot)
        if (pure_training_option > 0):
            if ( rankings_scheduled + training_scheduled < min):
                min = rankings_scheduled + training_scheduled
    return min



#####################################################################################



def getAveragePercent():
    sum=0
    ctr=0
    for i in range(players_nr):
        sched_slot,name,counter,incomp,e,f,mx=players[i]
        opt_slot,name,counter,incomp,e,f, mx=players_orig[i]
        rank_option, training_option, rankings_scheduled, training_scheduled, rest_rule, pure_training_option = getPlayerStats(opt_slot, sched_slot)
        if (pure_training_option > 0):
            ctr += 1
            ratio = float((100*(training_scheduled))/(pure_training_option))
            #print (ratio)
            sum += ratio
    #print "----"
    if (ctr>0):
        return float(sum/ctr)
    else:
        return 0



#####################################################################################



def getMinimumPercent():
    minimum = float(100)
    for i in range(players_nr):
        sched_slot,name,counter,incomp,e,f,mx=players[i]
        opt_slot,name,counter,incomp,e,f, mx=players_orig[i]
        rank_option, training_option, rankings_scheduled, training_scheduled, rest_rule, pure_training_option = getPlayerStats(opt_slot, sched_slot)
        if (training_option > 0):
            ratio = float((100*(training_scheduled))/(training_option))
            if (minimum > ratio):
                minimum = ratio
    return minimum



#####################################################################################



def count_unused_timeslots():
    global result
    counter=0
    for i in range(weeks):
        for j in range(timeslots):
            if result[i][j] == "" :
                counter += 1
    return counter



#####################################################################################



def analyze():
    global result
    min=1000
    max=0
    for i in range(0,players_nr):
        slot,name,counter,incomp,e,f,mx=players[i]
        if min >  counter:
            min = counter
        if max <  counter:
            max = counter
    return max,min



#####################################################################################



def readInput(text):
    print text
    # raw_input returns the empty string for "enter"
    yes = {'yes','y', 'ye', ''}
    no = {'no','r'}
    try:
        choice = raw_input()

        if choice in yes:
            return True
        elif choice in no:
            return False
        else:
            sys.stdout.write("Please respond with 'yes' or 'no'")   
    except:
        print "."



#####################################################################################



import time
from threading import Thread
def thread_func(i):
    global stop
    global pause
    while 1:
        #print 'Press <ENTER> to if result is good enough'
        try:
            raw_input("")
        except (EOFError):
            break
        pause = True
        handleResult(False)
        if stop:
            return



#####################################################################################



def thread_start():
    t = Thread(target=thread_func, args=(0,))
    t.start()



#####################################################################################



def handleResult(last):
    global stop
    global pause
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
    global stored_ranking_failure_counter
    global ranking_failure_report
    global cycles_used
    global stored_result
    global stored_analyze
    global stored_players
    global price_list
    global starting_week
    global ending_week
    global help_low_nr_games
    global max_play_per_week
    global max_slots_left
    global max_diff_between_most_and_least_plays
    global max_cycles
    global low_slot_nr
    global additional_plays
    global weeks_before_ranking
    global weeks_after_ranking
    global help_low_nr_games
    global locked

    players_payment = []
    players_payment_ctr = 0

    if locked:
        return
    else:
        locked = True

    if stop:
        print ".."
        exit(0)

    print ""
    #after loop, prepare results
    result= copy.deepcopy(stored_result)
    players=copy.deepcopy(stored_players)
    ranking_failure_counter = stored_ranking_failure_counter
    ranking_failure_report = stored_ranking_failure_report
    max, min, unused_slots, best_cycle = stored_analyze
    #prezent the results
    to_print = ''
    common_part_print=command_line_parameters + result_txt

    common_part_print = common_part_print +  ("\n\n\n\n\n\n\n\n")
    common_part_print = common_part_print +  ("Player groups:=============================================================================") + "\n"
    for i in range(group_nr):
        a,b=groups[i]
        common_part_print = common_part_print +  ("--------- ranking group: "+str(i+1)+"  ----------------------------------------------------------") + "\n"
        for j in range(a,b+1):
            slot,name,counter,incomp,e,f,mx=players[j]
            common_part_print = common_part_print +  ('%-20s  %-50s  %-20s' % (name,e,f)) + "\n"
    common_part_print = common_part_print +  ("--------- training group: ------------------------------------------------------------") + "\n"
    for i in range(b+1,players_nr):
        slot,name,counter,incomp,e,f,mx=players[i]
        common_part_print = common_part_print +  ('%-20s  %-50s  %-20s' % (name,e,f)) + "\n"
    common_part_print = common_part_print +  ("===========================================================================================") + "\n"
    common_part_print = common_part_print +  ("* - Player is not Ericsson employee") + "\n"


    common_part_print = common_part_print +  ("\n\n\n\n\n\n\n\n")


    for i in range(weeks):
        common_part_print = common_part_print + ("========= week: "+str("%02d" % convertIndexToWeekNumber(i,starting_week,ending_week))+"  ==========================================================") + "\n"
        for j in range(timeslots):
            if result[i][j]:
                text=result[i][j]
            else:
                text=" +++ UNUSED : AVAILABLE +++"
            common_part_print = common_part_print +  ('%-36s  %-40s' % (text, getTSInfo(tsdata[j], str(convertIndexToWeekNumberMachine(i,starting_week,ending_week))) )) + "\n"
    common_part_print = common_part_print + ("==============================================================================") + "\n"


    common_part_print = common_part_print +  ("\n\n\n\n===Available timeslots============================") + "\n"

    for i in range(weeks):
        common_part_print = common_part_print + ("week: "+str("%02d" % convertIndexToWeekNumber(i,starting_week,ending_week))+" --------------------------------------") + "\n"
        for j in range(timeslots):
            if (result[i][j] == ""):
                text=""
                formatted_price = (" base price/player: EUR %.2f" % (float(price_list[j])))
                common_part_print = common_part_print +  ('%-0s  %-40s %-20s' % (text, getTSInfo(tsdata[j], str(convertIndexToWeekNumberMachine(i,starting_week,ending_week))) ,formatted_price)) +"\n"
    common_part_print = common_part_print + ("=======================================================") + "\n"



    common_part_print = common_part_print +  ("\n\n\n\n\n\n\n\n")



    common_part_print = common_part_print +  ("Rankings===============================") + "\n"
    for group in range(group_nr):
        common_part_print = common_part_print + ("Group "+str(group+1)) + "\n"
        for index in range(players_nr):
            name = getPlayerInGroup(group,index)
            if name:
                for i in range(weeks):
                    for j in range(timeslots):
                        if result[i][j].find('#')>=0 and result[i][j].find( name )>=0:
                            text=result[i][j]
                            text=text.replace('          ','',1000)
                            text=text.replace('         ','',1000)
                            text=text.replace('        ','',1000)
                            text=text.replace('       ','',1000)
                            text=text.replace('      ','',1000)
                            text=text.replace('     ','',1000)
                            text=text.replace('    ','',1000)
                            text=text.replace('   ','',1000)
                            text=text.replace('  ','',1000)
                            text=text.replace(' ','',1000)
                            text=text.replace('#','',1000)
                            text=text.replace('-',',',1000)
                            text=text.replace('(F)','',1000)
                            text=text.replace('*','',1000)
                            if (common_part_print.find(text) < 0):
                                common_part_print = common_part_print +  ('%s' % (text)) + "\n"
    common_part_print = common_part_print + ("=======================================") + "\n"



    to_print = to_print + common_part_print
    os.system("rm -rf out")
    for i in range(players_nr):
        own_schedule_print=''
        price = 0
        slot,name,counter,incomp,e,f,mx=players[i]
        ics=read_ics_template_header()
        own_schedule_print = own_schedule_print + ("\n\n\n\n\n\n\n")
        own_schedule_print = own_schedule_print + ('=======  %s  plays %d times =============================================' % (name, counter)) + "\n"
        for x in range(weeks):
            own_schedule_print = own_schedule_print + ('w%02d:' % ((convertIndexToWeekNumber(x,starting_week,ending_week)))) + "\n"
            for y in range(timeslots):
                if slot[x][y] == SCHEDULE_RANKING or slot[x][y] == SCHEDULE_TRAINING:
                    own_schedule_print = own_schedule_print + ('%-36s  %-40s' % (result[x][y], getTSInfo(tsdata[y], str(convertIndexToWeekNumberMachine(x,starting_week,ending_week)) ))) + "\n" 
                    if slot[x][y] == SCHEDULE_RANKING:
                        ics+=addToICS(result[x][y], tsdata[y], str(convertIndexToWeekNumberMachine(x,starting_week,ending_week)), "Ranking Match")
                    else:
                        ics+=addToICS(result[x][y], tsdata[y], str(convertIndexToWeekNumberMachine(x,starting_week,ending_week)), "Training Match")
                    #price += float(price_list[y])
        ics+=read_ics_template_footer()
        ics=ics.replace(' ','',1000)
        if not os.path.exists("out"):
            os.makedirs("out")
        fname=name.replace('*','',1000)
        f=open('./out/'+fname+".ics", 'w+')
        f.write(ics)
        f.close()
        #print ics
        (slot1,name1,counter1,incomp1,e1,f1,mx1)=players_orig[i]
        (slot2,name1,counter1,incomp1,e1,f1,mx2)=players[i]
        own_schedule_print = own_schedule_print +('\n\n\n     Schedule vs. preferences:-----------------------------------\n')
        poss = 0
        avoid = 0
        own_schedule_print += ("    |Mon |Mon |Mon |Tue |Thu |Thu |Thu |Fri |Fri |Fri |Sun |Sun |\n")
        own_schedule_print += ("    |Mart|Mart|Mart|Olar|Mart|Mart|Meil|Mart|Mart|Mart|Mart|Mart|\n")
        own_schedule_print += ("    |1930|2030|2100|2000|700 |2000|2000|1930|2030|2130|1900|2000|")
        own_schedule_print = own_schedule_print +('\n     ------------------------------------------------------------')
        training_nr = 0
        ranking_nr = 0
        training_poss = 0
        ranking_when_both = 0
        for x in range(weeks):
            own_schedule_print = own_schedule_print+ "\n" +("w%02d:" % convertIndexToWeekNumber(x,starting_week,ending_week))
            play_count_per_week = 0
            options_per_week = 0
            for y in range(timeslots):
                    if ((slot2[x][y] != SCHEDULE_REST) and (slot1[x][y] == OPTION_TRAINING or slot1[x][y] == OPTION_BOTH)):
                        training_poss += 1
                    if (slot1[x][y] == OPTION_TRAINING or slot1[x][y] == OPTION_RANKING or slot1[x][y] == OPTION_BOTH):
                        poss += 1
                        options_per_week += 1
                    if (slot1[x][y] == OPTION_NONE or slot1[x][y] == OPTION_NO_PLAY or slot1[x][y] == OPTION_NO_TRAINING or slot1[x][y] == OPTION_NO_RANKING or slot1[x][y] == OPTION_NO_BOTH):
                        if (slot2[x][y] == SCHEDULE_RANKING):
                            z = 'R/-'
                        else:
                            z = '   '
                    else:
                        pref = "B"
                        if (slot1[x][y] == OPTION_TRAINING):
                            pref = SCHEDULE_TRAINING
                        if (slot1[x][y] == OPTION_RANKING):
                            pref = SCHEDULE_RANKING
                        chosen = ""
                        if (slot2[x][y] == SCHEDULE_TRAINING):
                                chosen = SCHEDULE_TRAINING
                                training_nr += 1
                        if (slot2[x][y] == SCHEDULE_RANKING):
                                chosen = SCHEDULE_RANKING
                                ranking_nr += 1
                        if (slot2[x][y] == SCHEDULE_RANKING and slot1[x][y] == OPTION_BOTH):
                                ranking_when_both += 1
                        if (slot2[x][y] == SCHEDULE_TRAINING or slot2[x][y] == SCHEDULE_RANKING):
                            z = chosen + '/' + pref
                            play_count_per_week += 1
                        else:
                            if (slot2[x][y] == SCHEDULE_REST):
                                z = '!/' + pref
                                avoid += 1;
                            else:
                                z = '-/' + pref
                    own_schedule_print = own_schedule_print+('|') +(z)+(' ')
            own_schedule_print = own_schedule_print + ("| ") +str(play_count_per_week)+("/")+ str(options_per_week)+("/")+mx1[x]
        own_schedule_print = own_schedule_print +('\n     ------------------------------------------------------------')
        own_schedule_print = own_schedule_print +('\n     sched/pref - per timeslot       | sched_nr/pref_nr/max_nr - per week')
        own_schedule_print = own_schedule_print +('\n                ! = resting rule  ' + SCHEDULE_RANKING + ' = ranking  ' + SCHEDULE_TRAINING + ' = training ' + OPTION_BOTH + ' = both')

        #own_schedule_print = own_schedule_print +("\n     slot usage(used vs all preferences): %d" % counter) +'/'+("%d" % poss)+' = '+("%.1f" % (100*(float(counter) / float(poss))) )+' %'
        #own_schedule_print = own_schedule_print +("\n     slot usage(used vs all preferences minus resting rule): %d" % counter) +'/'+("%d" % (poss - avoid))+' = '+("%.1f" % (100*(float(counter) / float(poss - avoid))) )+' %'
        if(training_poss>0):
                                        own_schedule_print = own_schedule_print +("\n     slot usage(training vs ning real possibilities): %d" % training_nr) +'/'+("%d" % (training_poss-ranking_when_both))+' = '+("%.1f" % (100*(float(training_nr) / float(training_poss-ranking_when_both))) )+' %'
        own_schedule_print = own_schedule_print +('\n\n\n')

        own_schedule_print = own_schedule_print +('\n     Payments:---------------------------------------------------') + "\n"
        own_schedule_print += ("    |Mon |Mon |Mon |Tue |Thu |Thu |Thu |Fri |Fri |Fri |Sun |Sun |\n")
        own_schedule_print += ("    |Mart|Mart|Mart|Olar|Mart|Mart|Meil|Mart|Mart|Mart|Mart|Mart|\n")
        own_schedule_print += ("    |1930|2030|2100|2000|700 |2000|2000|1930|2030|2130|1900|2000|\n")
        own_schedule_print = own_schedule_print +('     ------------------------------------------------------------\n')
        for x in range(weeks):
            own_schedule_print = own_schedule_print +("w%02d:" % convertIndexToWeekNumber(x,starting_week,ending_week))
            for y in range(timeslots):
                if slot[x][y] == SCHEDULE_RANKING or slot[x][y] == SCHEDULE_TRAINING:
                    own_schedule_print = own_schedule_print + ('|') + price_list[y]
                    price += float(price_list[y])
                else:
                    own_schedule_print = own_schedule_print +('|    ')
                #own_schedule_print = own_schedule_print +(' ')
            own_schedule_print = own_schedule_print +('|\n')
        own_schedule_print = own_schedule_print +('     ------------------------------------------------------------\n')
        if name.find('*')>=0:
            new_price = price*2
            own_schedule_print = own_schedule_print + ('     Total pay:'+str(price)+ ' x 2 = '+str(new_price)+' Euros') + "\n"
            players_payment.append( (name, new_price))
        else:
            own_schedule_print = own_schedule_print + ('     Total pay:'+str(price)+ ' Euros') + "\n"
            players_payment.append( (name, price))
        to_print = to_print + own_schedule_print
        f=open('./out/'+fname+".txt", 'w+')
        f.write( own_schedule_print + common_part_print + ("\n\n\n © Levente Varga 2018"))
        f.close()

    to_print = to_print +('\n-Payments:------------------------------------------------------') + "\n"
    for x in range(len(players_payment)):
        name, val = players_payment[x]
        to_print = to_print +('%-20s  %-5s %-0s' % (name , str(val)," EUR\n"))
    to_print = to_print +('---------------------------------------------------------------') + "\n"

    to_print = to_print + ('\n===============================================================') + "\n"

    report_to_print=''
    report_to_print = report_to_print + ("Report: ") + '\n'
    report_to_print = report_to_print +  ("   ranking failures: "+str(ranking_failure_counter)) + '\n'
    report_to_print = report_to_print +  (ranking_failure_report) + '\n'
    report_to_print = report_to_print +  ("   unused slots:     "+str(unused_slots)) + '\n'
    report_to_print = report_to_print +  ("   diff most/least:  "+str(max - min)) + '\n'
    report_to_print = report_to_print +  ("   max plays:        "+str(max)) + '\n'
    report_to_print = report_to_print +  ("   min plays:        "+str(min)) + '\n'
    report_to_print = report_to_print +  ("   cycles used:      "+str(cycles_used)) + '\n'
    report_to_print = report_to_print +  ("   cycles max:       "+str(max_cycles)) + '\n'
    report_to_print = report_to_print +  '\n'
    report_to_print = report_to_print +  ("© Levente Varga 2018") + '\n'

    print report_to_print

    to_print = to_print + report_to_print

    f=open('./out/'+"common"+".txt", 'w+')
    f.write(to_print)
    f.close()

    if readInput('Are you satisfied with the results? [Y/n] ') :
        stop = True
        out_folder="out_"+starting_week+"-"+ending_week
        out_folder_pub=out_folder+"_pub"
        os.system("cp -rf out "+out_folder_pub)
        os.system("cp tennis.conf out/")
        os.system("cp -rf out "+out_folder)
        os.system("rm  -rf "+out_folder+".zip "+out_folder_pub+".zip")
        os.system("unix2dos -q "+ out_folder +"/*.txt")
        os.system("unix2dos -q "+ out_folder_pub +"/*.txt")
        os.system("unix2dos -q "+ "out" +"/*.txt")
        os.system("zip -rq "+out_folder_pub+".zip "+out_folder_pub)
        os.system("zip -rq "+out_folder+".zip "+out_folder)
        os.system("rm  -rf "+out_folder+" "+out_folder_pub)
        pause = False
        print "results saved to "+out_folder+".zip "+out_folder_pub+".zip" + " and "+ out_folder_pub+".zip "+out_folder_pub
        if last:
            print ".."
            exit(0)
    else:
        if last:
            print "."
            exit(0)
        pause = False
    locked = False



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
    global pause
    global locked
    global command_line_parameters
    global result_txt
    global timeslots
    global weeks
    global raw
    global group_nr
    global players_nr
    global players
    global players_orig
    global a
    global groups
    global tsdata
    global result
    global unused_slots
    global diff_most_least
    global ranking_failure_counter
    global ranking_failure_report
    global stored_ranking_failure_counter
    global stored_ranking_failure_report
    global stored_result
    global cycles_used
    global stored_analyze
    global stored_players
    global price_list
    global starting_week
    global ending_week
    global help_low_nr_games


    locked = False
    stop = False
    pause = False
    #default settings
    max_play_per_week = 1
    max_slots_left = 0
    max_diff_between_most_and_least_plays=2
    max_cycles=500
    low_slot_nr=0
    additional_plays=0
    weeks_before_ranking=1
    weeks_after_ranking=1
    if len(sys.argv) > 1 and (sys.argv[1]=="help" or sys.argv[1]=="-h" or sys.argv[1]=="--help"):
            print ("Usage:")
            print ("python "+sys.argv[0]+" max_plays_per_week=1 low_slot_nr=5 additional_plays=0 max_cycles=5000 weeks_before_ranking=1 weeks_after_ranking=1")
            exit(0)
    print ("max_cycles="+str(max_cycles))
    print ("max_plays_per_week="+str(max_play_per_week))
    print ("low_slot_nr="+str(low_slot_nr))
    print ("additional_plays="+str(additional_plays))
    print ("weeks_before_ranking="+str(weeks_before_ranking))
    print ("weeks_after_ranking="+str(weeks_after_ranking))
    print ('-----------------')

    command_line_parameters = "Command used:\npython tennis.py"

    #read command line parameters
    for i in range(len(sys.argv)):
        val,t_pos =read_pair(sys.argv[i], "max_cycles")
        if val:
            max_cycles = int(val)
            print ("override max_cycles="+str(max_cycles))
            command_line_parameters = command_line_parameters + " " + ("max_cycles="+str(max_cycles))
            continue

        val,t_pos =read_pair(sys.argv[i], "max_plays_per_week")
        if val:
            max_play_per_week = int(val)
            print ("override max_plays_per_week="+str(max_play_per_week))
            command_line_parameters = command_line_parameters + " " + ("max_plays_per_week="+str(max_play_per_week))
            continue

        val,t_pos =read_pair(sys.argv[i], "low_slot_nr")
        if val:
            low_slot_nr = int(val)
            print ("override low_slot_nr="+str(low_slot_nr))
            command_line_parameters = command_line_parameters + " " + ("low_slot_nr="+str(low_slot_nr))
            continue

        val,t_pos =read_pair(sys.argv[i], "additional_plays")
        if val:
            additional_plays = int(val)
            print ("override additional_plays="+str(additional_plays))
            command_line_parameters = command_line_parameters + " " + ("additional_plays="+str(additional_plays))
            continue

        val,t_pos =read_pair(sys.argv[i], "weeks_before_ranking")
        if val:
            weeks_before_ranking = int(val)
            print ("override weeks_before_ranking="+str(weeks_before_ranking))
            command_line_parameters = command_line_parameters + " " + ("weeks_before_ranking="+str(weeks_before_ranking))
            continue

        val,t_pos =read_pair(sys.argv[i], "weeks_after_ranking")
        if val:
            weeks_after_ranking = int(val)
            print ("override weeks_after_ranking="+str(weeks_after_ranking))
            command_line_parameters = command_line_parameters + " " + ("weeks_after_ranking="+str(weeks_after_ranking))
            continue


    sys.stdout.write("\nStarted:")
    sys.stdout.flush()
    cycles_used=0
    best = -1000
    best_index = 0
    best_cycle = 0
    counter=0

    thread_start()
    print ""
    base = ""
    while(cycles_used < max_cycles):
        timeslots = 0
        weeks = 0
        raw=""
        group_nr=0

        help_low_nr_games=0
        #read configuration
        pre_read_config()
        read_config()
        players_orig=copy.deepcopy(players)
        #handle ranking matches

        for i in range(2):
            raiseLowestSlotPlayers(20)

        ranking_failure_counter = 0
        ranking_failure_report = ""
        handle_rankings()

        for i in range(2):
            raiseLowestSlotPlayers(50)

        for i in range(10):
            raiseLowestCoefPlayers(30)

        if (cycles_used % 2 == 0):
            orig_low_slot_nr = low_slot_nr
            low_slot_nr = 0
            handle_training_by_best_effort_random(False)
            #help_low_nr_games=1
            #handle_training_by_best_effort_random(False)
            #low_slot_nr = orig_low_slot_nr
            #handle_training_by_best_effort_random(False)
        else:
            orig_low_slot_nr = low_slot_nr
            low_slot_nr = 0
            #handle_training_by_best_effort(False)
            #help_low_nr_games=1
            #handle_training_by_best_effort(False)
            #low_slot_nr = orig_low_slot_nr
            #handle_training_by_best_effort(False)

        for i in range(5):
            raiseLowestCoefPlayers(30)
        for i in range(5):
            fill_slots()

        #collect statitistical data
        unused_slots = count_unused_timeslots()
        max,min=analyze()
        min = getLowestPlayerNr()
        diff_most_least = max-min
        #store best result so far
        percent = getAveragePercent()


        equiv = (min*10 - unused_slots*10 - max*1 - 100*ranking_failure_counter + percent)


        if best < equiv:
            best = equiv
            stored_result=copy.deepcopy(result)
            stored_players=copy.deepcopy(players)
            stored_ranking_failure_counter = ranking_failure_counter
            stored_ranking_failure_report = ranking_failure_report
            stored_analyze = max, min, unused_slots, cycles_used
            #sys.stdout.write("("+str(diff_most_least)+"/"+str(unused_slots)+"/"+str(min)+"/"+str(ranking_failure_counter)+")")
            base = " ("+str(diff_most_least)+"/"+str(unused_slots)+"/"+str(min)+"/"+str(ranking_failure_counter)+")"
            result_txt = " diff: %-2d unused: %-2d min: %-2d max: %-2d percent: %.2f rank_fail: %-2d score: %-3d " % (diff_most_least, unused_slots, min, max, percent, ranking_failure_counter, equiv)
            base = result_txt
            result_txt = ("\nresult: ") + result_txt + ("\n")
        else:
            counter = counter + 1
            '''
            perc = "["+str("%  d" % (int(100*counter/max_cycles)))+'%]'
            sys.stdout.write(perc)
            for i in range(len(perc)):
                sys.stdout.write('\b')
            sys.stdout.flush()
            '''
            perc = base
            perc += '['
            for i in range(30):
                if i < int(30*counter/max_cycles)+1:
                    perc +='*'
                else:
                    perc +=' '
            perc +=']     '
            sys.stdout.write(perc)
            for i in range(len(perc)):
                sys.stdout.write('\b')
            sys.stdout.flush()

        cycles_used = cycles_used + 1
        while (pause):
            time.sleep(0.1)
        if stop:
            print "......."
            exit(0)
    handleResult(True)



#####################################################################################
#####################################################################################
#####################################################################################
#####################################################################################
#####################################################################################



killOtherInstances()
main()
