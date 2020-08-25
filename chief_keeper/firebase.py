from datetime import timezone
import os
from typing import List

from firebase import Firebase
from pymaker import Address

config = {
  "apiKey": "AIzaSyDbPG-hPEgt745jbWqhi9szepQAHiUbJEQ",
  "authDomain": "cms-gov-aea3e.firebaseapp.com",
  "databaseURL": "https://cms-gov-aea3e.firebaseio.com",
  "storageBucket": "cms-gov-aea3e.appspot.com"
}

class FBDatabase:
  firebase = Firebase(config)

  def __init__(self):
    self.db = self.firebase.database()

  def getData(self):
    proposals = self.db.child("proposals").get()
    for proposal in proposals.each():
      print(proposal.key())
      print(proposal.val()['about'])

  def getKey(self, network, source: Address):
    proposals = self.db.child("proposals").get()
    if network == "mainnet":
      proposals = self.db.child("proposals_mainnet").get()
    key = ""
    for proposal in proposals.each():
      if (proposal.val()['source'] == source):
        key = proposal.key()
    return key

  def setDatePassed(self, key, datePassed):
    print("Set Date Passed")
    self.db.child("proposals").child(key).child("datePassed").set(datePassed)

  def setDateExecuted(self, key, dateExecuted):
    print("Set Date Executed")
    self.db.child("proposals").child(key).child("dateExecuted").set(dateExecuted)

  def setEndApprovals(self, key, endApprovals):
    print("Set End Approvals")
    self.db.child("proposals").child(key).child("end_approvals").set(endApprovals)
  
  def setActive(self, key, active):
    print("Set Active") 
    self.db.child("proposals").child(key).child("active").set(active)

  def setValue(self, network, key, field, value):
    # print(key + " " + "Set Value of " + field) 
    if network == "kovan":
      self.db.child("proposals").child(key).child(field).set(value)
    elif network == "mainnet":
      self.db.child("proposals_mainnet").child(key).child(field).set(value)