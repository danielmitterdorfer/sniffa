sniffa
======

sniffa is a small utility that allows you to watch Discuss forums for keywords.

Every time it is invoked, it checks for new posts matching the keywords and creates a notification in the Mac OS X notification bar.

# Requirements

* Mac OS X 10.8 or later: As it uses Mac OS X notifications, sniffa works only on Mac OS X 10.8 or later.
* Python 3
* certifi: Install with `pip3 install certifi`
* pync: Install with `pip3 install pync`

# Installation

Ensure that all prerequisites are installed, then copy `sniffa.py` to any directory, e.g. `~/bin` and run `chmod u+x sniffa.py`.

# Usage

sniffa can be used to query multiple Discuss forums. The keywords and the ids of all already seen posts are maintained in a file `~/.sniffa/watch-$(FORUM_NAME).ini`, where `$(FORUM_NAME)` is a name that you can choose to identify this forum.

## Example

Consider you want to watch for the keywords "Rally" and "JMeter" in the Elastic Discuss forum at https://discuss.elastic.co.

1. Create `~/.sniffa/watch-elastic.ini`
2. Add the following lines:

```
[sniffa.domain]
url = https://discuss.elastic.co

[Rally]

[JMeter]
```

Now invoke sniffa: ``python3 sniffa.py elastic``. It will load the watches file for the forum named "elastic", check for new posts (which will be a lot at the first time) and show a notice for each of them in the Mac OS X notification bar.

## Automatic regular invocation

Quite likely you don't want to invoke sniffa manually every time you want to check for new posts. Therefore, you can install sniffa as a launch agent.

Create a new file in `~/Library/LaunchAgents/org.github.sniffa.plist` with the following contents:

```plist
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
  <key>Label</key>
  <string>org.github.sniffa</string>

  <key>ProgramArguments</key>
  <array>
    <string>~/bin/sniffa.py</string>
    <string>elastic</string>
  </array>

  <key>Nice</key>
  <integer>1</integer>

  <key>StartInterval</key>
  <integer>7200</integer>

  <key>RunAtLoad</key>
  <true/>

  <key>StandardErrorPath</key>
  <string>~/.sniffa/sniffa-elastic.err.log</string>

  <key>StandardOutPath</key>
  <string>~/.sniffa/sniffa-elastic.out.log</string>
</dict>
</plist>
```

Change the paths depending on the install location of sniffa and also your domain parameter. 

With this plist file, sniffa will check the Elastic Discuss forum every two hours (7200 seconds) for new posts.

Finally register the launch agent with Mac OS X:

```
launchctl load ~/Library/LaunchAgents/org.github.sniffa.plist
```

After a restart, Mac OS X will pick up the plist file automatically.

If you are interested in more details about launch agents, check [Alvin Alexander's blog post about plist files](http://alvinalexander.com/mac-os-x/mac-osx-startup-crontab-launchd-jobs) (on which this description is based).

# License

'sniffa' is distributed under the terms of the [Apache Software Foundation license, version 2.0](http://www.apache.org/licenses/LICENSE-2.0.html).
