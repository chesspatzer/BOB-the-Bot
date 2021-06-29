

import random as r
import re
import smtplib
from email.mime.multipart import MIMEMultipart
# IMPORT DISCORD.PY. ALLOWS ACCESS TO DISCORD'S API.
# vtf-recruitment
from email.mime.text import MIMEText

import discord
import pymongo
from discord.ext import commands

from config import credentials, emojiLocal
from games.connect4 import ConnectFour
client = pymongo.MongoClient(
    'mongodb://' + credentials['username'] + ":" + credentials['password'] + credentials['database'])
db = client.test

collection = db.database_collection
messages = collection.messages
domain = collection.domain
verification = collection.verification
emailUserMap = collection.emailUserMap
userEmailMap = collection.userEmailMap
emojiDict = collection.emojiDict

prefix = "##"
intents = discord.Intents.default()
intents.members = True

bot = commands.Bot(command_prefix=prefix, intents=intents)
memberlist = []
import datetime

# Get yesterdays date.
lastweek = datetime.datetime.now() - datetime.timedelta(days=7)

last5days = datetime.datetime.now() - datetime.timedelta(days=5)

messagelist = []
validDomains = {}


@bot.event
async def on_ready():
    print('Hannibal Pondy Venu Bot is ready')


@bot.command(name="ping")
async def ping(ctx):
    await ctx.send('Thanks for checking on me ' + ctx.author.name + ', I am alive, up and running fine so dw.')


@bot.command(name="helpme")
async def helpme(ctx):
    await ctx.send(
        'Hello, If you are a northeastern university student, type the command **$$requestOTP <EmailId>**. Eg : **$$requestOTP   patzerpunda@northeastern.edu** Purdue students can tag Raushan to get your external role updated, others can tag the mods to get your admits verified.')


# TODO: verify server domain later (regex)
@bot.command(name="settings")
async def settings(ctx, domainName, addRoles, removeRoles, verificationMessage):
    if discord.utils.get(ctx.guild.roles, name='admin') in ctx.author.roles:
        add, remove = addRoles.strip().split(','), removeRoles.strip().split(',')
        dict_object = {
            '_id': ctx.guild.id,
            'domain': str(domainName),
            'add': add,
            'remove': remove,
            'message': verificationMessage
        }
        response = domain.save(dict_object)
        if response:
            validDomains[ctx.guild.id] = str(domainName)
        await ctx.send("The requested settings have been updated successfully.")
    else:
        await ctx.send("The command you are trying to execute is way above your pay grade!!!")




@bot.command(name="requestOTP")
async def requestOTP(ctx, emailID=""):
    domainName = getDomain(ctx)
    if len(emailID) == 0:
        await ctx.send("Invalid synatx. Correct command syntax : **" + prefix + "requestOTP  <email id> eg: $$requestOTP  test@"+domainName+"**")
    else:
        if domainName is None:
            await ctx.send("Admins, please set the domain of your server before verifying")
        else:
            if domainName == emailID[len(emailID) - len(domainName):]:
                userMapper = userEmailMap.find_one({'serverID': str(ctx.guild.id) , 'email': emailID}, {'userID': True})
                if userMapper is not None and userMapper['userID'] != str(ctx.author.id):
                    await ctx.send("This email address has already been mapped to another user here, please contact admin "
                                   "in case of any issues.")
                else:
                    otp = otpgen()
                    dict_object = {
                        '_id': str(ctx.guild.id) + '_' + str(ctx.author.id),
                        'timestamp': datetime.datetime.now(),
                        'otp': otp,
                        'email': emailID
                    }
                    verification.save(dict_object)
                    msg = MIMEMultipart()
                    msg['From'] = 'nuverifier@gmail.com'
                    msg['To'] = emailID
                    index = domainName.index('.')
                    msg['Subject'] = domainName[:index] + ' discord verification OTP'
                    msg.attach(MIMEText("Your OTP is : " + otp, 'plain'))
                    server = smtplib.SMTP('smtp.gmail.com', 587)
                    server.starttls()
                    server.login(credentials['emailID'], credentials['emailPassword'])
                    server.sendmail(credentials['emailID'], emailID, msg.as_string())
                    server.quit()

                    await ctx.send("Your OTP has been sent to your " + domainName[
                                                                       :index] + " email address, please check all folders (including spam) in your email inbox. Enter **" + prefix + "verifyOTP <enter otp> ** to get verified. Eg: **$$verifyOTP 123456**")
            else:
                await ctx.send(
                    'This email domain is invalid for the server, please use a valid ' + domainName + ' email address for verification')


