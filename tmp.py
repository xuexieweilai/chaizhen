#!/usr/bin/env python
# -*- coding: utf-8 -*-
import argparse
import os
import shutil
import webbrowser
import time
from sys import stdout, modules

from PIL import Image

__author__ = 'litang.wang'

seq = os.path.sep

nOpen = {}

nl = '\n'
doctype = '<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Strict//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-strict.dtd">\n'
charset = '<meta http-equiv="Content-Type" content="text/html;charset=utf-8" />\n'

tags = ['html', 'body', 'head', 'link', 'meta', 'div', 'p', 'form', 'legend',
        'input', 'select', 'span', 'b', 'i', 'option', 'img', 'script',
        'table', 'tr', 'td', 'th', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6',
        'fieldset', 'a', 'title', 'body', 'head', 'title', 'script', 'br',
        'ul', 'li', 'ol', 'pre', 'style', 'font', 'button']

selfClose = ['input', 'img', 'link', 'br']


class Tag(list):
    tagname = ''

    def __init__(self, *arg, **kw):
        self.attributes = kw
        if self.tagname:
            name = self.tagname
            self.isSeq = False
        else:
            name = 'sequence'
            self.isSeq = True
        self.id = kw.get('id', name)
        # self.extend(arg)
        for a in arg: self.addObj(a)

    def __iadd__(self, obj):
        if isinstance(obj, Tag) and obj.isSeq:
            for o in obj: self.addObj(o)
        else:
            self.addObj(obj)
        return self

    def addObj(self, obj):
        if not isinstance(obj, Tag): obj = unicode(obj)
        id = self.setID(obj)
        setattr(self, id, obj)
        self.append(obj)

    def setID(self, obj):
        if isinstance(obj, Tag):
            id = obj.id
            n = len([t for t in self if isinstance(t, Tag) and t.id.startswith(id)])
        else:
            id = 'content'
            n = len([t for t in self if not isinstance(t, Tag)])
        if n: id = '%s_%03i' % (id, n)
        if isinstance(obj, Tag): obj.id = id
        return id

    def __add__(self, obj):
        if self.tagname: return Tag(self, obj)
        self.addObj(obj)
        return self

    def __lshift__(self, obj):
        self += obj
        if isinstance(obj, Tag): return obj

    def render(self):
        result = ''
        if self.tagname:
            result = '<%s%s%s>' % (self.tagname, self.renderAtt(), self.selfClose() * ' /')
        if not self.selfClose():
            for c in self:
                if isinstance(c, Tag):
                    result += c.render()
                else:
                    result += c
            if self.tagname:
                result += '</%s>' % self.tagname
        result += '\n'
        return result

    def renderAtt(self):
        result = ''
        for n, v in self.attributes.iteritems():
            if n != 'txt' and n != 'open':
                if n == 'cl': n = 'class'
                result += ' %s="%s"' % (n, v)
        return result

    def selfClose(self):
        return self.tagname in selfClose


def TagFactory(name):
    class f(Tag):
        tagname = name

    f.__name__ = name
    return f


thisModule = modules[__name__]

for t in tags: setattr(thisModule, t, TagFactory(t))


def ValidW3C():
    out = a(img(src='http://www.w3.org/Icons/valid-xhtml10', alt='Valid XHTML 1.0 Strict'),
            href='http://validator.w3.org/check?uri=referer')
    return out


class PyH(Tag):
    tagname = 'html'

    def __init__(self, name='MyPyHPage'):
        self += head()
        self += body()
        self.attributes = dict(xmlns='http://www.w3.org/1999/xhtml', lang='en')
        self.head += charset
        self.head += title(name)

    def __iadd__(self, obj):
        if isinstance(obj, head) or isinstance(obj, body):
            self.addObj(obj)
        elif isinstance(obj, meta) or isinstance(obj, link):
            self.head += obj
        else:
            self.body += obj
            id = self.setID(obj)
            setattr(self, id, obj)
        return self

    def addJS(self, *arg):
        for f in arg: self.head += script(type='text/javascript', src=f)

    def addCSS(self, *arg):
        for f in arg: self.head += link(rel='stylesheet', type='text/css', href=f)

    def printOut(self, file=''):
        if file:
            f = open(file, 'w')
        else:
            f = stdout
        f.write(doctype)
        f.write(self.render().encode('utf-8'))
        f.flush()
        if file: f.close()


