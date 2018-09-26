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
    players_nr=0
    fh = open("tennis.conf", "r")
    raw = fh.read()
    raw=raw.replace('\r\n','\n',1000)
    raw=handle_comment_lines(raw)
    raw=raw.replace(' ','',1000)
    raw=raw.replace("/\n","//",1000)
    raw=raw.replace("\n\n","\n",1000)
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
    import datetime
    if day == 'Sunday': day='-0'
    if day == 'Monday': day='-1'
    if day == 'Tuesday': day='-2'
    if day == 'Wednesday': day='-3'
    if day == 'Thursday': day='-4'
    if day == 'Friday': day='-5'
    if day == 'Saturday': day='-6'
    t = datetime.datetime.strptime("2018-W"+ week_no + day, "%Y-W%W-%w") + datetime.timedelta(hours=int(hour), minutes=int(min))
    #print(t.__format__("%y%m%dT%H%M%S"))
    return t.__format__("%Y%m%dT%H%M%S")

def getTimeslotData(ts):
    #tts ="Monday_19:30_Martinmaki_R"
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
    #print day+"-"+hour+"-"+min+"-"+location
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
    #print ics+temp_ics
    return temp_ics



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
    ts = [0] * len(str)
    for i in range(len(str)):
        ts[i]=str[i]
    slot[int(weeknr)-base_week]=copy.deepcopy(ts)
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
    tsdata = [""]*timeslots
    #print (group_nr)
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

            name,t_pos=read_value(raw[pos:],"name")
            if (t_pos==-1):
                break
            pos+=t_pos
            player_counter+=1

            rule,t_pos=read_value(raw[pos:],"rule")
            data = copy.deepcopy(handle_rule(rule,weeks,timeslots))
            players[player_counter]=(data,name,0,[])
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
                    (data,name,t,z)=players[player_counter]
                    data=copy.deepcopy(handle_exception(data,ts,wnr))
                    players[player_counter]=(data,name,t,z)
                    pos+=t_pos
                    if not check_next_key(raw[pos:],"exception_week_rule"):
                        break
                    x,t_pos=read_value(raw[pos:],"exception_week_rule")



            if check_next_key(raw[pos:],"incompatible_with"):
                x,t_pos=read_value(raw[pos:],"incompatible_with")
                while t_pos>-1:
                    (data,name,t,z)=players[player_counter]
                    y=copy.deepcopy(z)
                    y.append(x)
                    #print name+" "+"incomaptible_with:"+str(z)
                    players[player_counter] = (data,name,t,y)
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
            name,t_pos=read_value(raw[pos:],"name")
            if t_pos == -1:
                break
            pos+=t_pos
            player_counter+=1
            rule,t_pos=read_value(raw[pos:],"rule")
            data = copy.deepcopy(handle_rule(rule,weeks,timeslots))
            players[player_counter]=(data,name,0,z)
            pos+=t_pos

            if check_next_key(raw[pos:],"exception_week_rule"):
                x,t_pos=read_value(raw[pos:],"exception_week_rule")
                while t_pos>-1:
                    wnr,ts=getException(x)
                    (data,name,t,z)=players[player_counter]
                    data=copy.deepcopy(handle_exception(data,ts,wnr))
                    players[player_counter]=(data,name,t,z)
                    pos+=t_pos
                    if not check_next_key(raw[pos:],"exception_week_rule"):
                        break
                    x,t_pos=read_value(raw[pos:],"exception_week_rule")

            if check_next_key(raw[pos:],"incompatible_with"):
                x,t_pos=read_value(raw[pos:],"incompatible_with")
                while t_pos>-1:
                    (data,name,t,z)=players[player_counter]
                    y=copy.deepcopy(z)
                    y.append(x)
                    #print name+" "+"incomaptible_with:"+str(z)
                    players[player_counter] = (data,name,t,y)
                    pos+=t_pos
                    if not check_next_key(raw[pos:],"incompatible_with"):
                        break
                    x,t_pos=read_value(raw[pos:],"incompatible_with")