@bot.command(name="verifyOTP")
async def verifyOTP(ctx, OTP):
    primaryKey = str(ctx.guild.id) + '_' + str(ctx.author.id)
    # query based on id and otp, returns only if otp valid
    userOTP = verification.find_one({'_id': primaryKey, 'otp': str(OTP)},
                                    {'email': True, 'otp': True, 'timestamp': True})
    if userOTP is None:
        await ctx.send(
            "Invalid OTP, please request for OTP again by using **" + prefix + "requestOTP <email_address>**")
    else:
        if userOTP['timestamp'] is None:
            await ctx.send(
                "Invalid OTP, please request for OTP again by using **" + prefix + "requestOTP <email_address>**")
        else:
            if datetime.datetime.now() - datetime.timedelta(minutes=10) > userOTP['timestamp']:
                await ctx.send(
                    "OTP has expired, please request for OTP again by using **" + prefix + "requestOTP <email_address>**")
            else:
                # else is executed only when OTP matches
                response = domain.find_one({'_id': ctx.guild.id}, {'add': True, 'remove': True, 'message': True})
                for role_plus in response['add']:
                    if role_plus is None or len(role_plus) == 0:
                        continue
                    await ctx.author.add_roles(discord.utils.get(ctx.guild.roles, name=role_plus))
                for role_minus in response['remove']:
                    if role_minus is None or len(role_minus) == 0:
                        continue
                    await ctx.author.remove_roles(discord.utils.get(ctx.guild.roles, name=role_minus))
                if response['message']:
                    await ctx.author.send(response['message'])
                else:
                    await ctx.author.send("You have been successfully verified, you should have access to other "
                                          "channels of the server now")
                await ctx.send("Verification is successful for " + ctx.author.name)
                try:
                    dict_object = {
                        'email': userOTP['email'],
                        'userID': str(ctx.author.id),
                        'serverID':str(ctx.guild.id),
                        'userCompositeID': str(ctx.guild.id) + '_' + str(ctx.author.id)
                    }
                    userEmailMap.save(dict_object)
                except :
                    print(dict_object)


def getDomain(ctx):
    if ctx.guild.id not in validDomains:
        currentDomain = domain.find_one({'_id': ctx.guild.id}, {'domain': True})
        if currentDomain is None: return currentDomain
        validDomains[ctx.guild.id] = currentDomain['domain']
    return validDomains[ctx.guild.id]


def otpgen():
    otp = ""
    for i in range(6):
        otp += str(r.randint(1, 9))
    return otp


@bot.command(name="violators")
async def violators(ctx):
    if discord.utils.get(ctx.guild.roles, name='admin') in ctx.author.roles:
        violators = list(set(filter(lambda val: val not in messagelist, memberlist)))
        for violator in violators:
            await ctx.channel.send(violator.mention + ' is a violator')
    else:
        await ctx.send("A wise man once said, don't ask question you don't want to know the answers to.")


