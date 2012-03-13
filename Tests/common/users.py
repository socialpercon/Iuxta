#!/usr/bin/env python

root    = "nd.automated"
keeper  = "nd.automated_keeper"

userAdmin = "nd.Automated_A"
userVESA = "nd.Automated_VESA"
userVES = "nd.Automated_VES"
userVE = "nd.Automated_VE"
userV = "nd.Automated_V"
userNA = "nd.Automated_NA"

password = "snoopy"

ducotDrones = {
    "user":"nd.automated-drone_", # 0 -1000
    "cabinets":["NG-Z346VE67"]
}

userList = [userAdmin, userVESA, userVES, userVE, userV, userNA]

uploadList = [root, keeper, userAdmin, userVESA]

if __name__ == "__main__":
    print "NetDocuments user files."