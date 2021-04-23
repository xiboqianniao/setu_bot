from hoshino import R, aiorequests
from hoshino.typing import Union
from hoshino.Gm import Gm
from urllib.parse import unquote
from random import choice
import time
score_class = {
        '0': 0,
        '1': 1,
        '2': 2,
        '4': 3,
        '8': 4,
        '16': 5,
        '32': 6,
        '64': 7}


class Config():
    data = R.data('setu_test/config.json', 'json')
    if not data.exist:
        data.write({
            'host': r'http://saki.fumiama.top/',
            'online': True,
            'key': '', # 在这里填入密码
            'sign': 'signup',
            'get': 'pick?',
            'score': 'vote',
            'up': 'upload?uuid='
        })
    config = data.read

    @property
    def host(self):
        return self.config['host']

    @property
    def online(self):
        return self.config['online']

    @property
    def key(self):
        return int.from_bytes(
            self.config['key'].encode("utf-16-be"), byteorder='big')

    def value(self, key):
        return self.config[key]

    def set(self, name, value):
        self.config[name] = value
        self.data.write(self.config)

    @property
    def signurl(self):
        signkey = self.key ^ int(time.time())
        return self.host+self.value('sign')+'?{:0>10d}'.format(signkey)

    def pickurl(self, name):
        return self.host+self.value('get')+name

    def scoreurl(self, name, img, score):
        img = img.split('.')[0]
        return self.host+self.value(
            'score')+f'?uuid={name}&img={img}&class={score}'

    def upurl(self, name):
        return self.host+self.value('up')+name


class User():
    data = R.data('setu_test/user.json', 'json')
    if not data.exist:
        data.write({'00000': {
            'name': '',
            'gcount': 0,
            'scount': 0,
            'ucount': 0,
            'uimg': [],
            'simg': {
                'online': [],
                'offline': []
        }}})
    user = data.read

    def __init__(self, uid: int) -> None:
        self.uid = str(uid)
        if self.uid not in self.user:
            self.user[self.uid] = {
                'name': '',
                'gcount': 0,
                'scount': 0,
                'ucount': 0,
                'uimg': [],
                'simg': {
                    'online': [],
                    'offline': []
                }}
            self.save
        self.name = self.user[self.uid]['name']

    def count(self, ctype: str) -> int:
        if ctype in ['get']:
            ctype = 'g'
        elif ctype in ['score']:
            ctype = 's'
        elif ctype in ['upload']:
            ctype = 'u'
        return self.user[self.uid][ctype+'count']

    @property
    def save(self):
        self.data.write(self.user)

    @property
    async def getname(self) -> str:
        if self.name == '':
            resp = await aiorequests.get(Config().signurl)
            self.name = await resp.text
            self.user[self.uid]['name'] = self.name
            self.save
        return self.name

    def addcount(self, ctype: str, num: int = 1) -> None:
        if ctype in ['get']:
            ctype = 'g'
        elif ctype in ['score']:
            ctype = 's'
        elif ctype in ['upload']:
            ctype = 'u'
        self.user[self.uid][ctype+'count'] += num
        self.save

    def addscinfo(self, img: str, ptype: str = 'on') -> None:
        if img not in self.user[self.uid]['simg'][ptype+'line']:
            self.addcount('s')
            self.user[self.uid]['simg'][ptype+'line'].append(img)
            self.save
            return True
        return False

    def addupinfo(self, img: str):
        self.user[self.uid]['uimg'].append(img)
        self.save

    @property
    def get_scored_img(self):
        return self.user[self.uid]['simg']['offline']

    @property
    async def nickname(self) -> str:
        if 'nickname' not in self.user[self.uid]:
            self.user[self.uid]['nickname'] = await Gm.user_info(
                                                        int(self.uid), 'nickname')
            self.save
        return self.user[self.uid]['nickname']

    @property
    def avator(self):
        return f'http://q1.qlogo.cn/g?b=qq&nk={self.uid}&s=1'


class Rec():
    data = R.data('setu_test/rec.json', 'json')
    if not data.exist:
        cont = {'data': {}, 'tem': []}
        data.write(cont)
    rec = data.read
    maxrec = 250
    popn = 50

    @classmethod
    def save(self):
        self.data.write(self.rec)

    @classmethod
    def add(self,
            msgid: int,
            img,
            online: bool = True
            ) -> None:
        self.rel()
        if isinstance(img, str):
            img = (img, )
        self.rec['data'][str(msgid)] = {'img': img, 'online': online}
        self.rec['tem'].append(str(msgid))
        self.save()

    @classmethod
    def rel(self):
        if len(self.rec['tem']) > self.maxrec:
            list(map(self.rec['data'].pop, self.rec['tem'][:self.popn]))
            self.rec['tem'] = self.rec['tem'][self.popn:]
            self.save()

    @classmethod
    def get(self, msgid: int) -> dict:
        return self.rec['data'][str(msgid)] if str(msgid) in self.rec['data'] else False

    @classmethod
    def clone(self, msgid: int, oid: int):
        cache = self.rec['data'][str(oid)]
        self.add(msgid, cache['img'], cache['online'])


