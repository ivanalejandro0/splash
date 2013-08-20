#!/usr/bin/env python
# encoding: utf-8
import sys
import signal

from PySide import QtGui
from MulticastServer import MulticastPingPong
from twisted.internet.task import LoopingCall

from utils import get_log_handler
from actions import Actions
logger = get_log_handler(__name__)

from ui.ui_splash import Ui_SplashWindow


class SplashWindow(QtGui.QWidget):
    _auto_refresh_delay = 2

    def __init__(self):
        QtGui.QWidget.__init__(self)

        # Create and setup the UI
        self.ui = Ui_SplashWindow()
        self.ui.setupUi(self)

        # Custom UI settings
        self.ui.twNodes.horizontalHeader().setResizeMode(
            0, QtGui.QHeaderView.Stretch)

        # Connections
        self.ui.pbAutoRefresh.clicked.connect(self.toggle_autorefresh)
        self.ui.pbQuit.clicked.connect(self.close)
        self.ui.twNodes.itemDoubleClicked.connect(self.on_item_doubleclicked)

        # Multicast
        self._start_listening()

        # Automatic refresh
        self._loop_refresh = LoopingCall(self.refresh_nodes)
        self.toggle_autorefresh()

        # Action processor
        self._actions = Actions()

    def _start_listening(self):
        from twisted.internet import reactor

        # Multicast Server
        self._pingpong = MulticastPingPong()
        port = MulticastPingPong.MULTICAST_ADDR[1]

        reactor.listenMulticast(port, self._pingpong, listenMultiple=True)
        reactor.runReturn()

        # Connect the multicast server signals with the app.
        self._pingpong.got_client.connect(self.add_node)
        self._pingpong.got_data.connect(self.parse_incoming_data)

    def toggle_autorefresh(self):
        """
        SLOT:
            Toggles the automatic node list refresh.
        """
        loop = self._loop_refresh
        if loop.running:
            loop.stop()
        else:
            loop.start(self._auto_refresh_delay)

    def add_node(self, ip, port):
        """
        SLOT
        TRIGGERS:
            self._pingpong.got_client

        Adds a node to the list.

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
        logger.debug('Refresh nodes list.')
        # empty table
        for r in xrange(self.ui.twNodes.rowCount()):
            self.ui.twNodes.removeRow(0)

        self._pingpong.send_alive()

    def ask_user(self, title='', question=''):
        response, ok = QtGui.QInputDialog.getText(None, title, question)
        return response, ok

    def display_data(self, data):
        QtGui.QMessageBox.information(self, 'Incoming Data', data)

    def on_item_doubleclicked(self, item):
        node = item.text()
        row = self.ui.twNodes.selectedItems()
        ip = row[1].text()
        port = int(row[2].text())
        address = (ip, port)
        logger.debug('Node clicked: {0}, address: {1}'.format(node, address))
        question = 'Input the message to send to the node'
        msg, ok = self.ask_user('Input message', question)
        if ok:
            self._pingpong.send_data(msg, address)

    def parse_incoming_data(self, data):
        """
        SLOT
        TRIGGERS:
            self._pingpong.got_data

        It process the data received from a peer.

        :param data: the data that we received and need to process.
        :type data: str
        """
        if self._actions.run(data) is None:
            # If there is no action to process, then display the data received.
            self.display_data(data)

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