def mark_related_timeslots(slot,week,timeslot):
    related_ts={0:[0,1,2],1:[0,1,2],2:[0,1,2],4:[4,5],5:[4,5],6:[6,7,8],7:[6,7,8],8:[6,7,8],9:[9,10],10:[9,10]}
    if timeslot in related_ts:
        mapped_array=related_ts[timeslot]
        for j in range(len(mapped_array)):
            if slot[week][mapped_array[j]]=='c':
                slot[week][mapped_array[j]] = 'b'
    return slot


def check_week(slot, week):
    counter=0
    for i in range(timeslots):
        if slot[week][i]=="T" or slot[week][i]=="R":
            counter+=1
    return counter


def match_players(player1,player2,force,ranking):
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
    (slot1,name1,counter1,incomp1)=player1
    (slot2,name2,counter2,incomp2)=player2
    if name1 == name2:
        return (slot1,name1,counter1,incomp1),(slot2,name2,counter2,incomp2),False
    for j in range(timeslots):
        for i in range(weeks):
            if (slot1[i][j] == 'c' and slot2[i][j] == 'c'
                and result[i][j] == ""
                and not isIncluded(name1,incomp1,name2) and not isIncluded(name2,incomp2,name1)
                and check_week(slot1, i)<max_play_per_week and check_week(slot2, i)<max_play_per_week) :
                result[i][j] = '%-2s %-20s  -  %-20s' % (comments, name1, name2)
                counter1 +=1
                counter2 +=1
                slot1=mark_related_timeslots(slot1,i,j)
                slot1[i][j] = mark
                slot2=mark_related_timeslots(slot2,i,j)
                slot2[i][j] = mark
                return (slot1,name1,counter1,incomp1),(slot2,name2,counter2,incomp2),True
    #print name1+"-"+name2+" no match found"
    if force==True:
        for j in range(timeslots):
            for i in range(weeks):
                if (slot1[i][j] == 'c'
                    and slot2[i][j] != 'R' and slot2[i][j] != 'T' and slot2[i][j] != 'b' and slot2[i][j] != 'a'
                    and result[i][j] == ""
                    and not isIncluded(name1,incomp1,name2) and not isIncluded(name2,incomp2,name1)
                    and check_week(slot1, i)<max_play_per_week and check_week(slot2, i)<max_play_per_week):
                    result[i][j] = '%-2s %-20s  -  %-20s' % (comments, name1, name2+"(F)")
                    counter1 +=1
                    counter2 +=1
                    slot1=mark_related_timeslots(slot1,i,j)
                    slot1[i][j] = mark
                    slot2=mark_related_timeslots(slot2,i,j)
                    slot2[i][j] = mark
                    return (slot1,name1,counter1,incomp1),(slot2,name2,counter2,incomp2),True
        for j in range(timeslots):
            for i in range(weeks):
                if (slot2[i][j] == 'c'
                    and slot1[i][j] != 'R' and slot1[i][j] != 'T' and slot1[i][j] != 'b' and slot1[i][j] != 'a'
                    and result[i][j] == ""
                    and not isIncluded(name1,incomp1,name2) and not isIncluded(name2,incomp2,name1)
                    and check_week(slot1, i)<max_play_per_week and check_week(slot2, i)<max_play_per_week):
                    result[i][j] = '%-2s %-20s  -  %-20s' % (comments, name1+"(F)", name2)
                    counter1 +=1
                    counter2 +=1
                    slot1=mark_related_timeslots(slot1,i,j)
                    slot1[i][j] = mark
                    slot2=mark_related_timeslots(slot2,i,j)
                    slot2[i][j] = mark
                    return (slot1,name1,counter1,incomp1),(slot2,name2,counter2,incomp2),True
        for j in range(timeslots):
            for i in range(weeks):
                if (slot1[i][j] != 'R' and slot1[i][j] != 'T' and slot1[i][j] != 'b' and slot1[i][j] != 'a'
                    and slot2[i][j] != 'R' and slot2[i][j] != 'T' and slot2[i][j] != 'b' and slot2[i][j] != 'a'
                    and result[i][j] == ""
                    and not isIncluded(name1,incomp1,name2) and not isIncluded(name2,incomp2,name1)
                    and check_week(slot1, i)<max_play_per_week and check_week(slot2, i)<max_play_per_week):
                    result[i][j] = '%-2s %-20s  -  %-20s' % (comments, name1+"(F)", name2+"(F)")
                    counter1 +=1
                    counter2 +=1
                    slot1=mark_related_timeslots(slot1,i,j)
                    slot1[i][j] = mark
                    slot2=mark_related_timeslots(slot2,i,j)
                    slot2[i][j] = mark
                    return (slot1,name1,counter1,incomp1),(slot2,name2,counter2,incomp2),True
    #if ranking==True:
    #    print comments+name1+" - "+name2+" FAILURE:"
    return (slot1,name1,counter1,incomp1),(slot2,name2,counter2,incomp2),False


