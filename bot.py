import discord, os, sys
from discord.ext import commands, tasks
from itertools import cycle

import requests
import random

# 명령어 설정
bot = commands.Bot(command_prefix = '복실아 ') 

# API키 설정
yt_api_key = os.environ['yt_api_key']
riot_api_key = os.environ['riot_api_key']

# 상태 메시지 리스트
playing = cycle(['남자친구랑 BL 감상', '여자친구랑 공부', '유튜브 시청', '여자친구랑 데이트', '여자친구랑 디씨', '여자친구랑 트위터'])

# 금지어
bad_word = ['씨발', '시발', '개새끼', '병신', '느금', '범성']

# 젠더 혐오발언
gender_hate = ['한남', '소추', '한녀', '김치녀']

# 노래추천 플레이리스트
pl_ids = {
'ff' : {
  '칼바람곡' : 'PLvQ2Ez_GF9ibjUabkEvFE1JPANErbsEj5',
  '롤곡' : 'PLvQ2Ez_GF9iZI_wXMLU0GZ6cisl5lM8b3',
  '오타쿠감성' : 'PLvQ2Ez_GF9ibBCPBxCzriMM6c5b6Pznc4'
},
'dm' : {
  '레오루' : 'PLfjCwAm4j423Kd-5IhURFOEr2BvkMSDyY',
  '빈지노' : 'PLfjCwAm4j423xlXXJnOU-lZzfArMm5fbO',
  '씹덕' : 'PLfjCwAm4j422tRqJ7SIeKP5MGmWqV-CaR',
  '아이유' : 'PLfjCwAm4j421brs50DpRGQYZQJQCzoHqd'
},
'jm' : {
  '띵곡' : 'PLwctH09-BYf1zsD8FPeDVm6xjEKS9zkAn'
}}

# 현재 상태
doing_now = ''

# 1시간마다 상태 변경
@tasks.loop(hours=1)
async def change_status():  
  doing_now = next(playing)
  await bot.change_presence(activity=discord.Game(doing_now))

@bot.event
async def on_ready():
  change_status.start() 
  print(f'--- 연결 성공 ---')
  print(f'봇 이름: {bot.user.name}')

# 인사
@bot.command(name='안녕')
async def hello(ctx):
  await ctx.send('안녕')

# 머해
@bot.command(name='뭐해')
async def doing(ctx):  
  msg = doing_now + '하고 있어'
  await ctx.send(msg)

# 금지어들 알려주기
@bot.command(name='금지어')
async def ban_word(ctx):
  notice = '금지어는 '
  for word in bad_word:
    notice += '\"'
    notice += word
    notice += '\", '
  for word in gender_hate:
    notice += '\"'
    notice += word
    notice += '\", '
  notice = notice[:-2]
  notice += ' 이상이야'
  await ctx.send(notice)

# 노래 추천
def song_recmd(name, name_initial, pl_title):  
  if pl_title in pl_ids[name_initial].keys():
    pl_id = pl_ids[name_initial][pl_title]
  else:
    notice = name + '의 재생목록은'
    for word in pl_ids[name_initial].keys():
      notice += '\n * '
      notice += word
    notice += '\n이상이야' 
    return notice, False
  get_pl_url = 'https://www.googleapis.com/youtube/v3/playlistItems?part=snippet&playlistId=' + pl_id + '&maxResults=50&key=' + yt_api_key
  pl_items = requests.get(get_pl_url).json()['items']
  item_vids = []
  for item in pl_items:
      item_vids.append('https://www.youtube.com/watch?v=' + item['snippet']['resourceId']['videoId'] + '&list=' + pl_id)
  return item_vids[random.randint(0, len(pl_items) - 1)], True

@bot.command(name='복실추천곡')
async def ff_song_recmd(ctx, pl_title = ''):
  recmd, success = song_recmd('복실이', 'ff', pl_title)
  await ctx.send(recmd)  
  if success:
    await ctx.send('이 노래는 어때?')

@bot.command(name='돌몽추천곡')
async def dm_song_recmd(ctx, pl_title = ''):
  recmd, success = song_recmd('돌몽이', 'dm', pl_title)
  await ctx.send(recmd)  
  if success: 
    await ctx.send('돌몽 : (대충 란 내 노래를 들어 콘)')

