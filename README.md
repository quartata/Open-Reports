Currently, this repo only contains a script to open pending Natty reports as a SOCVR report. It can be used as a local stand-alone tool as ./OpenReports or as a bot that runs in SOBotics.

For usage of the stand-alone script, please refer to the built-in help.

The bot currently understands the following commands:

 - 'open' or 'o': Open all pending reports not in the ignore list
 - '`number` [b[ack]]': Open up to `number` reports, fetch from the back of the list if b or back is present
 - 'ignore rest' or 'ir': Put all reports that where in your last report in your personal ignore list. Those reports will not be shown to you in the future.
 - 'dil' or 'delete ignorelist': Delete your ignorelist
 - 'fetch amount' or 'fa': Tells you, how many unhandled reports there are
 - 'reboot': Restarts the bot

If you want more filters or sorting facilities, please raise an issue on Github or ping me.

