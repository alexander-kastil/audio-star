# Source Generated with Decompyle++
# File: LPActionGroup.pyc (Python 3.9)

'''
@Time ： 2024/12/3 18:58
@Auth ： Chris
@File ：LPActionGroup.py
@Desc:
'''
from LPClientFramework.LPMenu.LPActionCallbackManager import ActionCallbackManager
ACTIONS_DICT = {
    'ACTION_ADD_NEXT': {
        'icon_path': 'miniBar/playlist.png',
        'action_name': 'Add to Next' },
    'ACTION_ADD_LAST': {
        'icon_path': 'miniBar/playlist.png',
        'action_name': 'Add to Last' },
    'ACTION_DELETE_FROM_QUEUE': {
        'icon_path': 'delete.png',
        'action_name': 'Delete from Queue',
        'callback_name': ActionCallbackManager.handle_delete_from_queue },
    'ACTION_SHOW_DETAIL': {
        'icon_path': 'miniBar/playlist.png',
        'action_name': 'Show Detail',
        'callback_name': ActionCallbackManager.handle_show_detail } }
ACTION_QUEUE_GROUP = {
    'ACTION_DELETE_FROM_QUEUE': ACTIONS_DICT['ACTION_DELETE_FROM_QUEUE'] }
ACTION_TRACKS_GROUP = [
    ACTIONS_DICT['ACTION_ADD_NEXT'],
    ACTIONS_DICT['ACTION_ADD_LAST'],
    ACTIONS_DICT['ACTION_DELETE_FROM_QUEUE'],
    ACTIONS_DICT['ACTION_SHOW_DETAIL']]