def handle_group(first,last):
    global ranking_failure_counter
    global ranking_failure_report
    for i in range(first, last+1):
        for j in range(i+1, last+1):
            players[i],players[j],res = match_players(players[i],players[j],True,True)
            if res == False:
                slot1,name1,counter1,incomp1=players[i]
                slot2,name2,counter2,incomp2=players[j]
                reason=""
                if isIncluded(name1,incomp1,name2) or isIncluded(name2,incomp2,name1):
                    reason = " due to incompatibilty"
                else:
                    reason = " due to strict rules"
                ranking_failure_report += "    # Ranking failure between: "+name1+" - "+name2 + reason +"\n"
                ranking_failure_counter +=1


def handle_rankings():
    #print groups
    for i in range(group_nr):
        a,b=groups[i]
        handle_group(a,b)


def handle_training_by_best_effort_random(mode):

    limit=2*players_nr/weeks+3
    for x in range(0,1000):
        i=random.randint(0, players_nr-1)
        j=random.randint(0, players_nr-1)
        if i!=j:
            slot1,name1,counter1,incomp1=players[i]
            if counter1 > limit:
                continue
            slot2,name2,counter2,incomp2=players[j]
            if counter2 > limit:
                continue
            players[i],players[j],res = match_players(players[i],players[j],mode,False)
    return False


def count_unused_timeslots():
    global result
    counter=0
    for i in range(weeks):
        for j in range(timeslots):
            if result[i][j] == "" :
                counter += 1
    #print "Unused timeslots: "+ str(counter) +" out of:"+str(weeks*timeslots)
    return counter


def analyze():
    global result
    min=1000
    max=0
    for i in range(0,players_nr):
        slot,name,counter,incomp=players[i]
        if min >  counter and counter > 0:
            min = counter
        if max <  counter:
            max = counter
    return max - min


#####################################################################################
#####################################################################################


