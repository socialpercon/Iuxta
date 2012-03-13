import csv, glob, time, random

def tstamp(): return str(int(time.time()))

with open('csvs/automated_users-%s.csv'%(tstamp()), 'wb') as f:
        writer = csv.writer(f, delimiter=',')
        writer.writerow(['User ID', 'Email', 'First Name', 'Last Name'])
        for userNum in xrange(0, 5000):
            writer.writerow([
                    "nd.automated-drone_%d"%(userNum),
                    "nd.automated+drone_%d@gmail.com"%(userNum),
                    "nd.drone_%d"%(userNum),
                    "Automated"])
