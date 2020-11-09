import unittest
import re

rule = re.compile(r'(?P<file>.*)__(?P<width>\d*)x(?P<height>\d*).(?P<suffix>jpg|png|bmp|webp)$')


class TestImg(unittest.TestCase):
    def test_re1(self):
        s = 'testA/a.jpg__400x400.jpg'
        m = rule.match(s)
        r = m.groups()
        assert r == ('testA/a.jpg', '400', '400', 'jpg')

    def test_re2(self):
        s = 'testA/a.jpg__400x.jpg'
        m = rule.match(s)
        r = m.groups()
        assert r == ('testA/a.jpg', '400', '', 'jpg')

    def test_re3(self):
        s = 'testA/a.jpg__x400.jpg'
        m = rule.match(s)
        r = m.groups()
        assert r == ('testA/a.jpg', '', '400', 'jpg')

    def test_re4(self):
        s = 'testA/a.jpg__400x400.webp'
        m = rule.match(s)
        r = m.groups()
        assert r == ('testA/a.jpg', '400', '400', 'webp')

    def test_re5(self):
        s = 'testA/testB/a.jpg__400x400.jpg'
        m = rule.match(s)
        r = m.groups()
        assert r == ('testA/testB/a.jpg', '400', '400', 'jpg')

    def test_re6(self):
        s = 'testA/a.jpg__400x400.jpg__400x400.jpg'
        m = rule.match(s)
        r = m.groups()
        assert r == ('testA/a.jpg__400x400.jpg', '400', '400', 'jpg')

    def test_re7(self):
        s = 'testA/a.jpg__400xx400.jpg'
        m = rule.match(s)
        assert m is None

    def test_re8(self):
        s = 'testA/a.jpg__400x400.jpg.png'
        m = rule.match(s)
        assert m is None

    def test_re9(self):
        s = 'testA/a.jpg__400x400.jjppgg'
        m = rule.match(s)
        assert m is None

    def test_re10(self):
        s = 'testA/a.jpg__0x.jpg'
        m = rule.match(s)
        r = m.groups()
        assert r == ('testA/a.jpg', '0', '', 'jpg')

    def test_re11(self):
        s = 'testA/a.jpg__x0.jpg'
        m = rule.match(s)
        r = m.groups()
        assert r == ('testA/a.jpg', '', '0', 'jpg')

    def test_re12(self):
        s = 'testA/a.jpg__0x10.jpg'
        m = rule.match(s)
        r = m.groups()
        assert r == ('testA/a.jpg', '0', '10', 'jpg')

    def test_re13(self):
        s = 'testA/a.jpg__x.jpg'
        m = rule.match(s)
        r = m.groups()
        assert r == ('testA/a.jpg', '', '', 'jpg')


if __name__ == '__main__':
    unittest.main()