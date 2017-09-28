"""Models and database functions for Bills Project."""
from flask_sqlalchemy import SQLAlchemy
from collections import defaultdict

# This is the connection to the PostgreSQL database; we're getting this through
# the Flask-SQLAlchemy helper library. On this, we can find the `session`
# object, where we do most of our interactions (like committing, etc.)

db = SQLAlchemy()

##############################################################################
# Model definitions

class Bill(db.Model):
    """Bill metadata"""

    __tablename__ = "bills"

    bill_id = db.Column(db.String(32), primary_key=True)
    title = db.Column(db.Text, nullable=False)
    date = db.Column(db.DateTime)
    description = db.Column(db.Text, nullable=True)
    bill_type = db.Column(db.String(32), nullable=False)

    tags = db.relationship("Tag", secondary="bill_tags", backref="bills")
    committees = db.relationship("Committee", secondary="bill_committees", backref="bills")


    def __repr__(self):
        """Provide helpful representation when printed."""

        return "<Bill bill_id=%s title=%s date=%s description=%s bill_type=%s>" % (self.bill_id, self.title, self.date, 
                                                                                   self.description, self.bill_type)

class Senator(db.Model):
    """Senator metadata"""

    __tablename__ = "senators"

    senator_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    name = db.Column(db.String(64))
    state = db.Column(db.String(16))
    party = db.Column(db.String(32))
    original_sponsor = db.Column(db.Boolean, nullable=True)

    def __repr__(self):
        """Provide helpful representation when printed."""

        return "<Senator senator_id=%s name=%s state=%s party=%s original_sponsor=%s>" % (self.senator_id, self.name, 
                                                                     self.state, self.party, self.original_sponsor)


class Tag(db.Model):
    """Tag text"""

    __tablename__ = "tags"

    tag_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    tag_text = db.Column(db.Text, nullable=True)

    def __repr__(self):
        """Provide helpful representation when printed."""

        return "<Tag tag_id=%s tag_text=%s>" % (self.tag_id, self.tag_text)


class Committee(db.Model):
    """Committee information"""

    __tablename__ = "committees"

    committee_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    name = db.Column(db.Text, nullable=True)

    def __repr__(self):
        """Provide helpful representation when printed."""

        return "<Committee committee_id=%s name=%s>" % (self.committee_id, self.name)


class Action(db.Model):
    """Bill Action items"""

    __tablename__ = "actions"

    action_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    bill_id = db.Column(db.String(16), db.ForeignKey('bills.bill_id'))
    action_text = db.Column(db.Text, nullable=True)

    date = db.Column(db.DateTime)

    bill = db.relationship('Bill', backref='actions')

    def __repr__(self):
        """Provide helpful representation when printed."""

        return "<Action action_id=%s bill_id=%s action_text=%s date=%s>" % (self.action_id, 
                                                                           self.bill_id, 
                                                                           self.action_text, 
                                                                           self.date)

class Sponsorship(db.Model):
    """Middle table between Bills and Senators"""

    __tablename__ = "sponsorships"

    sponsorship_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    bill_id = db.Column(db.String(16), db.ForeignKey('bills.bill_id'), nullable=False)
    senator_id = db.Column(db.Integer, db.ForeignKey('senators.senator_id'), nullable=False)
    withdrawn = db.Column(db.Boolean)
    withdrawn_date = db.Column(db.DateTime)

    bill = db.relationship("Bill", backref="sponsorships")

    def __repr__(self):
        """Provide helpful representation when printed."""

        return "<Sponsorship sponsorship_id=%s bill_id=%s senator_id=%s withdrawn=%s withdrawn_date=%s>" % (self.sponsorship_id, 
                                                                                                           self.bill_id, 
                                                                                                           self.senator_id, 
                                                                                                           self.withdrawn, 
                                                                                                           self.withdrawn_date)

class BillTag(db.Model):
    """Association Table between Bill and Tag"""

    __tablename__ = "bill_tags"

    bill_tag_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    bill_id = db.Column(db.String(16), db.ForeignKey('bills.bill_id'), nullable=False)
    tag_id = db.Column(db.Integer, db.ForeignKey('tags.tag_id'), nullable=False)

    def __repr__(self):
        """Provide helpful representation when printed."""

        return "<BillTag bill_tag_id=%s bill_id=%s tag_id=%s>" % (self.bill_tag_id, self.bill_id, self.tag_id)


class BillCommittee(db.Model):
    """Association Table between Bill and Committee"""

    __tablename__ = "bill_committees"

    bill_committee_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    bill_id = db.Column(db.String(16), db.ForeignKey('bills.bill_id'), nullable=False)
    committee_id = db.Column(db.Integer, db.ForeignKey('committees.committee_id'), nullable=False)

    def __repr__(self):
        """Provide helpful representation when printed."""

        return "<BillCommittee bill_committee_id=%s bill_id=%s committee_id=%s>" % (self.bill_committee_id, 
                                                                                   self.bill_id, self.committee_id)



##############################################################################

def connect_to_db(app):
    """Connect the database to our Flask app."""

    # Configure to use our PostgreSQL database
    app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql:///bills'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SQLALCHEMY_ECHO'] = True
    db.app = app
    db.init_app(app)


if __name__ == "__main__":
    # As a convenience, if we run this module interactively, it will leave
    # you in a state of being able to work with the database directly.

    from server import app

    connect_to_db(app)
    print "Connected to DB."
