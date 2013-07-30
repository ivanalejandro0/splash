import sys
import signal

from PySide import QtGui
from MulticastServer import MulticastPingPong, MULTICAST_ADDR

from utils import get_log_handler
logger = get_log_handler(__name__)

from ui.splashUi import Ui_SplashWindow


class SplashWindow(QtGui.QWidget):
    def __init__(self):
        QtGui.QWidget.__init__(self)

        # Create and setup the UI
        self.ui = Ui_SplashWindow()
        self.ui.setupUi(self)

        # Custom UI settings
        self.ui.twNodes.horizontalHeader().setResizeMode(
            0, QtGui.QHeaderView.Stretch)

        # Connections
        self.ui.pbRefresh.clicked.connect(self.refresh_nodes)
        self.ui.pbQuit.clicked.connect(self.close)

        # Multicast
        self._start_listening()

    def _start_listening(self):
        from twisted.internet import reactor

        # Multicast Server
        self._pingpong = MulticastPingPong()
        port = MULTICAST_ADDR[1]

        reactor.listenMulticast(port, self._pingpong, listenMultiple=True)
        reactor.runReturn()
        self._pingpong.got_client.connect(self.add_node)
        self._pingpong.got_message.connect(self.display_incoming_message)

    def add_node(self, ip, port):
        """
        Add a node to the list.

        :param node: a nodes to add.
        :type node: tuple(str, int)
        """
        node = "(%s, %d)" % (ip, port)
        logger.debug('Adding node: %s' % node)

        row = self.ui.twNodes.rowCount()
        self.ui.twNodes.insertRow(row)
        self.ui.twNodes.setItem(row, 0, QtGui.QTableWidgetItem(node))
        self.ui.twNodes.setItem(row, 1, QtGui.QTableWidgetItem(ip))
        self.ui.twNodes.setItem(row, 2, QtGui.QTableWidgetItem(str(port)))

    def refresh_nodes(self):
        """
        Refresh the node list sending a new multicast message.
        """
        # empty table
        for r in xrange(self.ui.twNodes.rowCount()):
            self.ui.twNodes.removeRow(0)

        self._pingpong.send_alive()

    def ask_user(self, title='', question=''):
        response, ok = QtGui.QInputDialog.getText(None, title, question)
        return response, ok

    def display_incoming_message(self, msg):
        QtGui.QMessageBox.information(self, 'Incoming Message', msg)

    def on_item_doubleclicked(self, item):
        node = item.text()
        logger.debug('Node clicked: {0}'.format(node))
        question = 'Input the message to send to the node'
        msg, ok = self.ask_user('Input message', question)
        if ok:
            self._pingpong.send_message(msg)

    def add_demo_nodes(self):
        demo_nodes = ['Demo node 01', 'Demo node 02', 'Demo node 03',
                      'Demo node 04', 'Demo node 05']
        for node in demo_nodes:
            self.add_node(node)

    def closeEvent(self, e):
        """
        Reimplementation of closeEvent to add actions before quit.
        """
        from twisted.internet import reactor
        reactor.stop()
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