@bot.command(name="identifyViolators")
async def detectViolators(ctx, args):
    if discord.utils.get(ctx.guild.roles, name='admin') in ctx.author.roles:
        print("started")
        print(args)
        start = datetime.datetime.now()
        memberlist.clear()
        messagelist.clear()
        for member in ctx.guild.members:
            for role in member.roles:
                if role.name == 'Visa Task Force':
                    memberlist.append(member)

        visa_slot_availability_channel = discord.utils.get(ctx.guild.channels, name='visa-slot-availability')
        print(visa_slot_availability_channel)

        visa_recruitment_channel = discord.utils.get(ctx.guild.channels, name='vtf-recruitment')
        print(visa_recruitment_channel)

        mod_channel = discord.utils.get(ctx.guild.channels, name='mod-channel')
        print(mod_channel)

        timeframe = datetime.datetime.now() - datetime.timedelta(days=int(args))

        messages = await visa_slot_availability_channel.history(limit=None, after=timeframe).flatten()

        counter = 0
        for msg in messages:
            counter += 1
            messagelist.append(msg.author)
        print(counter)

        violators = list(set(memberlist) - set(messagelist))
        print(len(violators))
        if violators == [] or violators == None:
            await ctx.channel.send('there are no violators')
        else:
            for violator in violators:
                await visa_recruitment_channel.send(
                    violator.mention + ' has not updated in the last ' + args + ' days. This is a warning. Update ASAP to avoid being removed from the task force.')
            await mod_channel.send(str(len(violators)) + ' have been warned')

        print("completed")
        end = datetime.datetime.now()
        time = end - start
        print(time.total_seconds())
    else:
        await ctx.send("A wise man once said, don't ask question you don't want to know the answers to.")


@bot.command(name="c4settings")
async def c4settings(ctx, addEmojis):
    emojis = addEmojis.strip().split(',')
    for emoji in emojis:
        if emojiDict.find_one({'emoji': str(emoji)}) is not None:
            dict_object = {'emoji' : str(emoji)}
            emojiDict.save(dict_object)
    await ctx.send(addEmojis)


@bot.command(name="challenge")
async def challenge(ctx, competitor):
    m = await ctx.send( ctx.author.name + " has challenged"  + competitor + "to a match")
    competitor = await getUser(ctx,competitor)
    await m.add_reaction(emojiLocal['ACCEPT'])
    await m.add_reaction(emojiLocal['DENY'])
    game = ConnectFour(ctx,ctx.author,competitor)
    try:
        def check(reactions, users):
            print("testing")
            return users.id == competitor.id and str(reactions) in [emojiLocal['ACCEPT'], emojiLocal['DENY']]
        reaction, user = await ctx.bot.wait_for('reaction_add', check=check, timeout=45)
        if str(reaction) == emojiLocal['ACCEPT']:
            await ctx.send("Challenge accepted")
            emojiMessage = await ctx.send("Player 1 " + game.player1.name +" please react to this message to choose your emoji")
            def checkplayer1(reactions, users):
                return users.id == ctx.author.id
            def checkplayer2(reactions, users):
                return users.id == competitor.id
            reaction, user = await ctx.bot.wait_for('reaction_add', check=checkplayer1, timeout=45)
            game.player1Emoji = reaction
            await ctx.send("Set Player1's emoji as "+ str(game.player1Emoji))
            emojiMessage = await ctx.send("Player 2 " + game.player2.name + " please react to this message to choose your emoji")
            reaction, user = await ctx.bot.wait_for('reaction_add', check=checkplayer2, timeout=45)
            game.player2Emoji = reaction
            await ctx.send("Set Player2's emoji as "+ str(game.player2Emoji))
            await ctx.send(game.display_current_grid())
            while game.gameover != True:
                await movePlayer(checkplayer1, ctx, game)
                await ctx.send(game.display_current_grid())
                if game.gameover == True:
                    await ctx.send(game.player1.name + " wins")
                    break
                await movePlayer(checkplayer2, ctx, game)
                await ctx.send(game.display_current_grid())
                if game.gameover == True:
                    await ctx.send(game.player2.name +" wins")
                    break

        else:
            await ctx.send("Challenge denied")
    except Exception as E:
        await ctx.send("The challenge request has timed out!" + str(E))


async def movePlayer(checkplayer, ctx, game):
    playerReaction = await ctx.send("Turn:" + game.currentPlayer.name + "\n Please react to the message  ")
    for emoji in game.emoji_dict:
        await playerReaction.add_reaction(emoji)
    reaction, user = await ctx.bot.wait_for('reaction_add', check=checkplayer, timeout=45)
    currentBoard = game.make_move(reaction.emoji)


async def getUser(ctx, comp):
    regex_id = re.search(r"^<@!?(\d+)>$", comp)
    try:
        id = int(regex_id.group(1))
        return await ctx.bot.fetch_user(id)
    except:
        return None

bot.run(credentials['token'])