def list_to_normal_report(dest_path, count, base_list, take_list, auto_open):
    page = PyH("report")
    wrap = page << div()
    key_div = wrap << div(cl='result')
    key_div << h2(u"关键点：", cl='result')

    for base in base_list:
        key_div << button(str(base), onclick="window.location.href='#{}';".format(base))

    result_div = page << div()
    start_div = result_div << div(cl='result')
    start_div << h2(u'起始帧：', cl='result')
    start_div << input(value=take_list[0], id='start', cl='result', onblur="caculate()")

    end_div = result_div << div(cl='result')
    end_div << h2(u'终止帧：', cl='result')
    end_div << input(value=take_list[-1], id='end', cl='result', onblur="caculate()")

    count_div = result_div << div(cl='result')
    count_div << h2(u'帧数：', cl='result')
    count_div << h2(0, id='count', cl='result')

    cost_div = result_div << div(cl='result')
    cost_div << h2(u'耗时：', cl='result')
    cost_div << h2('0ms', id='cost', cl='result')

    add_css(page)
    add_js(page)

    table1 = page << div(style="overflow-x: scroll") << table(border='1', id='mytable', cellpadding="8")

    tr2 = table1 << tr()
    for i in range(1, count, 1):

        if i in base_list:
            td1 = tr2 << td(id=str(i), cl='selected')
        else:
            td1 = tr2 << td(id=str(i))
        td1 << img(src='%05d.png' % i, height='512', width='288')
        td1 << h2('{}'.format(i))
        button_div = td1 << div()
        button_div << button(u'设为起始帧', onclick="setStart({})".format(i))
        button_div << button(u'设为终止帧', onclick="setEnd({})".format(i))

    page.printOut(dest_path)
    print 'report_path: file://{}'.format(os.path.abspath(dest_path))
    if auto_open:
        b = webbrowser.get()
        b.open('file://{}'.format(os.path.abspath(dest_path)))


def add_css(page):
    page.head << style('''
    html,  body,  div,  span,  object, h1,  h2,  h3,  h4,  h5,  h6,  p,  blockquote,  pre,  abbr,  address,  cite,  code,  del,  dfn,  em,  img,  ins,  kbd,  q,  samp,  small,  strong,  sub,  sup,  var,  b,  i,  dl,  dt,  dd,  ol,  ul,  li,  fieldset,  form,  label,  legend,  table,  caption,  tbody,  tfoot,  thead,  tr,  th,  td {
        margin: 3px;
        padding: 3px;
        border: 0;
        outline: 0;
        font-size: 100%;
        vertical-align: baseline;
        background: transparent;
        text-align: center;
        overflow: auto;
    }

     body {
        margin: 0;
        padding: 0;
        font: 12px/15px "Helvetica Neue", Arial, Helvetica, sans-serif;
        color: #555;
        background: #f5f5f5;
    }

     h1 {
        margin-top: 1em;
        padding: 0;
        font: 20px "Helvetica Neue", Arial, Helvetica, sans-serif;
        color: #555;
        text-align: center;
    }

     h2 {
        padding: 0;
        font: 18px "Helvetica Neue", Arial, Helvetica, sans-serif;
        color: #555;
        text-align: center;
    }

     h3 {
        padding: 0;
        font: 10px "Helvetica Neue", Arial, Helvetica, sans-serif;
        color: #555;
        text-align: center;
    }
     a {
        padding: 0;
        font: 18px "Helvetica Neue", Arial, Helvetica, sans-serif;
        color: #555;
        text-align: left;
    }

     p {
        font: 13px "Helvetica Neue", Arial, Helvetica, sans-serif;
        margin-bottom: 0;
    }

     table {
        width: 90%;
        margin: 10px auto 10px;
        overflow: hidden;
        border: 1px solid #d3d3d3;
        background: #fefefe;
        -moz-border-radius: 5px;
        -webkit-border-radius: 5px;
        border-radius: 5px;
    }

     th {
        padding: 18px 18px 18px;
        text-align: center;
        vertical-align: middle;
        background: #e8eaeb;
    }

     td {
        padding: 8px 10px 8px;
        text-align: center;
        vertical-align: middle;
    }

     td {
        border-top: 1px solid #e0e0e0;
        border-right: 1px solid #e0e0e0;
    }

     td.x_last {
        border-right: none;
    }

     tr.x_even-row td {
        background: #f6f6f6;
    }

    #wrap{
        background-color: rgba(255,255,255,0.9);
        width: 100%;
        height: 50px;
    }
    .selected{
        background-color: rgba(210,210,210,1);
    }
    .result{
        float:left;
        margin-top: 0px;
        margin-bottom: 0px;
        padding-bottom: 0px;
        padding-top: 2px;
    }

    input{
        height: 20px;
        width: 40px;
        border: 1px solid #ccc;
        padding: 7px 0px;
        border-radius: 3px;
        padding-left:5px;
    }

    #wrap[data-fixed="fixed"]{
        position: fixed;
        top:0;
        left: 0;
        margin: 0;
    }
    ''', type="text/css")


