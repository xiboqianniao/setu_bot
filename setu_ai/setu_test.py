import hoshino
from hoshino import Service, priv
from hoshino.typing import CQEvent
from hoshino.util import FreqLimiter
from .lib import User, Pic, Rec, scoreall, Config, PicListener, choice, Gm
HELP = '''自助评分终端机
[涩图] 叫一份涩图
[<回复图片> 打分x] 为涩图打分
ps：只支持打0，1，2，4，8，16，32，64分
[上传图片] 附带图片即可上传，如果不带图片则开启上传模式
ps：上传模式中发送的图片都会上传
[网页端] 获得网页端地址
[涩批信息] 获得个人一些简单的统计信息
====
私聊bot：
[开始评分] 进入高效打分模式
高效打分模式下直接回复分数，打分后立刻发送下一张图
[结束评分] 结束高效打分模式
'''
sv = Service('setu_ai', bundle='setu', help_=HELP)

_freq = FreqLimiter(2.5)
pls = PicListener()
Config = Config()


@sv.on_rex(r'^(([色涩瑟]图)|setu)|[来发给]((?P<num>\d+)|(?:.*))[张个幅点份丶][色涩瑟]图?$')
async def checkswitch(bot, ev: CQEvent):
    uid = ev.user_id
    if not _freq.check(uid):
        await bot.finish(ev, '您冲得太快了，请慢一点💦')
    _freq.start_cd(uid)
    num = ev['match'].group('num')
    if num:
        try:
            num = int(num)
            max_num = 5
            if num > max_num:
                await bot.send(ev, f'太贪心辣,一次只能要{max_num}份涩图哦~')
                num = max_num
            else:
                pass
        except:
            num = 1
    else:
        num = 1
    for _ in range(num):
        online = choice((True, False))
        if (pic := await Pic.getpic(uid, online)) is None:
            await bot.finish(ev, '已经没有更多图片了！')
        msginfo = await bot.send(ev, pic[0])
        Rec.add(msginfo['message_id'], *pic[1])


@sv.on_replay(startwith='打分')
async def testrep(bot, ev: CQEvent):
    msgid = ev['quote_message']['message_id']
    if not Rec.get(msgid):
        return
    uid = ev.user_id
    if not _freq.check(uid):
        await bot.finish(ev, '您冲得太快了，请慢一点💦')
    _freq.start_cd(uid)
    kw = ev['rep_message'].extract_plain_text().strip().split()
    for i in kw:
        if i not in Pic.score_class:
            await bot.finish(ev, '💦只支持评价0, 1, 2, 4, 8, 16, 32, 64分哦')
    resp = await scoreall(uid, msgid, kw)
    if not resp[0]:
        await bot.finish(ev, f'{resp[1]}张图片只收到了{resp[2]}个评分')
    msg = []
    count = 0
    for i, res in enumerate(resp):
        if res == 'succ':
            count += 1
        else:
            msg.append(f'{f"第{i+1}张图片" if len(resp) > 1 else ""}评价失败惹...{res}')
    if count:
        msg.append(f'{f"{count}张图片" if count > 1 else ""}评价成功！感谢反馈')
    Rec.clone(ev.message_id, msgid)
    await bot.send(ev, '\n'.join(msg))


@sv.on_suffix(('上传图片', '上传'))
@sv.on_prefix(('上传图片', '上传'))
async def upload(bot, ev: CQEvent):
    imginfo = {}
    uid = ev.user_id
    for i in ev.message:
        if i['type'] == 'image':
            imginfo[i['data']['file']] = i['data']['url']
    if imginfo:
        count = await Pic.uppic(uid, ev.message_id, imginfo)
        a = '张' if count < 2 else '些'
        await bot.finish(ev, f'成功上传{count}张图片, 现在可以回复这{a}图片打分了')
    else:
        gid = ev.group_id
        kw = ev.message.extract_plain_text().strip()
        if pls.get_on_off_status(gid, uid):
            if kw in ('关闭', '停止', '结束'):
                pls.turn_off(gid, uid)
                await bot.finish(ev, "上传模式已关闭！💤")
            await bot.finish(ev, "您已经在上传模式下啦！\n如想退出上传模式请发送“结束上传”~")
        elif kw == '':
            pls.turn_on(gid, uid)
            await bot.send(ev, "✨了解～请发送图片吧！支持批量噢！\n如想退出上传模式请发送“结束上传”~")


