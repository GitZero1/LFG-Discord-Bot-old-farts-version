class VoiceManager:
    def __init__(self) -> None:
        pass

    async def create_new_vc_maker(self, server, database, cat, creatorChanName, tempChanName, userLimit=0):
        #create the category
        await server.create_category(cat)
        gCat = self.get_category(server,cat)
        #create VC maker channel
        await server.create_voice_channel(creatorChanName, category=gCat)
        for c in server.channels:
            if c != None and c.name == creatorChanName:
                chanID = c.id
                #add vc maker to database
                database.insert_maker_data(tmpChanName=tempChanName, maxUsers=userLimit,chanID=chanID)
                
    
    def get_category(self, guild, cat):
        for c in guild.categories:
            if c.name == cat:
                return c
        return

    async def sort_category(self, server, database, category):
        cnum = 1
        channelsToSort = []
        for c in server.channels:
            if c.category is not None and c.category.id == category.id:
                channelsToSort.append(c)
        for c in channelsToSort:
            if database.is_maker_channel(c.id):
                makerdata = database.get_maker_data(c.id)
                tempName = makerdata[0]
        for c in channelsToSort:
            if database.is_tmp_channel(c.id):
                    await c.edit(name = tempName +" #" + str(cnum))
                    cnum = cnum +1


    async def create_custom_channel(self, server, database, cName, position, category, userLimit, player, bitrate):
        cnum = 0
        cpos = position + 1
        guild = server
        await guild.create_voice_channel(cName + " #" + str(cnum), position=cpos, category=category, bitrate = bitrate, user_limit=userLimit)
        #pull user into new VC
        for c in guild.channels:
            if c is not None and c.name == cName + " #" + str(cnum):
                await player.move_to(c)
                database.insert_tmp_data(category=category.id, chanID= c.id)
        await self.sort_category(server,database, category=category)