import sqlite3

#conn = sqlite3.connect('lfg.db')


# 0 = postID
# 1 = rank
# 2 = gameMode
# 3 = player1
# 4 = player2
# 5 = player3
# 6 = player4
# 7 = player5
# 8 = player6
# 9 = playerCount
# 10 = voiceChannel


class SQLdb():
  
  def __init__(self):
    self.conn = sqlite3.connect('lfg.db')
    self.c = self.conn.cursor()
    self.c.execute(""" CREATE TABLE IF NOT EXISTS lfgs (postID integer, rank string, gameMode string, player1 integer, player2 integer, player3 integer, player4 integer, player5 integer, player6 integer, playerCount integer, voiceChannel integer)""")
    self.c.execute(""" CREATE TABLE IF NOT EXISTS vcs (channelID integer)""")
    self.c.execute('''CREATE TABLE IF NOT EXISTS "makerChannels" ("tmpChanName" TEXT, "maxUsers" INTEGER, "channelID" INTEGER)''')
    self.c.execute('''CREATE TABLE IF NOT EXISTS "tempChannels" ("category" INTEGER, "channelID" INTEGER)''')
    self.conn.commit()


  
  def add_voice_channel(self, channelID):
    self.c.execute("INSERT INTO vcs (channelID) VALUES (?)", [channelID])
    self.conn.commit()

  def remove_voice_channel(self, channelID):
    self.c.execute("DELETE FROM vcs WHERE channelID = ?", [channelID])
    self.conn.commit()

  
  def create_lfg(self, postID, rank, gameMode, player1, voiceChannelID):
    self.c.execute("INSERT INTO lfgs (postID, rank, gameMode, player1, voiceChannel, playerCount) VALUES (?, ?, ?, ?, ?, ?)", [postID, rank, gameMode, player1, voiceChannelID, 1])
    self.conn.commit()

  def delete_lfg(self, postID):
    self.c.execute("DELETE FROM lfgs WHERE postID = ?", [postID])
    self.conn.commit()
  
  def add_player(self, postID, playerID, playerNum):
    self.c.execute("SELECT * FROM lfgs WHERE postID = ?", [postID])
    rows = self.c.fetchall()
    try:
       post = rows[0]
    except:
       print("could not find data...")
       return
    self.c.execute(f"UPDATE lfgs SET player{playerNum} = ? WHERE postID = ?",[playerID, postID])
    self.c.execute(f"UPDATE lfgs SET playerCount = ? WHERE postID = ?",[post[9] + 1, postID]) 
    self.conn.commit()

  def remove_player(self, postID, playerID):
    self.c.execute("SELECT * FROM lfgs WHERE postID = ?", [postID])
    rows = self.c.fetchall()
    try:
       post = rows[0]
    except:
       print("could not find data...")
       return
    
    for i in range(2,6):
      self.c.execute(f"UPDATE lfgs SET player{i} = NULL WHERE player{i} = ? AND postID = ?",[playerID, postID])
      if post[9] > 1:
        self.c.execute(f"UPDATE lfgs SET playerCount = ? WHERE postID = ?",[post[9] - 1, postID]) 
    self.conn.commit()


  def get_data(self, tablename):
      self.c.execute(f"SELECT * FROM {tablename}")
      rows = self.c.fetchall()
      for row in rows:
        print(row)
      return rows

  def get_lfg_by_vc(self, vcID):
    self.c.execute("SELECT * FROM lfgs WHERE voiceChannel = ?", [vcID])
    rows = self.c.fetchall()
    try:
       post = rows[0]
    except:
       print("could not find data...")
       return
    return post

  def get_lfg(self, postID):
    self.c.execute("SELECT * FROM lfgs WHERE postID = ?", [postID])
    rows = self.c.fetchall()
    try:
       post = rows[0]
    except:
       print("could not find data...")
       return
    return post
    
  def is_lfg_post(self, postID):
    self.c.execute("SELECT * FROM lfgs WHERE postID = ?", [postID])
    rows = self.c.fetchone()
    if not rows:
      return False
    else:
      return True
    
  def is_lfg_channel(self, channelID):
    self.c.execute("SELECT * FROM vcs WHERE channelID = ?", [channelID])
    rows = self.c.fetchone()
    if not rows:
      return False
    else:
      return True
  
  def is_lfg_creator(self, postID, playerID):
    self.c.execute("SELECT * FROM lfgs WHERE postID = ? AND player1 = ?", [postID, playerID])
    rows = self.c.fetchone()
    if not rows:
      return False
    else:
      return True
  

  def insert_maker_data(self, tmpChanName, maxUsers, chanID):
        self.c.execute(f"INSERT INTO 'makerChannels' ('tmpChanName', 'maxUsers', 'channelID') VALUES (?, ?, ?)", (tmpChanName, maxUsers, chanID))
        self.conn.commit()

  def insert_tmp_data(self, category, chanID):
      self.c.execute(f"INSERT INTO 'tempChannels' (category, 'channelID') VALUES (?, ?)", (category, chanID))
      self.conn.commit()

  
  def get_maker_data(self, chanID):
      self.c.execute(f"SELECT * FROM makerChannels WHERE channelID = {chanID}")
      rows = self.c.fetchone()
      return rows
  
  def is_maker_channel(self, channelID):
      # Define the SQL SELECT statement with a WHERE clause
      # Execute the SELECT statement with the channel ID as a parameter
      self.c.execute(f"SELECT * FROM makerChannels WHERE channelID = {channelID}")
      # Fetch the results of the query
      results = self.c.fetchone()
      if results:
          return True
      else:
          return False
      
  def is_tmp_channel(self, channelID):
      # Query tempchannels for channel
      self.c.execute(f"SELECT * FROM tempChannels WHERE channelID = {channelID}")
      # Fetch the results of the query
      results = self.c.fetchone()
      if results:
          return True
      else:
          return False
      
  def remove_tmp_channel(self, channelID):
      self.c.execute(f"DELETE FROM tempChannels WHERE channelID = {channelID}")
      self.conn.commit()
  def remove_maker_channel(self, channelID):
      self.c.execute(f"DELETE FROM makerChannels WHERE channelID = {channelID}")
      self.conn.commit()


  def __del__(self):
    self.conn.close()