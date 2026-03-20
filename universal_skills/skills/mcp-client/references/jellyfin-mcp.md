# Jellyfin MCP Reference

**Project:** `jellyfin-mcp`

## Required Environment Variables

| Variable | Description |
|----------|-------------|
| `JELLYFIN_API_KEY` | Required for authentication |
| `JELLYFIN_URL` | Required for authentication |

## Available Tool Tags (62)

| Env Variable | Default | Tools |
|-------------|---------|-------|
| `ACTIVITYLOGTOOL` | `True` | (No tools found) |
| `APIKEYTOOL` | `True` | (No tools found) |
| `ARTISTSTOOL` | `True` | (No tools found) |
| `AUDIOTOOL` | `True` | (No tools found) |
| `BACKUPTOOL` | `True` | (No tools found) |
| `BRANDINGTOOL` | `True` | (No tools found) |
| `CHANNELSTOOL` | `True` | (No tools found) |
| `CLIENTLOGTOOL` | `True` | (No tools found) |
| `COLLECTIONTOOL` | `True` | (No tools found) |
| `CONFIGURATIONTOOL` | `True` | (No tools found) |
| `DASHBOARDTOOL` | `True` | (No tools found) |
| `DEVICESTOOL` | `True` | (No tools found) |
| `DISPLAYPREFERENCESTOOL` | `True` | (No tools found) |
| `DYNAMICHLSTOOL` | `True` | (No tools found) |
| `ENVIRONMENTTOOL` | `True` | (No tools found) |
| `FILTERTOOL` | `True` | (No tools found) |
| `GENRESTOOL` | `True` | (No tools found) |
| `HLSSEGMENTTOOL` | `True` | (No tools found) |
| `IMAGETOOL` | `True` | (No tools found) |
| `INSTANTMIXTOOL` | `True` | (No tools found) |
| `ITEMLOOKUPTOOL` | `True` | (No tools found) |
| `ITEMREFRESHTOOL` | `True` | (No tools found) |
| `ITEMSTOOL` | `True` | (No tools found) |
| `ITEMUPDATETOOL` | `True` | (No tools found) |
| `LIBRARYSTRUCTURETOOL` | `True` | (No tools found) |
| `LIBRARYTOOL` | `True` | (No tools found) |
| `LIVETVTOOL` | `True` | (No tools found) |
| `LOCALIZATIONTOOL` | `True` | (No tools found) |
| `LYRICSTOOL` | `True` | (No tools found) |
| `MEDIAINFOTOOL` | `True` | (No tools found) |
| `MEDIASEGMENTSTOOL` | `True` | (No tools found) |
| `MISCTOOL` | `True` | (Internal tools) |
| `MOVIESTOOL` | `True` | (No tools found) |
| `MUSICGENRESTOOL` | `True` | (No tools found) |
| `PACKAGETOOL` | `True` | (No tools found) |
| `PERSONSTOOL` | `True` | (No tools found) |
| `PLAYLISTSTOOL` | `True` | (No tools found) |
| `PLAYSTATETOOL` | `True` | (No tools found) |
| `PLUGINSTOOL` | `True` | (No tools found) |
| `QUICKCONNECTTOOL` | `True` | (No tools found) |
| `REMOTEIMAGETOOL` | `True` | (No tools found) |
| `SCHEDULEDTASKSTOOL` | `True` | (No tools found) |
| `SEARCHTOOL` | `True` | (No tools found) |
| `SESSIONTOOL` | `True` | (No tools found) |
| `STARTUPTOOL` | `True` | (No tools found) |
| `STUDIOSTOOL` | `True` | (No tools found) |
| `SUBTITLETOOL` | `True` | (No tools found) |
| `SUGGESTIONSTOOL` | `True` | (No tools found) |
| `SYNCPLAYTOOL` | `True` | (No tools found) |
| `SYSTEMTOOL` | `True` | (No tools found) |
| `TIMESYNCTOOL` | `True` | (No tools found) |
| `TMDBTOOL` | `True` | (No tools found) |
| `TRAILERSTOOL` | `True` | (No tools found) |
| `TRICKPLAYTOOL` | `True` | (No tools found) |
| `TVSHOWSTOOL` | `True` | (No tools found) |
| `UNIVERSALAUDIOTOOL` | `True` | (No tools found) |
| `USERLIBRARYTOOL` | `True` | (No tools found) |
| `USERTOOL` | `True` | (No tools found) |
| `USERVIEWSTOOL` | `True` | (No tools found) |
| `VIDEOATTACHMENTSTOOL` | `True` | (No tools found) |
| `VIDEOSTOOL` | `True` | (No tools found) |
| `YEARSTOOL` | `True` | (No tools found) |

