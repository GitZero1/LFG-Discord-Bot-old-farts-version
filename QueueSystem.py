class LFGManager:

  def get_player_region(self, player):
    for r in player.roles:
       if r.name in [ "NAE", "NAW", "EU-Region", "SAM-Region", "ASIA-Region", "ME-Region", "OCE-Region", "AFRICA-Region"]:
          return r.name
    return "no region"

  def get_player_rank(self, player):
    rank = "no rank"
    if self.search_for_rank(player, "Bronze"):
        rank = "Bronze"
    
    if self.search_for_rank(player, "Silver"):
        rank = "Silver"
    
    if self.search_for_rank(player, "Gold"):
        rank = "Gold"
    
    if self.search_for_rank(player, "Platinum"):
        rank = "Platinum"
    
    if self.search_for_rank(player, "Diamond"):
        rank = "Diamond"

    if self.search_for_rank(player, "Champion"):
        rank = "Champion"
    
    if self.search_for_rank(player, "Grand Champ"):
        rank = "Grand Champ"

    if self.search_for_rank(player, "SuperSonic Legend"):
        rank = "SuperSonic Legend"
    return rank

  def search_for_rank(self, player, rank):
    for r in player.roles:
        if r.name == rank:
            return True
    return False

  def get_max_players(self,gameMode):
    if gameMode == "1v1":
        return 2
    elif gameMode == "2v2":
        return 2
    elif gameMode == "3v3":
        return 3
    elif gameMode == "Any":
        return 3
    elif gameMode == "Snow Day":
        return 3
    elif gameMode == "Rumble":
        return 3
    elif gameMode == "Hoops":
        return 2
    elif gameMode == "Dropshot":
        return 3
    elif gameMode == "In-House":
        return 6
    else:
        return 6

  def get_players(self, lfgPost, server):
    players = []
    for i in range(3,9):
        if server.get_member(lfgPost[i]) is not None:
            players.append(server.get_member(lfgPost[i]))
    return players

  def get_category(self, guild, cat):
    for c in guild.categories:
        if c.name == cat:
            return c
    return
  
  async def create_lfg_category(self,server):
    #find LFG category on server
    lfgCategory = self.get_category(server, "LFG")
    if lfgCategory is None:
        await server.create_category("LFG")
        lfgCategory = self.get_category(server, "LFG")
        # create LFG text channel to post to
        await server.create_text_channel(name= "active-lfgs", category=lfgCategory)
        
    # find LFG Voice channel category
    lfgVcCat = self.get_category(server,"LFG VOICE CHANNELS")
    if lfgVcCat is None:
        await server.create_category("LFG VOICE CHANNELS")


  async def get_channels(self, botObj):
    cf= False
    # get the channel to post LFGs into
    for c in botObj.server.channels:
        if c.name == "active-lfgs":
            print("found LFG channel")
            cf = True
            botObj.set_lfg_active_chan(c)
    if cf is False:
       print("Cant find LFG channel... exiting")
       quit





class MyBot:
  def __init__(self, server, lfgActiveChan, newChanBitRate):
    self.server = server
    self.lfgActiveChan = lfgActiveChan
    self.newChanBitRate = newChanBitRate
  
  def set_server(self, server):
    self.server = server
  
  def set_lfg_active_chan(self, lfgActiveChan):
    self.lfgActiveChan = lfgActiveChan

  def set_bit_rate(self, bitRate):
    self.newChanBitRate = bitRate
