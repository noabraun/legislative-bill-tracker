"""Utility file to seed bill database from the parsed data (parse.py)"""

import datetime
from sqlalchemy import func
from model import connect_to_db, db, Bill, Senator, Committee, Tag, Action, Sponsorship, BillTag, BillCommittee
from server import app