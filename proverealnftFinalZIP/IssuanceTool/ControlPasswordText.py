from pysettings import conf
from pyforms.Controls import ControlText

from PyQt4.QtGui import QLineEdit

class ControlPasswordText(ControlText):
    def __init__(self, *args, **kwargs):
        super(ControlPasswordText, self).__init__(*args, **kwargs)
        self.form.lineEdit.setEchoMode(QLineEdit.Password)
