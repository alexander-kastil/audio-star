# Source Generated with Decompyle++
# File: LPQobuzArtistDetailTableView.pyc (Python 3.9)

'''
@Time ： 2025/7/1 11:38
@Auth ： Chris
@File ：LPQobuzTableView.py
@Desc:
'''
from HOME.StreamService.Qobuz.Component.LPQobuzTableView import LPQobuzTracksTableWithCoverModel
TABLE_COLUMNS = 6

class LPQobuzArtistTracksTableWithCoverModel(LPQobuzTracksTableWithCoverModel):
    
    def rowCount(self = None, parent = None):
        super().rowCount(parent)
        return min(len(self._data), 5)

    __classcell__ = None

