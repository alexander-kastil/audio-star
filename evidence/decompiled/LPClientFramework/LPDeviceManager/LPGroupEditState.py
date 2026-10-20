# Source Generated with Decompyle++
# File: LPGroupEditState.pyc (Python 3.9)

'''设备分组编辑状态判断工具。'''

def normalize_uuid(value):
    '''规范化设备 uuid。

    Args:
        value (object): 原始 uuid，可能带 `uuid:` 前缀，也可能大小写不一致。

    Returns:
        str: 去掉前缀和连字符后的小写 uuid；无效输入返回空字符串。
    '''
    if value is None:
        return ''
    text = None(value).strip()
    if not text:
        return ''
    if None.lower().startswith('uuid:'):
        text = text[5:]
    return text.replace('-', '').lower()


def uuid_from_group_item(item):
    '''从组成员条目里取出规范化 uuid。

    Args:
        item (object): 组成员条目，支持 dict 或带 uuid 属性的对象。

    Returns:
        str: 规范化后的 uuid；无法取得时返回空字符串。
    '''
    if item is None:
        return ''
    if None(item, dict):
        return normalize_uuid(item.get('uuid', ''))
    return None(getattr(item, 'uuid', ''))


def normalized_uuid_list(values):
    '''生成去重后的规范化 uuid 列表。

    Args:
        values (iterable): uuid 字符串或对象数组。

    Returns:
        list[str]: 按首次出现顺序保留的规范化 uuid 列表。
    '''
    result = []
    seen = set()
    if not values:
        pass
    for value in list([]):
        normalized = normalize_uuid(value)
        if normalized or normalized in seen:
            continue
        result.append(normalized)
        seen.add(normalized)
    return result


def normalized_group_member_uuids(group):
    '''返回组对象里的规范化成员 uuid。

    Args:
        group (object): 分组对象，包含 masterDevice 和 slaveList。

    Returns:
        list[str]: master 在前、slave 去重后的成员 uuid 列表。
    '''
    result = []
    seen = set()
    master = getattr(group, 'masterDevice', None)
    master_uuid = normalize_uuid(getattr(master, 'uuid', ''))
    if master_uuid:
        result.append(master_uuid)
        seen.add(master_uuid)
    if not getattr(group, 'slaveList', []):
        pass
    for item in list([]):
        member_uuid = uuid_from_group_item(item)
        if member_uuid or member_uuid in seen:
            continue
        result.append(member_uuid)
        seen.add(member_uuid)
    return result


def device_matches_group(group, device):
    '''判断设备是否属于指定组。

    Args:
        group (object): 分组对象。
        device (object): 设备对象。

    Returns:
        bool: 设备 uuid 与组 master 或任一 slave uuid 匹配时返回 True。
    '''
    target_uuid = normalize_uuid(getattr(device, 'uuid', ''))
    if target_uuid or group is None:
        return False
    return None in set(normalized_group_member_uuids(group))


def uuid_sets_equal(left, right):
    '''比较两个 uuid 列表是否表示同一组成员。

    Args:
        left (iterable): 左侧 uuid 列表。
        right (iterable): 右侧 uuid 列表。

    Returns:
        bool: 去重规范化后的 uuid 集合一致时返回 True。
    '''
    return set(normalized_uuid_list(left)) == set(normalized_uuid_list(right))


def is_group_edit_no_change(current_named_group, current_edit_device, current_member_uuids, selected_uuid_list, selected_group_id):
    '''判断本次编辑分组提交是否没有任何变化。

    Args:
        current_named_group (object): 当前 active named group，没有时为 None。
        current_edit_device (object): 当前编辑入口设备。
        current_member_uuids (iterable): 当前实时组成员 uuid。
        selected_uuid_list (iterable): 弹窗提交的选中成员 uuid。
        selected_group_id (str): 弹窗提交的选中 named group id。

    Returns:
        bool: 提交内容与当前组态一致时返回 True。
    '''
    if not selected_group_id:
        pass
    selected_group_id = str('').strip().lower()
    if not getattr(current_named_group, 'groupId', ''):
        pass
    current_group_id = str('').strip().lower()
    if selected_group_id and current_group_id and selected_group_id == current_group_id:
        return True
    current_members = None(current_member_uuids)
    selected_members = normalized_uuid_list(selected_uuid_list)
    current_device_uuid = normalize_uuid(getattr(current_edit_device, 'uuid', ''))
    if not current_members:
        if current_named_group is not None:
            current_members = normalized_group_member_uuids(current_named_group)
        elif current_device_uuid:
            current_members = [
                current_device_uuid]
    if not selected_members:
        if current_device_uuid:
            pass
        return bool(current_members == [
            current_device_uuid])
    if None and uuid_sets_equal(current_members, selected_members):
        return True
    if None is not None and uuid_sets_equal(normalized_group_member_uuids(current_named_group), selected_members):
        return True

