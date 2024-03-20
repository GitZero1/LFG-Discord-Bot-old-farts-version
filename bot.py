import discord
import datetime
import dbManager
from QueueSystem import MyBot, LFGManager
from discord.ext import commands
from voiceManager import VoiceManager
import configparser

intents = discord.Intents.all()
intents.members = True
bot = commands.Bot(intents=intents)
db = dbManager.SQLdb()
db.__init__()

# config
config = configparser.ConfigParser()
config.read('oldFartBot.conf')
# server ID
serverID = config.get('IDs', 'serverID')
serverID = int(serverID)
# ID of channel to spam with logs
logChannelID = config.get('IDs', 'logChanID')
logChannelID = int(logChannelID)
# Bot Token
TOKEN = config.get('Token', 'token')

#how long LFG post stays up
postTimeoutInSeconds = 1800 # 30 min
#colors for LFG lsitings
casualColor =  0x0094fb 
rankedColor = 0x00ff00
extraColor = 0x00ff00
privateColor = 0x00ff00
# create managers
myLFGManager = LFGManager()
myVcManager = VoiceManager()
myBot = MyBot(0,0,9600)


# TODO add something to handle if a user creates a LFG, never joins the VC and then cancels the LFG
# it will need to make sure the VC is empty first, otherwise it can just be ignored and will clean itself up 
# TODO add a way to quickly assign rank/region via the bot for users who dont have it set already
# maybe more drop downs?
# TODO consider adding color coded stuff for ranked/unranked/private/extramodes
# TODO figure out how to handle private matches (how long before its removed? how to handle the VC? do we allow more than 6 users? do we need ranks?)

@bot.event
async def on_ready():

    print(bot.user.name + " is Online...")
    print(datetime.datetime.now().strftime('%H:%M:%S %m-%d-%Y'))
    print('------')

    # get the server object
    get_server()
    # find or create LFG category
    # await myLFGManager.create_lfg_category(server=myBot.server)
    # get channels 
    # await myLFGManager.get_channels(myBot)


async def handleVcLogging(member, before, after):
    logChannel = bot.get_channel(logChannelID)
    name = member.name

    time = datetime.datetime.now().strftime('%H:%M:%S %m-%d-%Y')
    ### Print who joined  #####
    ### Check if muted or check if before channel == after channel
    if before.channel != None and after.channel != None:
        if before.channel.name == after.channel.name:
            return
        Jchan = after.channel.name
        Lchan = before.channel.name
        msg = "```USER: {}\nMOVED FROM: {}\nTO: {}\nAT: {}```"
        await logChannel.send(msg.format(name, Lchan, Jchan, time))


        ## print who joined
    if before.channel == None:
        Jchan = after.channel.name
        msg = "```USER: {}\nJOINED: {}\nAT: {}```"
        await logChannel.send(msg.format(name, Jchan, time))


    if after.channel == None:
        Lchan = before.channel.name
        ### Print who left #######
        msg = "```USER: {}\nLEFT: {}\nAT: {}```"
        await logChannel.send(msg.format(name, Lchan, time))

@bot.event
async def on_voice_state_update(member, before, after):
     await handleVcLogging(member,before,after)
    #if the channel is empty now
     if before.channel != None and len(before.channel.members) == 0:
        # is it a LFG VC?
        """if db.is_lfg_channel(before.channel.id):
            # get the post associated with this vc
            post = db.get_lfg_by_vc(before.channel.id)
            await before.channel.delete()
            if post == None:
                print("LFG post was already removed")
                return
            #get the actual message object 
            message =  await myBot.lfgActiveChan.fetch_message(post[0])
            await message.delete() """
        #is it a temp channel we made?
        if db.is_tmp_channel(before.channel.id):
            catToSort = before.channel.category
            await before.channel.delete()
            #reorder the remaining channels in that category
            await myVcManager.sort_category(server=myBot.server, database=db, category=catToSort)

    # if user is joins a voice channel
     if after.channel != None:
        # if it's a maker channel
        if  db.is_maker_channel(int(after.channel.id)):
            #get maker info
            makerData = db.get_maker_data(after.channel.id)
            #make tmp chan
            await myVcManager.create_custom_channel(server= myBot.server, 
                                                    database= db, cName= makerData[0], 
                                                    position= after.channel.position, 
                                                    category= after.channel.category, 
                                                    userLimit= makerData[1], 
                                                    player=member, 
                                                    bitrate= myBot.newChanBitRate)
        # if user joins LFG Voice channel
        """if  db.is_lfg_channel(after.channel.id):
            # get the post associated with this vc
            post = db.get_lfg_by_vc(after.channel.id)
            if post == None:
                print("LFG post was already removed")
                return
            #get the actual message object 
            message =  await myBot.lfgActiveChan.fetch_message(post[0])
            pNum = post[9]
            # check if the player is already in the lfg
            players = myLFGManager.get_players(lfgPost= post, server= myBot.server)
            print(players)
            if member in players:
                print("player already in LFG for this VC")
                return
            #if not add them to the LFG and update the listing
            db.add_player(postID = post[0], playerID = member.id,playerNum= pNum + 1)
            await update_lfg_post(message=message)

    # if user leaves LFG channel but isnt the last one (that is dealt with already)
     if before.channel != None and db.is_lfg_channel(before.channel.id):
         # get the post associated with this vc
         post = db.get_lfg_by_vc(before.channel.id)
         print(post)
         if post == None:
                print("LFG post was already removed")
                return
         #get the actual message object 
         message =  await myBot.lfgActiveChan.fetch_message(post[0])
         # check if the user created the lfg
         if db.is_lfg_creator(postID = post[0], playerID = member.id):
             await message.delete()
            # if so remove the lfg, otherwise remove the user from the lfg.
         else:
             db.remove_player(postID = post[0], playerID = member.id)
             await update_lfg_post(message= message)
"""
"""
@bot.event
async def on_message_delete(message):
    # delete any LFG posts from the database when they done
    if db.is_lfg_post(message.id) == True:
        print("deleting LFG post from database...")
        db.delete_lfg(message.id)
"""