def add_js(page):
    page.head << script(
        '''
        function ceiling(obj) {
            var ot = obj.offsetTop;
            document.onscroll = function () {
                var st = document.body.scrollTop || document.documentElement.scrollTop;
                obj.setAttribute("data-fixed",st >= ot?"fixed":"");
            }
        }

        function setStart(i) {
            var start=document.getElementById("start");
            start.value=i;
            caculate()
        }

        function setEnd(i) {
            var end=document.getElementById("end");
            end.value=i;
            caculate()
        }

        function caculate(){
            var start=document.getElementById("start");
            var end=document.getElementById("end");
            var count=document.getElementById("count");
            var cost=document.getElementById("cost");
            count.innerHTML=end.value-start.value;
            cost.innerHTML=Math.round(count.innerHTML*33.33)+' ms';
        }

        document.onload=function () {
            caculate()
        }

        window.onload = function () {
            //var wrap = document.getElementById("wrap");
            //ceiling(wrap);
            caculate()
        };
        ''',
        type='text/javascript'
    )


def delete_dir(dir):
    shutil.rmtree(dir, True)


def mkdir(dir):
    if os.path.exists(dir):
        delete_dir(dir)
    os.mkdir(dir)


def make_regalur_image(img, size=(360, 640)):
    return img.resize(size).crop((0, 20, 360, 640)).convert('RGBA')


def split_image(img, part_size=(36, 62)):
    w, h = img.size
    pw, ph = part_size

    assert w % pw == h % ph == 0

    return [img.crop((i, j, i + pw, j + ph)).copy() \
            for i in xrange(0, w, pw) \
            for j in xrange(0, h, ph)]


def hist_similar(lh, rh):
    assert len(lh) == len(rh)
    result = sum(1 - (0 if l == r else float(abs(l - r)) / max(l, r)) for l, r in zip(lh, rh)) / len(lh)
    return result


def calc_similar(li, ri):
    all_similar = hist_similar(li.histogram(), ri.histogram())
    return all_similar * 0.3 + 0.7 * sum(
        hist_similar(l.histogram(), r.histogram()) for l, r in zip(split_image(li), split_image(ri))) / 100.0


def calc_similar_by_path(lf, rf):
    li, ri = make_regalur_image(Image.open(lf)), make_regalur_image(Image.open(rf))
    return calc_similar(li, ri)


def make_doc_data(lf, rf):
    li, ri = make_regalur_image(Image.open(lf)), make_regalur_image(Image.open(rf))
    li.save(lf + '_regalur.png')
    ri.save(rf + '_regalur.png')
    fd = open('stat.csv', 'w')
    fd.write('\n'.join(l + ',' + r for l, r in zip(map(str, li.histogram()), map(str, ri.histogram()))))
    fd.close()
    from PIL import ImageDraw
    li = li.convert('RGB')
    draw = ImageDraw.Draw(li)
    for i in xrange(0, 256, 64):
        draw.line((0, i, 256, i), fill='#ff0000')
        draw.line((i, 0, i, 256), fill='#ff0000')
    li.save(lf + '_lines.png')