def main():

    global max_play_per_week
    global max_slots_left
    global max_diff_between_most_and_least_plays
    global max_cycles

    #default settings
    max_play_per_week = 1
    max_slots_left = 0
    max_diff_between_most_and_least_plays=2
    max_cycles=250

    #read_ics_template()
    #convertDate('Monday', "2018-W39","19","30")
    #getTimeslotData("")
    #addToICS("","PLAYER1-PLAYER2","Monday_19:30_Martinmaki_Right_Court","35","Ranking Match")
    #exit(0)

    print ("max_cycles = "+str(max_cycles))
    print ("max_plays_per_week = "+str(max_play_per_week))
    print ("override max_unused_lots = "+str(max_slots_left))
    print ("max_diff = "+str(max_diff_between_most_and_least_plays))

    #read command line parameters
    for i in range(len(sys.argv)):

        if sys.argv[i]=="help" or sys.argv[i]=="-h" or sys.argv[i]=="--help":
            print ("Usage:")
            print ("python "+sys.argv[0]+" max_cycles=250 max_plays_per_week=2 max_unused_lots=3 max_diff=2")

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

        val,t_pos =read_pair(sys.argv[i], "max_unused_lots")
        if val:
            max_slots_left = int(val)
            print ("override max_unused_lots = "+str(max_slots_left))
            continue

        val,t_pos =read_pair(sys.argv[i], "max_diff")
        if val:
            max_diff_between_most_and_least_plays = int(val)
            print ("override max_diff = "+str(max_diff_between_most_and_least_plays))
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

    sys.stdout.write("\nStarted:")
    sys.stdout.flush()

    cycles_used=0
    best = 100
    best_index = 0
    best_cycle = 0

    while(True):
        timeslots = 0
        weeks = 0
        raw=""
        group_nr=0
        ranking_failure_counter = 0
        ranking_failure_report =""

        #read configuration
        pre_read_config()
        read_config()
        players_orig=copy.deepcopy(players)

        result=copy.deepcopy(a)

        #handle ranking matches
        handle_rankings()

        #handle training matches, respecting player options
        while (True):
            res = handle_training_by_best_effort_random(False)
            if res==False:
                break

        #handle training matches, forcinging player options
        while (True):
            res = handle_training_by_best_effort_random(True)
            if res==False:
                break

        #collect statitistical data
        unused_slots = count_unused_timeslots()
        diff_most_least = analyze()

        #store best result so far
        if best > (diff_most_least + unused_slots):
            best = (diff_most_least + unused_slots)
            stored_result=copy.deepcopy(result)
            stored_players=copy.deepcopy(players)
            stored_analyze = diff_most_least, unused_slots, cycles_used
            sys.stdout.write("("+str(diff_most_least)+"/"+str(unused_slots)+")")
        else:
            sys.stdout.write('-')
        sys.stdout.flush()

        #stop looping if conditions are fulfilled
        if diff_most_least <= max_diff_between_most_and_least_plays and unused_slots <= max_slots_left:
            break
        if cycles_used > max_cycles:
            break
        else:
            cycles_used = cycles_used + 1

    #after loop, prepare results
    result= copy.deepcopy(stored_result)
    players=copy.deepcopy(stored_players)
    diff_most_least, unused_slots, best_cycle = stored_analyze

    #prezent the results
    print ("\n\n\n\n\n\n\n\n")
    print ("--------------------------------------------------------------------------------------------------------")
    for i in range(group_nr):
        a,b=groups[i]
        print ("========= ranking group: "+str(i)+"  ===============================================================")
        for j in range(a,b+1):
            slot,name,counter,incomp=players[j]
            print ('%-20s  %-20s' % (name,"?????"))
    print ("========= training group: =================================================================")
    for i in range(b,players_nr):
        slot,name,counter,incomp=players[i]
        print ('%-20s  %-20s' % (name,"?????"))
    print ("===========================================================================================")

    print ("\n\n\n")

    for i in range(weeks):
        print ("========= week: "+str(i+base_week)+"  ===============================================================")
        for j in range(timeslots):
            if result[i][j]:
                text=result[i][j]
            else:
                text="   AVAILABLE FOR BOOKING  !!!!!!!!!!!!!!        "
            print ('%-35s  %-40s' % (text, tsdata[j]))
    print ("=======================================================================================================")
    
    os.system("rm -rf ics")
    for i in range(players_nr):
        slot,name,counter,incomp=players[i]
        ics=read_ics_template_header()
        print ("\n")
        print ('=======  %s  plays %d times =============================================================' % (name, counter))
        for x in range(weeks):
            print ('------------------------------------------------------------------------------week nr: %d:' % (x+base_week))
            for y in range(timeslots):
                if slot[x][y]=='R' or slot[x][y]=='T':
                    print ('%-35s  %-40s' % (result[x][y], tsdata[y]))
                    if slot[x][y]=='R':
                        ics+=addToICS(result[x][y], tsdata[y], str(x+base_week), "Ranking Match")
                    else:
                        ics+=addToICS(result[x][y], tsdata[y], str(x+base_week), "Training Match")
        ics+=read_ics_template_footer()
        ics=ics.replace(' ','',1000)
        if not os.path.exists("ics"):
            os.makedirs("ics")
        f=open('./ics/'+name+".ics", 'w+')
        f.write(ics)
        f.close()
        #print ics

    print ('=========================================================================================')
    print ("\n\n\n")

    print ("Report: ")
    print ("   ranking failures: "+str(ranking_failure_counter))
    print (ranking_failure_report)
    print ("   unused slots:     "+str(unused_slots))
    print ("   diff most/least:  "+str(diff_most_least))
    print ("   best cycle:       "+str(cycles_used))
    print ("   cycles used:      "+str(cycles_used))
    print ("")
    print (" © Levente Varga 2018")


main()