@bot.event
async def on_guild_channel_delete(channel):
    # remove voice channels from database on delete.
    if db.is_lfg_channel(channelID=channel.id) == True:
        print("deleting LFG VC from database...")
        db.remove_voice_channel(channelID=channel.id)
    if db.is_tmp_channel(channelID=channel.id) == True:
        print("deleting temp VC from database...")
        db.remove_tmp_channel(channelID=channel.id)
        

######## RANDOM FUNCTIONS ################################################################################################################################################


def get_server():
    serverFound = False
    for g in bot.guilds:
        if g.id == serverID:
            serverFound = True
            print("Server Found...")
            myBot.set_server(g)
            #set the new channel bitrate to whatever the max rate is for the server
            myBot.set_bit_rate(int(g.bitrate_limit))
    if serverFound == False:
        print("Server was not found... \nAborting...")
        quit


async def beta_create_lfg_post(playlist, gameMode, user):
    server = myBot.server
    rank = myLFGManager.get_player_rank(player= user)
    region = myLFGManager.get_player_region(player= user)
    maxPlayers = myLFGManager.get_max_players(gameMode)
    lfgCategory = myLFGManager.get_category(server, "LFG VOICE CHANNELS")

    # create a VC
    vcName = f"{user.name}'s Group"
    await server.create_voice_channel(vcName, category=lfgCategory, user_limit= maxPlayers, bitrate= myBot.newChanBitRate)
    for c in server.channels:
        if c.name == vcName:
            channel = c
            db.add_voice_channel(c.id)
    
    # Embed for LFG Post
    lfgEmbed = discord.Embed( color=rankedColor,
                             title= f"{user.name} is looking for a group",
                             description= f"\n\n```ansi\n[2;33m[0m[0;2m[0;31mGameMode[0;37m \n{playlist}{gameMode} \n\n[2;33m[0m[0;2m[0;31mRank[0;37m \n{rank} \n\n[2;33m[0m[0;2m[0;31mRegion[0;37m \n{region}```\n### Voice: {channel.mention}")
    lfgEmbed.set_footer(text=f'Party: {user.name} (1/{maxPlayers})')
    lfgEmbed.set_thumbnail(url= user.avatar.url)

    #filter ranks and get rank image
    if rank == "SuperSonic Legend":
        rank = "SuperSonicLegend"
    if rank == "Grand Champ":
        rank = "GrandChamp"
    file = discord.File(f"images/{rank}.png")
    lfgEmbed.set_thumbnail(url=f"attachment://{rank}.png")
    
    #create a LFG post
    await myBot.lfgActiveChan.send(embed=lfgEmbed, view = LFGView(timeout=None), file = file, delete_after=postTimeoutInSeconds)
    post = (await bot.get_channel(myBot.lfgActiveChan.id).history(limit=1).flatten())[0]
    db.create_lfg(postID= post.id, rank=rank, gameMode= gameMode, player1= user.id, voiceChannelID= channel.id)


