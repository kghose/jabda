#Run by doing python setup.py py2exe
from distutils.core import setup
import py2exe

opts = {
    "py2exe": {
        "dist_dir": "Winexe/bundle",
    }
}
setup(console=['pylog.py'] , data_files=[('.',['index.tpl'])], options=opts)