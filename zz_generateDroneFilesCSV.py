import csv, glob, time, random

def tstamp(): return str(int(time.time()))

with open('csvs/cito_fileupload-%s.csv'%(tstamp()), 'wb') as f:
        writer = csv.writer(f, delimiter=',')
        writer.writerow(['filepath', 'cFilePath', 'ACCESS', 'FOLDER', 'DOCUMENT NAME'])
        fs = glob.glob(r'C:\Users\bvandemerwe.NV\Documents\My Dropbox\NetDocuments\Automated\Tests\logs\*.*') + glob.glob(r'C:\cygwin\home\bvandemerwe\www.ols11.com.nyud.net\dprine\Books\Epub books\*.*')
        for userNum in xrange(0, 5000):
                for userFile in xrange(0, 25):
                        f = random.choice(fs)
                        writer.writerow([
                                f,
                                f,
                                'U:nd.automated-drone_%d|VESA'%(userNum),
                                'DRONEFOLDER_%d'%(userNum),
                                'doc_%d_%d_%s'%(userNum, userFile, tstamp())])
