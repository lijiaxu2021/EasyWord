import os
import sys

# Add src to path so we can import the package
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from easyword.main import EasyWordApp

if __name__ == '__main__':
    EasyWordApp().run()
