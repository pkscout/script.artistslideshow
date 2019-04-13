#v.0.0.1

def _getsetting( addon, name, default, type="string" ):
    if type.lower() == "bool":
        try:
            return addon.getSettingBool( name )
        except TypeError:
            return False
        except AttributeError:
            if addon.getSetting( name ).lower() == 'true':
                return True
            else:
                return False
    if type.lower() == "int":
        try:
            return addon.getSettingInt( name )
        except TypeError:
            return 0
        except AttributeError:
            try:
                return int( addon.getSetting( name ) )
            except:
                return 0
    if type.lower() == "number":
        try:
            return addon.getSettingNumber( name )
        except TypeError:
            return 0.0
        except AttributeError:
            try:
                return float( addon.getSetting( name ) )
            except:
                return 0.0
    else:
        return addon.getSetting( name )


def getSettingBool( addon, name, default=False ):
    return _getsetting( addon, name, default, 'bool' )


def getSettingInt( addon, name, default=0 ):
    return _getsetting( addon, name, default, 'int')


def getSettingNumber( addon, name, default=0.0 ):
    return _getsetting( addon, name, default, 'number')


def getSettingString( addon, name, default='' ):
    return _getsetting( addon, name, default, 'string')