@sv.on_message('group')
async def picmessage(bot, ev: CQEvent):
    uid = ev.user_id
    if not pls.get_on_off_status(ev.group_id, uid):
        return
    imginfo = {}
    for i in ev.message:
        if i['type'] == 'image':
            imginfo[i['data']['file']] = i['data']['url']
    if imginfo:
        count = await Pic.uppic(uid, ev.message_id, imginfo)
        a = '张' if count < 2 else '些'
        await bot.send(ev, f'成功上传{count}张图片🎈, 现在可以回复这{a}图片打分了')

hbot = hoshino.get_bot()
@hbot.on_message('private')
async def picmessagep(ev):
    uid = ev.user_id
    if str(ev.message) in ('开始评分', '开始'):
        pls.turn_on(0, uid)
        await hbot.send(ev, '🎉无情评价机器启动！私聊模式直接回复分数，打分后立刻下一张图\n结束打分请发送“结束”')
    elif str(ev.message) in ('结束', '结束评分'):
        pls.turn_off(0, uid)
        pls.rec[uid] = ()
        await hbot.send(ev, '已结束💤')
    if not pls.get_on_off_status(0, uid):
        return
    if info := pls.getrec(uid):
        msg = str(ev.message).strip().strip('打分').strip('分')
        if msg in Pic.score_class:
            resp = await Pic.scorepic(
                uid, Pic.score_class[msg], info[0], info[1])
            if resp == 'succ':
                await hbot.send(ev, '评价成功！感谢反馈')
            else:
                await hbot.send(ev, f'评价失败惹...{resp}')
        else:
            await hbot.finish(ev, '💦只支持评价0, 1, 2, 4, 8, 16, 32, 64分哦')
    online = choice((True, False))
    await hbot.send(ev, '💦正在扒拉图片...')
    if (pic := await Pic.getpic(uid, online)) is None:
        await hbot.finish(ev, '已经没有更多图片了！')
        pls.turn_off(0, uid)
    await hbot.send(ev, pic[0])
    pls.arec(uid, *pic[1])

@sv.on_fullmatch(('网页版', '网页端'))
async def rhost(bot, ev: CQEvent):
    await bot.send(ev, Config.host)


@sv.on_suffix('在线模式')
async def setv(bot, ev: CQEvent):
    if not priv.check_priv(ev, priv.ADMIN):
        return
    kw = ev.message.extract_plain_text().strip()
    if kw in ('开启'):
        online = True
    elif kw in ('关闭'):
        online = False
    Config.set('online', online)
    await bot.send(ev, '已'+kw)


@sv.on_prefix(('色批信息', '涩批信息'))
async def spinfo(bot, ev: CQEvent):
    for _ in ev.message:
        if _['type'] == 'at' and _['data']['qq'] != 'all':
            uid = int(_['data']['qq'])
            info = await Gm(ev).member_info(uid)
            name = info['card'] or info['nickname']
            break
    else:
        uid = ev.user_id
        name = ev.sender['card'] or ev.sender['nickname']
    if uid == ev.self_id:
        non = Pic.pics['online']
        noff = Pic.pics['offline']
        online = '开启✨' if Config.online else '关闭💤'
        _spinfo = f'在线模式已{online}\n已从服务器获取{non}份涩图\n已从群友处获取{noff}份涩图\n本插件已以GPL3.0开源https://github.com/LHXnois/setu_ai'
    else:
        user = User(uid)
        uuid = await user.getname
        gc = user.count('g')
        uc = user.count('u')
        sc = user.count('s')
        _spinfo = f'{name}({uid})：\n网页端用户名：{uuid}\n共叫了{gc}份涩图💦\n上传了{uc}份涩图🎈\n为{sc}份涩图打了分✔'
    await bot.send(ev, _spinfo)