## Stdio Connection (Default)

```json
{
  "mcpServers": {
    "jellyfin-mcp": {
      "command": "jellyfin-mcp",
      "args": [
        "--transport",
        "stdio"
      ],
      "env": {
        "JELLYFIN_URL": "${JELLYFIN_URL}",
        "JELLYFIN_API_KEY": "${JELLYFIN_API_KEY}",
        "ITEMREFRESHTOOL": "${ ITEMREFRESHTOOL:-True }",
        "COLLECTIONTOOL": "${ COLLECTIONTOOL:-True }",
        "TVSHOWSTOOL": "${ TVSHOWSTOOL:-True }",
        "SCHEDULEDTASKSTOOL": "${ SCHEDULEDTASKSTOOL:-True }",
        "TMDBTOOL": "${ TMDBTOOL:-True }",
        "DASHBOARDTOOL": "${ DASHBOARDTOOL:-True }",
        "CLIENTLOGTOOL": "${ CLIENTLOGTOOL:-True }",
        "SEARCHTOOL": "${ SEARCHTOOL:-True }",
        "BACKUPTOOL": "${ BACKUPTOOL:-True }",
        "MEDIASEGMENTSTOOL": "${ MEDIASEGMENTSTOOL:-True }",
        "HLSSEGMENTTOOL": "${ HLSSEGMENTTOOL:-True }",
        "DISPLAYPREFERENCESTOOL": "${ DISPLAYPREFERENCESTOOL:-True }",
        "MISCTOOL": "${ MISCTOOL:-True }",
        "LIVETVTOOL": "${ LIVETVTOOL:-True }",
        "VIDEOATTACHMENTSTOOL": "${ VIDEOATTACHMENTSTOOL:-True }",
        "CHANNELSTOOL": "${ CHANNELSTOOL:-True }",
        "DYNAMICHLSTOOL": "${ DYNAMICHLSTOOL:-True }",
        "LIBRARYTOOL": "${ LIBRARYTOOL:-True }",
        "AUDIOTOOL": "${ AUDIOTOOL:-True }",
        "PLUGINSTOOL": "${ PLUGINSTOOL:-True }",
        "SESSIONTOOL": "${ SESSIONTOOL:-True }",
        "IMAGETOOL": "${ IMAGETOOL:-True }",
        "STUDIOSTOOL": "${ STUDIOSTOOL:-True }",
        "ENVIRONMENTTOOL": "${ ENVIRONMENTTOOL:-True }",
        "PERSONSTOOL": "${ PERSONSTOOL:-True }",
        "TRICKPLAYTOOL": "${ TRICKPLAYTOOL:-True }",
        "INSTANTMIXTOOL": "${ INSTANTMIXTOOL:-True }",
        "MOVIESTOOL": "${ MOVIESTOOL:-True }",
        "SYNCPLAYTOOL": "${ SYNCPLAYTOOL:-True }",
        "STARTUPTOOL": "${ STARTUPTOOL:-True }",
        "UNIVERSALAUDIOTOOL": "${ UNIVERSALAUDIOTOOL:-True }",
        "USERTOOL": "${ USERTOOL:-True }",
        "MUSICGENRESTOOL": "${ MUSICGENRESTOOL:-True }",
        "SUGGESTIONSTOOL": "${ SUGGESTIONSTOOL:-True }",
        "TIMESYNCTOOL": "${ TIMESYNCTOOL:-True }",
        "ARTISTSTOOL": "${ ARTISTSTOOL:-True }",
        "SYSTEMTOOL": "${ SYSTEMTOOL:-True }",
        "LOCALIZATIONTOOL": "${ LOCALIZATIONTOOL:-True }",
        "ITEMUPDATETOOL": "${ ITEMUPDATETOOL:-True }",
        "LIBRARYSTRUCTURETOOL": "${ LIBRARYSTRUCTURETOOL:-True }",
        "MEDIAINFOTOOL": "${ MEDIAINFOTOOL:-True }",
        "QUICKCONNECTTOOL": "${ QUICKCONNECTTOOL:-True }",
        "VIDEOSTOOL": "${ VIDEOSTOOL:-True }",
        "REMOTEIMAGETOOL": "${ REMOTEIMAGETOOL:-True }",
        "PLAYSTATETOOL": "${ PLAYSTATETOOL:-True }",
        "APIKEYTOOL": "${ APIKEYTOOL:-True }",
        "DEVICESTOOL": "${ DEVICESTOOL:-True }",
        "FILTERTOOL": "${ FILTERTOOL:-True }",
        "BRANDINGTOOL": "${ BRANDINGTOOL:-True }",
        "GENRESTOOL": "${ GENRESTOOL:-True }",
        "USERVIEWSTOOL": "${ USERVIEWSTOOL:-True }",
        "YEARSTOOL": "${ YEARSTOOL:-True }",
        "LYRICSTOOL": "${ LYRICSTOOL:-True }",
        "TRAILERSTOOL": "${ TRAILERSTOOL:-True }",
        "ACTIVITYLOGTOOL": "${ ACTIVITYLOGTOOL:-True }",
        "PACKAGETOOL": "${ PACKAGETOOL:-True }",
        "SUBTITLETOOL": "${ SUBTITLETOOL:-True }",
        "PLAYLISTSTOOL": "${ PLAYLISTSTOOL:-True }",
        "USERLIBRARYTOOL": "${ USERLIBRARYTOOL:-True }",
        "CONFIGURATIONTOOL": "${ CONFIGURATIONTOOL:-True }",
        "ITEMSTOOL": "${ ITEMSTOOL:-True }",
        "ITEMLOOKUPTOOL": "${ ITEMLOOKUPTOOL:-True }"
      }
    }
  }
}
```