@bot.command(name='진목추천곡')
async def jm_song_recmd(ctx, pl_title = ''):
  recmd, success = song_recmd('진모쿠', 'jm', pl_title)
  await ctx.send(recmd)  
  if success:
    await ctx.send('진목 : 띵곡이다 들어라')

# 롤 전적 조회
@bot.command(name='롤')
async def get_lol_match_data(ctx, summoner_name = '', n_match = 1):
  n_match = int(n_match)
  if summoner_name == '':
    await ctx.send('복실아 롤 [소환사이름] [조회할 경기 수(1 ~ 10, default : 1)]')
  elif n_match < 1 or n_match > 10:
    await ctx.send('조회 가능한 경기 수는 최소 1, 최대 10이야')
  else:
    url_puu_id = 'https://kr.api.riotgames.com/lol/summoner/v4/summoners/by-name/' + summoner_name + '?api_key=' + riot_api_key
    puu_id_r = requests.get(url_puu_id)
    if puu_id_r.status_code == 200:
      puu_id = puu_id_r.json()['puuid']
      # 최근 n 경기 matchId 얻기
      url_match_id = 'https://asia.api.riotgames.com/lol/match/v5/matches/by-puuid/' + puu_id + '/ids?start=0&count=' + str(n_match) + '&api_key=' + riot_api_key    
      match_ids = requests.get(url_match_id).json()  
      for i in range(n_match):        
        match_id = match_ids[i]        
        # matchId로 경기 정보 가져오기
        url_match = 'https://asia.api.riotgames.com/lol/match/v5/matches/' + match_id + '?api_key=' + riot_api_key
        match = requests.get(url_match).json()          
        # participants 부분의 내가 입력한 소환사 정보만 가져오기
        info_participants = match['info']['participants']
        for participant in info_participants:
          if participant['summonerName'] == summoner_name:
            summoner = participant
            break          
        # 게임 모드 가져오기
        game_mode = match['info']['gameMode']
        # 소환사 픽한 챔피언, 라인, 승패 정보 가져오기
        champion = summoner['championName']
        lane = summoner['lane']
        win = 'WIN! :D'
        if summoner['win'] == False:
          win = 'Lose... :('          
        # 소환사 킬뎃 가져오기
        kills = summoner['kills']
        deaths = summoner['deaths']
        assists = summoner['assists']
        msg = '================================\n'
        msg = msg + '{}\nGameMode : {}\nChampion : {}\nLane : {}\nkills : {} / deaths : {} / assists : {}\n'.format(win, game_mode, champion, lane, kills, deaths, assists)
        msg = msg + '================================'     
        await ctx.send(msg)
    elif puu_id_r.status_code == 404:
      await ctx.send('소환사 이름 틀린 것 같은데?')
    elif puu_id_r.status_code == 403:
      await ctx.send('API KEY 만료됐나 봐, 돌몽이한테 알려줘')
    else:
      await ctx.send('요청 실패! 돌몽이 불러')    

@bot.command(name = '주사위')
async def dice(ctx):
  await ctx.send('얍!')
  await ctx.send('나온 숫자는 {}!'.format(random.randint(1, 6)))
  
# 글삭튀 검거
@bot.event
async def on_message_delete(message):
  bad = False
  ban_word = bad_word + gender_hate
  for word in ban_word:
    if word in message.content:
      bad = True    
  if not bad:
    await message.channel.send('내가 봤는데 ' + str(message.author) + ' 얘가 \"' + message.content + '\" 쓰고 글삭튀 했어')

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
  warning = ''

  for word in bad_word:
    if word in message_content and str(message.author) != '복실 개구리#0898':
      bad = True
      warning = '나쁜 말 하지마!'

  for word in gender_hate:
    if word in message_content and str(message.author) != '복실 개구리#0898':
      bad = True
      warning = '젠더 혐오발언 금지!'  

  if bad:
    await message.channel.send(warning)
    await message.delete()

  await bot.process_commands(message)



bot.run(os.environ['token'])
