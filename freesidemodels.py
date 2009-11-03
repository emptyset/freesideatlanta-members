import datetime

from google.appengine.ext import db


class Person(db.Model):
  """Can I see some ID please?"""
  firstname = db.StringProperty()
  lastname = db.StringProperty()
  #TODO validate username, no dupes
  username = db.StringProperty()
  email = db.EmailProperty(required=True)
  altemails = db.ListProperty(item_type=db.Email)
  phone = db.PhoneNumberProperty()
  altphones = db.ListProperty(item_type=db.PhoneNumber)
  address = db.PostalAddressProperty()
  # password is hashed with sha256
  password = db.BlobProperty(required=True)
  active = db.BooleanProperty(default=True)
  admin = db.BooleanProperty(default=False)
  joined = db.DateTimeProperty()
  left = db.DateTimeProperty()


class Member(Person):
  """Your basic freeside member."""
  starving = db.BooleanProperty(default=False)
  rfid = db.IntegerProperty()
  doormusic = db.BlobProperty()
  liability = db.BooleanProperty(default=False)
  liabilitypdf = db.BlobProperty()


class Election(db.Model):
  """Election Base Class."""
  position = db.StringProperty(required=True)
  description = db.TextProperty()
  nominate_start = db.DateTimeProperty(required=True)
  nominate_end = db.DateTimeProperty(required=True)
  vote_start = db.DateTimeProperty(required=True)
  vote_end = db.DateTimeProperty(required=True)
  # Unique list of Nominees
  nominees = db.ListProperty(item_type=db.Key)
  # List of votes stored as keys to Members or boardmembers
  votes = db.ListProperty(item_type=db.Key)
  # Unique list of member keys to prevent double voting.
  nominators = db.ListProperty(item_type=db.Key)
  voters = db.ListProperty(item_type=db.Key)


class OfficerElection(Election):
  """Object that holds all data for an officer election."""
  def ValidateNomineeDate(self):
    """Make sure nominations are open."""
    if not self.nominate_start < datetime.datetime.now() < self.nominate_end:
      raise db.Error('This election is not accepting nominations right now.')

  def ValidateVoteDate(self):
    """Make sure nominations are open."""
    if not self.vote_start < datetime.datetime.now() < self.vote_end:
      raise db.Error('This election is not accepting votes right now.')

  def ValidateMemberKey(self, memberkey):
    """Make sure a key is actually an active Member key.

    Returns:
      member - The Member Model from datastore
    """
    if memberkey.kind() != "Member":
      raise db.BadValueError('%s is not a key to a Member.' % nominee)

    member = db.get(memberkey)
    if not member.active:
      raise db.BadValueError('%s is not an active member.' % member.username)

    return member

  def ValidateNominee(self, nominee):
    """Validate a new Nominee."""
    self.ValidateNomineeDate()
    member = self.ValidateMemberKey(nominee)
    if nominee in self.nominees:
      raise db.BadValueError('%s has already been nominated.' % member.username)

  def ValidateNominator(self, nominator):
    """Make people only nominate once."""
    self.ValidateNomineeDate()
    member = self.ValidateMemberKey(nominator)

    if nominator in self.nominators:
      raise db.BadValueError('%s has already nominated someone.' % member.username)

  def ValidateVote(self, vote):
    """Make sure a vote is valid."""
    member = self.ValidateMemberKey(vote)
    if vote not in self.nominees:
      raise db.BadValueError('%s was not nominated.' % member.username)


class BoardElection(Election):
  """A Board Member Election."""
  # Board Members don't have to be members.