class Pic():
    score_class = {
        '0': 0,
        '1': 1,
        '2': 2,
        '4': 3,
        '8': 4,
        '16': 5,
        '32': 6,
        '64': 7}
    data = R.data('setu_test/data.json', 'json')
    if not data.exist:
        data.write({
            'online': 0,
            'offline': 0,
            'onlinepic': {},
            'offlinepic': {}
        })
    pics = data.read

    @classmethod
    def save(self):
        self.data.write(self.pics)

    @classmethod
    def addpic(self, img: str, ptype: bool = 'on', **info) -> bool:
        if img not in self.pics[ptype+'linepic']:
            self.pics[ptype+'line'] += 1
            info['score'] = {}
            self.pics[ptype+'linepic'][img] = info
            self.save()
            return True
        return False

    @classmethod
    async def scorepic(
            self, uid: int, score: int, img: str, ptype: str = 'on') -> str:
        user = User(uid)
        user.addscinfo(img, ptype)
        self.pics[ptype+'linepic'][img]['score'][user.uid] = score
        self.save()
        if ptype == 'on' and Config().online:
            name = await user.getname
            url = Config().scoreurl(name, img, score)
            resp = await aiorequests.get(url)
            resp = await resp.text
            return resp
        else:
            return 'succ'

    @classmethod
    async def getpic(self, uid: int, online: bool = True) -> tuple:
        user = User(uid)
        if self.pics['offline'] < 10:
            online = True
        if len(user.get_scored_img) > self.pics['offline']:
            online = True
        if online and Config().online:
            url = Config().pickurl(await user.getname)
            resp = await aiorequests.get(url)
            img = await resp.text
            imgname = f'{unquote(img)}.webp'
            pic = R.tem_img('setu_test/online', imgname)
            if self.addpic(imgname):
                await pic.download(Config().host+img)
            source = 'powered by '+Config().host
        else:
            allpic = set(self.pics['offlinepic'].keys())
            unspic = allpic.difference(set(user.get_scored_img))
            if not unspic:
                return
            imgname = choice(list(unspic))
            pic = R.tem_img('setu_test/upload', imgname)
            upid = self.pics['offlinepic'][imgname]['uid']
            nickname = await User(upid).nickname
            source = f'uploader: {nickname}({upid})'
        user.addcount('g')
        pic = f'{pic.cqcode}\n{source}'
        return (pic, (imgname, online))

    @classmethod
    async def uppic(self, uid: int, msgid: int, imginfo: dict):
        user = User(uid)
        upcount = 0
        upedimg = []
        for imgname in imginfo:
            img = await R.tem_img(
                'setu_test/upload', imgname).download(imginfo[imgname])
            imgname = img.path.split('\\')[-1]
            upedimg.append(imgname)
            with open(img.path, 'rb') as f:
                url = Config().upurl(await user.getname)
                resp = await aiorequests.post(url, data=f)
                resp = await resp.text
            if self.addpic(imgname, 'off',
                           uid=uid,
                           uptime=time.asctime()) or resp == 'succ':
                upcount += 1
                user.addupinfo(imgname)
        user.addcount('u', upcount)
        Rec.add(msgid, tuple(upedimg), False)
        return upcount


class PicListener:
    def __init__(self):
        self.on = {}
        self.rec = {}

    def get_on_off_status(self, gid, uid):
        if gid not in self.on:
            self.on[gid] = []
            return False
        else:
            return uid in self.on[gid]

    def turn_on(self, gid, uid):
        if gid not in self.on:
            self.on[gid] = [uid]
        else:
            self.on[gid].append(uid)

    def turn_off(self, gid, uid):
        if gid not in self.on:
            self.on[gid] = []
        elif uid in self.on[gid]:
            self.on[gid].remove(uid)

    def arec(self, uid, img, online):
        online = 'on' if online else 'off'
        self.rec[uid] = (img, online)

    def getrec(self, uid):
        return self.rec[uid] if uid in self.rec else None


async def scoreall(uid: int, msgid: int, score: list) -> Union[tuple, list]:
    imgs = Rec.get(msgid)
    if len(imgs['img']) == len(score):
        ptype = 'on' if imgs['online'] else 'off'
        resp = []
        for img, s in zip(imgs['img'], score):
            resp.append(
                await Pic.scorepic(uid, Pic.score_class[s], img, ptype))
        return resp if len(resp) > 0 else [False]
    return False, len(imgs['img']), len(score)
