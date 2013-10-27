from distutils.core import setup
from glob import glob
import py2exe
import matplotlib


data_files = [("Microsoft.VC90.CRT", glob(r'C:\Program Files\Microsoft Visual Studio 9.0\VC\redist\x86\Microsoft.VC90.CRT\*.*'))]+matplotlib.get_py2exe_datafiles()
includes=["scipy.io.matlab.streams","matplotlib.backends.backend_tkagg"]
excludes=['matplotlib.backends.backend_gtkagg', 'matplotlib.backends.backend_wxagg','scipy.linalg.flapack','scipy.linalg.fblas','scipy.linalg.clapack','numpy.core._dotblas','scipy.linalg._flinalg','scipy.special.specfun']
setup(
    console=['Perfectone.py'],
    data_files=data_files,
    options= {
        "py2exe": {
            "includes":includes,
            "excludes":excludes
        }
    }
)