def del_succession_item(data, step=3):
    for index, item in enumerate(data):
        count = 0
        i = index
        for i in range(index + 1, len(data)):
            if data[i] - data[i - 1] <= 2:
                count += 1
            else:
                break
        if count >= step:
            del data[index + 1:i - 1]

    return data


def comp_code(code1, code2):
    num = 0
    for index in range(0, len(code1)):
        if code1[index] != code2[index]:
            num += 1
    return num


seq = os.path.sep


def record_for_android(duration, record_video_path):
    os.system('adb shell screenrecord  --time-limit {} {} &'.format(duration, record_video_path))
    print('start recording')
    time.sleep(duration + 1)
    os.system('adb pull {record_video_path} result{seq}'.format(record_video_path=record_video_path, seq=seq))
    os.system('adb shell rm {} '.format(record_video_path))


def record_for_ios(duration, record_video_path):
    os.system('osascript ./record_for_ios.scpt {} {}'.format(record_video_path, duration))
    time.sleep(duration / 2)
    os.system('mv ~/Desktop/{} ./result/'.format(record_video_path))


def str_to_list(s):
    try:
        l = [int(i) for i in s.split(',')]
        if len(l) >= 2:
            return l[0:2]
        else:
            return None
    except Exception as e:
        return None


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-n', '--name', type=str, help='name')
    parser.add_argument('-d', '--duration', type=int, default=10, help='record video duratioin')
    parser.add_argument('-p', '--platform', type=str, help='platform:ios|android')
    parser.add_argument('-t', '--take', type=str_to_list, default=None,
                        help='take list of key frame index,split by ","')
    parser.add_argument('-o', '--open', action='store_true', default=False,
                        dest='auto_open',
                        help='open report automatically')
    args = parser.parse_args()

    print(args)
    name = args.name
    record_duration = args.duration
    platform = args.platform
    take = args.take
    auto_open = args.auto_open

    # name = 'kwai_open_camera_normal'
    # record_duration = 3
    # platform = 'ios'
    # take=None

    if not os.path.exists(os.path.abspath('result')):
        os.mkdir('result')

    pic_dir = os.path.abspath('result{seq}{name}'.format(name=name, seq=seq))

    # record video
    if platform == 'ios':
        video_path = os.path.abspath('result{seq}{name}.mov'.format(name=name, seq=seq))
        record_video_path = os.path.abspath('{}.mov'.format(name))
        record_for_ios(record_duration, record_video_path)
    else:
        video_path = os.path.abspath('result{seq}{name}.mp4'.format(name=name, seq=seq))
        record_video_path = '/sdcard/{}.mp4'.format(name)
        record_for_android(record_duration, record_video_path)

    # video to pic
    mkdir(pic_dir)
    os.system(
        'ffmpeg -i {video_path} -r 30 -f image2 {pic_dir}{seq}%05d.png'.format(video_path=video_path, pic_dir=pic_dir,
                                                                               seq=seq))

    # calculate similar
    count = len(filter(lambda x: x.endswith('.png'), os.listdir(pic_dir)))
    path = os.path.abspath('{pic_dir}{seq}%05d.png'.format(pic_dir=pic_dir, seq=seq))
    base = 1
    base_list = []
    for n in range(2, count):
        similarity = calc_similar_by_path(path % (base), path % (n)) * 100
        print('{} vs {}: {}'.format(base, n, similarity))
        if similarity < 87:
            base = n
            base_list.append(base)
    del_succession_item(base_list)

    # generate report
    if take and take[0] < take[1] < len(base_list):
        take_list = [base_list[take[0]], base_list[take[1]]]
    elif len(base_list) < 2:
        take_list = [0, 0]
    else:
        take_list = [base_list[0], base_list[-1]]

    list_to_normal_report(os.path.abspath('{pic_dir}{seq}index.html'.format(pic_dir=pic_dir, seq=seq)), count,
                          base_list, take_list, auto_open)