## HTTP Connection

```bash
jellyfin-mcp --transport streamable-http --host 0.0.0.0 --port 8000
```

## Single-Tag Config Example

Only ACTIVITYLOGTOOL enabled:

```json
{
  "mcpServers": {
    "jellyfin-mcp": {
      "command": "jellyfin-mcp",
      "args": [
        "--transport",
        "stdio"
      ],
      "env": {
        "JELLYFIN_URL": "${JELLYFIN_URL}",
        "JELLYFIN_API_KEY": "${JELLYFIN_API_KEY}",
        "ITEMREFRESHTOOL": "False",
        "COLLECTIONTOOL": "False",
        "TVSHOWSTOOL": "False",
        "SCHEDULEDTASKSTOOL": "False",
        "TMDBTOOL": "False",
        "DASHBOARDTOOL": "False",
        "CLIENTLOGTOOL": "False",
        "SEARCHTOOL": "False",
        "BACKUPTOOL": "False",
        "MEDIASEGMENTSTOOL": "False",
        "HLSSEGMENTTOOL": "False",
        "DISPLAYPREFERENCESTOOL": "False",
        "MISCTOOL": "False",
        "LIVETVTOOL": "False",
        "VIDEOATTACHMENTSTOOL": "False",
        "CHANNELSTOOL": "False",
        "DYNAMICHLSTOOL": "False",
        "LIBRARYTOOL": "False",
        "AUDIOTOOL": "False",
        "PLUGINSTOOL": "False",
        "SESSIONTOOL": "False",
        "IMAGETOOL": "False",
        "STUDIOSTOOL": "False",
        "ENVIRONMENTTOOL": "False",
        "PERSONSTOOL": "False",
        "TRICKPLAYTOOL": "False",
        "INSTANTMIXTOOL": "False",
        "MOVIESTOOL": "False",
        "SYNCPLAYTOOL": "False",
        "STARTUPTOOL": "False",
        "UNIVERSALAUDIOTOOL": "False",
        "USERTOOL": "False",
        "MUSICGENRESTOOL": "False",
        "SUGGESTIONSTOOL": "False",
        "TIMESYNCTOOL": "False",
        "ARTISTSTOOL": "False",
        "SYSTEMTOOL": "False",
        "LOCALIZATIONTOOL": "False",
        "ITEMUPDATETOOL": "False",
        "LIBRARYSTRUCTURETOOL": "False",
        "MEDIAINFOTOOL": "False",
        "QUICKCONNECTTOOL": "False",
        "VIDEOSTOOL": "False",
        "REMOTEIMAGETOOL": "False",
        "PLAYSTATETOOL": "False",
        "APIKEYTOOL": "False",
        "DEVICESTOOL": "False",
        "FILTERTOOL": "False",
        "BRANDINGTOOL": "False",
        "GENRESTOOL": "False",
        "USERVIEWSTOOL": "False",
        "YEARSTOOL": "False",
        "LYRICSTOOL": "False",
        "TRAILERSTOOL": "False",
        "ACTIVITYLOGTOOL": "True",
        "PACKAGETOOL": "False",
        "SUBTITLETOOL": "False",
        "PLAYLISTSTOOL": "False",
        "USERLIBRARYTOOL": "False",
        "CONFIGURATIONTOOL": "False",
        "ITEMSTOOL": "False",
        "ITEMLOOKUPTOOL": "False"
      }
    }
  }
}
```

## CLI Usage

```bash
# List all resources (example)
python mcp_client.py jellyfin-mcp help
```
