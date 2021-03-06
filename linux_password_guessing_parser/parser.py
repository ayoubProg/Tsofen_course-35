from event_line import Event_Line, Event_Report, Event_Type, Attempt_Type
import re
from datetime import datetime



'''
TODO:
1) directory mngmt
2) event types (ftp ssh telnet x username valid/invalid x successful x single ip)
3) database
'''

#log_file_name   = "auth.log"
log_file_name   = "auth.2.log"
#filter_string   = "Failed password"
filter_strings = ["Failed password", "Accepted password"]
timestamp_regex = "^[a-zA-Z]+\s+\d+\s+[\d\:]+"
ip_addr_regex   = "\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}"
#invalid_username_regex = "Failed password for invalid user "
timestamp_re = re.compile(timestamp_regex)
ipaddress_re = re.compile(ip_addr_regex)

#trigger if 10 events in 30 seconds
event_window_secs   = 60
event_trigger_count = 10
event_lines = []

def lineToEventLine(line, filter_string):
  #Setup timestamp of event:
  m  = timestamp_re.search(line)
  dt =  datetime.strptime(m.group(0),'%b  %d %H:%M:%S')\
        .replace(year=datetime.now().year)

  #Parse IP address from line
  m          = ipaddress_re.search(line)
  ipaddress  = m.group(0)

  #Detect event type
  valid_username   = line.find("invalid") == -1
  successful_login = filter_string == "Accepted password"
  attempt_type = Attempt_Type.FAILED_LOGIN
  if valid_username:
    attempt_type = Attempt_Type.FAILED_PASSWORD
  if successful_login:
    attempt_type = Attempt_Type.ACCEPTED_PASSWORD


  el = Event_Line(dt, ipaddress, attempt_type)
  event_lines.append(el)

count = 0
with open(log_file_name) as infile:
    for line in infile:
      for f_string in filter_strings:
        if f_string in line:
          print 'found '+f_string+' in line.'
          count += 1
          #valid_username = line.find("invalid") == -1
          lineToEventLine(line, f_string)
      '''
        if filter_string in line:
          count += 1
          lineToEventLine(line, Event_Type.FAILED_PASSWORD)
          print line
        elif :
          #re.search("", line).start()
      '''
print "Total failed passwords: "+str(count)
print "=====\n"






upper_pointer = 0
lower_pointer = 0
event_report  = None
events_array  = []
deltas_array  = []
event_reports = []
current_event_type = Event_Type.FAIL_WRONG_USER
event_type_line_no = lower_pointer
while lower_pointer < len(event_lines) -1:
  lower_pointer += 1
  delta = (event_lines[lower_pointer].event_time - event_lines[upper_pointer].event_time).total_seconds()
  print "("+str(upper_pointer)+","+str(lower_pointer)+") TYPE: "+str(event_lines[lower_pointer].attempt_type)+". In event: "+str(event_report is not None)
  
  #Check attempt type, compare with current and escalate.
  if  current_event_type == Event_Type.FAIL_WRONG_USER \
      and event_lines[lower_pointer].attempt_type == Attempt_Type.FAILED_PASSWORD:

          current_event_type = Event_Type.FAIL_RIGHT_USER
          event_type_line_no = lower_pointer

  elif current_event_type != Event_Type.SUCCESSFUL_ACCESS \
       and event_lines[lower_pointer].attempt_type == Attempt_Type.ACCEPTED_PASSWORD:

          current_event_type = Event_Type.SUCCESSFUL_ACCESS
          event_type_line_no = lower_pointer

  #print "delta: "+str(delta)+"<="+str(event_window_secs)+" counter: "+str(lower_pointer - upper_pointer)+">="+str(event_trigger_count)



  #Case no event active and event conditions are triggered => Add new event
  if (delta <= event_window_secs) and (lower_pointer - upper_pointer + 1 >= event_trigger_count) and event_report is None:
    event_report = event_lines[upper_pointer]
    events_array.append(event_report)
    print "("+str(upper_pointer)+","+str(lower_pointer)+")"



  #Case no event active and window got larger than defined window
  elif delta > event_window_secs and event_report is None:
    upper_pointer += 1

  #Event over/reset
  elif ((event_lines[lower_pointer].event_time - event_lines[lower_pointer-1].event_time).total_seconds() >= event_window_secs \
        and event_report is not None) \
        or (lower_pointer == len(event_lines)-1 and event_report is not None):
    deltas_array.append((event_lines[lower_pointer-1].event_time - event_lines[upper_pointer].event_time).total_seconds())
    ev = Event_Report(event_lines[upper_pointer], event_lines[lower_pointer-1], current_event_type)
    event_reports.append(ev)
    print 'APPENDINGGGGGGGGGGG'
    event_report = None
    upper_pointer = lower_pointer

  #elif event_report is not None and (event_lines[lower_pointer].event_time - event_lines[lower_pointer-1].event_time).total_seconds() <= event_window_secs:

    #print "upper_pointer += 1"
  

  #print str(delta)+" seconds - ipaddr: "+el.machine_ip_address
  #lower_pointer += 1

for event_report in event_reports:
  print "Event ("+str(event_report.event_type)+"): "+str(event_report.start_line.event_time)+" to "+str(event_report.end_line.event_time)
"""
if event_report is not None:
  print "Event triggered! "+\
        str(lower_pointer - upper_pointer)+\
        " attempts in "+\
        str((event_lines[lower_pointer].event_time - event_lines[upper_pointer].event_time).total_seconds())+\
        " seconds"+\
        " from IP addr: "+str(event_lines[upper_pointer].machine_ip_address)+\
        " at time "+str(event_lines[upper_pointer].event_time)
else:
  print "No events detected"
"""

