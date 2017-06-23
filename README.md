# Pydomoticz
A Domoticz API for Python

# Documentation:
First, you need to get a Domoticz Server with

    Pydomoticz.Domotiz(ip[,user,password])

Exemple:<space><space>

    import Pydomoticz
    myhome = Pydomoticz.Domoticz('192.168.1.9',user='Oliver',password='My.p4ssw0rd')
    
Then, you can get some parameters like the status of the Domoticz server, the server time, the sunset or the sunrise:

    print myhome.ServerTime
    >>> datetime.datetime(2017, 6, 22, 16, 31, 41)
    
    print myhome.sunset
    >>> datetime.datetime(2017, 6, 22, 21, 30)
    
    print myhome.sunrise
    >>> datetime.datetime(2017, 6, 22, 5, 33)
    
    print myhome.status
    >>> u'OK'


You can, of course, interact with some devices.

To get devices, you can proceed by:

    myhome.devices
    >>> [<Domoticz Device at idx 3>, <Domoticz Device at idx 2>, <Domoticz Device at idx 1>]
    
Or you can do a research with:

    domoticzInstance.getDevices(attribut=value)
    >>> [All devices matching in a list]
    
Exemple:

    allclosedblinds = myhome.getDevices(status="Closed",switch_type="Blinds")
    
(To retrieve attributs from a device you can do: )

    deviceInstance.keys()
    >>> ['MaxDimLevel', 'AddjMulti2', 'PlanID', 'HaveDimmer', 'UsedByCamera', 'ShowNotifications', 'HaveGroupCmd', 'YOffset', 'StrParam1', 'StrParam2', 'TypeImg', 'Type', 'AddjMulti', 'XOffset', 'Status', 'Used', 'Description', 'SubType', 'HardwareType', 'PlanIDs', 'Notifications', 'LevelInt', 'SwitchType', 'Data', 'IsSubDevice', 'HaveTimeout', 'Name', 'Level', 'CustomImage', 'Favorite', 'AddjValue2', 'Protected', 'Timers', 'HardwareName', 'BatteryLevel', 'ID', 'LastUpdate', 'idx', 'HardwareTypeVal', 'HardwareID', 'AddjValue', 'SwitchTypeVal', 'SignalLevel', 'Image', 'Unit']

To get values for these parameters, all these ways are correct and equivalent:

    device.switchtype
    device.SwitchType #Case isn't sensitive
    device.switch_type #Backslashes are ignored
    device['SwitchType']
    
You can obviously pilot your devices:

    device.on()
    device.off()
    device.setLevel(6)
    
Exemples:

    for blind in allclosedblinds:
        blind.off()
       
    for light in (myhome.getDevices(switchtype='On/Off') ):
        light.off()

   
