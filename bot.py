import discord, os, sys
from discord.ext import commands, tasks
from itertools import cycle

# 명령어 설정
bot = commands.Bot(command_prefix = '복실아 ') 

# 상태 메시지 리스트
playing = cycle(['BL만화 감상', '공부', '유튜브 시청', '넷플릭스 시청', '디씨', '트위터'])

# 금지어
badtalk = ['씨발', '시발', '개새끼', '병신', '느금']

# 1시간마다 상태 변경
@tasks.loop(hours=1)
async def change_status():  
  await bot.change_presence(activity=discord.Game(next(playing)))

@bot.event
async def on_ready():
  change_status.start() 
  print(f'--- 연결 성공 ---')
  print(f'봇 이름: {bot.user.name}')

# 인사
@bot.command(name='안녕')
async def hello(ctx):
  await ctx.send('안녕')

# 인성질
@bot.command(name='뭐해')
async def whatrudoing(ctx):
  await ctx.send('혹시 네 눈은 데코레이션이니? 내 상태 메시지를 보면 되잖아')

# 금지어들 알려주기
@bot.command(name='금지어')
async def badtalking(ctx):
  notice = '금지어는 '
  for word in badtalk:
    notice += '\"'
    notice += word
    notice += '\", '
  notice = notice[:-2]
  notice += ' 이상이야'
  await ctx.send(notice)

# 글삭튀 검거
@bot.event
async def on_message_delete(message):
  bad = False
  for word in badtalk:
    if word in message.content:
      bad = True
  if not bad:
    await message.channel.send('내가 봤는데 ' + str(message.author) + ' 얘가 \"' + message.content + '\" 쓰고 글삭튀 했어')

# 글수정 검거
@bot.event
async def on_message_edit(before, after):
  bad = False
  for word in badtalk:
    if word in before.content:
      bad = True
    elif word in after.content:
      bad = True
  if not bad:
	  await before.channel.send('내가 봤는데 ' + str(after.author)  + ' 얘가 \"' + before.content + "->" + after.content + '\" 이렇게 수정했어')

# 환영 인사
@bot.event
async def on_member_join(member):  
  channel = discord.utils.get(member.guild.text_channels, name='welcome')
  await channel.send('어서 와, 난 복실 개구리야.')

# 검열
@bot.event
async def on_message(message):
  message_content = message.content
  bad = False
  for word in badtalk:
    if word in message_content and str(message.author) != '복실 개구리#0898':
      bad = True
  if bad:
    await message.channel.send('나쁜 말 하지마 :(')
    await message.delete()
  await bot.process_commands(message)



bot.run(os.environ['token'])
