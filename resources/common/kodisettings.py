#v.0.0.1

def _get_setting( addon, setting_name, default, type="string" ):
    if type.lower() == "bool":
        try:
            thebool = addon.getSettingBool( setting_name )
            if thebool == 0:
                return False
            elif thebool == 1:
                return True
            else:
                return thebool
        except TypeError:
            return default
        except AttributeError:
            if addon.getSetting( setting_name ).lower() == 'true':
                return True
            if addon.getSetting( setting_name ).lower() == 'false':
                return False
            return default
    if type.lower() == "int":
        try:
            return addon.getSettingInt( setting_name )
        except TypeError:
            return default
        except AttributeError:
            try:
                return int( addon.getSetting( setting_name ) )
            except:
                return default
    if type.lower() == "number":
        try:
            return addon.getSettingNumber( setting_name )
        except TypeError:
            return default
        except AttributeError:
            try:
                return float( addon.getSetting( setting_name ) )
            except:
                return default
    else:
        setting = addon.getSetting( setting_name )
        if setting:
            return setting
        else:
            return default


def getSettingBool( addon, setting_name, default=False ):
    return _get_setting( addon, setting_name, default, 'bool' )


def getSettingInt( addon, setting_name, default=0 ):
    return _get_setting( addon, setting_name, default, 'int')


def getSettingNumber( addon, setting_name, default=0.0 ):
    return _get_setting( addon, setting_name, default, 'number')


def getSettingString( addon, setting_name, default='' ):
    return _get_setting( addon, setting_name, default, 'string')

