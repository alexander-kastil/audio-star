# Source Generated with Decompyle++
# File: LPActionCallbackManager.pyc (Python 3.9)

'''
@Time ： 2024/12/4 9:09
@Auth ： Chris
@File ：LPActionCallbackManager.py
@Desc:
'''
from PyQt6.QtCore import QCoreApplication, pyqtSignal
import LPGlobalUI
from LPClientFramework.LPUtility import logger

class ActionCallbackManager:
    
    def __init__(self):
        self.cbs = { }

    
    def register_default_callback(self = None, action_group = None):
        pass

    
    def register_callback(self, action_name, cb):
        self.cbs[action_name] = cb

    
    def execute(self, cb, *args, **kwargs):
        pass
    # WARNING: Decompyle incomplete

    
    def handle_add_to_next(self):
        pass

    
    def handle_delete_from_queue(queue_lock_signal, table_view, index, play_item, action_key = ('ACTION_DELETE_FROM_QUEUE',)):
        logger.debug('handle_context_menu_action delete from queue! index = %d play_item = %s' % (index, play_item.trackName))
        row = index - 1
        if row < 0:
            return None
        None.model().removeRow(row)
        queue_lock_signal.emit()
        LPGlobalUI.currentDevice.queueManager.delete_from_queue(index, action_key, ActionCallbackManager.finished_method)

    handle_delete_from_queue = staticmethod(handle_delete_from_queue)
    
    def handle_show_detail():
        pass

    handle_show_detail = staticmethod(handle_show_detail)
    
    def finished_method(action_key, is_success):
        if action_key == 'ACTION_DELETE_FROM_QUEUE' and is_success:
            logger.debug('delete from queue success !')

    finished_method = staticmethod(finished_method)