async def update_lfg_post(message):
    pass
    # get post from db
    lfgPost = db.get_lfg(message.id)
    # get embed\
    embed = message.embeds[0]
    rank = lfgPost[1]
    #testing local file as thumbnail
    file = discord.File(f"images/{rank}.png")
    embed.set_thumbnail(url=f"attachment://{rank}.png")

    #get max players
    maxPlayers = myLFGManager.get_max_players(lfgPost[2])
    players = myLFGManager.get_players(lfgPost=lfgPost, server=myBot.server)
    playerCount = lfgPost[9]
    #is the party full?
    if playerCount == maxPlayers:
        #delete lfg post and send invite to players
        await complete_lfg(lfgPost= lfgPost)
        return
    # update party members in embed footer
    partyString = "Party:\n"
    for p in players:
        partyString += p.name + "\n"
    partyString += f" ({playerCount}/{maxPlayers})"
    embed.set_footer(text= partyString)

    # update the post
    await message.edit(embed=embed, view = LFGView(timeout=None), file = file, delete_after=postTimeoutInSeconds)


async def complete_lfg(lfgPost):
    server = myBot.server
    player = server.get_member(lfgPost[3])
    for c in server.channels:
        if c.id == lfgPost[10]:
            channel = c
    s = ""
    for i in range(3,9):
        if server.get_member(lfgPost[i]) is not None:
            s += f"{server.get_member(lfgPost[i]).mention}, "
    s += f" Your party is ready!\nJoin them in >> {channel.mention}"

    # Embed for Party Full post
    lfgEmbed = discord.Embed( color=0x00ff00,
                             title= f"{player.name}'s group is now full!",
                             description= s)
    lfgEmbed.set_thumbnail(url= player.avatar.url)
    lfgEmbed.set_footer(text="Good Luck!")
    #delete lfg listing
    async for m in myBot.lfgActiveChan.history(limit=200):
        if m.id == lfgPost[0]:
            await m.delete()
    # ping party members with link to temp VC then delete message after 10 min
    await myBot.lfgActiveChan.send(embed = lfgEmbed, delete_after= 600)


async def handlePlaylistSelection(gameMode, interaction):
    match gameMode:
        case "Ranked":
                await interaction.message.edit(content= "Select Game Mode", view = RankedGamesOptionsView(), delete_after = 20)
        case "Casual":
                await interaction.message.edit(content= "Select Game Mode", view = CasualGamesOptionsView(), delete_after = 20)
        case "Extra":
                await interaction.message.edit(content= "Select Game Mode", view = ExtraGamesOptionsView(), delete_after = 20)
        case "Private":
                await interaction.message.edit(content= "Select Game Mode", view = PrivateGamesOptionsView(), delete_after = 20)
        case _:
                await interaction.message.edit(content= "Select Game Mode", view = RankedGamesOptionsView(), delete_after = 20)
   
####### VIEWS ################################################################################################################################################
##############################################################################################################################################################


####### VOICE MAKER OPTIONS ##################################################################################################################################

class VoiceMakerView(discord.ui.Modal):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)

        self.add_item(discord.ui.InputText(label="Category Name", required= True,placeholder="ex '3v3 VOICE-CHANNELS'"))
        self.add_item(discord.ui.InputText(label="Temp Channel Generator Name", required= True,placeholder="+ Create New 3 Max VC"))
        self.add_item(discord.ui.InputText(label="Temp Channel Template Prefix", required= True, placeholder= "'3v3' (becomes '3v3 #1'... #2... #3...)"))
        self.add_item(discord.ui.InputText(label="User Limit", required= False, max_length=1, placeholder=" 3 (0 = no limit)"))
    async def select_callback(self, select, interaction): 
        await interaction.response.defer()

    async def callback(self, interaction: discord.Interaction):
        embed = discord.Embed(title="Modal Results")
        embed.add_field(name="Category Name", value=self.children[0].value)
        embed.add_field(name="Creator Name", value=self.children[1].value)
        embed.add_field(name="Temp Channel Name", value=self.children[2].value)
        await myVcManager.create_new_vc_maker(server=myBot.server, database=db, cat=self.children[0].value, creatorChanName=self.children[1].value, tempChanName=self.children[2].value, userLimit=int(self.children[3].value))
        await interaction.response.send_message(embeds=[embed])


##### LFG VIEWS #############################################################################################################################################

