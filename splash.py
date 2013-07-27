import sys
import signal

from PySide import QtGui

from utils import get_log_handler
logger = get_log_handler(__name__)


class SplashWindow(QtGui.QWidget):
    def __init__(self):
        QtGui.QWidget.__init__(self)

        self.setWindowTitle('Splash!')
        self.setMinimumSize(200, 400)

        # Nodes list
        self._nodes_list = QtGui.QListWidget(self)
        self._nodes_list.itemDoubleClicked.connect(self.on_item_doubleclicked)

        # Quit button
        pbQuit = QtGui.QPushButton('Quit')

        # Layout
        layout = QtGui.QVBoxLayout()
        layout.addWidget(self._nodes_list)
        layout.addWidget(pbQuit)
        self.setLayout(layout)

        # Connections
        pbQuit.clicked.connect(self.close)

    def add_nodes(self, nodes):
        """
        Add a list of nodes to the list.

        :param nodes: a list of nodes
        :type nodes: list of str
        """
        for node in nodes:
            item = QtGui.QListWidgetItem(node)
            count = self._nodes_list.count()
            self._nodes_list.insertItem(count, item)

    def ask_user(self, title='', question=''):
        response, ok = QtGui.QInputDialog.getText(None, title, question)
        return response, ok

    def display_incoming_message(self, msg):
        QtGui.QMessageBox.information(self, 'Incoming Message', msg)
        # msgBox = QtGui.QMessageBox()
        # msgBox.setText('Incoming Message')
        # msgBox.setInformativeText(msg)
        # msgBox.setIcon(QtGui.QMessageBox.Information)
        # msgBox.exec_()

    def on_item_doubleclicked(self, item):
        node = item.text()
        logger.debug('Node clicked: {0}'.format(node))
        question = 'Input the message to send to the node'
        msg, ok = self.ask_user('Input message', question)
        if ok:
            self.display_incoming_message(msg)

    def add_demo_nodes(self):
        demo_nodes = ['Demo node 01', 'Demo node 02', 'Demo node 03',
                      'Demo node 04', 'Demo node 05']
        self.add_nodes(demo_nodes)

    def closeEvent(self, e):
        """
        Reimplementation of closeEvent to add actions before quit.
        """
        logger.debug('Quit app')
        QtGui.QMainWindow.closeEvent(self, e)


if __name__ == '__main__':
    app = QtGui.QApplication(sys.argv)

    # Install the reactor (twisted <-> qt)
    import qt4reactor
    qt4reactor.install()

    window = SplashWindow()
    window.show()

    # Ensure that the application quits using CTRL-C
    signal.signal(signal.SIGINT, signal.SIG_DFL)

    sys.exit(app.exec_())
