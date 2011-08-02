from distutils.core import setup
import py2exe

setup(console=['pylog.py'] ,data_files=[('.',['index.tpl'])])