# Actual LFG Post
class LFGView(discord.ui.View):
    # Create button

    @discord.ui.button(label="Join", row= 4, style=discord.ButtonStyle.success)
    async def button_callback(self, button, interaction):
        post = db.get_lfg(interaction.message.id)
        pNum = post[9]
        db.add_player(postID = interaction.message.id, playerID = interaction.user.id,playerNum= pNum + 1)
        # https://discord.com/channels/<SERVERID>/<VC ID>    << using this as the URL for a url style button will make the person join the vc
        await update_lfg_post(interaction.message)
        await interaction.response.defer()

    @discord.ui.button(label="Leave", row= 4, style=discord.ButtonStyle.danger)
    async def second_button_callback(self, button, interaction):
        db.remove_player(postID = interaction.message.id, playerID = interaction.user.id)
        await update_lfg_post(interaction.message)
        await interaction.response.defer()
    
    @discord.ui.button(label="Cancel", row= 4, style=discord.ButtonStyle.gray)
    async def third_button_callback(self, button, interaction):
        if db.is_lfg_creator(postID = interaction.message.id, playerID = interaction.user.id) is True:
            #delete the post
            await interaction.message.delete()
        else:
            await interaction.response.defer()


class PlaylistSelectView(discord.ui.View):
    
    @discord.ui.select( 
        placeholder = "Select a Playlist", 
        min_values = 1, 
        max_values = 1, 
        options = [ 
            discord.SelectOption(
                label="Ranked"
            ),
            discord.SelectOption(
                label="Casual"
            ),
            discord.SelectOption(
                label="Extra"
            )#,
            #discord.SelectOption(
            #    label="Private"
            #)
        ]
    )
    async def select_callback(self, select, interaction): 
        await interaction.response.defer()
        await handlePlaylistSelection(select.values[0], interaction)


class RankedGamesOptionsView(discord.ui.View):
    @discord.ui.select( 
        placeholder = "2s or 3s", 
        min_values = 1, 
        max_values = 1, 
        options = [ 
            discord.SelectOption(
                label="2v2"
            ),
            discord.SelectOption(
                label="3v3"
            ),
            discord.SelectOption(
                label="Any"
            )
        ]
    )
    async def select_callback(self, select, interaction): 
        await beta_create_lfg_post("Ranked - ",select.values[0], interaction.user)
        await interaction.response.defer()
        await interaction.message.delete()


class CasualGamesOptionsView(discord.ui.View):
    @discord.ui.select( 
        placeholder = "2s or 3s?", 
        min_values = 1, 
        max_values = 1, 
        options = [ 
            discord.SelectOption(
                label="2v2"
            ),
            discord.SelectOption(
                label="3v3"
            ),
            discord.SelectOption(
                label="Any"
            )
        ]
    )
    async def select_callback(self, select, interaction): 
        await beta_create_lfg_post("Casual - ", select.values[0], interaction.user)
        await interaction.response.defer()
        await interaction.message.delete()


class ExtraGamesOptionsView(discord.ui.View):
    @discord.ui.select( 
        placeholder = "Game Mode", 
        min_values = 1, 
        max_values = 1, 
        options = [ 
            discord.SelectOption(
                label="Snow Day"
            ),
            discord.SelectOption(
                label="Hoops"
            ),
            discord.SelectOption(
                label="Dropshot"
            ),
            discord.SelectOption(
                label="Rumble"
            ),
            discord.SelectOption(
                label="Any"
            )
        ]
    )
    async def select_callback(self, select, interaction): 
        await beta_create_lfg_post("Extra - ", select.values[0], interaction.user)
        await interaction.response.defer()
        await interaction.message.delete()


class PrivateGamesOptionsView(discord.ui.View): ## TODO figure out private matches setup
    @discord.ui.select( 
        placeholder = "Game Mode", 
        min_values = 1, 
        max_values = 1, 
        options = [ 
            discord.SelectOption(
                label="Chaos"
            ),
            discord.SelectOption(
                label="Hockey"
            )
        ]
    )
    async def select_callback(self, select, interaction): 
        await beta_create_lfg_post("Private - ", select.values[0], interaction.user)
        await interaction.response.defer()
        await interaction.message.delete()


####### SLASH COMMANDS ##################################################################################################################################################

@bot.slash_command(description="create a new voice maker category.")
async def vc_maker(ctx):
    if not ctx.author.guild_permissions.administrator:
        await ctx.respond("Only admins can use this command")
        return
    modal = VoiceMakerView(title="Create Tmp Maker")
    await ctx.send_modal(modal)

"""
@bot.slash_command(description="Creates LFG post")
async def lfg(ctx): 
    rank = myLFGManager.get_player_rank(ctx.user)
    region = myLFGManager.get_player_region(ctx.user)
    if rank == "no rank" or region == "no region":
        await ctx.respond("You must select a rank and region in rank reg setup to use this feature", delete_after=10)
        return
    await ctx.respond(content=f"Hello, {ctx.user.mention}! Please Choose a Playlist.", view=PlaylistSelectView(), delete_after=20)
    """

#######################################################################################################################################################################

bot.run(TOKEN)
